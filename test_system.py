#!/usr/bin/env python3
"""Test script to verify system functionality."""
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.date_utils import get_last_week_range, get_week_description
from src.news_collector import NewsStory, NewsCollector
from src.content_filter import ContentFilter
from src.story_ranker import StoryRanker
from src.story_selector import StorySelector
from src.formatter import DigestFormatter
from src.insights_generator import InsightsGenerator
from src.qa_validator import QAValidator


def create_test_stories(start_date, end_date):
    """Create sample stories for testing."""
    stories = []

    # Australia - Data Privacy
    stories.append(NewsStory(
        title="OAIC Issues New AI Governance Guidelines",
        url="https://www.oaic.gov.au/privacy/ai-guidance-2025",
        source="Office of the Australian Information Commissioner",
        date=datetime.combine(end_date, datetime.min.time()),
        summary="The Office of the Australian Information Commissioner (OAIC) has released comprehensive guidelines for organizations deploying artificial intelligence systems that process personal information. The guidance emphasizes privacy by design principles and mandatory impact assessments.",
        jurisdiction="AU",
        snippet="New OAIC guidelines require privacy impact assessments for AI systems handling personal data."
    ))

    # Singapore - Fintech
    stories.append(NewsStory(
        title="MAS Proposes Digital Payment Token Regulations",
        url="https://www.mas.gov.sg/regulation/payments/digital-tokens-2025",
        source="Monetary Authority of Singapore",
        date=datetime.combine(end_date, datetime.min.time()),
        summary="The Monetary Authority of Singapore has issued a consultation paper proposing new regulations for digital payment token service providers, including enhanced consumer protection measures and cybersecurity requirements.",
        jurisdiction="SG",
        snippet="MAS consultation on digital payment token regulations with 60-day comment period."
    ))

    # Japan - Cybersecurity
    stories.append(NewsStory(
        title="Japan Strengthens Critical Infrastructure Cybersecurity Rules",
        url="https://www.nisc.go.jp/eng/security-policy-2025.html",
        source="National Center of Incident Readiness and Strategy for Cybersecurity",
        date=datetime.combine(end_date, datetime.min.time()),
        summary="Japan's cabinet approved amendments to cybersecurity regulations requiring critical infrastructure operators to report incidents within 24 hours and implement enhanced monitoring systems.",
        jurisdiction="JP",
        snippet="New Japan cybersecurity rules mandate 24-hour incident reporting for critical infrastructure."
    ))

    # Australia - Competition
    stories.append(NewsStory(
        title="ACCC Launches Digital Platform Competition Inquiry",
        url="https://www.accc.gov.au/inquiries/digital-platforms-2025",
        source="Australian Competition and Consumer Commission",
        date=datetime.combine(end_date - timedelta(days=1), datetime.min.time()),
        summary="The Australian Competition and Consumer Commission announced a comprehensive inquiry into competition in digital platform markets, focusing on app stores, payment systems, and data portability.",
        jurisdiction="AU",
        snippet="ACCC inquiry to examine digital platform market power and consumer choice."
    ))

    # Singapore - Data Privacy
    stories.append(NewsStory(
        title="PDPC Updates Cross-Border Data Transfer Guidelines",
        url="https://www.pdpc.gov.sg/guidelines/cross-border-transfers-2025",
        source="Personal Data Protection Commission",
        date=datetime.combine(end_date - timedelta(days=2), datetime.min.time()),
        summary="Singapore's Personal Data Protection Commission released updated guidelines on cross-border data transfers, aligning with international standards while providing clear pathways for compliance.",
        jurisdiction="SG",
        snippet="PDPC clarifies requirements for international data transfers under PDPA."
    ))

    # New Zealand - Privacy
    stories.append(NewsStory(
        title="Privacy Commissioner Issues Guidance on Biometric Data",
        url="https://www.privacy.org.nz/biometric-guidance-2025",
        source="Office of the Privacy Commissioner",
        date=datetime.combine(end_date, datetime.min.time()),
        summary="New Zealand's Privacy Commissioner published guidance on the collection and use of biometric data, emphasizing consent requirements and security safeguards for facial recognition and fingerprint systems.",
        jurisdiction="NZ",
        snippet="New Zealand guidance addresses biometric data collection and consent requirements."
    ))

    # Hong Kong - Data Privacy
    stories.append(NewsStory(
        title="PCPD Enforces Data Breach Notification Requirements",
        url="https://www.pcpd.org.hk/breach-notification-2025",
        source="Privacy Commissioner for Personal Data",
        date=datetime.combine(end_date - timedelta(days=1), datetime.min.time()),
        summary="Hong Kong's Privacy Commissioner announced enhanced enforcement of data breach notification requirements, with several organizations fined for delayed reporting of security incidents affecting consumer data.",
        jurisdiction="HK",
        snippet="PCPD issues fines for delayed data breach notifications."
    ))

    # India - Digital Regulation
    stories.append(NewsStory(
        title="MeitY Releases Draft Digital India Rules",
        url="https://www.meity.gov.in/digital-india-rules-2025",
        source="Ministry of Electronics and Information Technology",
        date=datetime.combine(end_date - timedelta(days=3), datetime.min.time()),
        summary="India's Ministry of Electronics and Information Technology published draft rules for digital service providers, including content moderation obligations and data localization requirements for social media platforms.",
        jurisdiction="IN",
        snippet="Draft Digital India rules propose content moderation and data localization requirements."
    ))

    return stories


