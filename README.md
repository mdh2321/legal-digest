# APAC Legal News Digest Generator

An automated system to generate weekly legal news digests covering Asia-Pacific jurisdictions, focused on technology law developments relevant to global SaaS companies.

## Overview

This system automatically:
- Collects legal news from 10 APAC jurisdictions (AU, SG, JP, IN, PH, ID, HK, KR, NZ, VN)
- Filters for technology-relevant topics (AI, data privacy, eSignatures, tax, etc.)
- Ranks stories by materiality and jurisdiction priority
- Generates **RSS feeds** or markdown digests with regional insights
- Includes SaaS-specific relevance analysis and key takeaways
- Validates output against quality standards

## Features

### Jurisdiction Coverage
**Tier 1 (Priority)** - minimum 1 story each:
- 🇦🇺 Australia
- 🇸🇬 Singapore
- 🇯🇵 Japan

**Tier 2** - maximum 3 stories total:
- 🇮🇳 India
- 🇵🇭 Philippines
- 🇮🇩 Indonesia
- 🇭🇰 Hong Kong
- 🇰🇷 South Korea
- 🇳🇿 New Zealand
- 🇻🇳 Vietnam

### Content Focus Areas
- AI/ML regulation & governance
- Data privacy & protection (cross-border transfers, data localization)
- Cybersecurity requirements
- Cloud & SaaS (software licensing, subscription services)
- Electronic signatures & digital identity
- Contract law (standard terms, limitation of liability)
- Competition & digital markets
- Consumer protection (unfair contract terms)
- Corporate governance & ESG
- Fintech & financial services
- Tax (digital services tax, transfer pricing)
- Anti-money laundering (AML)
- Anti-bribery & corruption
- Outsourcing & vendor management

### Output Formats

**RSS Feed** (default, for Readwise Reader and other RSS readers):
- Valid RSS 2.0 with `content:encoded` for rich content
- Each story includes: headline, executive summary, key takeaways, SaaS relevance
- Categories for country and practice areas (enables filtering)
- Clean source URLs

**Markdown** (alternative):
- Target: 8-10 stories
- Maximum: 1,000 words
- Region insights (≤120 words)
- Source citations with clean URLs
- Category tags
- Relevance statements

## Installation

### Prerequisites
- Python 3.8 or higher
- Web search capability (provided by Claude Code integration)

### Setup

1. Clone or download this repository:
```bash
cd legal-digest
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### With Claude Code Integration

The primary way to use this system is through Claude Code, which provides web search integration:

1. Open Claude Code in the repository directory
2. Request digest generation:
   ```
   Generate this week's APAC legal digest
   ```

3. Claude Code will:
   - Calculate the date range (last Monday-Sunday)
   - Search for relevant legal news
   - Process and filter stories
   - Generate the formatted digest
   - Save to `output/digest_YYYY-MM-DD.md`

### Manual/Testing Mode

For testing without web search:

```bash
# Generate RSS feed (default)
python run_digest.py --format rss

# Generate Markdown digest
python run_digest.py --format markdown

# Use cached search results
python run_digest.py --format rss --results search_results.json

