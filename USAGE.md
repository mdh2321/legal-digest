# Usage Guide

## Quick Start

### Option 1: With Claude Code (Recommended)

The easiest way to generate a digest is through Claude Code with web search integration:

1. Open Claude Code in this repository
2. Say: "Generate this week's APAC legal digest"
3. Claude Code will automatically:
   - Search for relevant news stories
   - Filter and rank them
   - Generate the formatted digest
   - Save to `output/digest_YYYY-MM-DD.md`

### Option 2: Manual Testing

Run the test script to verify the system with sample data:

```bash
python test_system.py
```

This will:
- Test all modules
- Generate a sample digest with test data
- Save to `output/test_digest.md`
- Display validation results

## Understanding the Output

### File Location
Generated digests are saved to:
```
output/digest_YYYY-MM-DD.md
```

Where `YYYY-MM-DD` is the Sunday ending the target week.

### Output Format

```markdown
# Weekly APJ Legal Digest — DD Month YYYY (≈XXX words)

## 🇦🇺  Australia
[1+ stories from Australia]

## 🇸🇬  Singapore
[1+ stories from Singapore]

## 🇯🇵  Japan
[1+ stories from Japan]

## 🌏  Other APJ
[Up to 3 stories from NZ, PH, HK, VN, IN]

## 📊  Region Insights
[Cross-jurisdictional analysis, ≤120 words]
```

### Story Format

Each story includes:
- **Headline** (≤12 words, bold)
- Source link (embedded in source name)
- Date (DD MMM format)
- Summary (2-4 sentences)
- Relevance statement ("Why it matters")
- Category tags

Example:
```markdown
- **PDPC Updates Cross-Border Data Transfer Guidelines** ([Personal Data Protection Commission](https://example.sg), 15 Dec)
  Singapore's Personal Data Protection Commission released updated guidelines...
  *Why it matters:* Affects data handling and privacy compliance obligations.
  `Data Privacy`
```

## Customization

### Adjust Date Range

By default, the system calculates "last Monday-Sunday ending yesterday."

To use a custom date range, modify `src/date_utils.py`:

```python
def get_last_week_range():
    # Custom implementation here
    start_date = datetime(2025, 12, 15).date()
    end_date = datetime(2025, 12, 21).date()
    return start_date, end_date
```

### Change Story Limits

Edit `src/config.py`:

```python
TARGET_STORY_COUNT = (6, 8)  # (min, max) - changed from (8, 10)
TIER2_MAX_STORIES = 2        # Changed from 3
```

### Add/Remove Jurisdictions

Edit `src/config.py`:

```python
# Add to Tier 2
TIER2_JURISDICTIONS = {
    'TH': {'name': 'Thailand', 'flag': '🇹🇭', 'priority': 1},
    # ... existing jurisdictions
}

# Or promote to Tier 1
TIER1_JURISDICTIONS = {
    'HK': {'name': 'Hong Kong', 'flag': '🇭🇰', 'min_stories': 1, 'priority': 2},
    # ... existing jurisdictions
}
```

### Modify Topic Categories

Edit `src/config.py`:

```python
INCLUDE_TOPICS = {
    'Quantum Computing': ['quantum', 'quantum computing', 'quantum encryption'],
    # ... existing topics
}
```

### Adjust Ranking Weights

Edit `src/config.py`:

```python
# Increase focus on materiality vs jurisdiction
MATERIALITY_WEIGHT = 0.7  # Changed from 0.6
JURISDICTION_WEIGHT = 0.3  # Changed from 0.4
```

## Validation Checks

The system automatically validates:
- ✓ Date range (all stories from target week)
- ✓ Jurisdiction minimums (AU: 1, SG: 1, JP: 1)
- ✓ Tier 2 maximum (≤3 stories)
- ✓ Total story count (8-10, or 6+ if low quality week)
- ✓ Word count (≤1,000 words)
- ✓ No duplicate URLs
- ✓ Clean URLs (no tracking parameters)
- ✓ Category tags assigned
- ✓ Proper formatting

### Interpreting Validation Results

**Errors** (must fix):
- Stories outside date range
- Missing Tier 1 jurisdictions
- Duplicate URLs
- Exceeds maximum story count

**Warnings** (review):
- Below target story count (acceptable if low news week)
- Exceeds word count (minor overage OK)
- Missing category tags
- Tracking parameters in URLs

## Troubleshooting

### "No stories found"
- Check if it's a slow news week (system will generate fewer stories)
- Review `INCLUDE_TOPICS` in config - may be too restrictive
- Verify date range is correct

### "Too many/few stories"
- Adjust `TARGET_STORY_COUNT` in config.py
- Modify ranking thresholds in story_ranker.py
- Update materiality keywords

### "Word count exceeded"
- Reduce `TARGET_STORY_COUNT`
- Shorten `MAX_INSIGHTS_WORDS`
- Review story summaries for verbosity

### "Validation errors"
- Read error messages carefully
- Check `output/digest_*.md` for issues
- Run `python test_system.py` to verify system health

## Tips for Best Results

1. **Run on Mondays**: Fresh weekly digest of previous week
2. **Review output**: Always check generated digest for accuracy
3. **Verify URLs**: Click a few links to ensure they're live
4. **Edit insights**: Manual review of Region Insights recommended
5. **Track trends**: Compare week-over-week for regulatory patterns

## Integration

### With Editorial Workflow

1. Generate digest (automated)
2. Review for accuracy (human)
3. Edit insights section if needed (human)
4. Add editorial notes (human)
5. Publish (automated)

### With Email Newsletter

```python
# Read digest
with open('output/digest_2025-12-21.md', 'r') as f:
    digest_content = f.read()

# Convert markdown to HTML
import markdown
html_content = markdown.markdown(digest_content)

# Send via email
send_email(
    subject="Weekly APJ Legal Digest",
    body=html_content,
    recipients=subscriber_list
)
```

### With Slack/Teams

```python
# Post to Slack
import requests

with open('output/digest_2025-12-21.md', 'r') as f:
    digest = f.read()

requests.post(
    webhook_url,
    json={"text": digest}
)
```

## Support

For issues:
1. Check this guide
2. Review README.md
3. Run test_system.py
4. Check validation output
5. Review src/config.py settings
