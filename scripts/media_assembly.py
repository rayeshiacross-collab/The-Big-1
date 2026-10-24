"""Mechanical local media assembly. All creative scene code/copy comes from Hermes.

speech --script input_script.txt --voice MODEL: writes exact narration.txt,
  narration.wav, captions.srt and timing.json (paragraph and phrase intervals).
encode --visual VIDEO --thumbnail-at SECONDS --content-id ID:
  combines a Hermes-rendered silent video with existing narration/captions,
  extracts Hermes's chosen thumbnail frame and writes production_manifest.json.
  Requires Hermes-authored hermes_plan.json and youtube.json already present.
No perception receipt, self-QA, release approval or publishing is performed.
"""
import argparse, hashlib, json, re, subprocess, textwrap, wave
from pathlib import Path


def caption_lines(text):
    return textwrap.wrap(text,width=55,break_long_words=False,break_on_hyphens=False)


def caption_phrases(text):
    phrases=[];current=[]
    for word in text.split():
        candidate=' '.join(current+[word])
        if current and (len(caption_lines(candidate))>2 or len(candidate)>88):
            phrases.append(' '.join(current));current=[]
        current.append(word)
        if re.search(r'[.!?]["\u201d\u2019]?$' ,word):
            phrases.append(' '.join(current));current=[]
    if current:phrases.append(' '.join(current))
    if any(len(line)>55 for phrase in phrases for line in caption_lines(phrase)):
        raise ValueError('Source contains a word too long for readable captions')
    return phrases


def stamp(seconds):
    ms=round(seconds*1000);s,ms=divmod(ms,1000);m,s=divmod(s,60);h,m=divmod(m,60)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'


def save(name,data):
    Path(name).write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')


def speech(script,voice):
    from piper import PiperVoice, SynthesisConfig
    text=script.read_text(encoding='utf-8')
    if not text.strip():raise ValueError('Empty narration')
    v=PiperVoice.load(str(voice));rate=v.config.sample_rate
    settings=SynthesisConfig(volume=.7,length_scale=1.05)
    phrases=[];paragraphs=[];samples=0;cue=0;srt=[]
    with wave.open('narration.wav','wb') as out:
        out.setnchannels(1);out.setsampwidth(2);out.setframerate(rate)
        for i,paragraph in enumerate(re.split(r'\n\s*\n',text.strip())):
            begin=samples/rate
            for phrase in caption_phrases(paragraph):
                start=samples/rate
                for chunk in v.synthesize(phrase,settings):
                    data=chunk.audio_int16_bytes;out.writeframes(data);samples+=len(data)//2
                end=samples/rate
                if end<=start:raise ValueError('Speech engine produced empty phrase')
                phrases.append(dict(text=phrase,start=start,end=end));cue+=1
                srt.append(f'{cue}\n{stamp(start)} --> {stamp(end)}\n'+ '\n'.join(caption_lines(phrase)))
                pause=round(.12*rate);out.writeframes(b'\0\0'*pause);samples+=pause
            paragraphs.append(dict(index=i,text=paragraph,start=begin,end=samples/rate,duration=samples/rate-begin))
    Path('narration.txt').write_text(text,encoding='utf-8')
    Path('captions.srt').write_text('\n\n'.join(srt)+'\n',encoding='utf-8')
    save('timing.json',dict(duration=samples/rate,paragraphs=paragraphs,phrases=phrases,
                           voice=dict(engine='piper',voice_id=voice.name)))
    print(json.dumps(dict(status='SPEECH_SYNTHESIZED_NOT_REVIEWED',duration=samples/rate,paragraphs=paragraphs)))


def duration(path):
    return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(path)]))


def encode(visual,thumbnail_at,content_id):
    for name in ('narration.wav','narration.txt','captions.srt','hermes_plan.json','youtube.json','standing_policy.json'):
        if not Path(name).is_file():raise ValueError('Missing '+name)
    policy=json.loads(Path('standing_policy.json').read_text());d=duration('narration.wav')
    if not 0<=thumbnail_at<d:raise ValueError('Thumbnail timestamp outside video')
    if abs(duration(visual)-d)>.2:raise ValueError('Render duration must match timing.json within 0.2 seconds')
    width,height=policy['dimensions'];fps=policy.get('fps',24)
    subprocess.run(['ffmpeg','-v','error','-y','-i','captions.srt','captions.ass'],check=True)
    ass=Path('captions.ass').read_text(encoding='utf-8')
    ass=re.sub(r'PlayResX: \d+',f'PlayResX: {width}',ass)
    ass=re.sub(r'PlayResY: \d+',f'PlayResY: {height}',ass)
    Path('captions.ass').write_text(ass,encoding='utf-8')
    font=round(height*.045);margin=round(height*.067)
    vf=f"scale={width}:{height},subtitles=captions.ass:force_style='FontName=DejaVu Sans,FontSize={font},Outline=3,MarginV={margin}'"
    subprocess.run(['ffmpeg','-v','error','-y','-i',str(visual),'-i','narration.wav','-map','0:v:0','-map','1:a:0','-vf',vf,'-r',str(fps),'-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-t',str(d),'-movflags','+faststart','final.mp4'],check=True)
    subprocess.run(['ffmpeg','-v','error','-y','-ss',str(thumbnail_at),'-i','final.mp4','-frames:v','1','-q:v','2','thumbnail.jpg'],check=True)
    mapping=dict(video='final.mp4',audio='narration.wav',captions='captions.srt',thumbnail='thumbnail.jpg',metadata='youtube.json',plan='hermes_plan.json',narration='narration.txt')
    save('production_manifest.json',dict(content_id=content_id,source_sha256=hashlib.sha256(Path('narration.txt').read_bytes()).hexdigest(),files=mapping))
    print('ASSEMBLED_NOT_REVIEWED: final.mp4. Run the existing validator; full playback review is still required.')


def main():
    p=argparse.ArgumentParser(description=__doc__);commands=p.add_subparsers(dest='command',required=True)
    s=commands.add_parser('speech');s.add_argument('--script',type=Path,required=True);s.add_argument('--voice',type=Path,required=True)
    e=commands.add_parser('encode');e.add_argument('--visual',type=Path,required=True);e.add_argument('--thumbnail-at',type=float,required=True);e.add_argument('--content-id',required=True)
    a=p.parse_args()
    if a.command=='speech':speech(a.script,a.voice)
    else:encode(a.visual,a.thumbnail_at,a.content_id)


if __name__=='__main__':main()
