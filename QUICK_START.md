# Quick Start Guide - Enhanced APJ Digest

## Overview

The APJ Legal Digest Generator now includes enhanced features for superior quality:
- ✅ URL validation (no broken links)
- ✅ Full article content extraction
- ✅ Source credibility scoring
- ✅ LLM-powered summaries and analysis
- ✅ Professional formatting

## Basic Usage

### With Claude Code (Recommended)

Simply request a digest:
```
Generate this week's APAC legal digest
```

Claude Code will automatically:
1. Search for relevant stories across all jurisdictions
2. Validate all URLs
3. Fetch full article content
4. Generate LLM-powered summaries
5. Create executive summary and cross-jurisdictional analysis
6. Save professional digest to `output/digest_YYYY-MM-DD.md`

### Enhanced Features are On by Default

The system automatically uses enhanced features if:
- ✅ Dependencies installed (`pip install -r requirements.txt`)
- ✅ Claude API key set (for LLM features)

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

## Configuration Options

### Standard Mode (No LLM, basic features)

```python
from generate_digest import DigestGenerator

# Create generator with basic features only
generator = DigestGenerator(
    search_function=your_search_function,
    use_enhanced_features=False  # Disable enhancements
)

# Run digest generation
result = generator.run(output_dir='output', verbose=True)
```

### Enhanced Mode (All features - DEFAULT)

```python
from generate_digest import DigestGenerator

# Create generator with all enhanced features
generator = DigestGenerator(
    search_function=your_search_function,
    use_enhanced_features=True  # This is the default
)

# Run digest generation
result = generator.run(output_dir='output', verbose=True)
```

## What Enhanced Mode Provides

### During Story Collection
- **URL Validation**: Every URL tested before inclusion
- **Source Quality Check**: Rejects aggregators and low-quality sources
- **Content Fetching**: Downloads full article instead of just snippet
- **Credibility Scoring**: Each source scored 0.0-1.0

Example output:
```
[2/8] Collecting news stories...
  Enhanced features: URL validation + content fetching enabled
  Collected 45 stories
    URLs validated: 45
    Full content fetched: 38
    Avg source credibility: 0.82
```

### During Story Ranking
- **Multi-factor Scoring**: Materiality (50%) + Jurisdiction (30%) + Credibility (20%)
- **Official Sources Prioritized**: Government/regulatory sources ranked higher

Example output:
```
[4/8] Ranking stories...
  Ranked 32 stories by materiality, jurisdiction, and source credibility
```

### During Content Generation
- **LLM Summaries**: 150-word comprehensive summaries per story
- **Contextual Analysis**: "Why it matters" tailored to each development
- **Executive Summary**: 200-word overview of the week
- **Regional Analysis**: 400-word cross-jurisdictional insights

Example output:
```
[6/8] Generating insights and enhanced summaries...
  Generating LLM-powered story summaries...
    Enhanced 10 story summaries
  Generating executive summary...
  Generating cross-jurisdictional analysis...
  Executive summary: 195 words
  Cross-jurisdictional analysis: 387 words
```

### Final Output
- **Professional Format**: Executive summary + stories + analysis
- **Estimated Read Time**: Calculated based on word count
- **2,500 words**: Perfect for 5-10 minute comprehensive read

Example output:
```
[7/8] Formatting digest...
  Enhanced digest: 2,487 words (~10 min read)
```

## Requirements

### Minimum (Basic Mode)
```bash
pip install python-dateutil>=2.8.2
```

### Full Enhanced Mode
```bash
pip install -r requirements.txt
```

This includes:
- `requests` - HTTP requests
- `beautifulsoup4`, `lxml` - HTML parsing
- `trafilatura` - Content extraction (primary)
- `newspaper3k` - Content extraction (fallback)
- `anthropic` - Claude API for LLM features

### Environment Variables

For LLM features:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

Without this key:
- System falls back to template-based summaries
- No executive summary or cross-jurisdictional analysis
- Still gets URL validation and content fetching

## Output Structure

### Enhanced Digest Format

