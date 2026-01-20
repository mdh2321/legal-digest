# Digest Search Instructions

When generating a weekly digest, Claude must run comprehensive searches across all jurisdictions and topics to ensure complete coverage.

## Search Matrix

### Jurisdictions (12 + 1 Regional = 13 total)
1. Australia (AU)
2. Singapore (SG)
3. Japan (JP)
4. South Korea (KR)
5. Hong Kong (HK)
6. India (IN)
7. Indonesia (ID)
8. Vietnam (VN)
9. New Zealand (NZ)
10. Malaysia (MY)
11. Philippines (PH)
12. ASEAN (Regional)

### Keywords (7 per jurisdiction)
1. `privacy data protection law`
2. `cybersecurity law regulation`
3. `AI artificial intelligence regulation`
4. `fintech digital assets crypto regulation`
5. `platform regulation online safety`
6. `enforcement penalty fine data privacy`
7. `technology law digital economy`

## Total Searches Required
**13 jurisdictions × 7 keywords = 91 searches**

## Search Query Format
Each search should follow this format:
```
{Jurisdiction} {keyword} {Month} {Year}
```

Example:
```
Australia privacy data protection law January 2026
Singapore cybersecurity law regulation January 2026
Japan AI artificial intelligence regulation January 2026
```

## Execution Instructions

When asked to generate a digest:

1. **Run all 91 searches in parallel batches** (WebSearch tool supports parallel calls)
2. **Collect and deduplicate results** by URL
3. **Filter for the target week** (e.g., January 13-20, 2026)
4. **Select top 7-10 stories** based on:
   - Materiality (new laws, enforcement, deadlines)
   - Geographic diversity (aim for 6+ different jurisdictions)
   - Topic diversity (mix of privacy, AI, cybersecurity, fintech, etc.)
5. **Update digest.html** with selected stories
6. **Update Compliance Countdown** with any new deadlines
7. **Commit and push** changes

## Search Batching

To maximize efficiency, run searches in parallel batches:

**Batch 1: Australia + Singapore + Japan (21 searches)**
**Batch 2: South Korea + Hong Kong + India (21 searches)**
**Batch 3: Indonesia + Vietnam + New Zealand (21 searches)**
**Batch 4: Malaysia + Philippines + ASEAN (21 searches)**

Each batch runs 21 searches in parallel (3 jurisdictions × 7 keywords).

## Notes

- Always include the current month and year in searches
- Prefer government/regulator sources over general news
- Flag AI-related stories with the `ai` tag
- Extract compliance deadlines for the Compliance Countdown section
