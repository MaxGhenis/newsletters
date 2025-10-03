#!/usr/bin/env python3
"""
Add or update UK contacts from CSV file.

Reads uk_contacts.csv and ensures all contacts are:
1. Subscribed to the list
2. Have COUNTRY set to "United Kingdom"
"""

import csv
import hashlib
import os
import requests
from pathlib import Path


def get_subscriber_id(email):
    """Get Mailchimp subscriber ID (MD5 hash of lowercase email)."""
    return hashlib.md5(email.lower().encode()).hexdigest()


def main():
    API_KEY = os.getenv("MAILCHIMP_API_KEY")
    if not API_KEY:
        print("Error: MAILCHIMP_API_KEY not set")
        return 1

    BASE_URL = f"https://{API_KEY.split('-')[-1]}.api.mailchimp.com/3.0"
    LIST_ID = "71ed1f89d8"

    # Read CSV
    csv_path = Path(__file__).parent / "uk_contacts.csv"
    contacts = []

    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['email']:  # Skip empty rows
                contacts.append({
                    'email': row['email'].strip(),
                    'first_name': row['first_name'].strip()
                })

    print(f"Found {len(contacts)} UK contacts in CSV\n")

    # Process each contact
    added = 0
    updated = 0
    already_set = 0
    failed = 0

    for i, contact in enumerate(contacts, 1):
        email = contact['email']
        first_name = contact['first_name']
        subscriber_id = get_subscriber_id(email)

        # Check if subscriber exists
        check_response = requests.get(
            f"{BASE_URL}/lists/{LIST_ID}/members/{subscriber_id}",
            auth=("anystring", API_KEY)
        )

        if check_response.status_code == 200:
            # Subscriber exists
            member = check_response.json()
            current_country = member.get('merge_fields', {}).get('COUNTRY', '').strip()

            if current_country == 'United Kingdom':
                already_set += 1
                if i % 10 == 0:
                    print(f"Progress: {i}/{len(contacts)} (already set: {already_set})")
                continue

            # Update country
            update_response = requests.patch(
                f"{BASE_URL}/lists/{LIST_ID}/members/{subscriber_id}",
                auth=("anystring", API_KEY),
                json={
                    "merge_fields": {
                        "COUNTRY": "United Kingdom"
                    }
                }
            )

            if update_response.status_code == 200:
                updated += 1
                print(f"✓ Updated: {email}")
            else:
                failed += 1
                print(f"✗ Failed to update: {email}")

        else:
            # Subscriber doesn't exist - add them
            add_response = requests.post(
                f"{BASE_URL}/lists/{LIST_ID}/members",
                auth=("anystring", API_KEY),
                json={
                    "email_address": email,
                    "status": "subscribed",
                    "merge_fields": {
                        "FNAME": first_name,
                        "COUNTRY": "United Kingdom"
                    }
                }
            )

            if add_response.status_code == 200:
                added += 1
                print(f"✓ Added: {email}")
            else:
                error_data = add_response.json()
                # Check if already subscribed with different status
                if error_data.get('title') == 'Member Exists':
                    # Try updating instead
                    update_response = requests.patch(
                        f"{BASE_URL}/lists/{LIST_ID}/members/{subscriber_id}",
                        auth=("anystring", API_KEY),
                        json={
                            "status": "subscribed",
                            "merge_fields": {
                                "FNAME": first_name,
                                "COUNTRY": "United Kingdom"
                            }
                        }
                    )
                    if update_response.status_code == 200:
                        updated += 1
                        print(f"✓ Resubscribed: {email}")
                    else:
                        failed += 1
                        print(f"✗ Failed: {email}")
                else:
                    failed += 1
                    print(f"✗ Failed to add: {email} - {error_data.get('detail', '')}")

    print(f"\n{'='*70}")
    print(f"✅ COMPLETE")
    print(f"{'='*70}")
    print(f"Added new subscribers: {added}")
    print(f"Updated to UK: {updated}")
    print(f"Already set to UK: {already_set}")
    print(f"Failed: {failed}")
    print(f"\nTotal UK contacts processed: {len(contacts)}")

    return 0


if __name__ == "__main__":
    exit(main())
