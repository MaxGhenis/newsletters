#!/usr/bin/env python3
"""
Extract DMV (DC/MD/VA) subscribers.

Includes:
1. Subscribers with location in DC, VA, or MD
2. Subscribers from DC-based organizations (regardless of location)
3. Flags known policy people even without location data
"""

import os
import requests
import csv
from datetime import datetime
from collections import defaultdict


# Known DC-based organizations
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
    'progressivepolicy.org': 'Progressive Policy Institute',
    'niskanencenter.org': 'Niskanen Center',
    'crfb.org': 'Committee for a Responsible Federal Budget',
    'itep.org': 'Institute on Taxation and Economic Policy',
    'resultsfordevelopment.org': 'Results for Development',
    'americanenterpriseinstitute.org': 'American Enterprise Institute',
    'bipartisanpolicy.org': 'Bipartisan Policy Center',
    'equitablegrowth.org': 'Washington Center for Equitable Growth',
    'arnoldventures.org': 'Arnold Ventures',
    'aspeninstitute.org': 'Aspen Institute',
    'ntu.org': 'National Taxpayers Union',
    'taxpayer.net': 'Taxpayers for Common Sense',
    'ppionline.org': 'Progressive Policy Institute',
    'petersonsolutions.org': 'Peter G. Peterson Foundation',
    'economicstrategygroup.org': 'Economic Strategy Group',
    'codeforamerica.org': 'Code for America',
    'neophilanthropy.org': 'NeoPHILanthropy',
    # Government
    'treasury.gov': 'U.S. Department of the Treasury',
    'irs.gov': 'Internal Revenue Service',
    'cbo.gov': 'Congressional Budget Office',
    'gao.gov': 'Government Accountability Office',
    'frb.gov': 'Federal Reserve Board',
    'house.gov': 'U.S. House of Representatives',
    'mail.house.gov': 'U.S. House of Representatives',
    'senate.gov': 'U.S. Senate',
    'warren.senate.gov': 'U.S. Senate (Warren)',
    'finance.senate.gov': 'Senate Finance Committee',
    'warner.senate.gov': 'U.S. Senate (Warner)',
    'ronjohnson.senate.gov': 'U.S. Senate (Johnson)',
    'bennet.senate.gov': 'U.S. Senate (Bennet)',
    'welch.senate.gov': 'U.S. Senate (Welch)',
    'vanhollen.senate.gov': 'U.S. Senate (Van Hollen)',
    'cassidy.senate.gov': 'U.S. Senate (Cassidy)',
    'merkley.senate.gov': 'U.S. Senate (Merkley)',
    'whitehouse.gov': 'White House',
    'omb.gov': 'Office of Management and Budget',
    'crs.loc.gov': 'Congressional Research Service',
    'nas.edu': 'National Academy of Sciences',
    'mitre.org': 'MITRE',
    # Universities with DC presence
    'georgetown.edu': 'Georgetown University',
    'gwu.edu': 'George Washington University',
    'american.edu': 'American University',
    # Other policy orgs
    'pluralpolicy.com': 'Plural Policy',
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

    # Extract DMV subscribers
    dmv_subscribers = []

    for member in all_members:
        if member['status'] != 'subscribed':
            continue

        email = member['email_address']
        domain = email.split('@')[-1].lower()
        location = member.get('location', {})
        region = location.get('region', '').upper()
        country_code = location.get('country_code', '')

        name = f"{member.get('merge_fields', {}).get('FNAME', '')} {member.get('merge_fields', {}).get('LNAME', '')}".strip()

        # Get tags
        tags = [tag['name'] for tag in member.get('tags', [])]
        tags_str = ', '.join(tags) if tags else ''

        # Determine if DMV
        is_dmv = False
        dmv_reason = []
        organization = ''

        # Check if we know they're located outside DMV
        is_outside_dmv = (country_code == 'US' and region and region not in ['DC', 'VA', 'MD'])

        # Check location - always include if in DMV
        if country_code == 'US' and region in ['DC', 'VA', 'MD']:
            is_dmv = True
            dmv_reason.append(f"Located in {region}")

        # Check organization - only include if NOT known to be outside DMV
        if domain in DC_ORGANIZATIONS:
            organization = DC_ORGANIZATIONS[domain]
            if not is_outside_dmv:
                is_dmv = True
                dmv_reason.append(f"Works at {organization}")
            # If they're outside DMV but we already included them for location, note the org
            elif is_dmv:
                dmv_reason.append(f"Works at {organization}")

        if is_dmv:
            dmv_subscribers.append({
                'email': email,
                'name': name,
                'organization': organization,
                'org_domain': domain if organization else '',
                'region': region,
                'country_code': country_code,
                'tags': tags_str,
                'dmv_reason': ' | '.join(dmv_reason)
            })

    # Sort by organization, then region, then name
    dmv_subscribers.sort(key=lambda x: (x['organization'], x['region'], x['name']))

    # Display results
    print(f"Found {len(dmv_subscribers)} DMV-area subscribers\n")

    # Summary
    location_count = len([s for s in dmv_subscribers if s['region'] in ['DC', 'VA', 'MD']])
    org_count = len([s for s in dmv_subscribers if s['organization']])
    dc_count = len([s for s in dmv_subscribers if s['region'] == 'DC'])
    va_count = len([s for s in dmv_subscribers if s['region'] == 'VA'])
    md_count = len([s for s in dmv_subscribers if s['region'] == 'MD'])

    print(f"Summary:")
    print(f"  By location: {location_count} (DC: {dc_count}, VA: {va_count}, MD: {md_count})")
    print(f"  By DC organization: {org_count}")
    print(f"  Total unique: {len(dmv_subscribers)}")

    # Show samples
    print(f"\nSample DMV subscribers:")
    for sub in dmv_subscribers[:20]:
        print(f"  {sub['region'] or '???':3} | {sub['email']:45} | {sub['organization'][:30] if sub['organization'] else sub['org_domain']}")

    # Export to CSV
    timestamp = datetime.now().strftime('%Y-%m-%d')
    filename = f"dmv_subscribers_{timestamp}.csv"

    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['email', 'name', 'organization', 'org_domain', 'region', 'country_code', 'tags', 'dmv_reason'])
        writer.writeheader()
        writer.writerows(dmv_subscribers)

    print(f"\n✅ Exported {len(dmv_subscribers)} DMV subscribers to {filename}")

    # Organization breakdown
    org_counts = defaultdict(int)
    for sub in dmv_subscribers:
        if sub['organization']:
            org_counts[sub['organization']] += 1

    if org_counts:
        print(f"\nSubscribers by DC organization:")
        for org in sorted(org_counts.keys()):
            print(f"  {org:50} {org_counts[org]:3}")

    return 0


if __name__ == "__main__":
    exit(main())