# Specify output directory
python run_digest.py --format rss --output ./digests
```

**CLI Options:**
- `--format, -f`: Output format (`rss` or `markdown`, default: `rss`)
- `--output, -o`: Output directory (default: `output`)
- `--results, -r`: JSON file with cached search results
- `--quiet, -q`: Suppress progress output

## System Architecture

### Core Modules

```
src/
├── config.py              # Configuration constants
├── date_utils.py          # Date range calculation
├── news_collector.py      # Web search integration
├── content_filter.py      # Inclusion/exclusion filtering
├── story_ranker.py        # Materiality-based ranking
├── story_selector.py      # Story selection logic
├── formatter.py           # Markdown output generation
├── rss_generator.py       # RSS 2.0 feed generation
├── insights_generator.py  # Regional trend analysis
└── qa_validator.py        # Quality assurance checks
```

### Processing Pipeline

1. **Date Calculation**: Determine last Monday-Sunday period ending yesterday
2. **News Collection**: Search for stories across all jurisdictions
3. **Content Filtering**: Apply topic inclusion/exclusion rules
4. **Story Ranking**: Score by materiality (60%) and jurisdiction priority (40%)
5. **Story Selection**: Select 8-10 stories meeting tier requirements
6. **Insights Generation**: Identify cross-jurisdictional trends
7. **Formatting**: Generate markdown with proper structure
8. **Quality Assurance**: Validate against all requirements

## Configuration

Edit `src/config.py` to customize:

- Jurisdiction priorities
- Topic inclusion/exclusion keywords
- Story count targets
- Word limits
- Ranking weights
- Search query templates

## Output Structure

```markdown
# Weekly APJ Legal Digest — DD Month YYYY (≈XXX words)

## 🇦🇺  Australia
- **[Headline]** ([Source](URL), DD MMM)
  Summary paragraph...
  *Why it matters:* Relevance statement.
  `Category` `Tags`

## 🇸🇬  Singapore
[Stories...]

## 🇯🇵  Japan
[Stories...]

## 🌏  Other APJ
### New Zealand
[Stories...]

## 📊  Region Insights
- **Trend Name:** Description
- **Cross-border impacts:** Analysis
- **Upcoming:** Key dates
```

## Quality Assurance

The system validates:
- ✓ All stories from target week
- ✓ Minimum jurisdiction requirements (AU: 1, SG: 1, JP: 1)
- ✓ Maximum Tier 2 stories (≤3)
- ✓ Total word count (≤1,000)
- ✓ No duplicate URLs
- ✓ Clean URLs (no tracking parameters)
- ✓ Proper formatting
- ✓ Category tags assigned
- ✓ Acronyms expanded on first use

## Customization

### Adding New Jurisdictions

Edit `src/config.py`:

```python
TIER2_JURISDICTIONS = {
    'TH': {'name': 'Thailand', 'flag': '🇹🇭', 'priority': 1},
    # Add more...
}
```

### Adding Topic Categories

Edit `src/config.py`:

```python
INCLUDE_TOPICS = {
    'Web3': ['blockchain', 'cryptocurrency', 'NFT', 'DeFi'],
    # Add more...
}
```

### Adjusting Ranking Weights

Edit `src/config.py`:

```python
MATERIALITY_WEIGHT = 0.7  # Increase focus on materiality
JURISDICTION_WEIGHT = 0.3
```

## Troubleshooting

### No Stories Found
- Check date range is correct
- Verify search function is working
- Review filter criteria (may be too restrictive)

### Too Many/Few Stories
- Adjust `TARGET_STORY_COUNT` in config.py
- Modify ranking thresholds
- Update inclusion keywords

### Word Count Exceeded
- Reduce target story count
- Shorten insights section
- Adjust summary lengths

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black src/ *.py
flake8 src/ *.py
```

### Adding Features

1. Create new module in `src/`
2. Update `generate_digest.py` to integrate
3. Add tests in `tests/`
4. Update documentation

## License

This project is provided as-is for internal use.

## Support

For issues or questions:
1. Check this README
2. Review configuration in `src/config.py`
3. Examine validation output for specific errors
4. Consult Claude Code documentation

## Version History

- **1.1.0** (2026-01-07): RSS Feed Support
  - Added RSS 2.0 feed generation for Readwise Reader
  - Added SaaS-specific relevance analysis and key takeaways
  - Expanded jurisdiction coverage to 10 (added Korea, Indonesia)
  - Added Tax category for digital services tax tracking
  - Enhanced topic keywords for SaaS company relevance
  - CLI now defaults to RSS output format

- **1.0.0** (2026-01-06): Initial release
  - Core digest generation pipeline
  - 8 jurisdiction coverage
  - 13 topic categories
  - QA validation system
  - Markdown formatting
  - Regional insights generation
