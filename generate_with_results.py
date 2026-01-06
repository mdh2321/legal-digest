#!/usr/bin/env python3
"""
Digest generation script with collected search results.
"""
import sys
sys.path.insert(0, 'src')

from generate_digest import DigestGenerator

# Search results collected from web searches
search_results_data = {
    "Australia data privacy": [
        {"title": "Australia's Bold Leap into a New Era of Privacy Law", "url": "https://www.lexisnexis.com/blogs/en-au/insights/australias-bold-leap-into-a-new-era-of-privacy-law", "snippet": "Australia's privacy landscape is undergoing its biggest reform since 1988. Social media ban for under 16s takes effect December 10, 2025.", "source": "LexisNexis Australia"},
        {"title": "Australia's New Privacy Laws Explained: What's Changing and What's Next for 2026", "url": "https://manofmany.com/culture/advice/australian-privacy-laws", "snippet": "December 10, 2025: Nationwide social media ban for persons under 16 takes effect. New age-assurance obligations commence. June 10, 2025: New statutory tort for serious invasions of privacy commenced.", "source": "Man of Many"},
        {"title": "The privacy law reforms finally passed in 2024 set the priorities for 2025", "url": "https://www.holdingredlich.com/the-privacy-law-reforms-finally-passed-in-2024-set-the-priorities-for-2025", "snippet": "Privacy and Other Legislation Amendment Bill 2024 became active. Major components of government's wider privacy reforms are now in effect.", "source": "Holding Redlich"},
    ],
    "Australia AI": [
        {"title": "Australian Government Releases National AI Plan 2025", "url": "https://www.twobirds.com/en/insights/2025/australia/a-new-era-for-ai-governance-in-australia-what-the-national-ai-plan-means-for-industry", "snippet": "On December 2, 2025, the Australian Government unveiled the National AI Plan 2025, steering clear of standalone AI legislation. The government does not plan to pursue AI Act-style regulation, instead indicating existing legal frameworks could apply to AI. AUD 29.9 million committed to launch a safety institute in early 2026.", "source": "Bird & Bird"},
        {"title": "Australia Updates Government AI Policy to Version 2.0", "url": "https://www.digital.gov.au/ai/ai-in-government-policy", "snippet": "Version 2.0 of the Policy for the responsible use of AI in government became effective December 15, 2025. The update strengthens government's approach to safe and responsible AI through new measures on AI governance.", "source": "digital.gov.au"},
        {"title": "Australia Abandons Proposed Mandatory AI Rules in New Plan", "url": "https://www.bankinfosecurity.asia/blogs/australia-abandons-proposed-mandatory-ai-rules-in-new-plan-p-3986", "snippet": "Three months after proposing mandatory artificial intelligence guardrails with regulatory teeth, Australia's government released a national plan that asks companies to consider safety measures instead. The proposal for mandatory guardrails has not progressed.", "source": "Bank Info Security Asia"},
    ],
    "Australia cybersecurity": [
        {"title": "Data Breach, Cyber Security and Privacy Law Update - Sept 2025", "url": "https://stephens.com.au/data-breach-cybersecurity-and-privacy-law-update-september-2025/", "snippet": "Phase 2 of ransomware reporting obligations begins January 1, 2026, adopting a compliance and enforcement approach. Phase 1 ran from May 30, 2025 to December 31, 2025 with an education first approach.", "source": "Stephens Lawyers"},
        {"title": "Digital Governance, Cyber and Privacy | Quarterly Roundup | December 2025", "url": "https://www.lexology.com/library/detail.aspx?g=2dc98eaa-a98c-49f5-aa46-1ce166feec85", "snippet": "The Cyber Security Act 2024 introduced mandatory ransomware and cyber extortion reporting obligation for certain businesses to report ransom payments within 72 hours.", "source": "Lexology"},
    ],
    "Singapore PDPA": [
        {"title": "Personal Data Protection (Statutory Bodies) (Amendment) Notification 2025", "url": "https://sso.agc.gov.sg/SL-Supp/S217-2025/Published/20250328?DocDate=20250328", "snippet": "Personal Data Protection Act underwent administrative updates. The official Singapore Statutes Online shows the PDPA was last updated on January 4, 2026.", "source": "Singapore Statutes Online"},
    ],
    "Singapore AI": [
        {"title": "MAS Consults on AI Risk Management Guidelines for Financial Institutions", "url": "https://www.mas.gov.sg/news/media-releases/2025/mas-guidelines-for-artificial-intelligence-risk-management", "snippet": "MAS issued consultation paper on November 13, 2025, proposing Guidelines on AI Risk Management to guide financial institutions on the responsible use of AI in the financial sector. The consultation period is open until January 31, 2026. Proposed Guidelines will apply to all financial institutions and set out MAS' supervisory expectations on oversight of AI risk management.", "source": "Monetary Authority of Singapore"},
    ],
    "Singapore cybersecurity": [
        {"title": "Singapore Cybersecurity Act Amendments Take Effect", "url": "https://privacymatters.dlapiper.com/2025/12/singapore-key-amendments-to-the-cybersecurity-act-now-in-force/", "snippet": "On 31 October 2025, key provisions of the Cybersecurity (Amendment) Act 2024 came into effect. CII owners must now report incidents involving Advanced Persistent Threats within two hours. The 2024 Amendment Act expands incident reporting obligations and now directly regulates third-party-owned critical information infrastructure.", "source": "DLA Piper"},
    ],
    "Japan AI privacy": [
        {"title": "Understanding Japan's AI Promotion Act: An Innovation-First Blueprint for AI Regulation", "url": "https://fpf.org/blog/understanding-japans-ai-promotion-act-an-innovation-first-blueprint-for-ai-regulation/", "snippet": "Japan's National Diet passed the AI Promotion Act on May 28, 2025, with most provisions taking effect on June 4, 2025. The Act follows an Innovation-First approach, lighter-touch than the EU.", "source": "Future of Privacy Forum"},
        {"title": "Data Protection & Privacy 2025 - Japan", "url": "https://practiceguides.chambers.com/practice-guides/data-protection-privacy-2025/japan/trends-and-developments", "snippet": "In June 2025, the government adopted a Basic Policy on the Ideal Data Utilization System, which outlines a proposed amendment to the APPI aiming to allow sharing of personal data for statistical analysis and AI development without requiring individual consent.", "source": "Chambers and Partners"},
    ],
    "Japan cybersecurity": [
        {"title": "Japan Adopts New Five-Year Cybersecurity Strategy", "url": "https://www.japantimes.co.jp/news/2025/12/23/japan/crime-legal/new-cybersecurity-strategy-police-sdf/", "snippet": "The Japanese government formally adopted a new cybersecurity strategy at a cabinet meeting in late December 2025 that will guide national policy over the next five years. Japan will establish a framework enabling closer cooperation between the police, Defense Ministry, and Self-Defense Forces when responding to serious cyber incidents. The strategy explicitly identifies cyber operations linked to China, Russia, and North Korea as serious threats to Japan.", "source": "The Japan Times"},
    ],
    "New Zealand privacy": [
        {"title": "New Zealand Privacy Amendment Act 2025 Introduces New Notification Requirements", "url": "https://www.hunton.com/privacy-and-information-security-law/new-zealand-privacy-amendment-act-2025-introduces-new-notification-requirements", "snippet": "On September 23, 2025, the New Zealand Privacy Amendment Act 2025 received royal assent. Parliament extended the commencement date for Part 1 to 1 May 2026 to provide time for agencies to prepare to comply with IPP 3A on indirect collection of personal information.", "source": "Hunton Andrews Kurth"},
    ],
    "Philippines privacy": [
        {"title": "HOME - National Privacy Commission", "url": "https://privacy.gov.ph/", "snippet": "The NPC released NPC Circular 2025-01 which provides guidelines on the processing of personal data through the use of Body-Worn Cameras and alternative recording devices. The NPC held activities in December 2025.", "source": "National Privacy Commission Philippines"},
    ],
    "Hong Kong cybersecurity": [
        {"title": "Hong Kong's First Cybersecurity Law Takes Effect January 1, 2026", "url": "https://www.globalcompliancenews.com/2025/04/21/https-insightplus-bakermckenzie-com-bm-data-technology-hong-kong-the-citys-first-cybersecurity-law-is-expected-to-take-effect-on-1-january-2026_04032025/", "snippet": "Hong Kong's Legislative Council enacted the Protection of Critical Infrastructures (Computer Systems) Bill on March 19, 2025, gazetted as the Protection of Critical Infrastructures (Computer Systems) Ordinance on March 28, 2025. The Ordinance took effect on January 1, 2026, and aims to enhance cybersecurity standards for providers of essential services in eight sectors including energy, banking and financial services, healthcare, and telecommunications.", "source": "Baker McKenzie"},
        {"title": "AI Governance: Practical Guidance from Hong Kong Privacy Commissioner for Personal Data", "url": "https://www.mayerbrown.com/en/insights/publications/2025/10/ai-governance-practical-guidance-from-hong-kong-privacy-commissioner-for-personal-data", "snippet": "The Privacy Commissioner for Personal Data conducted compliance checks in May 2025 and found that 80% of organizations reported using AI in their daily operations, and subsequently issued new practical guidance on AI adoption.", "source": "Mayer Brown"},
    ],
    "Vietnam data protection": [
        {"title": "Vietnam's Personal Data Protection Law Takes Effect January 1, 2026", "url": "https://www.hoganlovells.com/en/publications/vietnam-enacts-landmark-law-on-personal-data-protection-stable-standing-with-stricter-compliance", "snippet": "Vietnam's Law on Personal Data Protection (PDP Law) took effect on January 1, 2026. The PDPL was passed by the National Assembly on June 26, 2025. The implementing decree was issued on December 31, 2025, and took effect on January 1, 2026, creating immediate compliance obligations for organizations already processing Vietnamese personal data. The law proposes significant fines for violations, including up to 5% of an organization's revenue for unauthorized cross-border data transfers.", "source": "Hogan Lovells"},
        {"title": "Vietnam Passes New Cybersecurity Law", "url": "https://rouse.com/insights/news/2025/vietnam-s-draft-cybersecurity-law-2025-key-changes-businesses-need-to-know", "snippet": "On December 10, 2025, Vietnam's National Assembly passed a new Cybersecurity Law, which will take effect on July 1, 2026, consolidating the 2018 Cybersecurity Law and the 2015 Law on Network Information Security.", "source": "Rouse"},
    ],
    "India DPDP": [
        {"title": "Transforming data privacy: Digital Personal Data Protection Rules, 2025", "url": "https://www.ey.com/en_in/insights/cybersecurity/transforming-data-privacy-digital-personal-data-protection-rules-2025", "snippet": "On November 13, 2025, the Government of India formally brought into effect the Digital Personal Data Protection Rules, 2025, which enforce the Digital Personal Data Protection Act, 2023.", "source": "EY India"},
        {"title": "Digital Personal Data Protection (DPDP) Rules 2025 Notified", "url": "https://www.india-briefing.com/news/dpdp-rules-2025-india-data-protection-law-compliance-40769.html/", "snippet": "The Digital Personal Data Protection Rules, 2025, introduced under the DPDPA, 2023, mark a critical step in India's journey towards establishing a robust framework for data privacy. The Data Protection Board of India will be instituted on November 13, 2025.", "source": "India Briefing"},
    ],
}

