# content_id Rules

Format: `{lane-short}-{YYYYMMDD}-{short-slug}`

Examples:
- `psych-20261022-autonomy-cost`
- `glitch-20261022-instant-money`
- `hypit-20261022-autonomy-cost-pack`
- `omni-20261022-autonomy-cost-rss`

Rules:
1. Generated once
2. Never reused for a different subject
3. On retry, retain the same content_id. An active claim rejects a second claimant; use token-checked abandon only after stopping the old worker. Completed/approved work cannot be re-claimed.
4. All downstream assets carry the same root content_id
5. Ledger and Drive paths always include it

Enforced prefixes: psych, glitch, hypit, omni. Dates must exist; slugs are lowercase alphanumeric words separated by hyphens. Run IDs are validated calendar timestamps in YYYYMMDD-HHMM-central format. `target_lane: any` is rejected.
