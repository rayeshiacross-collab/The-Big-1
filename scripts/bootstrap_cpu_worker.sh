#!/usr/bin/env bash
set -euo pipefail
# Official, pinned upstreams. No provider login, paid service, or publishing.
root=$(realpath -m "${1:?Pass an installation directory}")
repo=$(cd "$(dirname "$0")/.." && pwd)
hermes_sha=bf0203a794a07aac3ff764972ab9087baa4e4f4e
llama_sha=6b9ba4f2e8c1436511956f0b3c309e2c9e642071
mkdir -p "$root/models"
command -v uv >/dev/null
command -v ffmpeg >/dev/null
command -v ffprobe >/dev/null

source "$repo/scripts/worker_checkout.sh"

worker_checkout https://github.com/NousResearch/hermes-agent.git "$root/hermes-agent" "$hermes_sha"
(cd "$root/hermes-agent" && uv sync --python 3.14.8 --frozen --no-dev)
uv venv --python 3.14.8 --allow-existing "$root/worker-env"
uv pip install --python "$root/worker-env/bin/python" -r "$repo/requirements.txt" \
  piper-tts==1.8.0 cmake==4.4.4 ninja==1.13.2
export PATH="$root/worker-env/bin:$PATH"
worker_checkout https://github.com/ggml-org/llama.cpp.git "$root/llama.cpp" "$llama_sha"
cmake -S "$root/llama.cpp" -B "$root/llama.cpp/build" -G Ninja \
  -DGGML_CUDA=OFF -DGGML_NATIVE=OFF -DLLAMA_CURL=OFF \
  -DLLAMA_BUILD_TESTS=OFF -DLLAMA_BUILD_EXAMPLES=OFF -DLLAMA_BUILD_SERVER=ON \
  -DCMAKE_BUILD_TYPE=Release
cmake --build "$root/llama.cpp/build" --target llama-server -j 4

download() {
  local url=$1 dest=$2 digest=$3
  if [ -f "$dest" ] && echo "$digest  $dest" | sha256sum --check --status; then return; fi
  curl --fail --location --retry 2 --max-time 600 "$url" -o "$dest.part"
  echo "$digest  $dest.part" | sha256sum --check
  mv "$dest.part" "$dest"
}

download https://huggingface.co/unsloth/Qwen3-4B-Instruct-2507-GGUF/resolve/main/Qwen3-4B-Instruct-2507-Q4_K_M.gguf \
  "$root/models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf" 3605803b982cb64aead44f6c1b2ae36e3acdb41d8e46c8a94c6533bc4c67e597
voice_base=https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/ljspeech/high
download "$voice_base/en_US-ljspeech-high.onnx" "$root/models/en_US-ljspeech-high.onnx" \
  5d4f08ba6a2a48c44592eed3ce56bf85e9de3dd4e20df90541ae68a8310c029a
download "$voice_base/en_US-ljspeech-high.onnx.json" "$root/models/en_US-ljspeech-high.onnx.json" \
  7e1f4634af596d83cca997fb7a931ba80b70f8a316a2655ee69c55365e0ace14
curl --fail --location --retry 2 "$voice_base/MODEL_CARD" -o "$root/models/ljspeech_MODEL_CARD"
curl --fail --location --retry 2 https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507/raw/main/LICENSE -o "$root/models/QWEN_LICENSE"

"$root/worker-env/bin/python" - "$root" "$hermes_sha" "$llama_sha" <<'PY'
import json,sys
from pathlib import Path
r=Path(sys.argv[1])
runtime=dict(hermes_executable=str(r/'hermes-agent/.venv/bin/hermes'),model_server=str(r/'llama.cpp/build/bin/llama-server'),
             model='Qwen3-4B-Instruct-2507-Q4_K_M.gguf',model_path=str(r/'models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf'),context_tokens=65536,
             piper=str(r/'worker-env/bin/piper'),voice_path=str(r/'models/en_US-ljspeech-high.onnx'),
             hermes_commit=sys.argv[2],llama_commit=sys.argv[3])
(r/'worker.json').write_text(json.dumps(runtime,indent=2)+'\n')
tools=dict(hermes_executable=runtime['hermes_executable'],model=runtime['model'],model_base_url='http://127.0.0.1:11434/v1',
 local_tools=[dict(name='piper',executable=runtime['piper'],args=['--model',runtime['voice_path']],capability='speech',license='Piper GPL-3.0; LJ Speech dataset public domain'),
              dict(name='ffmpeg',executable='/usr/bin/ffmpeg',args=[],capability='render',license='GPL, installed distribution')],
 timeout_seconds=3600,max_repair_attempts=2)
(r/'media-tools.json').write_text(json.dumps(tools,indent=2)+'\n')
print('Installed runtime manifest:',r/'worker.json')
print('Full playback review tools are not installed or represented by this bootstrap.')
PY