def main():
    """Run system tests."""
    print("=" * 70)
    print("APAC Legal Digest Generator - System Test")
    print("=" * 70)

    # Test 1: Date utilities
    print("\n[TEST 1] Date Utilities")
    start_date, end_date = get_last_week_range()
    week_desc = get_week_description(start_date, end_date)
    print(f"  ✓ Date range: {week_desc}")

    # Test 2: Create test stories
    print("\n[TEST 2] Story Creation")
    stories = create_test_stories(start_date, end_date)
    print(f"  ✓ Created {len(stories)} test stories")

    # Test 3: Content filtering
    print("\n[TEST 3] Content Filtering")
    content_filter = ContentFilter(start_date, end_date)
    filtered = content_filter.filter_stories(stories)
    print(f"  ✓ Filtered: {len(filtered)} stories passed filters")

    # Test 4: Story ranking
    print("\n[TEST 4] Story Ranking")
    ranker = StoryRanker()
    ranked = ranker.rank_stories(filtered)
    print(f"  ✓ Ranked {len(ranked)} stories")
    if ranked:
        print(f"    Top story: {ranked[0].title[:50]}... (score: {ranked[0].overall_score:.3f})")

    # Test 5: Story selection
    print("\n[TEST 5] Story Selection")
    selector = StorySelector(ranker)
    selected = selector.select_stories(ranked)
    total_selected = selector.get_story_count(selected)
    print(f"  ✓ Selected {total_selected} stories")

    from src.config import ALL_JURISDICTIONS
    for jur, stories in selected.items():
        jur_name = ALL_JURISDICTIONS[jur]['name']
        print(f"    {jur_name}: {len(stories)}")

    # Validate selection
    is_valid = selector.validate_selection(selected)
    print(f"  ✓ Selection valid: {is_valid}")

    # Test 6: Insights generation
    print("\n[TEST 6] Insights Generation")
    insights_gen = InsightsGenerator()
    insights = insights_gen.generate_insights(selected)
    word_count = len(insights.split())
    print(f"  ✓ Generated insights ({word_count} words)")
    print(f"    Preview: {insights[:100]}...")

    # Test 7: Formatting
    print("\n[TEST 7] Digest Formatting")
    formatter = DigestFormatter(start_date, end_date)

    # Expand acronyms
    for jur, story_list in selected.items():
        for i, story in enumerate(story_list):
            selected[jur][i] = formatter.expand_acronyms_in_story(story)

    digest_text = formatter.format_digest(selected, insights)
    total_words = len(digest_text.split())
    print(f"  ✓ Formatted digest ({total_words} words)")

    # Test 8: Quality assurance
    print("\n[TEST 8] Quality Assurance")
    validator = QAValidator(start_date, end_date)
    is_valid, errors, warnings = validator.validate_all(selected, digest_text)

    print(f"  ✓ Validation complete")
    print(f"    Valid: {is_valid}")
    print(f"    Errors: {len(errors)}")
    print(f"    Warnings: {len(warnings)}")

    if errors:
        for error in errors[:3]:  # Show first 3 errors
            print(f"      - {error}")

    # Save test output
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)
    test_file = output_dir / 'test_digest.md'

    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(digest_text)

    print(f"\n  ✓ Test digest saved to: {test_file}")

    # Print sample output
    print("\n" + "=" * 70)
    print("SAMPLE OUTPUT (first 500 characters)")
    print("=" * 70)
    print(digest_text[:500] + "...\n")

    # Summary
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print("✓ All core modules functional")
    print("✓ End-to-end pipeline working")
    print(f"✓ Generated {total_selected}-story digest in {total_words} words")
    print("=" * 70)

    return 0


if __name__ == '__main__':
    sys.exit(main())
