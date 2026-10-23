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
3. On retry, the same content_id is re-claimed
4. All downstream assets carry the same root content_id
5. Ledger and Drive paths always include it
