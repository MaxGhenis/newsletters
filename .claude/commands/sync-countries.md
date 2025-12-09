---
description: Sync subscriber COUNTRY field from Mailchimp predicted location
---

Run the country sync script to update subscriber COUNTRY fields based on Mailchimp's predicted location data.

## What This Does

Automatically assigns countries to subscribers who don't have the COUNTRY field set by:
1. Reading Mailchimp's predicted location data (based on signup IP/engagement)
2. Syncing to the COUNTRY merge field
3. Enabling proper UK/US audience targeting

## Process

Run the sync script:

```bash
export MAILCHIMP_API_KEY=$(grep MAILCHIMP_API_KEY .env | cut -d= -f2)
python3 scripts/sync_country_from_location.py --yes
```

This will:
- Fetch all subscribers
- Check those without COUNTRY set
- Sync from `location.country_code` (GB → United Kingdom, US → United States of America, etc.)
- Update in batch

## Expected Output

```
Fetching all subscribers...
Found 564 total members

Can sync 202 subscribers from predicted location:
  UK (GB): 20
  US: 145
  Other: 37

Auto-confirming 202 updates (--yes flag)

Syncing COUNTRY from predicted location...
  Progress: 50/202...
  Progress: 100/202...
  Progress: 150/202...

✅ Complete!
   Success: 163
   Failed: 39
```

## When to Use

- After importing new subscribers
- Before creating audience-targeted campaigns
- To improve UK vs US segmentation accuracy