```markdown
# Weekly APJ Legal & Regulatory Digest
**30 Dec 2024 - 5 Jan 2025** | ~2,487 words | 10 min read

---

## Executive Summary

This week saw significant developments in AI regulation across Singapore
and Australia, with both jurisdictions advancing framework consultations.
Data privacy enforcement continued with notable actions in India...

[Full executive summary]

---

## Key Developments

### 🇦🇺  Australia

#### ACCC Releases AI Regulatory Framework Draft
**Source:** [Australian Competition & Consumer Commission](https://accc.gov.au/...)
**Date:** 2 Jan 2025 | **Type:** Regulation

**Summary:** The Australian Competition and Consumer Commission (ACCC)
released a draft regulatory framework for artificial intelligence systems,
proposing mandatory risk assessments for high-risk AI applications... [150 words]

**Why It Matters:** Requires technology companies deploying AI in Australia
to implement risk management frameworks by Q3 2025, affecting product
development timelines and compliance programs.

**Categories:** `AI/ML` `Competition` `Consumer Protection`

---

[More stories...]

---

## Cross-Jurisdictional Analysis

### Regional Trends
- **AI Governance Convergence:** Multiple jurisdictions advancing
  risk-based AI frameworks with similar principles...

### Cross-Border Implications
- Companies operating across APJ will need harmonized compliance approaches...

---

*This digest covers 30 Dec 2024 - 5 Jan 2025. Stories selected based
on relevance to global technology companies operating in Asia-Pacific.*
```

## Performance

### Processing Time

**Basic Mode**: ~1-2 minutes
**Enhanced Mode**: ~5-10 minutes
- URL validation: +1-2 min
- Content fetching: +2-3 min
- LLM summaries: +2-3 min

### API Costs (Enhanced Mode)

Per digest with 10 stories:
- ~20 API calls (2 per story + summaries)
- ~10,500 tokens total
- **Cost**: ~$0.10-0.15 USD

## Troubleshooting

### "LLM features not available"

**Cause**: Claude API key not set or anthropic package not installed

**Solution**:
```bash
pip install anthropic>=0.18.0
export ANTHROPIC_API_KEY="your-key"
```

### "Enhanced features not available"

**Cause**: Required packages not installed

**Solution**:
```bash
pip install -r requirements.txt
```

### Low source credibility scores

**Cause**: Search returning blog posts instead of official sources

**Solution**: System automatically filters these out. If too many stories filtered:
- Check search queries are targeting official domains
- Review `src/config.py` PRIORITY_SOURCES

### URLs still broken

**Cause**: Validation may be disabled

**Solution**: Ensure `use_enhanced_features=True` (default)

## Best Practices

### 1. Always Use Enhanced Mode
```python
# Good - enhanced features on (default)
generator = DigestGenerator(search_function)

# Less good - missing quality improvements
generator = DigestGenerator(search_function, use_enhanced_features=False)
```

### 2. Set Claude API Key
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### 3. Review Output
Even with automation, manually review:
- ✅ Are summaries accurate?
- ✅ Is "why it matters" relevant?
- ✅ Are key stories included?

### 4. Monitor Credibility Scores
Average credibility should be ≥0.70. If lower:
- Check search queries
- Review filtered stories
- Adjust source lists if needed

## Advanced Usage

### Custom Source Lists

Edit `src/config.py`:
```python
PRIORITY_SOURCES = {
    'AU': {
        'official': [
            'yourdomain.gov.au',  # Add custom official source
            ...
        ]
    }
}
```

### Adjust Word Limits

Edit `src/config.py`:
```python
MAX_TOTAL_WORDS = 3000  # Increase for longer digest
MAX_STORY_SUMMARY = 200  # Longer summaries
```

### Disable Specific Features

```python
# URL validation only, no content fetch
collector = NewsCollector(
    start_date, end_date,
    enable_validation=True,
    enable_content_fetch=False
)

# Use LLM but not enhanced formatter
# (Customize in generate_digest.py)
```

## Next Steps

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Set API key**: `export ANTHROPIC_API_KEY="..."`
3. **Generate digest**: Ask Claude Code to generate this week's digest
4. **Review output**: Check `output/digest_YYYY-MM-DD.md`
5. **Iterate**: Adjust configuration as needed

## Support

- **Detailed docs**: See `DIGEST_IMPROVEMENTS.md` and `IMPLEMENTATION_SUMMARY.md`
- **Configuration**: See `src/config.py`
- **Issues**: Check validation output for specific errors

---

**Version**: 2.0.0
**Enhanced Mode**: Enabled by default
**Quality**: Publication-ready
