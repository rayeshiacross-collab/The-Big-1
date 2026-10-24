# Frozen research → complete assigned writing

This repair completes the missing entrypoints for an existing evidence batch. It does not install a live-source discovery schedule, a model server, Hermes, credentials, or a video rendering host. New incoming evidence stays in another edition. No publication command exists here.

## Runtime

Use Python 3.11+, the existing requirements, an installed Hermes CLI and a local OpenAI-compatible model server with the configured tool-capable model. `config/text_tools.example.json` is an example, not a working machine configuration. The text-only doctor checks the actual executable, required isolated CLI flags and model inventory; it does not require speech/render/perception tools or prove inference quality.

Set the same persistent `LEDGER_PATH`, `HANDOFF_PATH`, `OUTPUT_PATH` and `MACHINE_LEDGER_PATH` in all three checkouts. Set `HUB_ROOT` in the lane adapters to the repaired The-Big-1 checkout. Keep model access loopback-only. No hosted GitHub runner can use another machine's loopback.

Storage requires a machine-owned OAuth access token in `GOOGLE_DRIVE_ACCESS_TOKEN`, a `RESEARCH_DRIVE_FOLDER_ID` under the existing Daily Intelligence location, and a `WRITING_DRIVE_FOLDER_ID` for finished writing. These IDs are explicit and no folder is invented. The token must allow Drive file list, create and media readback for those folders. It is not logged or passed to Hermes. Token refresh/login setup remains machine-owned; expiry fails closed, and a refreshed token can resume without regenerating validated text.

Drive upload uses appProperties identity plus filename and SHA256, reuses identical objects, rejects ambiguous/conflicting objects, and reads the returned media back before completion. It never overwrites or deletes remote files. This is a real REST adapter, not the existing local-only placeholder helper. Readback proves stored bytes, not research truth or creative quality.

## Existing evidence input

`sources.json` describes already-collected UTF-8 source snapshots beside the packet. Source paths must stay under the packet's directory. Include actual source URLs/dates, limitations and SHA256 of the exact supplied bytes:

```json
{
  "edition_date": "2026-10-24",
  "sources": [{
    "id": "source1",
    "url": "https://PRIMARY_SOURCE/PAGE",
    "published_at": "2026-10-23",
    "observed_at": "2026-10-24T00:00:00-05:00",
    "claim_limitation": "State exactly what this document does and does not establish",
    "text_path": "source1.txt",
    "sha256": "ACTUAL_SHA256_OF_SOURCE1_TXT"
  }]
}
```

This schema is not production evidence. Do not copy placeholder hashes, URLs or dates into a real run. Supply a nonempty catalog snapshot too. Hermes reviews supplied snapshots and reports exact source quotations; `checked` means snapshot-reviewed, explicitly not a fresh verification of today's web page. Unchecked upstream collection, fabricated quotes and missing live statistics cannot become verified facts through this wrapper. Inadequate evidence must block rather than pad ten topics with duplicates.

## Commands

Run on the actual machine, with real paths/configuration:

```bash
python -m src.text_rotation doctor --tools /machine/text_tools.json
python -m src.text_rotation research --run-id 20261024-0600-central --sources /batch/sources.json --catalog /batch/catalog.txt --tools /machine/text_tools.json
python -m src.text_rotation write --lane psychology --content-id psych-20261024-CHOSEN-SLUG --tools /machine/text_tools.json
python -m src.text_rotation write --lane system-glitch --content-id glitch-20261024-CHOSEN-SLUG --tools /machine/text_tools.json
```

Use the actual lowercase IDs returned by research; the uppercase slugs above are explanatory placeholders and intentionally invalid. The run ID date must match the frozen edition, and source observations use Central-date boundaries. The private Master Research `daily` adapter calls research; `sunday` additionally requires an evidence-based Sunday section and must state when authenticated analytics are unavailable. It does not fabricate private YouTube metrics. Sunday and daily modes cannot replace the same frozen edition.

Research output is `OUTPUT_PATH/research/RUN_ID/`: immutable `evidence.json`, validated `report.json` (signals, exactly ten distinct ranked candidates with 15 fields, source checks, catalog comparison, market uncertainty and two assignments), frozen `handoffs.json`, and private timestamped Hermes attempts/logs. Only after real Drive readback are handoffs saved under `HANDOFF_PATH` and `RESEARCH_COMPLETE` ledger events appended. The completion ledger binds SHA256 digests of evidence, report and both manifests; writers reject changed files before claiming or invoking Hermes. Repeating the same edition reuses report output and reconciles storage without invoking Hermes again; changed inputs fail and preserve originals.

Psychology assigned writing produces the full flagship, three distinct Shorts, companion article, essay specification, titles/thumbnail packages, architecture, comment question and content chain. The companion gate requires 900–1500 words, flagship 1300–1500. The existing Psychology `src/runner.py` script-to-video commands are unchanged; `src/assignment_runner.py` is the new assigned-writing entrypoint.

System Glitch produces narration, four-beat concrete scene plan with captions, packaging, sourced claims and timing estimate. Its new 25–35 second script gate uses 63–87 words at 150 words/minute. That is an estimate, not rendered-audio measurement. The legacy 11-second format is not generated by this entrypoint.

Writers claim only existing source-verified assignments in their fixed lane. Completed writing is reused; interrupted claims require explicit `--resume`, after checking the prior process stopped. A per-content process lock prevents concurrent resumption on the shared filesystem. Failed attempts stay on disk. A hash-bound validated-attempt pointer is saved before copying any assets, so a partially copied package resumes from those exact files without a second model generation. Validated saved assets are reused after an upload failure; they are not regenerated just to refresh a credential. No automatic claim deletion or crash recovery guesses.

Before `WRITING_COMPLETE`, the full required package must pass quality gates, a hash-bound Hermes writing review, and Drive readback of assets, evidence and review. A receipt checks identity/content consistency, not reviewer honesty. No video has been produced, inspected or approved by a writing status. Video production and owner review remain separate later steps.

## Validation and handoff

`python -m unittest discover -s tests -v` runs existing hub/media tests and synthetic research, Hermes, review and Drive protocol fixtures. These test contracts, not live source research or real agent review. Adapter CI tests use a synthetic hub. Real preflight in this repair workspace failed because Hermes is absent; the configured local model port is also unavailable. No real edition was claimed or rendered. All changes remain reviewable repair branches; no merge/deploy/delete/visibility change is performed.
