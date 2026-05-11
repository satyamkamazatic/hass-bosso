# Setup runbook — pushing to Bosso GitHub org

This document is for whoever has access to the Bosso GitHub org and is publishing the integration. Run through the steps in order.

## Prerequisites

- [ ] Access to a GitHub account that can create/push to the Bosso GitHub org
- [ ] The org name (e.g., `bosso`, `bosso-lights`, etc.) — call this `<ORG>` below
- [ ] This repo content extracted somewhere on your laptop
- [ ] `git` installed locally
- [ ] Either a GitHub Personal Access Token OR SSH key set up for that account

## Step 1: Find-and-replace the templated URLs

Throughout the repo, the placeholder `BOSSO_GITHUB_ORG` is used wherever the org name needs to appear. Replace it with the real org name in two files:

```bash
# Replace BOSSO_GITHUB_ORG with the real org name (e.g., 'bosso')
ORG=bosso  # CHANGE THIS to the real org name

sed -i "s|BOSSO_GITHUB_ORG|${ORG}|g" README.md
sed -i "s|BOSSO_GITHUB_ORG|${ORG}|g" custom_components/bosso/manifest.json

# Verify no placeholders left
grep -rn "BOSSO_GITHUB_ORG" . && echo "STILL HAS PLACEHOLDERS" || echo "ALL REPLACED"
```

## Step 2: Create the empty repo on GitHub

1. Go to https://github.com/organizations/`<ORG>`/repositories/new
   (or click "New repository" inside the org)
2. Repository name: **`hass-bosso`**
3. Description: **"Home Assistant integration for Bosso smart lights"**
4. Visibility: **Public**
5. **Do not** check "Add a README" / "Add a .gitignore" / "Add a license" — we already have these
6. Click **Create repository**

## Step 3: Initialize git locally and push

In a terminal, in the directory containing this SETUP.md:

```bash
# Initialize git (if not already)
git init -b main

# Set up your commit identity (optional but recommended for clean history)
git config user.email "[email protected]"
git config user.name "Bosso Developer"

# Stage and commit everything
git add .
git commit -m "Initial release v1.1.0

- Email/password auth with auto token refresh
- Light entity (on/off, brightness, RGB, CCT)
- Effect support
- Predefined and user-defined preset selection
- Multi-device support"

# Connect to GitHub
git remote add origin https://github.com/<ORG>/hass-bosso.git

# Push to main
git push -u origin main
```

## Step 4: Add GitHub topics

Go to: `https://github.com/<ORG>/hass-bosso`

Click the gear icon ⚙ next to "About" in the right sidebar. Add these topics:
- `home-assistant`
- `hacs`
- `home-assistant-integration`
- `bosso`
- `smart-lights`

Click **Save changes**.

## Step 5: Verify CI passes

Go to: `https://github.com/<ORG>/hass-bosso/actions`

Wait ~1-2 minutes. Both jobs should turn green:
- ✅ HACS Validation
- ✅ Hassfest Validation

If either fails, see TROUBLESHOOTING.md.

## Step 6: Tag and publish v1.1.0 release

```bash
git tag v1.1.0
git push origin v1.1.0
```

Then go to: `https://github.com/<ORG>/hass-bosso/releases/new`

- **Choose a tag:** `v1.1.0` (already exists)
- **Release title:** `v1.1.0`
- **Description:** copy from CHANGELOG.md (the v1.1.0 section)
- Click **Publish release**

## Step 7: Test installation via HACS

(Assumes HACS is installed in your Home Assistant.)

1. Open HACS → Integrations
2. ⋮ menu → Custom repositories
3. Repository: `https://github.com/<ORG>/hass-bosso`
4. Type: Integration → Add
5. Find **Bosso Lights** in HACS list → Install
6. Restart Home Assistant
7. Settings → Devices & Services → + Add Integration → search "Bosso"
8. Sign in with a test Bosso account → verify devices appear

## Step 8: Submit to home-assistant/brands (cat icon)

This makes the cat logo appear next to the integration in HA's UI everywhere.

See BRANDS_PR.md for the exact PR text and submission instructions.

## Step 9: Submit to HACS default list

This makes "Bosso" searchable directly in HACS without users adding a custom repository.

See HACS_DEFAULT_PR.md for the exact PR text and submission instructions.

## Done

After steps 1-9, the integration is:
- ✅ Public on GitHub under the Bosso org
- ✅ Tagged at v1.1.0
- ✅ Installable via HACS custom repository (anyone can install today)
- ⏳ Pending brands PR review (icon will appear after merge, ~3-7 days)
- ⏳ Pending HACS default PR review (searchable in HACS after merge, ~1-2 weeks)
