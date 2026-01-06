# RSS Feed Export

The legal digest system can export digests to RSS 2.0 format for easy distribution and subscription.

## Quick Start

Generate an RSS feed from your digests:

```bash
python export_rss.py
```

This creates `output/feed.xml` with the 20 most recent digests.

## Features

- **RSS 2.0 compliant** - Works with all RSS readers
- **Full content or summary** - Choose between complete digests or summaries
- **Automatic updates** - Run after each digest generation to update the feed
- **Validation** - Built-in feed validation
- **Configurable** - Customize feed metadata and behavior

## Usage

### Basic Usage

```bash
# Generate feed with default settings
python export_rss.py

# Generate with validation
python export_rss.py --validate

# Summary-only feed (smaller file size)
python export_rss.py --summary-only
```

### Advanced Options

```bash
# Custom output location
python export_rss.py --output /path/to/feed.xml

# Limit number of items
python export_rss.py --max-items 10

# Custom feed URL
python export_rss.py --feed-url https://yourdomain.com/legal-digest

# Custom feed title and description
python export_rss.py \
  --feed-title "My Legal Digest" \
  --feed-description "Custom description"

# Specify digest directory
python export_rss.py --digest-dir /path/to/digests
```

### All Options

| Option | Description | Default |
|--------|-------------|---------|
| `--output` | Output RSS file path | `output/feed.xml` |
| `--max-items` | Maximum items in feed | `20` |
| `--summary-only` | Include only summary | Full content |
| `--feed-url` | Base URL for feed | `https://example.com/digests` |
| `--feed-title` | Feed title | `Weekly APJ Legal Digest` |
| `--feed-description` | Feed description | Default description |
| `--digest-dir` | Source directory | `output` |
| `--validate` | Validate generated feed | Off |

## Output Modes

### Full Content Mode (Default)

Includes the complete digest in HTML format:
- All stories with full text
- Formatted with proper HTML tags
- Larger file size (~8 KB per digest)
- Readers show entire digest

```bash
python export_rss.py
```

### Summary Mode

Includes only a brief summary:
- Story count and jurisdictions covered
- Much smaller file size (~1 KB per digest)
- Readers show summary with link to full digest

```bash
python export_rss.py --summary-only
```

## Feed Structure

The generated RSS feed includes:

```xml
<rss version="2.0">
  <channel>
    <title>Weekly APJ Legal Digest</title>
    <link>https://example.com/digests</link>
    <description>Feed description</description>

    <item>
      <title>Weekly APJ Legal Digest — 04 January 2026</title>
      <link>https://example.com/digests/2026-01-04</link>
      <description><![CDATA[...content...]]></description>
      <pubDate>Mon, 06 Jan 2026 00:00:00 GMT</pubDate>
      <guid>digest-2026-01-04</guid>
    </item>
    <!-- More items... -->
  </channel>
</rss>
```

## Hosting the Feed

### 1. GitHub Pages (Free)

```bash
# Generate feed
python export_rss.py --feed-url https://username.github.io/repo-name

# Commit and push
git add output/feed.xml
git commit -m "Update RSS feed"
git push

# Feed URL: https://username.github.io/repo-name/output/feed.xml
```

### 2. Static Hosting (Netlify, Vercel, etc.)

1. Generate feed: `python export_rss.py --feed-url https://yourdomain.com`
2. Deploy `output/` directory
3. Feed URL: `https://yourdomain.com/feed.xml`

### 3. S3/CloudFront

```bash
# Generate feed
python export_rss.py --feed-url https://yourdomain.com

# Upload to S3
aws s3 cp output/feed.xml s3://your-bucket/feed.xml --content-type "application/rss+xml"
```

### 4. Your Own Server

```bash
# Generate feed
python export_rss.py --feed-url https://yourdomain.com

# Upload via SCP
scp output/feed.xml user@server:/var/www/html/feed.xml
```

## Automation

### Update Feed After Each Digest

Add to your workflow:

```bash
# Generate digest
python generate_with_results.py

# Update RSS feed
python export_rss.py --validate

# Upload to hosting
# (your upload command here)
```

### Scheduled Updates

Cron job to regenerate feed weekly:

```bash
# crontab -e
0 9 * * MON cd /path/to/legal-digest && python export_rss.py && ./upload.sh
```

### GitHub Actions

