# APJ Legal Digest Quality Improvements

## Executive Summary

The current digest implementation has three critical weaknesses:

1. **Poor Source Quality**: Generic web searches return low-quality sources, aggregators, and outdated content
2. **Broken/Invalid URLs**: No URL validation or content verification before inclusion
3. **Barebones Content**: Using only search snippets instead of actual article content, resulting in shallow summaries

This document outlines comprehensive improvements to create a professional-grade legal news digest that can be read in 5-10 minutes and provides real value to tech company legal teams.

---

## Current Issues Analysis

### 1. Source Quality Problems

**Current Approach:**
- Generic searches: `{country} {topic} {year} law policy regulation`
- No prioritization of authoritative sources
- SOURCE_PRIORITY config exists but is never used
- No source validation or credibility scoring

**Problems:**
- Returns blog posts, press releases, and secondary sources
- Misses official regulatory announcements
- Includes law firm marketing content
- No distinction between primary and secondary sources

### 2. URL and Content Issues

**Current Approach:**
- Takes search result URLs as-is (after cleaning tracking params)
- Uses only the snippet from search results
- No content validation or extraction
- No check if URLs are accessible

**Problems:**
- URLs may be paywalled, broken, or redirect
- Snippets are truncated and lack context
- No actual article content is analyzed
- Missing key details and nuance

### 3. Content Depth Issues

**Current Approach:**
- Summary = search snippet (often 1-2 sentences)
- "Why it matters" is a template lookup table
- Insights are generic and template-based
- 1,000 word limit is too restrictive

**Problems:**
- Doesn't provide enough context
- Can't be read as standalone brief
- Requires clicking through to understand stories
- Fails the "5-10 minute comprehensive overview" requirement

---

## Recommended Improvements

### Phase 1: Source Quality Enhancement

#### 1.1 Prioritized Source Lists

Create curated source lists for each jurisdiction:

**Australia:**
- Official: legislation.gov.au, treasury.gov.au, dfat.gov.au
- Regulators: ACCC, ASIC, OAIC, eSafety Commissioner
- Courts: Federal Court, High Court
- Quality publications: Australian Financial Review, The Australian

**Singapore:**
- Official: MAS, IMDA, PDPC, AGC
- Publications: Straits Times, Business Times
- Legal: Singapore Law Gazette

**Japan:**
- Official: Digital Agency, METI, FSA, PPC
- Publications: Nikkei Asia, Japan Times
- Legal: Anderson Mori & Tomotsune insights

**Continue for all jurisdictions...**

#### 1.2 Multi-Tier Search Strategy

```python
def collect_stories_tiered(jurisdiction, search_function):
    """
    Tier 1: Official government/regulatory sources (60% weight)
    Tier 2: Major news publications (30% weight)
    Tier 3: Legal publications/law firms (10% weight)
    """
    stories = []

    # Tier 1: Search official domains FIRST
    official_queries = build_official_source_queries(jurisdiction)
    for query in official_queries:
        results = search_function(query)
        stories.extend(parse_and_validate(results, source_tier=1))

    # Tier 2: Major publications
    news_queries = build_news_source_queries(jurisdiction)
    for query in news_queries:
        results = search_function(query)
        stories.extend(parse_and_validate(results, source_tier=2))

    # Tier 3: Legal publications (only if needed)
    if len(stories) < minimum_threshold:
        legal_queries = build_legal_source_queries(jurisdiction)
        for query in legal_queries:
            results = search_function(query)
            stories.extend(parse_and_validate(results, source_tier=3))

    return rank_by_source_quality(stories)
```

#### 1.3 Source Validation

Add source credibility scoring:

```python
def score_source_credibility(url, source_name):
    """
    Score source credibility: 0.0 (low) to 1.0 (high)
    """
    score = 0.5  # baseline

    # Official government/regulatory: +0.5
    if matches_official_domains(url):
        score += 0.5

    # Major news publication: +0.3
    elif is_major_news_outlet(source_name):
        score += 0.3

    # Legal publication: +0.2
    elif is_legal_publication(source_name):
        score += 0.2

    # Law firm: +0.1
    elif is_law_firm(url):
        score += 0.1

    # Penalties
    if is_aggregator(url):  # -0.3
        score -= 0.3
    if is_press_release_only(url):  # -0.2
        score -= 0.2

    return max(0.0, min(1.0, score))
```

### Phase 2: URL and Content Validation

#### 2.1 URL Validation

