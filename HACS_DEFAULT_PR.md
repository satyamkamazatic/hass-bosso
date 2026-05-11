# HACS default listing PR — making Bosso searchable in HACS

After the main repo is published and tagged with a v1.1.0 release, submit this PR to get listed in the HACS default repository. After merge, HACS users worldwide can search "Bosso" in HACS and install with one click — no need to add a custom repository.

## Prerequisites — must be true before submitting

- [ ] `https://github.com/<ORG>/hass-bosso` is public
- [ ] Repo has GitHub topics: `home-assistant`, `hacs`, `home-assistant-integration`, etc.
- [ ] Repo has a description in the About sidebar
- [ ] Repo has at least one published release (v1.1.0 or newer)
- [ ] CI is passing (HACS Validation + Hassfest Validation green ✅)
- [ ] Brand icons are either:
  - Uploaded to `custom_components/bosso/brand/icon.png` (already done in this repo), OR
  - Submitted to home-assistant/brands and merged

If any of these are missing, fix first. The HACS default review will block on these.

## Step-by-step

### 1. Fork hacs/default

1. Visit https://github.com/hacs/default
2. Click **Fork**
3. **Owner:** Bosso GitHub org/account
4. Repository name: keep `default`
5. Click **Create fork**

### 2. Edit the `integration` file

The `integration` file is a flat list of `owner/repo` entries, one per line, alphabetically sorted.

Easiest way: edit directly on GitHub web UI.

1. Go to your fork: `https://github.com/<ORG>/default/blob/main/integration`
2. Click the pencil icon to edit
3. Add a new line for your repo (alphabetical position)

The line you add looks like:
```
<ORG>/hass-bosso
```

(Replace `<ORG>` with the real org name. Just the path, no URL prefix.)

Find where alphabetically it should go — look for entries near `b...` for "bosso", or `h...` for "hass-bosso", depending on the org name.

### 3. Commit the change

In the GitHub commit form below the editor:
- **Commit message:** `Add bosso/hass-bosso`
  (Replace with real org/repo)
- Choose: **Create a new branch for this commit and start a pull request**
- Branch name: `add-bosso`
- Click **Propose changes**

### 4. Open the PR

The next page shows the PR creation form.

**Title:**
```
Add <ORG>/hass-bosso
```

**Description:** (copy-paste this)
```markdown
Adding the Bosso Lights integration to HACS default.

- **Repository:** https://github.com/<ORG>/hass-bosso
- **Domain:** `bosso`
- **Description:** Home Assistant integration for Bosso smart lights

This integration provides:
- Full light control (on/off, brightness, RGB color, color temperature)
- Lighting effects from the Bosso effects catalog
- Predefined and user-defined preset selection
- Multi-device support

The integration has been tested against the production Bosso API and passes both HACS Validation and Hassfest checks.

Brand assets: [pending PR / merged via PR #X] in home-assistant/brands.
```

Click **Create pull request**.

### 5. Wait for automated validation

HACS has a bot that runs checks:
- Repo exists and is public
- Has a release
- Has valid topics
- Has brand assets (or is in brands repo)
- Code structure is HACS-compatible

These should all pass since we set everything up correctly.

### 6. Wait for human review

Typical turnaround: **1-2 weeks**.

A HACS maintainer will review and either:
- Approve and merge ✅ → Bosso appears in HACS searches
- Ask for changes → fix and push to the same branch

### 7. After merge — testing

Anyone with HACS installed can now:
1. Open HACS → Integrations
2. Type "Bosso" in search
3. Find Bosso Lights → click → Install

No custom repository step. This is the standard polished experience.

## What if the PR is rejected?

Common reasons:
- **Brand assets missing** — make sure brands PR is merged or local fallback exists
- **No releases** — must have at least one tagged release
- **CI failing** — fix what HACS Validation flags
- **Topics missing** — add them in repo settings
- **Description empty** — add one to the repo About section

These are easy to fix and the maintainer will tell you what's wrong.

## After both brands PR + HACS default PR are merged

This is the final state — your stated goal achieved:

- Users open HACS → search "Bosso" → see Bosso Lights with the cat logo → install
- After install, **Settings → Devices & Services → Add Integration → search "Bosso"** → see Bosso Lights with the cat logo → click → enter email/password → done

The "search 'bosso lights' with cat logo, add integration" experience is fully working.
