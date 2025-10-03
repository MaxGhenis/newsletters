#!/usr/bin/env python3
"""
Assign countries to Mailchimp subscribers based on email domains and tags.

Uses domain-country-mapping.json for organization-specific mappings.
"""

import json
import os
import sys
import requests
from pathlib import Path


def load_mappings():
    """Load domain-country mappings from config file."""
    config_path = Path(__file__).parent / "config" / "domain-country-mapping.json"
    with open(config_path) as f:
        return json.load(f)


def infer_country(email, tags, mappings):
    """
    Infer country from email domain and tags.

    Args:
        email: Email address
        tags: List of tag names
        mappings: Domain-country mapping configuration

    Returns:
        Tuple of (country, reason) or (None, reason) if can't determine
    """
    domain = email.split('@')[1].lower() if '@' in email else ''

    # Check tags first
    if tags:
        tag_names = [t.lower() for t in tags]
        for tag in mappings['tags']['us']:
            if tag.lower() in ' '.join(tag_names):
                return 'United States of America', f'Tag: {tag}'

    # Clear UK domain patterns
    if any(pattern in domain for pattern in ['.uk', '.ac.uk', '.gov.uk', '.co.uk', '.org.uk']):
        return 'United Kingdom', 'UK domain'

    # Clear US domain patterns
    if domain.endswith('.edu') or domain.endswith('.gov'):
        return 'United States of America', 'US domain (.edu/.gov)'

    if domain.endswith('.us'):
        return 'United States of America', 'US domain (.us)'

    # Check UK organizations (non-obvious TLDs)
    for org in mappings['uk_organizations']:
        if org in domain:
            return 'United Kingdom', f'UK org: {org}'

    # Check US organizations (non-obvious TLDs)
    for org in mappings['us_organizations']:
        if org in domain:
            return 'United States of America', f'US org: {org}'

    return None, 'Unknown (generic domain)'


def main():
    API_KEY = os.getenv("MAILCHIMP_API_KEY")
    if not API_KEY:
        print("Error: MAILCHIMP_API_KEY not set")
        return 1

    BASE_URL = f"https://{API_KEY.split('-')[-1]}.api.mailchimp.com/3.0"
    LIST_ID = "71ed1f89d8"

    # Load mappings
    mappings = load_mappings()

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

    # Analyze what needs updating
    needs_update = []
    for member in all_members:
        if member['status'] != 'subscribed':
            continue

        current_country = member.get('merge_fields', {}).get('COUNTRY', '').strip()
        if current_country:
            continue  # Already has country

        tags = [t['name'] for t in member.get('tags', [])]
        inferred_country, reason = infer_country(member['email_address'], tags, mappings)

        if inferred_country:
            needs_update.append({
                'id': member['id'],
                'email': member['email_address'],
                'country': inferred_country,
                'reason': reason
            })

    # Show summary
    uk_updates = [u for u in needs_update if 'United Kingdom' in u['country']]
    us_updates = [u for u in needs_update if 'United States' in u['country']]

    print(f"Can assign country to {len(needs_update)} subscribers:\n")
    print(f"  UK: {len(uk_updates)}")
    print(f"  US: {len(us_updates)}")
    print(f"  Unassigned: {len([m for m in all_members if m['status'] == 'subscribed']) - len(needs_update) - len([m for m in all_members if m['status'] == 'subscribed' and m.get('merge_fields', {}).get('COUNTRY', '').strip()])}")

    # Show examples
    print(f"\nUK examples:")
    for u in uk_updates[:5]:
        print(f"  {u['email']:45} | {u['reason']}")

    print(f"\nUS examples:")
    for u in us_updates[:5]:
        print(f"  {u['email']:45} | {u['reason']}")

    # Ask for confirmation
    print(f"\n{'='*70}")

    # Check for --yes flag
    if '--yes' not in sys.argv:
        try:
            response = input(f"Update {len(needs_update)} subscribers? (yes/no): ")
            if response.lower() != 'yes':
                print("Cancelled.")
                return 0
        except EOFError:
            print("\nError: Interactive input not available. Use --yes flag to confirm.")
            return 1
    else:
        print(f"Auto-confirming update of {len(needs_update)} subscribers (--yes flag)")

    # Perform updates
    print("\nUpdating subscribers...")
    success = 0
    failed = 0

    for update in needs_update:
        update_response = requests.patch(
            f"{BASE_URL}/lists/{LIST_ID}/members/{update['id']}",
            auth=("anystring", API_KEY),
            json={
                "merge_fields": {
                    "COUNTRY": update['country']
                }
            }
        )

        if update_response.status_code == 200:
            success += 1
            if success % 50 == 0:
                print(f"  Updated {success}/{len(needs_update)}...")
        else:
            failed += 1
            print(f"  Failed: {update['email']}")

    print(f"\n✅ Complete!")
    print(f"   Success: {success}")
    print(f"   Failed: {failed}")
    print(f"\n   UK subscribers: {len(uk_updates)}")
    print(f"   US subscribers: {len(us_updates)}")

    return 0


if __name__ == "__main__":
    exit(main())
