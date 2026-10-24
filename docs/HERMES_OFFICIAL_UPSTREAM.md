# Official Hermes upstream (source-first)

Source: https://github.com/NousResearch/hermes-agent
Docs: https://hermes-agent.nousresearch.com/docs

The-Big-1's production entrypoint remains `python -m src.autonomous_video`. Do not replace it with a simulated renderer.

To retrieve the **actual upstream source**, run from repository root:

```bash
bash scripts/fetch_official_hermes.sh
# For a reproducible build, set HERMES_REF to an audited tag or commit SHA.
```

This fetches the official repository into `vendor/hermes-agent`, records the upstream commit, and refuses to overwrite an existing directory. The upstream source is **not yet copied into this branch**, installed, executed, or validated. The fetch script requires a machine with git/network access. Do not run an unreviewed upstream installer with inherited secrets. No publishing or paid services are enabled. Existing engine and content remain unchanged.

Next gate: run this fetch on the intended worker, inspect official installation/runtime instructions, install its pinned revision, configure model and licensed speech/render/review tools, and produce one real private MP4 with full QA.