def create_search_function():
    """Create a search function that returns our collected results."""
    # Track which results have been returned to avoid duplicates
    returned_urls = set()

    def search_function(query):
        """Return matching results for query."""
        nonlocal returned_urls
        results = []
        query_lower = query.lower()

        # Map queries to specific result sets
        if 'australia' in query_lower:
            if 'privacy' in query_lower or 'data' in query_lower:
                results = search_results_data.get('Australia data privacy', [])
            elif 'ai' in query_lower or 'artificial' in query_lower:
                results = search_results_data.get('Australia AI', [])
            elif 'cyber' in query_lower:
                results = search_results_data.get('Australia cybersecurity', [])
        elif 'singapore' in query_lower:
            if 'pdpa' in query_lower or 'privacy' in query_lower or 'data' in query_lower:
                results = search_results_data.get('Singapore PDPA', [])
            elif 'ai' in query_lower or 'artificial' in query_lower:
                results = search_results_data.get('Singapore AI', [])
            elif 'cyber' in query_lower:
                results = search_results_data.get('Singapore cybersecurity', [])
        elif 'japan' in query_lower:
            if 'ai' in query_lower or 'privacy' in query_lower or 'data' in query_lower:
                results = search_results_data.get('Japan AI privacy', [])
            elif 'cyber' in query_lower:
                results = search_results_data.get('Japan cybersecurity', [])
        elif 'new zealand' in query_lower:
            results = search_results_data.get('New Zealand privacy', [])
        elif 'philippines' in query_lower:
            results = search_results_data.get('Philippines privacy', [])
        elif 'hong kong' in query_lower:
            results = search_results_data.get('Hong Kong cybersecurity', [])
        elif 'vietnam' in query_lower:
            results = search_results_data.get('Vietnam data protection', [])
        elif 'india' in query_lower:
            results = search_results_data.get('India DPDP', [])

        # Filter out already-returned URLs to avoid duplicates
        unique_results = []
        for result in results:
            url = result.get('url', '')
            if url and url not in returned_urls:
                unique_results.append(result)
                returned_urls.add(url)

        return unique_results

    return search_function


def main():
    """Main entry point."""
    print("Starting digest generation with collected search results...")
    print()

    # Create search function
    search_function = create_search_function()

    # Run generator
    generator = DigestGenerator(search_function=search_function)
    result = generator.run(verbose=True)

    if result is None:
        return 1

    # Print summary
    print("\n" + "=" * 70)
    print("GENERATION COMPLETE")
    print("=" * 70)
    print(f"Output file: {result['output_file']}")
    print(f"Total words: {result['stats']['word_count']}")
    print(f"Stories collected: {result['stats']['total_collected']}")
    print(f"Stories filtered: {result['stats']['filtered']}")
    print(f"Stories selected: {result['stats']['selected']}")
    print(f"Valid: {'Yes' if result['is_valid'] else 'No'}")
    if result['errors']:
        print(f"\nErrors:")
        for error in result['errors']:
            print(f"  - {error}")
    if result['warnings']:
        print(f"\nWarnings:")
        for warning in result['warnings']:
            print(f"  - {warning}")
    print("=" * 70)

    return 0


if __name__ == '__main__':
    sys.exit(main())
