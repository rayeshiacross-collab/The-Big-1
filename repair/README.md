# The-Big-1 Repair Package

Keep The-Big-1 as the control plane. Repair the existing production path.

This package contains everything mapped from the current hub so you can move from inspection to a real end-to-end video test without building a competing engine.

## Contents

```
repair/
├── README.md
├── config/
│   ├── standing_policy.json     # ready-to-use standing identity/format policy
│   └── local_tools.json         # template — replace every REPLACE_* entry
├── scripts/
│   ├── drive_verifier.py        # minimal Google Drive upload+readback adapter
│   └── dry_run.sh               # end-to-end command sequence
└── docs/
    └── OPERATOR_CHECKLIST.md    # ordered steps + hard rules
```

## Quick start

1. Read `docs/OPERATOR_CHECKLIST.md`
2. Install Hermes + local model + four real tools on a persistent machine
3. Fill `config/local_tools.json` (the empty list is the current primary breakage)
4. Run `scripts/dry_run.sh` from a The-Big-1 checkout

Success ends at `READY_FOR_OWNER_INSPECTION`. Nothing publishes.

## Status of the hub itself

- Shared claiming, ledger, open-stack guards, writing gates, and the autonomous video entrypoint are implemented and regression-tested.
- Missing pieces are external: real tool binaries, perception receipts, Drive adapter, and lane-runtime wiring.
- No overnight render or repository changes were performed by generating this package beyond this overlay.
