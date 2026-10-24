# Perception receipt contract (exact hub requirements)

The autonomous video validator rejects any package that lacks full video **and** full audio perception receipts. Frame sampling or ASR alone is insufficient.

## 1. self_qa.json (Hermes writes this)

```json
{
  "reviewer": "Hermes",
  "content_id": "psych-YYYYMMDD-slug",
  "stage": "video",
  "verdict": "PASS",
  "reviewed_at": "2026-10-23T20:00:00-05:00",
  "unresolved_issues": [],
  "watched_full_video": true,
  "listened_full_audio": true,
  "artifact_sha256": {
    "final.mp4": "<sha256 of final.mp4>",
    "narration.wav": "<sha256>",
    "captions.srt": "<sha256>",
    "thumbnail.jpg": "<sha256>",
    "youtube.json": "<sha256>",
    "hermes_plan.json": "<sha256>",
    "narration.txt": "<sha256>"
  },
  "checks": {
    "narration":          { "status": "PASS", "evidence": "concrete observation + timestamps" },
    "visible_action":     { "status": "PASS", "evidence": "..." },
    "captions":           { "status": "PASS", "evidence": "..." },
    "timing":             { "status": "PASS", "evidence": "..." },
    "sound":              { "status": "PASS", "evidence": "..." },
    "continuity":         { "status": "PASS", "evidence": "..." },
    "technical_export":   { "status": "PASS", "evidence": "..." },
    "thumbnail":          { "status": "PASS", "evidence": "..." },
    "youtube_metadata":   { "status": "PASS", "evidence": "..." }
  },
  "perception_evidence": [
    {
      "path": "receipts/video_review.json",
      "sha256": "<sha256 of that receipt file>",
      "tool": "video-perception-review",
      "modality": "video"
    },
    {
      "path": "receipts/audio_review.json",
      "sha256": "<sha256 of that receipt file>",
      "tool": "audio-perception-review",
      "modality": "audio"
    }
  ]
}
```

Rules enforced by `src/self_qa.py` + `validate_package`:
- `reviewer` must be `"Hermes"`
- `verdict` must be `"PASS"`
- `unresolved_issues` must be `[]`
- `reviewed_at` must be timezone-aware ISO-8601
- `artifact_sha256` must match the actual delivered files byte-for-byte
- all nine checks must have `status: PASS` and non-empty evidence strings
- `watched_full_video` and `listened_full_audio` must be the Python boolean `true`

## 2. Tool receipt files (review tools emit these)

Each entry in `perception_evidence` points at a JSON file on disk. That file must contain:

```json
{
  "artifact_sha256": "<sha256 of the media file that was reviewed>",
  "duration_seconds": 32.4,
  "reviewed_seconds": 32.4,
  "coverage": [[0.0, 32.4]]
}
```

| Field | Rule |
|-------|------|
| `artifact_sha256` | Must equal the SHA of `final.mp4` (video) or `narration.wav` (audio) |
| `duration_seconds` | Within 0.2 s of the actual media duration |
| `reviewed_seconds` | ≥ duration − 0.05 |
| `coverage` | List of `[start, end]` segments that form continuous coverage of the full duration (gaps > 0.05 s fail; end must reach duration − 0.05) |

## 3. Tool registration link

In `local_tools.json` the tool `name` used in the receipt must match a registered tool whose `capability` is exactly:

- `video_review` for modality `"video"`
- `audio_review` for modality `"audio"`

Example:

```json
{
  "name": "video-perception-review",
  "executable": "/machine/bin/video-review-wrapper",
  "args": ["--full-playback", "--emit-receipt"],
  "capability": "video_review",
  "license": "Open / local only"
}
```

If the tool name in the receipt is not registered, or its capability does not match `{modality}_review`, validation fails with:

`Perception evidence uses an unregistered review tool`

## 4. Minimal wrapper shape (illustrative)

A review wrapper only needs to:

1. Accept the media path
2. Actually process the full duration (not sample frames only)
3. Write a receipt JSON with the four required fields
4. Exit 0

Hermes is responsible for calling the registered tools and attaching the receipts to `self_qa.json`. The hub only validates structure, hashes, and continuous coverage.

## 5. What fails closed

- Missing video or audio receipt
- Receipt SHA does not match file on disk
- Tool not registered / wrong capability
- Coverage has gaps or does not reach full duration
- `watched_full_video` / `listened_full_audio` not true
- Any of the nine checks missing or not PASS
- artifact hashes stale (file changed after review)
