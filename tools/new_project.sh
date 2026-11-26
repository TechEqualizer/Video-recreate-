#!/usr/bin/env bash
# Scaffold projects/<slug>/ and bring in reference videos.
# Usage: bash tools/new_project.sh <slug> [video ...]   (no videos: moves everything in inbox/)
set -euo pipefail
cd "$(dirname "$0")/.."
slug="${1:?usage: new_project.sh <slug> [video ...]}"; shift || true
p="projects/$slug"
mkdir -p "$p"/{refs,style,shots,renders}
[ -f "$p/brief.md" ] || cat > "$p/brief.md" <<MD
# $slug

- References:
- Brand:
- Likeness:
- Mode: close / inspired
- Format (length, aspect, channel):
- Job (product, offer, CTA):
- Decisions Dw still owns:
MD
if [ "$#" -gt 0 ]; then
  cp -n "$@" "$p/refs/"
else
  shopt -s nullglob nocaseglob
  for f in inbox/*.{mp4,mov,m4v,webm,mkv}; do mv -n "$f" "$p/refs/"; done
fi
ls -1 "$p/refs"
