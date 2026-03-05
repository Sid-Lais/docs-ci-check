# Documentation CI/CD Checks

Automated validation for documentation changes using GitHub Actions.

## What This Repository Uses

- Workflow: `.github/workflows/doc-checks.yml`
- Scripts:
  - `scripts/validate_docs.py`
  - `scripts/validate_images.py`
  - `scripts/check_placeholders.py`
  - `scripts/validate_assets.py`
- Docs page for CI testing: `docs/aws-integration.md`

## Validation Rules

### 1) Image Naming

Required format:
```
AMNIC_DASHBOARD_NAME.{png|jpg|jpeg|gif}
```

Examples:
- ✅ `AMNIC_DASHBOARD_MAIN.png`
- ✅ `AMNIC_SETTINGS_PAGE_ALERTS.jpg`
- ❌ `dashboard-main.png`

### 2) Placeholders

Allowed placeholder format:
```
[PLACEHOLDER IMAGE|TABLE|CONTENT NAME_OF_ITEM]
```

Examples:
- ✅ `[PLACEHOLDER IMAGE DASHBOARD_SCREENSHOT]`
- ✅ `[PLACEHOLDER TABLE USER_ROLES]`
- ✅ `[PLACEHOLDER CONTENT INTEGRATION_GUIDE]`
- ❌ `{{ placeholder }}`
- ❌ `[[PLACEHOLDER]]`

### 3) Draft Markers

Reserved marker:
```
[DRAFT/TO-DO, CHANGE]
```

If present in PR content, the check fails until removed.

### 4) Asset References

- Markdown/HTML file references are validated.
- Missing files in `images/`, `assets/`, or `docs/` fail checks.

### 5) Reviewer Approval

- At least one reviewer approval is required before merge.

## PR Flow

1. Commit docs changes and open a PR.
2. Workflow runs all checks automatically.
3. Fix any reported issues and push again.
4. Merge only after all checks pass and review is approved.

## Local Run

```bash
python scripts/validate_docs.py
python scripts/validate_images.py
python scripts/check_placeholders.py
python scripts/validate_assets.py
```

## Common Failures

- Invalid image filename → rename to `AMNIC_...` format
- Invalid placeholder syntax → use `[PLACEHOLDER TYPE NAME]`
- `[DRAFT/TO-DO, CHANGE]` left in content → remove before merge
- Missing referenced file → add file or fix the reference path
