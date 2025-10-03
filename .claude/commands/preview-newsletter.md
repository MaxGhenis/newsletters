---
description: Preview newsletter HTML with screenshots and validation checks
argument-hint: <html-file>
---

Open the newsletter in a browser, capture screenshots, and validate email compatibility.

## Usage

```bash
/preview-newsletter editions/2025-10-02-uk.html
```

## Process

Use the `newsletter-previewer` subagent to:

1. **Open in browser** - Display the HTML for visual review
2. **Capture screenshots** - Desktop (600px) and mobile (320px) views
3. **Validate compatibility** - Check for email client issues
4. **Review content** - Verify links, images, styling

## What Gets Checked

**Email Compatibility:**
- Inline styles only (no external CSS)
- 600px max width
- No modern CSS features
- Table-based layouts
- Full URLs for images
- Mailchimp merge tags present

**Visual Quality:**
- Logo renders
- Colors match brand palette
- Buttons styled correctly
- Text readable and properly spaced
- Cards and sections have proper borders

**Content:**
- All links valid and working
- Images load correctly
- Headers use sentence case
- Professional tone (no inappropriate emoji)

## Output

Shows screenshots and validation report:
```
# Newsletter Preview Report

## Screenshots
[Desktop and mobile screenshots]

## Validation Results
✓ All email compatibility checks pass
✗ Warning: [any issues found]

## Recommendations
- [Suggested improvements]
```

## When to Use

- Before uploading to Mailchimp
- After making styling changes
- To verify cross-client compatibility
- Before scheduling a send
