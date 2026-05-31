# Antigravity Chinese Language Pack

[中文](./README.md) | [English](./README_EN.md)

[![GitHub Repo stars](https://img.shields.io/github/stars/greatleo31/antigravity-chinesepack?style=flat-square)](https://github.com/greatleo31/antigravity-chinesepack/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/greatleo31/antigravity-chinesepack?style=flat-square)](https://github.com/greatleo31/antigravity-chinesepack/issues)
[![GitHub last commit](https://img.shields.io/github/last-commit/greatleo31/antigravity-chinesepack?style=flat-square)](https://github.com/greatleo31/antigravity-chinesepack/commits/main)
[![Check dictionaries](https://img.shields.io/github/actions/workflow/status/greatleo31/antigravity-chinesepack/check-dicts.yml?branch=main&style=flat-square)](https://github.com/greatleo31/antigravity-chinesepack/actions/workflows/check-dicts.yml)
[![License](https://img.shields.io/github/license/greatleo31/antigravity-chinesepack?style=flat-square)](./LICENSE)

> A Chinese language pack project for **Antigravity Agent Manager**.
> 
> Built to make installation easier, translations more natural, troubleshooting simpler, and community collaboration smoother.

## Why this project is worth following

- **Not just a one-off script** — includes install/restore scripts, diagnostics, dictionary checks, workflows, templates, and contributor docs
- **Supports two layout types** — legacy `resources/app` and modern `app.asar`
- **Designed for public maintenance** — with changelog, release checklist, stage summary, and next-step planning
- **Friendly for normal users** — direct main-script usage is recommended, making troubleshooting easier
- **Friendly for contributors** — issue templates, PR template, workflow checks, and documentation

## Quick start

### Recommended approach: run the main script directly

Compared with `.bat` / `.command` wrapper scripts, **running `AntigravityHanHua_GongJu.py` directly is recommended** for better compatibility and easier troubleshooting.

### Windows
1. Open this project directory
2. Run:

```bash
py -3 .\AntigravityHanHua_GongJu.py --diagnose
```

If `py` is unavailable, try:

```bash
python .\AntigravityHanHua_GongJu.py --diagnose
```

Then install with:

```bash
py -3 .\AntigravityHanHua_GongJu.py
```

or:

```bash
python .\AntigravityHanHua_GongJu.py
```

### macOS
1. Open this project directory
2. Run:

```bash
python3 ./AntigravityHanHua_GongJu.py --diagnose
```

If `python3` is unavailable, try:

```bash
python ./AntigravityHanHua_GongJu.py --diagnose
```

Then install with:

```bash
python3 ./AntigravityHanHua_GongJu.py
```

or:

```bash
python ./AntigravityHanHua_GongJu.py
```

## Scope

- Focused on **Antigravity Agent Manager** UI translation
- Supports **Windows / macOS**
- Compatible with:
  - legacy `resources/app`
  - modern `app.asar`
- Uses a rollback-friendly injection approach instead of hard-patching binaries whenever possible

## Key capabilities

- Dynamic DOM translation via `MutationObserver`
- Exact dictionary translation for stable UI labels
- Regex-based dynamic text translation rules
- Fuzzy long-text matching for spacing/newline variations
- Environment diagnostics for Python, npx, and install-path detection
- Backup and restore support
- Dictionary validation with `--check-dicts`
- Untranslated text collection for further dictionary improvement

## Useful files

- `README.md` — Chinese documentation
- `README_EN.md` — English documentation
- `CHANGELOG.md` — recent updates
- `STAGE_SUMMARY.md` — what has been completed in the current stage
- `NEXT_STEPS.md` — where the project can continue next
- `COMPATIBILITY.md` — compatibility matrix
- `PROJECT_INTRO.md` — reusable project intro / release copy
- `TRANSLATION_STYLE_GUIDE.md` — localization style guide
- `UNTRANSLATED_REVIEW.md` — untranslated-text collection workflow
- `QA_CHECKLIST.md` — translation quality checklist
- `tools/generate_translation_candidates.py` — helper script for AI-assisted translation candidates

## Notes

- This project mainly covers Agent Manager related pages, not every Antigravity screen.
- If Antigravity changes frontend structure, HTML paths, preload locations, or packaging strategy, the script may need updates.
- Dynamic texts, extension UIs, and model-generated content may not always be fully covered by the dictionary.

## Want to help?

You can contribute by:

- Reporting untranslated strings
- Suggesting better Chinese wording
- Expanding dynamic translation rules in `dicts/patterns.json`
- Verifying compatibility on more Antigravity versions
- Submitting issues or pull requests

If this project helps you, a **Star** is always appreciated.
