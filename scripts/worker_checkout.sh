#!/usr/bin/env bash
# Sourced by the installer; refuses to modify preexisting dirty checkouts.
worker_checkout() {
  local url=$1 dest=$2 commit=$3 fresh=0
  if [ ! -e "$dest" ]; then
    git clone --depth 1 --no-checkout "$url" "$dest" || return
    fresh=1
  fi
  test "$(git -C "$dest" remote get-url origin)" = "$url" || return 2
  if [ "$fresh" -eq 0 ] && [ -n "$(git -C "$dest" status --porcelain)" ]; then
    echo "Refusing to overwrite changed checkout: $dest" >&2
    return 2
  fi
  git -C "$dest" fetch --depth 1 origin "$commit" || return
  git -C "$dest" checkout --detach "$commit" || return
  test "$(git -C "$dest" rev-parse HEAD)" = "$commit"
}
