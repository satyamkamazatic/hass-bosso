# Bosso Lights Home Assistant Integration — Handoff Package

This package contains everything needed to publish the Bosso Lights Home Assistant integration under the official Bosso GitHub organization. The integration code is complete, tested against production, and validated against HACS + Hassfest. What's left is the deployment.

## What's included

```
bosso_handoff/
├── HANDOFF.md                       ← you are here
├── SETUP.md                         ← runbook: how to push to GitHub
├── BRANDS_PR.md                     ← runbook: cat icon → HA brands repo
├── HACS_DEFAULT_PR.md               ← runbook: searchable in HACS
├── TROUBLESHOOTING.md               ← when things go wrong
│
├── README.md                        ← user-facing repo readme
├── LICENSE                          ← Apache 2.0
├── CHANGELOG.md                     ← release notes
├── hacs.json                        ← HACS metadata
├── info.md                          ← HACS UI display
├── .gitignore
│
├── .github/workflows/
│   └── validate.yml                 ← CI: HACS + hassfest checks
│
└── custom_components/bosso/         ← the integration code (v1.1.0)
    ├── __init__.py
    ├── api.py
    ├── config_flow.py
    ├── const.py
    ├── coordinator.py
    ├── light.py
    ├── manifest.json
    ├── presets.py
    ├── select.py
    ├── strings.json
    ├── translations/en.json
    └── brand/
        ├── icon.png                 ← 256×256 cat (transparent)
        └── icon@2x.png              ← 512×512 cat (transparent)
```

## What still needs to happen — overview

### Required, sequential
1. Push this code to `github.com/<bosso-org>/hass-bosso` — see SETUP.md
2. Confirm CI passes — see SETUP.md step 5
3. Tag and publish v1.1.0 release — see SETUP.md step 6
4. Verify HACS install works on a real HA instance — see SETUP.md step 7

### Required, parallel (after step 4 above)
5. Submit cat icon PR to home-assistant/brands — see BRANDS_PR.md
6. Submit listing PR to hacs/default — see HACS_DEFAULT_PR.md

Steps 5 and 6 each take 1-2 weeks for review + merge.

## What gets you to the "search Bosso, see cat logo, install" experience

That goal requires all of the above to be merged:

| Step | What it enables |
|---|---|
| 1-4 | Anyone with HACS can install Bosso via custom repository (today) |
| 5 (brands merged) | Cat logo appears next to Bosso in HA UI everywhere |
| 6 (HACS default merged) | Searching "Bosso" in HACS finds it directly (no custom repo needed) |

## Templated values

Throughout this package, the placeholder `BOSSO_GITHUB_ORG` is used wherever the GitHub org name is needed. Before pushing, find-and-replace it with the actual org name. SETUP.md step 1 has the exact commands.

## Code state

The code in `custom_components/bosso/` is the latest tested production version (v1.1.0) with:

- Email/password authentication with automatic token refresh
- Light entity per Bosso device (on/off, brightness, RGB, CCT, effects)
- Predefined and user-defined preset selection (separate select entities)
- Multi-device support with pagination
- HTTP request timeouts (15s) to prevent hangs
- Defensive error handling (proper exception classes, no bare `except`)
- Production API endpoint (`https://be.bosso.biz/api/v1`)

Do not edit code unless necessary. The TODOs that remain (effects API call could be cached longer, palette handling could be refined, etc.) are non-blocking.

## Roughly how long this all takes

- Steps 1-4: ~30 minutes of focused work
- Steps 5-6: ~10 minutes of work + 1-2 weeks of waiting per PR

**Realistic timeline:** Bosso integration is publicly listed in HACS and discoverable by all HACS users in **2-3 weeks** from the day Bosso GitHub access is given.

## Questions / context

If you're picking this up cold and need context on how the integration was built, what the API patterns are, or why specific decisions were made — refer back to the assistant conversation. The full development log is in your conversation history.

For the technical "what does this do and why" — start with `README.md`, then read `custom_components/bosso/__init__.py` (50 lines, sets the architecture), then `coordinator.py` (the central state manager).
