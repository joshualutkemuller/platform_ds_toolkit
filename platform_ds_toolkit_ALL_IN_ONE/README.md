
# platform-ds-toolkit

A unified, platform-oriented Python toolkit designed for day-one productivity
in institutional data science roles.

## Included systems
- Encrypted credential vault (flexible secrets + metadata)
- IO (CSV / Parquet / Excel / JSON)
- Archival with checksum + manifests
- Data validation guardrails
- Task & pipeline orchestration
- Notifications (SMTP, safe dry-run)
- Feature store (versioned, metadata-backed)
- Model store (artifact-based)
- Registry (name → artifact indirection)
- Lineage tracking
- Data shaping / manipulation
- Batching utilities
- Multiprocessing helpers (Windows-safe)

## Install
```bash
pip install -e .
```

## Philosophy
Artifacts > scripts. Determinism > convenience. Simplicity > buzzwords.
