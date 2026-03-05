# Documentation CI/CD Checks

Automated validation for all documentation commits using GitHub Actions.

## Quick Start

1. **GitHub Actions automatically runs on every PR**:
   - Validates image naming
   - Checks placeholders
   - Verifies asset references
   - Requires reviewer approval

2. **Fix errors** shown in PR comments and push again

## Naming Conventions

### Image Naming
```
✅ AMNIC_DASHBOARD_MAIN.png
✅ AMNIC_SETTINGS_PAGE_ALERTS.jpg
❌ dashboard-main.png
```

**Examples:**
- ❌ `dashboard-screenshot.png` → Wrong
- ✅ `AMNIC_DASHBOARD_MAIN.png` → Correct
- ✅ `AMNIC_SETTINGS_PAGE_ALERT.jpg` → Correct
- ✅ `AMNIC_WIDGET_CONFIRMATION_MODAL.gif` → Correct

### Placeholder Naming
Use this format for incomplete content:
```
[PLACEHOLDER IMAGE|TABLE|CONTENT NAME_OF_ITEM]
```

**Examples:**
- `[PLACEHOLDER IMAGE DASHBOARD_SCREENSHOT]`
- `[PLACEHOLDER TABLE USER_ROLES_COMPARISON]`
- `[PLACEHOLDER CONTENT INTEGRATION_GUIDE]`

### Draft Markers
Mark incomplete work:
```
[DRAFT/TO-DO, CHANGE]
```

---

## Document Structure

```
repo/
├── .github/
│   ├── workflows/
│   │   └── doc-checks.yml          # Main CI/CD workflow
│   └── CODEOWNERS
├── docs/
│   ├── guides/
│   │   └── getting-started.md
│   ├── features/
│   │   └── overview.md
│   └── README.md
├── images/
│   ├── AMNIC_DASHBOARD_MAIN.png
│   └── AMNIC_SETTINGS_PAGE.jpg
├── assets/
│   └── csv-export-data.csv
└── scripts/
    ├── validate_docs.py
    ├── validate_images.py
    ├── check_placeholders.py
    └── validate_assets.py
```

---

## Workflow Details

### Triggers
The workflow runs automatically on:
- **Pull Requests** to `main` branch (when files in `docs/`, `assets/`, or `images/` change)
- **Direct Commits** to `main` (blocks direct push)

### Checks Performed

#### 1. **Image Validation**
- ✅ Checks all `.png`, `.jpg`, `.jpeg`, `.gif` files
- ✅ Enforces naming convention: `AMNIC_DASHBOARD_NAME.ext`
- ❌ Fails if naming is incorrect

#### 2. **Placeholder Validation**
- ✅ Ensures all placeholders follow format: `[PLACEHOLDER TYPE NAME]`
- ✅ Detects invalid patterns: `{{ }}`, `[[ ]]`, `<TODO>`, etc.
- ❌ Fails if `[DRAFT/TO-DO, CHANGE]` markers are found
- ❌ Fails if malformed placeholders exist

#### 3. **Asset Reference Validation**
- ✅ Checks all image/asset references in markdown files
- ✅ Verifies referenced files exist
- ✅ Warns about unused assets
- ❌ Fails if missing references detected

#### 4. **Component Reference Validation**
- ✅ Validates component names: Vantage, Cloudzero, AWS, GCP, Azure
- ⚠️ Warns if components mentioned without proper context

#### 5. **Reviewer Approval**
- ✅ Requires at least 1 approval (Aniket)
- ❌ Blocks merge if no approvals

---

## PR Workflow

1. **Developer creates PR** with documentation changes
2. **Automated checks run:**
   - Image naming validation
   - Placeholder format check
   - Asset reference validation
   - Component reference validation
3. **Checks must pass** - if not, PR provides detailed error report
4. **Aniket reviews & approves** PRs
5. **Merge** when all checks pass and approval received

---

## Fixing Common Errors

### ❌ Image Naming Error
```
Error: Invalid image name: 'dashboard-screenshot.png'
Expected format: AMNIC_DASHBOARD_NAME.{png|jpg|jpeg|gif}
```
**Fix:** Rename to `AMNIC_DASHBOARD_SCREENSHOT.png`

### ❌ Unresolved Placeholder Error
```
Error: Unresolved DRAFT marker in docs/guides.md:42
[DRAFT/TO-DO, CHANGE]
```
**Fix:** Remove the marker or replace placeholder content

### ❌ Missing Asset Error
```
Error: Missing asset reference in docs/overview.md
Referenced: /images/screenshot.png
File does not exist
```
**Fix:** Either add the missing image file or remove the reference

### ❌ Missing Approval Error
```
Error: PR requires at least one approval from a reviewer
```
**Fix:** Wait for Aniket's review and approval

---

## Local Testing

### Test validation locally before pushing:

```bash
# Test all validations
python scripts/validate_docs.py
python scripts/validate_images.py
python scripts/check_placeholders.py
python scripts/validate_assets.py

# Or run all at once
python scripts/validate_docs.py && \
python scripts/validate_images.py && \
python scripts/check_placeholders.py && \
python scripts/validate_assets.py
```

---

## Component References

Valid component names that must appear in context:
- **Vantage** - Platform/product name
- **Cloudzero** - Integration/feature name
- **AWS** - Cloud provider
- **GCP** - Cloud provider
- **Azure** - Cloud provider

---

## Quick Reference

| Check | Required? | Fail Condition |
|-------|-----------|---|
| Image naming | ✅ | Invalid format |
| Placeholders | ✅ | Malformed or unresolved |
| Asset references | ✅ | Missing files |
| Component context | ⚠️ | Bare mentions (warning only) |
| Reviewer approval | ✅ | No approvals |
| Checks pass | ✅ | Any check fails |
