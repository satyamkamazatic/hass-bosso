# Troubleshooting — common issues during setup

## CI failures

### HACS Validation fails: "no valid topics"
**Cause:** Repo has no GitHub topics, or only invalid ones.

**Fix:** Go to repo → ⚙ next to "About" sidebar → add at least one of:
- `home-assistant`
- `hacs`
- `home-assistant-integration`
- `home-automation`

### HACS Validation fails: "no brand assets"
**Cause:** HACS expects either local brand files OR brands repo entry.

**Fix:** Confirm `custom_components/bosso/brand/icon.png` and `icon@2x.png` exist in the repo. If they do and CI still fails, the path or filename may be wrong (must be exactly `brand/icon.png`, singular, lowercase).

### Hassfest fails: "Manifest keys are not sorted correctly"
**Cause:** manifest.json keys must be: `domain`, `name`, then everything else alphabetical.

**Fix:** Open `custom_components/bosso/manifest.json`. Order should be:
```
domain, name, codeowners, config_flow, dependencies, documentation, iot_class, issue_tracker, requirements, version
```

### Hassfest fails: "Invalid URL"
**Cause:** `documentation` or `issue_tracker` URL has placeholder text.

**Fix:** Make sure `BOSSO_GITHUB_ORG` was replaced with the real org name in `manifest.json`.

## Push problems

### "rejected" / "fetch first" error
**Cause:** GitHub has commits your local doesn't.

**Fix:**
```bash
git pull origin main
# resolve any conflicts
git push
```

### Asks for password and rejects it
**Cause:** GitHub deprecated password auth. You need a Personal Access Token (PAT).

**Fix:** Create a PAT at https://github.com/settings/tokens with `repo` scope. Use it as your password when prompted.

Or use SSH:
```bash
git remote set-url origin [email protected]:<ORG>/hass-bosso.git
```
(Requires SSH key set up in GitHub.)

## Installation problems

### "Bosso Lights" doesn't appear in HACS after adding custom repository
**Possible causes:**
- Repo doesn't have a published release
- Repo `hacs.json` is malformed
- Repo doesn't pass HACS validation

**Fix:** Check Actions tab is green. Confirm v1.1.0 release exists. Confirm `hacs.json` is valid JSON.

### Login fails after install
**Cause:** Either credentials are wrong, or backend URL in `const.py` is wrong.

**Fix:** First test credentials with cURL:
```bash
curl -X POST https://be.bosso.biz/api/v1/auth/login/ \
  -H 'Content-Type: application/json' \
  -d '{"email": "[email protected]", "password": "yourpassword"}'
```
Should return `{"access": "...", "refresh": "..."}`. If not, the credentials or endpoint URL is the problem.

### Devices don't appear after login
**Cause:** Account has no devices, or device list response is malformed.

**Fix:** Open Bosso mobile app, confirm devices are visible there. If they are, enable debug logging in HA:
```yaml
# configuration.yaml
logger:
  default: warning
  logs:
    custom_components.bosso: debug
```
Restart, retry, check logs for the device list response.

## After-publish problems

### Brands PR rejected
**Common reasons + fixes:**

- "Icon needs more padding" → regenerate from `cat.svg` with the cat at ~70% canvas size
- "Add `logo.png`" → optional, but if asked: design with cat + "Bosso lights" wordmark, save as 256×N (max 80px tall)
- "Icon is blurry" → re-render directly from SVG at full 512×512 (don't upscale from a smaller raster)

### HACS default listing PR rejected
**Common reasons + fixes:**

- Brand assets missing → first finish the brands PR, then mention it in this PR
- No releases → publish v1.1.0 release first
- Repo description empty → add one in repo About sidebar
- CI failing → fix all CI errors first, then comment on the PR

## "I broke something, want to start over"

The whole repo state is in this handoff package. To reset:

```bash
# Save any new commits you want to keep
git log --oneline -5

# Nuclear option: delete everything, re-extract handoff
cd ..
rm -rf bosso-repo
unzip ~/Downloads/bosso_handoff.zip -d ~/bosso-repo
cd bosso-repo
# Run the SETUP.md sequence from step 1
```

Nothing is irreversible. GitHub repos can be deleted and recreated. Releases can be re-tagged.

## Getting help

- Home Assistant docs: https://developers.home-assistant.io/
- HACS docs: https://hacs.xyz/docs/publish/start/
- Brands repo guidelines: https://github.com/home-assistant/brands#readme
- HA forum: https://community.home-assistant.io/

For Bosso-specific questions, refer back to the conversation history with the assistant.
