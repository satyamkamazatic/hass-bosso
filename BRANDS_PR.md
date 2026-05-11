# Brands repo PR — adding the Bosso cat icon to Home Assistant

After Bosso's GitHub access is set up and the main repo is published, submit this PR so the cat icon appears in Home Assistant's UI.

## Files to submit

The icons are already prepared in `custom_components/bosso/brand/`:
- `icon.png` (256×256, transparent background)
- `icon@2x.png` (512×512, transparent background)

These need to be placed in the `home-assistant/brands` repo under `custom_integrations/bosso/`.

## Step-by-step

### 1. Fork home-assistant/brands

1. Visit https://github.com/home-assistant/brands
2. Click **Fork** (top-right)
3. **Owner:** select the Bosso GitHub org/account
4. Repository name: keep `brands`
5. Click **Create fork**

### 2. Clone your fork locally

```bash
# Replace <ORG> with the Bosso GitHub org/handle
git clone https://github.com/<ORG>/brands.git brands-fork
cd brands-fork
```

### 3. Add the Bosso icons

```bash
mkdir -p custom_integrations/bosso

# Copy icons from this handoff package (adjust path as needed)
cp /path/to/bosso_handoff/custom_components/bosso/brand/icon.png custom_integrations/bosso/
cp /path/to/bosso_handoff/custom_components/bosso/brand/icon@2x.png custom_integrations/bosso/

# Verify
ls custom_integrations/bosso/
```

### 4. Commit and push

```bash
git checkout -b add-bosso-icons
git add custom_integrations/bosso/
git commit -m "Add Bosso integration icons"
git push origin add-bosso-icons
```

### 5. Open the PR

Go to your fork on GitHub. You'll see a banner "add-bosso-icons had recent pushes" with a **Compare & pull request** button.

Click it. Fill in:

**Title:**
```
Add Bosso integration icons
```

**Description:** (copy-paste this — replace `<ORG>` with your real org)
```markdown
This PR adds icon assets for the Bosso Lights Home Assistant integration.

- **Custom integration domain:** `bosso`
- **Repository:** https://github.com/<ORG>/hass-bosso
- **HACS:** Pending listing in default repository

## Files added
- `custom_integrations/bosso/icon.png` — 256×256, transparent background
- `custom_integrations/bosso/icon@2x.png` — 512×512, transparent background

Source artwork: vector SVG provided by Bosso.
```

Click **Create pull request**.

### 6. Wait for CI + review

- CI checks (image dimensions, format, etc.) run within a minute. They should pass since icons were generated to spec.
- A maintainer reviews. Typical turnaround 2-7 days.
- They may ask for changes (more padding, etc.). If so, regenerate from the source SVG and push to the same branch.

### 7. After merge

The cat icon is automatically served from `https://brands.home-assistant.io/_/bosso/icon.png` and appears everywhere the Bosso integration is shown in HA. No code changes needed in the integration — it just starts working.

## Common feedback from brands reviewers (and how to respond)

- **"Add more padding around the icon"** — regenerate with the cat occupying ~70% of the canvas instead of filling it edge-to-edge
- **"Add a logo.png too"** — logos are wider, include the brand text. Optional but they sometimes ask. Generate from a design with "Bosso lights" wordmark
- **"Icon looks blurry"** — usually a rendering issue from upscaling. Re-render directly from the SVG at 512×512

If feedback comes in, the source `cat.svg` file should be on hand to regenerate.
