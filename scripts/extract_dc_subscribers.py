#!/usr/bin/env python3
"""
Extract subscribers based in Washington DC.

Uses Mailchimp's predicted location data to find DC-based subscribers.
"""

import os
import requests
import csv
from datetime import datetime


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
            print(f"Error: {response.status_code}")
            print(response.text)
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

    # Filter for DC-based subscribers
    dc_subscribers = []

    for member in all_members:
        if member['status'] != 'subscribed':
            continue

        location = member.get('location', {})
        region = location.get('region', '').upper()

        # Check for DC in various formats
        if region in ['DC', 'D.C.', 'DISTRICT OF COLUMBIA']:
            dc_subscribers.append({
                'email': member['email_address'],
                'name': f"{member.get('merge_fields', {}).get('FNAME', '')} {member.get('merge_fields', {}).get('LNAME', '')}".strip(),
                'country': member.get('merge_fields', {}).get('COUNTRY', ''),
                'region': location.get('region', ''),
                'city': location.get('city', ''),
                'zip': location.get('zip', ''),
                'subscribed_date': member.get('timestamp_opt', '')
            })

    # Display results
    print(f"Found {len(dc_subscribers)} DC-based subscribers\n")

    if dc_subscribers:
        print("Sample subscribers:")
        for sub in dc_subscribers[:10]:
            print(f"  {sub['email']:45} | {sub['name']:30} | {sub['city']}")

        # Export to CSV
        timestamp = datetime.now().strftime('%Y-%m-%d')
        filename = f"dc_subscribers_{timestamp}.csv"

        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['email', 'name', 'country', 'region', 'city', 'zip', 'subscribed_date'])
            writer.writeheader()
            writer.writerows(dc_subscribers)

        print(f"\n✅ Exported {len(dc_subscribers)} DC subscribers to {filename}")
    else:
        print("No DC-based subscribers found.")

    return 0


if __name__ == "__main__":
    exit(main())
