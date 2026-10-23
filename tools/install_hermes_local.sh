#!/usr/bin/env bash
set -euo pipefail
# Reproducible official runtime dependency installation, no model/provider login.
install_root=${1:?Pass a machine-owned persistent runtime directory}
hermes_source_commit=bf0203a794a07aac3ff764972ab9087baa4e4f4e
command -v uv >/dev/null
command -v git >/dev/null
mkdir -p "$install_root"
hermes_checkout="$install_root/hermes-agent"
fresh_checkout=0
if [ ! -d "$hermes_checkout/.git" ]; then
  if [ -e "$hermes_checkout" ]; then echo 'Destination exists and is not a Git checkout' >&2; exit 2; fi
  fresh_checkout=1
  git clone --depth 1 --no-checkout https://github.com/NousResearch/hermes-agent.git "$hermes_checkout"
fi
[ "$(git -C "$hermes_checkout" remote get-url origin)" = 'https://github.com/NousResearch/hermes-agent.git' ]
if [ "$fresh_checkout" -eq 0 ] && [ -n "$(git -C "$hermes_checkout" status --porcelain)" ]; then
  echo 'Runtime checkout contains changes; preserve and review them before installation' >&2; exit 2
fi
git -C "$hermes_checkout" fetch --depth 1 origin "$hermes_source_commit"
git -C "$hermes_checkout" checkout --detach "$hermes_source_commit"
(cd "$hermes_checkout" && uv sync --python 3.14.8 --frozen --no-dev)
printf 'Installed official Hermes at %s\n' "$hermes_checkout/.venv/bin/hermes"
printf 'No model, speech/render/review stack, worker or publishing connection was started.\n'