```python
def validate_url(url):
    """
    Validate URL before including in digest
    Returns: (is_valid, final_url, error_message)
    """
    try:
        # Check accessibility (head request)
        response = requests.head(url, timeout=5, allow_redirects=True)

        # Follow redirects to final URL
        final_url = response.url

        # Check status code
        if response.status_code != 200:
            return False, None, f"HTTP {response.status_code}"

        # Check for paywalls (common patterns)
        if is_paywalled(response.headers):
            return False, None, "Paywalled content"

        # Prefer original sources over aggregators
        if is_aggregator(final_url):
            original = find_original_source(final_url)
            if original:
                return validate_url(original)

        return True, final_url, None

    except requests.RequestException as e:
        return False, None, str(e)
```

#### 2.2 Content Fetching

**Critical Improvement:** Fetch actual article content instead of just snippets.

```python
def fetch_article_content(url):
    """
    Fetch and extract article content
    Returns: (title, content, publish_date, author)
    """
    # Use a library like newspaper3k, readability, or trafilatura
    from newspaper import Article

    article = Article(url)
    article.download()
    article.parse()

    return {
        'title': article.title,
        'content': article.text,
        'publish_date': article.publish_date,
        'authors': article.authors,
        'summary': article.summary if article.summary else generate_summary(article.text)
    }
```

### Phase 3: Enhanced Content Generation

#### 3.1 LLM-Powered Summaries

Instead of using snippets, generate proper summaries:

```python
def generate_story_summary(article_content, max_words=150):
    """
    Use Claude to generate a comprehensive summary
    """
    prompt = f"""
    Summarize this legal/regulatory news article in 3-4 sentences ({max_words} words max).
    Focus on:
    1. What happened (new law, ruling, enforcement action, etc.)
    2. Key details (who, what, when, scope)
    3. Implications for technology companies

    Article:
    {article_content}

    Summary:
    """

    # Call Claude API
    summary = call_claude_api(prompt, max_tokens=200)
    return summary.strip()
```

#### 3.2 Contextual "Why It Matters" Analysis

Replace template-based relevance with actual analysis:

```python
def generate_why_it_matters(article_content, jurisdiction, categories):
    """
    Generate contextual relevance statement
    """
    prompt = f"""
    For this {jurisdiction} legal/regulatory development, explain in 1-2 sentences why it matters to global technology companies operating in Asia-Pacific.

    Focus on practical business implications:
    - Compliance requirements
    - Operational impacts
    - Strategic considerations
    - Timeline/deadlines

    Article summary:
    {article_content}

    Categories: {', '.join(categories)}

    Why it matters:
    """

    analysis = call_claude_api(prompt, max_tokens=100)
    return analysis.strip()
```

#### 3.3 Key Takeaways Extraction

Add actionable takeaways:

```python
def extract_key_takeaways(article_content):
    """
    Extract 2-3 key takeaways
    """
    prompt = f"""
    Extract 2-3 key action items or takeaways from this legal/regulatory article.
    Format as bullet points. Focus on what tech companies should know or do.

    Article:
    {article_content}

    Key Takeaways:
    """

    takeaways = call_claude_api(prompt, max_tokens=150)
    return takeaways.strip()
```

### Phase 4: Improved Digest Structure

#### 4.1 New Digest Format

```markdown
# Weekly APJ Legal & Regulatory Digest
**{Date Range}** | ~{word_count} words | {read_time} min read

## Executive Summary
[2-3 paragraph overview of the week's key themes and most important developments]

---

## Key Developments

### 🇦🇺 Australia

#### [Story Headline]
**Source:** [Publication Name](url) | **Date:** DD MMM YYYY | **Type:** Regulation/Court Decision/Enforcement

**Summary:**
[3-4 sentence comprehensive summary of the development]

**Why It Matters:**
[2-3 sentences on practical implications for tech companies]

**Key Takeaways:**
- Action item or important detail #1
- Action item or important detail #2
- Action item or important detail #3

**Categories:** `AI/ML` `Data Privacy` `Competition`

---

### 🇸🇬 Singapore
[Stories...]

---

## Cross-Jurisdictional Analysis

### Emerging Trends
- **AI Governance Convergence:** [Detailed analysis of how AI regulations are developing across the region]
- **Data Localization:** [Analysis of data sovereignty requirements]

### Regional Implications
[Analysis of how developments in one jurisdiction might influence others or create compliance challenges for regional operations]

### Compliance Calendar
- **15 Jan 2025:** Singapore PDPA amendment effective date
- **31 Mar 2025:** Australia Privacy Act consultation period closes

---

## Spotlight: [Deep Dive on Most Important Story]

[Longer analysis of the week's most significant development, 200-300 words]

---

## Resources & Further Reading

- Link to full official documents
- Link to regulatory guidance
- Link to expert analysis

---

*This digest covers {start_date} - {end_date}. For questions or custom analysis, contact [team].*
```