```yaml
name: Update RSS Feed

on:
  push:
    paths:
      - 'output/digest_*.md'

jobs:
  update-feed:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Generate RSS feed
        run: python export_rss.py --validate
      - name: Commit feed
        run: |
          git config user.name "Bot"
          git config user.email "bot@example.com"
          git add output/feed.xml
          git commit -m "Update RSS feed"
          git push
```

## Subscribing to the Feed

Users can subscribe using any RSS reader:

### Popular RSS Readers

- **Feedly** - https://feedly.com
- **Inoreader** - https://www.inoreader.com
- **NewsBlur** - https://newsblur.com
- **The Old Reader** - https://theoldreader.com
- **Feedbin** - https://feedbin.com

### Browser Extensions

- Firefox: Built-in RSS support
- Chrome: "RSS Feed Reader" extension
- Safari: Built-in RSS support

### How to Subscribe

1. Copy your feed URL: `https://yourdomain.com/feed.xml`
2. Open RSS reader
3. Click "Add Feed" or "Subscribe"
4. Paste feed URL
5. Done! New digests appear automatically

## Validation

Validate your feed online:

- **W3C Feed Validator**: https://validator.w3.org/feed/
- **FeedValidator**: http://www.feedvalidator.org/

Or use the built-in validator:

```bash
python export_rss.py --validate
```

## Configuration

Edit `src/config.py` to set defaults:

```python
# RSS Feed configuration
RSS_FEED_TITLE = "Your Feed Title"
RSS_FEED_LINK = "https://yourdomain.com/digests"
RSS_FEED_DESCRIPTION = "Your feed description"
RSS_MAX_ITEMS = 20
RSS_INCLUDE_FULL_CONTENT = True  # False for summary only
```

## Programmatic Usage

Use the RSS exporter in your own scripts:

```python
from src.rss_exporter import RSSExporter

# Create exporter
exporter = RSSExporter(
    feed_title="My Legal Digest",
    feed_link="https://example.com/digests",
    feed_description="Custom description",
    base_url="https://example.com/digests"
)

# Generate feed
feed_path = exporter.generate_feed(
    digest_dir='output',
    output_file='feed.xml',
    max_items=20,
    include_full_content=True
)

# Validate
is_valid = exporter.validate_feed(feed_path)
```

## Troubleshooting

### Feed Not Validating

```bash
# Check validation errors
python export_rss.py --validate

# Common issues:
# - Invalid XML characters in digest
# - Missing required fields
# - Malformed URLs
```

### RSS Reader Not Updating

- **Cache**: RSS readers cache feeds (update interval varies)
- **Solution**: Most readers have a "refresh now" button
- **Typical update**: 15 minutes to 1 hour

### Feed Too Large

```bash
# Use summary mode
python export_rss.py --summary-only

# Or reduce items
python export_rss.py --max-items 10
```

### Encoding Issues

The exporter uses UTF-8. If you see encoding issues:
- Check digest markdown files are UTF-8
- Validate feed with `--validate` flag
- Use summary mode if full content has issues

## Best Practices

1. **Update regularly** - Run after each digest generation
2. **Validate feeds** - Use `--validate` flag
3. **Keep history** - Include 10-20 recent digests
4. **Test subscription** - Subscribe with a reader to verify
5. **Set proper URLs** - Use your actual domain in `--feed-url`
6. **Monitor size** - Large feeds (>500 KB) may not work in all readers

## Examples

### Weekly Workflow

```bash
# Monday: Generate this week's digest
python generate_with_results.py

# Update RSS feed
python export_rss.py --validate --feed-url https://legal-digest.example.com

# Upload to hosting
scp output/feed.xml server:/var/www/html/

# Share with subscribers
echo "New digest available: https://legal-digest.example.com/feed.xml"
```

### Multiple Feeds

Create different feeds for different audiences:

```bash
# Full feed for power users
python export_rss.py \
  --output output/feed-full.xml \
  --max-items 30

# Summary feed for mobile users
python export_rss.py \
  --summary-only \
  --output output/feed-summary.xml \
  --max-items 10

# Recent only (last 5 digests)
python export_rss.py \
  --output output/feed-recent.xml \
  --max-items 5
```

## Support

For issues or questions:
1. Check this documentation
2. Validate your feed: `python export_rss.py --validate`
3. Test with online validator: https://validator.w3.org/feed/
4. Review `src/rss_exporter.py` source code
