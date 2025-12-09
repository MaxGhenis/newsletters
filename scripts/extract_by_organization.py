#!/usr/bin/env python3
"""
Extract subscribers grouped by organization (email domain).

Shows organization (domain) and individual location data.
Useful for finding DC-based organizations and their employees.
"""

import os
import requests
import csv
from datetime import datetime
from collections import defaultdict


# Known DC-based think tanks and organizations (add more as needed)
DC_ORGANIZATIONS = {
    # Think tanks
    'americanprogress.org': 'Center for American Progress',
    'aei.org': 'American Enterprise Institute',
    'brookings.edu': 'Brookings Institution',
    'cato.org': 'Cato Institute',
    'cbpp.org': 'Center on Budget and Policy Priorities',
    'cepr.net': 'Center for Economic and Policy Research',
    'heritage.org': 'Heritage Foundation',
    'urban.org': 'Urban Institute',
    'taxfoundation.org': 'Tax Foundation',
    'americanactionforum.org': 'American Action Forum',
    'thirdway.org': 'Third Way',
    'newamerica.org': 'New America',
    'americanprogress.org': 'Center for American Progress',
    'progressivepolicy.org': 'Progressive Policy Institute',
    'niskanencenter.org': 'Niskanen Center',
    'crfb.org': 'Committee for a Responsible Federal Budget',
    'itep.org': 'Institute on Taxation and Economic Policy',
    # Government
    'treasury.gov': 'U.S. Department of the Treasury',
    'irs.gov': 'Internal Revenue Service',
    'cbo.gov': 'Congressional Budget Office',
    'gao.gov': 'Government Accountability Office',
    'frb.gov': 'Federal Reserve Board',
    'house.gov': 'U.S. House of Representatives',
    'senate.gov': 'U.S. Senate',
    # Universities with DC presence
    'georgetown.edu': 'Georgetown University',
    'gwu.edu': 'George Washington University',
    'american.edu': 'American University',
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

    # Group by organization (domain)
    org_subscribers = defaultdict(list)

    for member in all_members:
        if member['status'] != 'subscribed':
            continue

        email = member['email_address']
        domain = email.split('@')[-1].lower()

        location = member.get('location', {})

        subscriber_info = {
            'email': email,
            'name': f"{member.get('merge_fields', {}).get('FNAME', '')} {member.get('merge_fields', {}).get('LNAME', '')}".strip(),
            'country_code': location.get('country_code', ''),
            'region': location.get('region', '').upper(),
            'country': member.get('merge_fields', {}).get('COUNTRY', ''),
        }

        org_subscribers[domain].append(subscriber_info)

    # Filter for DC-based organizations
    dc_org_subscribers = []

    for domain, subscribers in org_subscribers.items():
        if domain in DC_ORGANIZATIONS:
            org_name = DC_ORGANIZATIONS[domain]
            for sub in subscribers:
                sub['organization'] = org_name
                sub['org_domain'] = domain
                dc_org_subscribers.append(sub)

    # Sort by organization, then by name
    dc_org_subscribers.sort(key=lambda x: (x['organization'], x['name']))

    # Display results
    print(f"Found {len(dc_org_subscribers)} subscribers from {len(set(s['organization'] for s in dc_org_subscribers))} DC-based organizations\n")

    if dc_org_subscribers:
        # Group by org for display
        current_org = None
        for sub in dc_org_subscribers:
            if sub['organization'] != current_org:
                current_org = sub['organization']
                print(f"\n{current_org} ({sub['org_domain']}):")

            location_str = f"{sub['region'] or sub['country_code'] or 'unknown location'}"
            print(f"  {sub['email']:45} | {sub['name']:30} | {location_str}")

        # Export to CSV
        timestamp = datetime.now().strftime('%Y-%m-%d')
        filename = f"dc_org_subscribers_{timestamp}.csv"

        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['organization', 'org_domain', 'email', 'name', 'country', 'country_code', 'region'])
            writer.writeheader()
            writer.writerows(dc_org_subscribers)

        print(f"\n✅ Exported {len(dc_org_subscribers)} subscribers from DC orgs to {filename}")

        # Summary by org
        print("\nSummary by organization:")
        org_counts = defaultdict(int)
        for sub in dc_org_subscribers:
            org_counts[sub['organization']] += 1

        for org in sorted(org_counts.keys()):
            print(f"  {org:50} {org_counts[org]:3} subscribers")
    else:
        print("No subscribers from DC-based organizations found.")

    return 0


if __name__ == "__main__":
    exit(main())
