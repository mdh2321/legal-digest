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

# =============================================================================
# SOURCE CONFIGURATION
# =============================================================================

# Major international law firms with APAC technology/privacy practices
LAW_FIRM_SOURCES = [
    # Global firms with strong APAC presence
    'bakermckenzie.com',
    'herbertsmithfreehills.com',
    'allens.com.au',
    'kwm.com',              # King & Wood Mallesons
    'cliffordchance.com',
    'linklaters.com',
    'freshfields.com',
    'whitecase.com',
    'dentons.com',
    'dlapiper.com',
    'nortonrosefulbright.com',
    'ashurst.com',
    'simmons-simmons.com',
    'hoganlovells.com',
    'minterellison.com',
    'corrs.com.au',
    'gtlaw.com.au',         # Gilbert + Tobin
    'claytonutz.com',
    # Asia-focused firms
    'wongpartnership.com',  # Singapore
    'rajahtan.com',         # Rajah & Tann (Singapore/SEA)
    'drewnapier.com',       # Singapore
    'nishimura.com',        # Japan
    'amt-law.com',          # Japan (Anderson Mori & Tomotsune)
    'nagashima.jp',         # Japan (Nagashima Ohno & Tsunematsu)
    'mhmjapan.com',         # Japan (Mori Hamada & Matsumoto)
    'trilegal.com',         # India
    'azbpartners.com',      # India
    'nishithdesai.com',     # India
    'kimchang.com',         # Korea
    'leeko.com',            # Korea
    'yoonyang.com',         # Korea
    'ssek.com',             # Indonesia
    'abnrlaw.com',          # Indonesia (Ali Budiardjo)
    'makabata.com',         # Indonesia
    'syciplaw.com',         # Philippines (SyCip Salazar)
    'accralaw.com',         # Philippines
    'zicolaw.com',          # Vietnam/SEA
    'vci-legal.com',        # Vietnam
    'russellmcveagh.com',   # New Zealand
    'bellgully.com',        # New Zealand
    'chapmantripp.com',     # New Zealand
    'mayerbrown.com',
    'twobirds.com',         # Bird & Bird
    'fieldfisher.com',
    'osborneclarke.com',
]

# Regulator and government sites by jurisdiction
REGULATOR_SOURCES = {
    'AU': [
        'oaic.gov.au',          # Privacy Commissioner
        'accc.gov.au',          # Competition & Consumer
        'asic.gov.au',          # Securities
        'apra.gov.au',          # Prudential Regulation
        'homeaffairs.gov.au',   # Cyber security
        'ag.gov.au',            # Attorney-General
        'industry.gov.au',      # Industry/AI policy
    ],
    'SG': [
        'pdpc.gov.sg',          # Personal Data Protection Commission
        'mas.gov.sg',           # Monetary Authority
        'imda.gov.sg',          # Infocomm Media Development
        'csa.gov.sg',           # Cyber Security Agency
        'mlaw.gov.sg',          # Ministry of Law
        'aiverify.sg',          # AI Verify Foundation
    ],
    'JP': [
        'ppc.go.jp',            # Personal Information Protection Commission
        'meti.go.jp',           # Ministry of Economy, Trade and Industry
        'soumu.go.jp',          # Ministry of Internal Affairs
        'fsa.go.jp',            # Financial Services Agency
        'nisc.go.jp',           # Cybersecurity Center
        'cao.go.jp',            # Cabinet Office
    ],
    'IN': [
        'meity.gov.in',         # Ministry of Electronics and IT
        'rbi.org.in',           # Reserve Bank of India
        'sebi.gov.in',          # Securities and Exchange Board
        'cci.gov.in',           # Competition Commission
        'cert-in.org.in',       # CERT-India
    ],
    'KR': [
        'pipc.go.kr',           # Personal Information Protection Commission
        'kcc.go.kr',            # Korea Communications Commission
        'fsc.go.kr',            # Financial Services Commission
        'ftc.go.kr',            # Fair Trade Commission
        'kisa.or.kr',           # Korea Internet & Security Agency
    ],
    'HK': [
        'pcpd.org.hk',          # Privacy Commissioner
        'hkma.gov.hk',          # Monetary Authority
        'sfc.hk',               # Securities and Futures Commission
        'ogcio.gov.hk',         # Office of Government CIO
    ],
    'NZ': [
        'privacy.org.nz',       # Privacy Commissioner
        'comcom.govt.nz',       # Commerce Commission
        'dia.govt.nz',          # Department of Internal Affairs
        'ncsc.govt.nz',         # National Cyber Security Centre
    ],
    'ID': [
        'kominfo.go.id',        # Ministry of Communications
        'ojk.go.id',            # Financial Services Authority
        'kppu.go.id',           # Competition Commission
        'bi.go.id',             # Bank Indonesia
    ],
    'PH': [
        'privacy.gov.ph',       # National Privacy Commission
        'bsp.gov.ph',           # Central Bank
        'dict.gov.ph',          # Dept of ICT
        'sec.gov.ph',           # Securities and Exchange Commission
    ],
    'VN': [
        'mic.gov.vn',           # Ministry of Information and Communications
        'sbv.gov.vn',           # State Bank of Vietnam
        'moj.gov.vn',           # Ministry of Justice
    ],
}

# Legal news publications and aggregators
LEGAL_PUBLICATIONS = [
    # Major legal news aggregators
    'lexology.com',
    'law360.com',
    'mondaq.com',
    'iclg.com',                 # International Comparative Legal Guides
    'globallegalpost.com',
    'legalbusinessonline.com',  # Asia focused
    'law.asia',                 # Asia Law Portal
    # Technology/privacy focused
    'iapp.org',                 # International Association of Privacy Professionals
    'dataprotectionreport.com',
    'privacylaws.com',
    'technologylawdispatch.com',
    'techlawinsight.com',
    # Regional publications
    'lawyersweekly.com.au',     # Australia
    'afr.com',                  # Australian Financial Review (legal)
    'lawsociety.com.au',
    'straitstimes.com',         # Singapore
    'businesstimes.com.sg',
    'japantimes.co.jp',
    'nikkei.com',               # Japan
    'livemint.com',             # India
    'barandbench.com',          # India legal
    'livelaw.in',               # India legal
    'koreaherald.com',          # Korea
    'koreatimes.co.kr',
    'scmp.com',                 # South China Morning Post (HK)
    'nzherald.co.nz',           # New Zealand
    'jakartapost.com',          # Indonesia
    'philstar.com',             # Philippines
    'businessmirror.com.ph',
    'vnexpress.net',            # Vietnam
    'vietnamnews.vn',
]

# All sources flattened for easy searching
ALL_REGULATOR_SITES = []
for sites in REGULATOR_SOURCES.values():
    ALL_REGULATOR_SITES.extend(sites)

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
