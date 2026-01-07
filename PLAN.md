# Implementation Plan: APAC Legal News Digest with RSS Feed

## Executive Summary

Transform the existing APAC Legal News Digest system to generate an **RSS feed** for consumption in Readwise Reader, with enhanced formatting, additional jurisdiction coverage (Korea), and a clean, minimalist aesthetic tailored for a global SaaS company legal team.

---

## Current State Analysis

### What Exists
The codebase already includes a functional digest generation pipeline:
- **News collection** via web search across 8 APAC jurisdictions
- **Content filtering** with inclusion/exclusion rules for tech-relevant topics
- **Story ranking** by materiality (60%) and jurisdiction priority (40%)
- **Story selection** with tier-based requirements (Tier 1: AU, SG, JP; Tier 2: others)
- **Markdown formatting** with jurisdiction sections and regional insights
- **QA validation** for story count, word limits, and formatting

### Gaps to Address
| Requirement | Current State | Action Needed |
|-------------|---------------|---------------|
| RSS Feed output | Markdown only | Add RSS generator module |
| Korea coverage | Not in config | Add KR to Tier 2 jurisdictions |
| Story format (expandable details) | Basic format | Enhance with CDATA HTML content |
| Clean minimalist aesthetic | Functional but basic | Redesign RSS item structure |
| Automation (Monday morning) | Manual execution | Add scheduling mechanism |
| SaaS company relevance framing | Generic tech focus | Refine relevance statements |

---

## Implementation Plan

### Phase 1: Configuration Updates

**File: `src/config.py`**

1. **Add Korea to Tier 2 jurisdictions**
   ```python
   TIER2_JURISDICTIONS = {
       'KR': {'name': 'South Korea', 'flag': '🇰🇷', 'priority': 1},
       # ... existing entries
   }
   ```

2. **Add Korea search template**
   ```python
   SEARCH_TEMPLATES = {
       'KR': 'South Korea {topic} law technology regulation site:korea.kr OR site:kr',
       # ... existing entries
   }
   ```

3. **Refine topic keywords for SaaS relevance**
   - Add: `software licensing`, `subscription services`, `API regulation`, `cross-border data`, `data localization`
   - Ensure `eSignature` and `Contract Law` keywords are comprehensive

4. **Add Tax to INCLUDE_TOPICS**
   ```python
   'Tax': ['digital services tax', 'withholding tax', 'transfer pricing', 'tax treaty', 'permanent establishment'],
   ```

---

### Phase 2: RSS Feed Generator Module

**New File: `src/rss_generator.py`**

Create a new module to generate valid RSS 2.0 feeds compatible with Readwise Reader.

#### RSS Structure Design
```xml
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/">
  <channel>
    <title>APAC Legal Digest — Week of [Date]</title>
    <link>file://path/to/digest</link>
    <description>Weekly legal and regulatory news for global technology companies</description>
    <language>en</language>
    <lastBuildDate>[RFC 822 date]</lastBuildDate>
    <item>
      <title>[Headline]</title>
      <link>[Source URL]</link>
      <pubDate>[RFC 822 date]</pubDate>
      <category>[Country]</category>
      <category>[Practice Area 1]</category>
      <category>[Practice Area 2]</category>
      <description>[Executive Summary - 2-3 sentences]</description>
      <content:encoded><![CDATA[
        <h2>Key Takeaways</h2>
        <ul>
          <li>Takeaway 1</li>
          <li>Takeaway 2</li>
        </ul>
        <h2>Why This Matters for SaaS</h2>
        <p>Relevance statement...</p>
        <p><strong>Source:</strong> <a href="[URL]">[Source Name]</a></p>
      ]]></content:encoded>
    </item>
    <!-- More items... -->
  </channel>
</rss>
```

#### Module Implementation
```python
class RSSGenerator:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

    def generate_feed(self, selected_stories: Dict, insights: str) -> str:
        """Generate complete RSS 2.0 feed XML."""

    def format_item(self, story: NewsStory) -> str:
        """Format single story as RSS item with CDATA content."""

    def generate_takeaways(self, story: NewsStory) -> List[str]:
        """Generate key takeaways from story content."""

    def generate_saas_relevance(self, story: NewsStory) -> str:
        """Generate SaaS-specific relevance statement."""

    def to_rfc822_date(self, dt: datetime) -> str:
        """Convert datetime to RFC 822 format for RSS."""
```

---

### Phase 3: Enhanced Story Formatting

**File: `src/formatter.py`**

1. **Add `generate_takeaways()` method**
   - Extract key points from story summary
   - Generate 2-3 actionable takeaways
   - Focus on compliance implications

2. **Add `generate_saas_relevance()` method**
   - Map categories to SaaS-specific impacts:
     - `Data Privacy` → "Affects customer data handling, DPA requirements, and cross-border transfers"
     - `eSignature` → "Impacts validity of electronically signed agreements and authentication requirements"
     - `AI/ML` → "Influences AI feature development, disclosure requirements, and liability frameworks"
     - `Contract Law` → "Affects standard terms, limitation of liability clauses, and auto-renewal provisions"
     - etc.

