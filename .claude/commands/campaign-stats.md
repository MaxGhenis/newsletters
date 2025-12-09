---
description: Get campaign statistics from Mailchimp
argument-hint: <YYYY-MM-DD>
---

Fetch and display statistics for a newsletter campaign by date.

## Usage

```bash
/campaign-stats 2024-10-29
/campaign-stats 2024-11-04
```

## Process

1. **Extract date** from `$1` argument

2. **Use campaign-analyzer subagent** to:
   - Fetch all sent campaigns from Mailchimp
   - Find campaign matching the date
   - Retrieve detailed statistics
   - Analyze performance

3. **Display metrics**:
   - Campaign subject line and send time
   - Recipients count
   - Open rate (unique opens / sent)
   - Click rate (subscriber clicks / sent)
   - Top clicked links
   - Archive URL

4. **Provide context**:
   - Compare to newsletter average
   - Identify standout performance areas
   - Suggest improvements if below average

## Example Output

```
📊 Campaign: UK Autumn Budget & US Election Policies

Sent: October 25, 2024 at 2:51 AM
Recipients: 202

📧 Performance:
   Opens: 90 (48.1%)
   Clicks: 21 (11.2%)

🔗 Top Links:
   1. UK Autumn Budget Analysis (45 clicks)
   2. 2024 Election Calculator (32 clicks)
   3. Harris CTC Analysis (18 clicks)

📈 vs Average:
   Open rate: +5.2% above average
   Click rate: +3.1% above average

🔗 Full report: http://eepurl.com/i16_4c
```

## Error Handling

If no campaign found for the date, show available campaigns from the past 3 months.
