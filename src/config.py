"""Configuration constants for the legal digest generator."""

# Jurisdiction configuration
TIER1_JURISDICTIONS = {
    'AU': {'name': 'Australia', 'flag': '🇦🇺', 'min_stories': 1, 'priority': 4},
    'SG': {'name': 'Singapore', 'flag': '🇸🇬', 'min_stories': 1, 'priority': 3},
    'JP': {'name': 'Japan', 'flag': '🇯🇵', 'min_stories': 1, 'priority': 2}
}

TIER2_JURISDICTIONS = {
    'IN': {'name': 'India', 'flag': '🇮🇳', 'priority': 1},
    'PH': {'name': 'Philippines', 'flag': '🇵🇭', 'priority': 1},
    'ID': {'name': 'Indonesia', 'flag': '🇮🇩', 'priority': 1},
    'HK': {'name': 'Hong Kong', 'flag': '🇭🇰', 'priority': 1},
    'KR': {'name': 'South Korea', 'flag': '🇰🇷', 'priority': 1},
    'NZ': {'name': 'New Zealand', 'flag': '🇳🇿', 'priority': 1},
    'VN': {'name': 'Vietnam', 'flag': '🇻🇳', 'priority': 1}
}

ALL_JURISDICTIONS = {**TIER1_JURISDICTIONS, **TIER2_JURISDICTIONS}

# Story selection limits
TARGET_STORY_COUNT = (8, 10)  # (min, max)
TIER2_MAX_STORIES = 3

# Word limits
MAX_TOTAL_WORDS = 1000
MAX_INSIGHTS_WORDS = 120
MAX_HEADLINE_WORDS = 12

# Content exclusion keywords
EXCLUDE_TOPICS = [
    'criminal law', 'criminal', 'murder', 'assault', 'theft',
    'wills', 'estates', 'probate', 'inheritance', 'testament',
    'family law', 'divorce', 'custody', 'marriage', 'domestic',
    'personal injury', 'tort claim'
]

# Content inclusion topics (focus areas)
INCLUDE_TOPICS = {
    'AI/ML': ['artificial intelligence', 'machine learning', 'AI', 'ML', 'neural network', 'deep learning',
              'generative AI', 'AI governance', 'AI regulation', 'algorithmic'],
    'Data Privacy': ['data privacy', 'data protection', 'GDPR', 'personal data', 'privacy law', 'PDPA', 'PDPC',
                     'cross-border data', 'data localization', 'data residency', 'data transfer'],
    'Cybersecurity': ['cybersecurity', 'cyber security', 'data breach', 'ransomware', 'hacking',
                      'information security', 'security incident', 'cyber resilience'],
    'Cloud': ['cloud computing', 'cloud service', 'SaaS', 'PaaS', 'IaaS', 'cloud provider',
              'software licensing', 'subscription services', 'API regulation', 'software as a service'],
    'eSignature': ['electronic signature', 'e-signature', 'digital signature', 'digital identity',
                   'electronic contract', 'electronic transaction', 'electronic record', 'remote notarization'],
    'Contract Law': ['contract law', 'commercial contract', 'contractual', 'agreement', 'standard terms',
                     'limitation of liability', 'indemnification', 'auto-renewal', 'terms of service'],
    'Competition': ['competition law', 'antitrust', 'anti-trust', 'monopoly', 'market dominance', 'cartel',
                    'digital markets', 'platform regulation', 'gatekeeper'],
    'Consumer Protection': ['consumer protection', 'consumer rights', 'consumer law', 'unfair practice',
                            'unfair contract terms', 'consumer guarantee', 'digital consumer'],
    'Corporate Governance': ['corporate governance', 'director duties', 'shareholders', 'board', 'ESG'],
    'Fintech': ['fintech', 'financial technology', 'digital payment', 'cryptocurrency', 'blockchain', 'digital wallet'],
    'AML': ['anti-money laundering', 'AML', 'money laundering', 'financial crime'],
    'Anti-Bribery': ['anti-bribery', 'anti-corruption', 'bribery', 'corruption', 'FCPA'],
    'Outsourcing': ['outsourcing', 'vendor management', 'third party', 'service provider',
                    'subcontracting', 'offshore', 'BPO'],
    'Tax': ['digital services tax', 'withholding tax', 'transfer pricing', 'tax treaty',
            'permanent establishment', 'VAT digital', 'GST digital', 'tax compliance']
}

# Source priority tiers
SOURCE_PRIORITY = {
    'government': 3,
    'regulator': 3,
    'court': 3,
    'newspaper': 2,
    'legal_publication': 2,
    'law_firm': 1
}

# Search query templates
SEARCH_TEMPLATES = {
    'AU': 'Australia {topic} law technology regulation site:gov.au OR site:com.au',
    'SG': 'Singapore {topic} law technology regulation site:gov.sg OR site:sg',
    'JP': 'Japan {topic} law technology regulation site:go.jp OR site:jp',
    'IN': 'India {topic} law technology regulation site:gov.in OR site:in',
    'PH': 'Philippines {topic} law technology regulation site:gov.ph OR site:ph',
    'ID': 'Indonesia {topic} law technology regulation site:go.id OR site:id',
    'HK': 'Hong Kong {topic} law technology regulation site:gov.hk OR site:hk',
    'KR': 'South Korea {topic} law technology regulation site:korea.kr OR site:kr',
    'NZ': 'New Zealand {topic} law technology regulation site:govt.nz OR site:nz',
    'VN': 'Vietnam {topic} law technology regulation site:gov.vn OR site:vn'
}

# Ranking weights
MATERIALITY_WEIGHT = 0.6
JURISDICTION_WEIGHT = 0.4