#### 4.2 Adjusted Word Limits

For a 5-10 minute read:
- **Current:** 1,000 words (too short)
- **Recommended:** 2,000-2,500 words
  - Executive Summary: 150-200 words
  - Stories (8-10 × 200 words each): 1,600-2,000 words
  - Cross-Jurisdictional Analysis: 300-400 words
  - Spotlight: 200-300 words

```python
# Updated config
MAX_TOTAL_WORDS = 2500  # Up from 1000
MAX_STORY_SUMMARY = 150  # New limit per story
MAX_EXECUTIVE_SUMMARY = 200  # New section
MAX_INSIGHTS_WORDS = 400  # Up from 120
MAX_SPOTLIGHT_WORDS = 300  # New section
```

### Phase 5: Enhanced Search Queries

#### 5.1 More Specific Queries

```python
def build_enhanced_search_queries(jurisdiction, start_date, end_date):
    """
    Build more targeted search queries
    """
    jur_info = JURISDICTION_INFO[jurisdiction]

    queries = []

    # Official announcements
    for regulator in jur_info['regulators']:
        queries.extend([
            f'site:{regulator} announced OR issued OR published after:{start_date}',
            f'site:{regulator} new regulation OR guidance after:{start_date}',
        ])

    # Court decisions
    for court in jur_info['courts']:
        queries.append(
            f'site:{court} decision OR judgment OR ruling after:{start_date}'
        )

    # News coverage with date range
    for topic in PRIORITY_TOPICS:
        queries.append(
            f'{jur_info["name"]} {topic} regulation law after:{start_date} before:{end_date}'
        )

    # Enforcement actions
    queries.append(
        f'{jur_info["name"]} enforcement action OR fine OR penalty technology after:{start_date}'
    )

    return queries
```

#### 5.2 Source-Specific Queries

```python
# Australia
AUSTRALIA_SOURCES = {
    'regulators': [
        'accc.gov.au',
        'asic.gov.au',
        'oaic.gov.au',
        'esafety.gov.au',
    ],
    'legislation': [
        'legislation.gov.au',
        'aph.gov.au',  # Parliament
    ],
    'courts': [
        'fedcourt.gov.au',
        'hcourt.gov.au',
    ],
    'news': [
        'afr.com',
        'theaustralian.com.au',
        'smh.com.au',
    ]
}

# Singapore
SINGAPORE_SOURCES = {
    'regulators': [
        'mas.gov.sg',  # Monetary Authority
        'imda.gov.sg',  # Info-communications Media Development Authority
        'pdpc.gov.sg',  # Personal Data Protection Commission
        'csa.gov.sg',  # Cyber Security Agency
    ],
    'legislation': [
        'sso.agc.gov.sg',  # Singapore Statutes Online
        'parliament.gov.sg',
    ],
    'courts': [
        'judiciary.gov.sg',
    ],
    'news': [
        'straitstimes.com',
        'businesstimes.com.sg',
    ]
}

# Continue for all jurisdictions...
```

---

## Implementation Priority

### High Priority (Fix Immediately)
1. ✅ Add URL validation
2. ✅ Implement content fetching (not just snippets)
3. ✅ Use source credibility scoring
4. ✅ Increase word limit to 2,000-2,500 words
5. ✅ Add LLM-powered summaries and analysis

### Medium Priority
6. Implement tiered source searches
7. Add executive summary section
8. Add cross-jurisdictional analysis
9. Add compliance calendar
10. Add key takeaways per story

### Low Priority (Nice to Have)
11. Add spotlight/deep dive section
12. Add resources section
13. Implement caching for content fetching
14. Add email-friendly HTML formatting

---

## Technical Implementation Notes

### Required Dependencies

```python
# Add to requirements.txt
newspaper3k>=0.2.8  # Article extraction
readability-lxml>=0.8.1  # Content extraction
trafilatura>=1.6.0  # Alternative content extraction
anthropic>=0.18.0  # Claude API for summaries
beautifulsoup4>=4.12.0  # HTML parsing
lxml>=4.9.0  # XML/HTML processing
```

