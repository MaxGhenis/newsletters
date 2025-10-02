# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a simple newsletter repository containing HTML email templates for PolicyEngine's Mailchimp campaigns. No build tools, testing frameworks, or development servers are needed - this is pure HTML/CSS.

## Repository Structure

```
newsletters/
├── editions/          # Newsletter HTML files (one per edition)
│   ├── 2024-10-29.html
│   └── 2024-11-04.html
├── assets/
│   ├── images/       # Newsletter image assets
│   └── styles.css    # Shared CSS (currently unused)
├── config/
│   └── mailchimp-settings.json  # API key configuration (not committed)
└── README.md
```

## Newsletter Template Structure

All newsletter HTML files follow this pattern:

1. **Inline Styles**: All styling is inline (required for email compatibility)
2. **Font**: Roboto loaded from Google Fonts
3. **Max Width**: 600px centered container
4. **Color Scheme**:
   - Primary blue: #2C6496
   - Teal accent: #39C6C0
   - Background grays: #F2F2F2, #D8E6F3, #F7FDFC
5. **Mailchimp Variables**: Footer includes merge tags like `*|EMAIL|*`, `*|UNSUB|*`, `*|UPDATE_PROFILE|*`
6. **Logo**: Links to PolicyEngine logo in main app repository on GitHub

## Creating New Newsletters

1. Create a new file in `editions/` with date format: `YYYY-MM-DD.html`
2. Copy structure from existing edition
3. Update content while maintaining:
   - Inline styles for email client compatibility
   - Responsive table layout in footer (Mailchimp CAN-SPAM compliance)
   - Mailchimp merge tags in footer
   - External assets use full URLs (no relative paths)

## Email Compatibility

- **No CSS files**: All styles must be inline
- **Limited CSS**: Avoid modern CSS features (flexbox, grid)
- **Table layouts**: Use tables for complex layouts (email clients don't support modern layout)
- **No JavaScript**: Email clients block JavaScript
- **External images**: Use full URLs for all images
- **Responsive design**: Use media queries in `<style>` tags for mobile
- **Logo format**: Use PNG, not SVG - many email clients don't render SVGs properly
  - Upload logo PNG to Mailchimp Content Studio and use that hosted URL
  - Or host on policyengine.org and reference the PNG version

## File Naming Conventions

- Newsletter editions: `YYYY-MM-DD.html` (e.g., `2024-11-04.html`)
- Images: Descriptive names in `assets/images/`

## Configuration

- `config/mailchimp-settings.json` contains API key (gitignored, template provided)
- `.env` file contains `MAILCHIMP_API_KEY` for the upload script
- No build configuration needed

## Uploading to Mailchimp

This repo includes a Python package (`newsletter_uploader`) with full test coverage.

### Installation

```bash
pip install -e ".[dev]"
export MAILCHIMP_API_KEY="your-key-us5"
```

### Usage

```bash
# UK subscribers only
upload-newsletter editions/2025-10-01-uk.html \
  --audience uk \
  --subject "UK Happy Hour Tomorrow + New Research" \
  --preview "Join us for drinks and discussion"

# US (non-UK) subscribers
upload-newsletter editions/2025-01-15-us.html \
  --audience us \
  --subject "New US Policy Analysis" \
  --preview "Latest research on tax reforms"

# All subscribers
upload-newsletter editions/2025-01-01-global.html \
  --audience all \
  --subject "PolicyEngine Year in Review" \
  --preview "Our 2024 impact and progress"
```

**Audience targeting:**
- `--audience uk` - Only UK subscribers (COUNTRY = "United Kingdom")
- `--audience us` - All non-UK subscribers (COUNTRY ≠ "United Kingdom") - includes US and missing country data
- `--audience all` - All subscribers (no filtering)

The command creates a **draft campaign** (not sent) that you can review, test, and send from the Mailchimp web interface.

### Development

```bash
# Run tests (93% coverage)
pytest -v

# Format and lint
black src/ tests/
ruff check src/ tests/
```

The package is structured with:
- `src/newsletter_uploader/` - Core package modules
- `tests/` - Comprehensive test suite
- CI runs on GitHub Actions for Python 3.8-3.11
