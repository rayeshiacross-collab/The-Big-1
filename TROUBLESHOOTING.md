# Troubleshooting — Read This Before Crying

## 1. “It said success but nothing is in Drive”
- A green GitHub Action is not completion.
- Check the ledger for the content_id.
- Confirm the quality gate actually passed.
- Confirm the Drive path in the ledger matches reality.

## 2. “It made a second episode for the same topic”
- content_id was not re-claimed on retry.
- Run the recovery-resume skill.
- Never let a runner invent a new content_id for an existing assignment.

## 3. “Model is slow / out of memory”
- Drop to a smaller quant or smaller model (see LOCAL_MODELS.md).
- Use the workhorse model for daily work; reserve large models for hard ranking or complex explanations.

## 4. “Hermes tried to call a paid API”
- ALLOW_PAID_APIS must be 0.
- Check .env and Hermes provider config.
- Doctor skill should catch this before the run.

## 5. “Partial script was marked complete”
- Quality gate was skipped or bypassed.
- Re-run the quality-gate skill; it must fail closed.

## 6. “Sunday early-warning has no metrics”
- Only public / authenticated metrics you actually have access to.
- If metrics are missing, say so — do not invent numbers.

## 7. “Video package doesn’t match the cyborg”
- video-from-script must reference the approved asset only.
- No redesign, no mirroring.
- Re-run with the hard visual rules enforced.

## 8. “I don’t know what state anything is in”
- Open the ledger first.
- Status vocabulary is global and mandatory.
- If the ledger is missing, treat the work as incomplete.

## Golden rule
When in doubt, re-run the doctor skill, then recovery-resume, then the quality gate. Do not start new work on top of a broken state.