3. **Create `StoryEnricher` class**
   - Enhance stories with structured takeaways
   - Generate expandable content for RSS

---

### Phase 4: Output Pipeline Updates

**File: `generate_digest.py`**

1. **Add RSS output option**
   ```python
   def run(self, output_dir: str = 'output', format: str = 'rss', verbose: bool = True):
       # ... existing pipeline ...

       if format == 'rss':
           rss_gen = RSSGenerator(self.start_date, self.end_date)
           output = rss_gen.generate_feed(selected_stories, insights)
           filename = f"digest_{self.end_date.strftime('%Y-%m-%d')}.xml"
       else:
           # existing markdown logic
   ```

2. **Update output file handling**
   - RSS files saved as `.xml`
   - Maintain both formats if needed

---

### Phase 5: Scheduling & Automation

**New File: `scheduler.py`**

Option A: **Cron-based scheduling** (recommended for simplicity)
```bash
# Run every Monday at 7:00 AM local time
0 7 * * 1 cd /path/to/legal-digest && python run_digest.py --format rss
```

Option B: **Python scheduler** (for self-contained solution)
```python
import schedule
import time

def run_weekly_digest():
    generator = DigestGenerator(search_function=web_search)
    generator.run(format='rss')

schedule.every().monday.at("07:00").do(run_weekly_digest)

while True:
    schedule.run_pending()
    time.sleep(60)
```

**Automation considerations:**
- Requires persistent search function (Claude Code integration or API-based)
- Output file hosting for RSS reader access
- Error handling and notification for failures

---

### Phase 6: Clean Minimalist RSS Styling

For Readwise Reader consumption, the RSS content should be:

1. **Structured with semantic HTML**
   - `<h2>` for section headers (Key Takeaways, Why This Matters)
   - `<ul><li>` for takeaway lists
   - `<p>` for prose content
   - `<strong>` for emphasis sparingly

2. **Visual hierarchy through content structure**
   ```html
   <h2>Key Takeaways</h2>
   <ul>
     <li>First actionable insight</li>
     <li>Second actionable insight</li>
   </ul>

   <h2>Why This Matters for SaaS Companies</h2>
   <p>Relevance statement with specific implications...</p>

   <p><em>Country: Australia | Topics: Data Privacy, AI/ML</em></p>
   <p><a href="[url]">Read full article →</a></p>
   ```

3. **Consistent tagging**
   - Country as first `<category>`
   - Practice areas as subsequent `<category>` elements
   - Enables filtering in Readwise

---

## File Changes Summary

| File | Action | Description |
|------|--------|-------------|
| `src/config.py` | Modify | Add Korea, refine topics, add Tax category |
| `src/rss_generator.py` | Create | New RSS 2.0 feed generator |
| `src/story_enricher.py` | Create | Takeaway and relevance generation |
| `src/formatter.py` | Modify | Add RSS formatting methods |
| `generate_digest.py` | Modify | Add RSS output option |
| `run_digest.py` | Modify | Add CLI format flag |
| `scheduler.py` | Create | Optional automation script |
| `requirements.txt` | Modify | Add `schedule` if using Python scheduler |

---

## Testing Plan

1. **Unit tests for RSS generator**
   - Valid XML output
   - Correct RFC 822 date formatting
   - Proper CDATA escaping

2. **Integration test**
   - Generate sample RSS feed
   - Validate in RSS validator (https://validator.w3.org/feed/)
   - Import into Readwise Reader and verify rendering

3. **End-to-end test**
   - Run full pipeline with mock search results
   - Verify story count and jurisdiction distribution
   - Check takeaway quality

---

## Implementation Order

1. **Phase 1: Configuration** — Update `config.py` with Korea and refined topics
2. **Phase 2: RSS Generator** — Create core RSS generation module
3. **Phase 3: Story Enricher** — Add takeaway and relevance generation
4. **Phase 4: Pipeline Integration** — Wire RSS output into main generator
5. **Phase 5: Testing** — Validate RSS feed compatibility
6. **Phase 6: Automation** — Set up scheduling (optional, based on hosting)

---

## Open Questions for User

1. **RSS Hosting**: Where will the RSS feed file be hosted for Readwise Reader to access?
   - Local file sync (Dropbox, iCloud)?
   - Self-hosted web server?
   - GitHub Pages or similar?

2. **Search API**: For full automation, how should web search be performed?
   - Continue using Claude Code integration (manual trigger)?
   - Integrate with a search API (SerpAPI, Google Custom Search)?

3. **Notification**: Should the system notify you when a new digest is generated?
   - Email notification?
   - Slack/Teams message?
   - Just rely on Readwise Reader showing new items?

---

## Estimated Deliverables

After implementation, you will have:
- A fully functional RSS feed generator producing valid RSS 2.0
- Coverage of 9 APAC jurisdictions (AU, SG, JP, KR, NZ, PH, HK, VN, IN)
- Each story with: headline, executive summary, key takeaways, SaaS relevance, source link, country/topic tags
- Clean, minimalist formatting optimized for Readwise Reader
- Optional automation for Monday morning generation
