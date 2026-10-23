# Script-only Hermes production

Owner direction: read the script, inspect it, create the video independently, inspect/fix it, then deliver for owner inspection. The operator does not author scenes or feed scene ideas.

## Actual entrypoint

`python -m src.autonomous_video --content-id psych-20261022-example --script /production/script.txt --policy /machine/standing_policy.json --tools /machine/local_tools.json`

The only creative input is a plain narration TXT. JSON scene jobs, previous assistant scene directions, draft titles/tags and hand-authored plans are not consumed. Standing policy supplies the existing brand/style, voice-selection limits, output format and licenses. Configure policy once per show; it must not contain scene/storyboard keys. An exact voice can be locked with voice.mode=locked plus engine/voice_id; autonomous_local lets Hermes select from available free local engines. High Thoughts' separate locked voices must not be replaced with a Psychology profile.

The Psychology lane runner delegates to this entrypoint; the private Harvest queue supplies script paths only. Existing scene jobs are preserved as legacy reference, not active creative input.

## What the code does

1. Records actual use in the machine's own usage ledger and creates a unique attempt directory.
2. Checks for Hermes, FFmpeg, a loopback local model configuration and explicitly registered local speech, render, video_review and audio_review tools. The example tool file is intentionally empty; it is not a working installation or permission to invent tools.
3. Invokes the actual documented Hermes one-shot CLI with an isolated home, local custom provider, no inherited credential/proxy environment and terminal/file tools only. There is no --yolo, shell interpolation, paid gateway, plugin profile, legacy memory or publishing tool in the invocation.
4. Hermes reads/inspects the narration and independently creates its plan, production code/assets, voice, animation, caption files, thumbnail and YouTube package using installed tools. Missing capabilities must produce blocked.json. The wrapper does not replace Hermes with an LLM JSON response, predefined phone/hourglass scene or static renderer.
5. Requires actual artifact files, exact source identity and narration, scene coverage, H.264 dimensions/audio track, full FFmpeg decode, temporal motion, source-matched readable SRT, thumbnail and YouTube metadata/disclosure fields.
6. Requires Hermes's own final video QA plus registered perception-tool receipts covering the entire video AND audio and bound to the actual hashes. Frame sampling or ASR alone cannot be called full playback review. Missing perception keeps the output blocked. Self-attestations and receipts are an integration contract, not cryptographic proof of reviewer honesty; actual semantic review remains essential.
7. Returns deterministic defects to Hermes for up to three repairs, retaining failed attempts. It never supplies creative fixes. Successful validated output becomes READY_FOR_OWNER_INSPECTION, not human-approved or published.

Each final package includes final.mp4, narration.wav, narration.txt, captions.srt, thumbnail.jpg, youtube.json, Hermes's own plan, self_qa.json, actual review-tool receipts, verified_delivery.json and private agent logs. Captions must also be burned into the MP4; the visual self-check must verify them because text-file validation alone cannot prove that rendering step.

## Runtime setup, not a second creative brief

Copy the two example config files to a machine-owned persistent directory and replace runtime placeholders with installed components. `local_tools` is a list of {name, executable, args, capability, license, optional endpoint}. Executable/args describe real installed tools; capabilities must include speech, render, video_review and audio_review. Expose local ComfyUI/Wan through its installed wrapper or allow Hermes's own code to call it; workflow/model paths are operational inputs, never preselected scenes. Review tools must actually consume the final medium and emit their measured receipts; a hand-written report or test fixture is not a production review.

Hermes and model weights are NOT installed by this feature. A model/server can still be missing even when its configuration is valid. No public Ollama endpoint or paid service is needed or authorized. CLI help options are checked before launching; incompatible Hermes versions stop explicitly. The agent runs trusted local tools, not an OS sandbox; the isolated environment removes inherited credentials but is not a complete network/filesystem security boundary.

The production directory and machine ledger must be on persistent storage. This code does not provision hardware, register a self-hosted runner, launch a daemon, deploy credentials, or create a background render. Run status says BLOCKED_OR_FAILED on missing prerequisites and leaves counts of completed production videos at zero.

## Validation

Regression tests cover source-only prompts, rejecting legacy plan config/JSON input, local endpoint checks, credential isolation, missing runtime logging, actual FFmpeg fixture decode/motion/captions/metadata, missing full-audio review evidence, and a two-attempt repair loop. The agent/QA are synthetic fixtures in those tests, explicitly not evidence that Hermes generated or watched a real production video. Run the suite with FFmpeg installed; live generation requires the actual runtime.

Official CLI reference used for invocation: https://github.com/NousResearch/hermes-agent/blob/main/website/docs/reference/cli-commands.md
