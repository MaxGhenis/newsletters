#!/usr/bin/env python3
"""
Sync COUNTRY merge field from Mailchimp's predicted location data.

Uses location.country_code to set the COUNTRY merge field.
"""

import os
import sys
import requests
import hashlib


# Map country codes to Mailchimp COUNTRY field values
COUNTRY_CODE_MAP = {
    'GB': 'United Kingdom',
    'US': 'United States of America',
    'AU': 'Australia',
    'NZ': 'New Zealand',
    'CA': 'Canada',
    'IE': 'Ireland',
    'NL': 'Netherlands',
    'DE': 'Germany',
    'FR': 'France',
    'ES': 'Spain',
    'IT': 'Italy',
    'SE': 'Sweden',
    'NO': 'Norway',
    'DK': 'Denmark',
    'FI': 'Finland',
    'BE': 'Belgium',
    'CH': 'Switzerland',
    'AT': 'Austria',
    'IN': 'India',
    'SG': 'Singapore',
    'JP': 'Japan',
    'KR': 'South Korea',
    'CN': 'China',
    'BR': 'Brazil',
    'MX': 'Mexico',
    'AR': 'Argentina',
}


def main():
    API_KEY = os.getenv("MAILCHIMP_API_KEY")
    if not API_KEY:
        print("Error: MAILCHIMP_API_KEY not set")
        return 1

    BASE_URL = f"https://{API_KEY.split('-')[-1]}.api.mailchimp.com/3.0"
    LIST_ID = "71ed1f89d8"

    print("Fetching all subscribers...")
    offset = 0
    all_members = []

    while True:
        response = requests.get(
            f"{BASE_URL}/lists/{LIST_ID}/members?count=1000&offset={offset}",
            auth=("anystring", API_KEY)
        )

        if response.status_code != 200:
            break

        data = response.json()
        members = data.get("members", [])

        if not members:
            break

        all_members.extend(members)

        if len(members) < 1000:
            break
        offset += 1000

    print(f"Found {len(all_members)} total members\n")

    # Analyze what needs syncing
    needs_update = []

    for member in all_members:
        if member['status'] != 'subscribed':
            continue

        current_country = member.get('merge_fields', {}).get('COUNTRY', '').strip()
        location = member.get('location', {})
        country_code = location.get('country_code', '')

        # Skip if already has country set
        if current_country:
            continue

        # Skip if no location data
        if not country_code:
            continue

        # Map country code to full name
        country_name = COUNTRY_CODE_MAP.get(country_code)
        if country_name:
            needs_update.append({
                'id': member['id'],
                'email': member['email_address'],
                'country_code': country_code,
                'country_name': country_name
            })

    # Show summary
    uk_updates = [u for u in needs_update if u['country_code'] == 'GB']
    us_updates = [u for u in needs_update if u['country_code'] == 'US']
    other_updates = [u for u in needs_update if u['country_code'] not in ['GB', 'US']]

    print(f"Can sync {len(needs_update)} subscribers from predicted location:\n")
    print(f"  UK (GB): {len(uk_updates)}")
    print(f"  US: {len(us_updates)}")
    print(f"  Other: {len(other_updates)}")

    print(f"\nUK examples:")
    for u in uk_updates[:10]:
        print(f"  {u['email']:45} | {u['country_code']} → {u['country_name']}")

    print(f"\nUS examples:")
    for u in us_updates[:5]:
        print(f"  {u['email']:45} | {u['country_code']} → {u['country_name']}")

    # Ask for confirmation
    print(f"\n{'='*70}")

    if '--yes' not in sys.argv:
        try:
            response = input(f"Update {len(needs_update)} subscribers? (yes/no): ")
            if response.lower() != 'yes':
                print("Cancelled.")
                return 0
        except EOFError:
            print("\nUse --yes flag to auto-confirm")
            return 1
    else:
        print(f"Auto-confirming {len(needs_update)} updates (--yes flag)")

    # Perform updates
    print("\nSyncing COUNTRY from predicted location...")
    success = 0
    failed = 0

    for i, update in enumerate(needs_update, 1):
        update_response = requests.patch(
            f"{BASE_URL}/lists/{LIST_ID}/members/{update['id']}",
            auth=("anystring", API_KEY),
            json={
                "merge_fields": {
                    "COUNTRY": update['country_name']
                }
            }
        )

        if update_response.status_code == 200:
            success += 1
            if success % 50 == 0:
                print(f"  Progress: {success}/{len(needs_update)}...")
        else:
            failed += 1
            print(f"  ✗ Failed: {update['email']}")

    print(f"\n✅ Complete!")
    print(f"   Success: {success}")
    print(f"   Failed: {failed}")
    print(f"\n   UK: {len(uk_updates)}")
    print(f"   US: {len(us_updates)}")
    print(f"   Other: {len(other_updates)}")

    return 0


if __name__ == "__main__":
    exit(main())