### API Integration

The digest generator will need to call Claude API for:
- Story summarization
- "Why it matters" analysis
- Executive summary generation
- Cross-jurisdictional insights

Estimate: ~15-20 API calls per digest generation
- 10 stories × 2 calls each (summary + why it matters)
- 1 call for executive summary
- 1 call for cross-jurisdictional analysis

### Performance Considerations

- **Content fetching**: Parallelize article downloads (async/concurrent)
- **URL validation**: Cache results to avoid repeated checks
- **LLM calls**: Batch where possible, cache results
- **Estimated runtime**: 5-10 minutes per digest generation (vs. current ~1 minute)

### Error Handling

```python
def robust_story_collection(jurisdiction, search_function):
    """
    Collect stories with comprehensive error handling
    """
    stories = []
    errors = []

    try:
        # Get search results
        search_results = search_function(query)

        for result in search_results:
            try:
                # Validate URL
                is_valid, final_url, error = validate_url(result['url'])
                if not is_valid:
                    errors.append(f"Invalid URL {result['url']}: {error}")
                    continue

                # Fetch content
                content = fetch_article_content(final_url)
                if not content:
                    errors.append(f"Could not fetch content from {final_url}")
                    continue

                # Generate summary
                summary = generate_summary(content)

                # Create story
                story = create_story(result, content, summary)
                stories.append(story)

            except Exception as e:
                errors.append(f"Error processing {result.get('url', 'unknown')}: {e}")
                continue

        # Log errors but don't fail
        if errors:
            log_errors(errors)

        return stories

    except Exception as e:
        log_critical_error(f"Failed to collect stories for {jurisdiction}: {e}")
        return []
```

---

## Testing Strategy

### Test Cases

1. **Source Quality Test**
   - Verify official sources ranked higher than blogs
   - Verify broken URLs are filtered out
   - Verify paywalled content is excluded

2. **Content Quality Test**
   - Verify summaries are comprehensive (not just snippets)
   - Verify "why it matters" is contextual (not templated)
   - Verify key takeaways are relevant

3. **Format Test**
   - Verify all sections present
   - Verify word count in acceptable range (2,000-2,500)
   - Verify read time is 5-10 minutes

4. **Jurisdiction Coverage Test**
   - Verify all Tier 1 jurisdictions have ≥1 story
   - Verify Tier 2 stories ≤3 total
   - Verify total story count 8-10

### Sample Digest Review

Before deploying, manually review a sample digest for:
- ✅ Are all URLs working?
- ✅ Are sources authoritative and credible?
- ✅ Are summaries accurate and comprehensive?
- ✅ Does "why it matters" provide real value?
- ✅ Can this be read in 5-10 minutes?
- ✅ Does it provide good overview of the week's legal developments?
- ✅ Would a tech company legal team find this valuable?

---

## Migration Path

### Week 1: Core Improvements
- Implement URL validation
- Add content fetching
- Increase word limit
- Add LLM summaries

### Week 2: Structure Improvements
- Add executive summary
- Improve insights generation
- Add cross-jurisdictional analysis

### Week 3: Source Quality
- Implement source credibility scoring
- Add tiered source search
- Curate priority source lists

### Week 4: Polish
- Add key takeaways
- Add compliance calendar
- Add resources section
- Final testing and refinement

---

## Success Metrics

After implementing these improvements, the digest should achieve:

1. **Source Quality**: ≥70% of stories from official or Tier 1 news sources
2. **URL Validity**: 100% of URLs working and accessible
3. **Content Depth**: Average summary length 100-150 words (vs. current ~30 words)
4. **Read Time**: 5-10 minutes (vs. current ~2 minutes)
5. **Comprehensiveness**: Reader can understand stories without clicking through
6. **Actionability**: Clear implications and takeaways for each story

---

## Conclusion

The current digest implementation is a solid foundation but needs significant enhancement to meet the "comprehensive legal news digest" requirement. The key improvements are:

1. **Better sources** through tiered search and credibility scoring
2. **Valid URLs** through validation and content verification
3. **Richer content** through article fetching and LLM-powered analysis
4. **Better structure** with executive summary and cross-jurisdictional insights
5. **Appropriate length** (2,000-2,500 words for 5-10 min read)

These changes will transform the digest from a basic link aggregator into a professional-grade legal intelligence briefing that provides real value to global tech companies operating in Asia-Pacific.
