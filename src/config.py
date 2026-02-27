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
    'VN': {'name': 'Vietnam', 'flag': '🇻🇳', 'priority': 1},
    'MY': {'name': 'Malaysia', 'flag': '🇲🇾', 'priority': 1},
    'TW': {'name': 'Taiwan', 'flag': '🇹🇼', 'priority': 1},
    'TH': {'name': 'Thailand', 'flag': '🇹🇭', 'priority': 1},
}

# Regional grouping for ASEAN-wide searches
REGIONAL_JURISDICTIONS = {
    'ASEAN': {'name': 'ASEAN', 'flag': '🌏', 'priority': 1}
}

EXTRATERRITORIAL_JURISDICTIONS = {
    'EXTRA': {'name': 'Global/Extraterritorial', 'flag': '🌐', 'priority': 2}
}

ALL_JURISDICTIONS = {**TIER1_JURISDICTIONS, **TIER2_JURISDICTIONS, **EXTRATERRITORIAL_JURISDICTIONS}

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
        'transparency.org.au',  # Transparency International Australia
    ],
    'SG': [
        'pdpc.gov.sg',          # Personal Data Protection Commission
        'mas.gov.sg',           # Monetary Authority
        'imda.gov.sg',          # Infocomm Media Development
        'csa.gov.sg',           # Cyber Security Agency
        'mlaw.gov.sg',          # Ministry of Law
        'aiverify.sg',          # AI Verify Foundation
        'cpib.gov.sg',          # Corrupt Practices Investigation Bureau
    ],
    'JP': [
        'ppc.go.jp',            # Personal Information Protection Commission
        'meti.go.jp',           # Ministry of Economy, Trade and Industry
        'soumu.go.jp',          # Ministry of Internal Affairs
        'fsa.go.jp',            # Financial Services Agency
        'nisc.go.jp',           # Cybersecurity Center
        'cao.go.jp',            # Cabinet Office
        'npsc.go.jp',           # National Public Safety Commission
    ],
    'IN': [
        'meity.gov.in',         # Ministry of Electronics and IT
        'rbi.org.in',           # Reserve Bank of India
        'sebi.gov.in',          # Securities and Exchange Board
        'cci.gov.in',           # Competition Commission
        'cert-in.org.in',       # CERT-India
        'cvc.gov.in',           # Central Vigilance Commission
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
    'MY': [
        'pdp.gov.my',           # Personal Data Protection Department
        'mcmc.gov.my',          # Malaysian Communications and Multimedia Commission
        'bnm.gov.my',           # Bank Negara Malaysia
        'nacsa.gov.my',         # National Cyber Security Agency
        'mdec.my',              # Malaysia Digital Economy Corporation
        'kkmm.gov.my',          # Ministry of Communications and Multimedia
        'sc.com.my',            # Securities Commission Malaysia
    ],
    'TW': [
        'ndc.gov.tw',           # National Development Council
        'moj.gov.tw',           # Ministry of Justice
        'ncc.gov.tw',           # National Communications Commission
        'fsc.gov.tw',           # Financial Supervisory Commission
    ],
    'TH': [
        'pdpc.or.th',           # PDPA Commission
        'etda.or.th',           # Electronic Transactions Development Agency
        'bot.or.th',            # Bank of Thailand
        'nbtc.go.th',           # National Broadcasting and Telecommunications Commission
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
    'jdsupra.com',              # Legal intelligence
    'lawcom.gov.uk',            # Law Commission resources
    # Technology/privacy focused
    'iapp.org',                 # International Association of Privacy Professionals
    'dataprotectionreport.com',
    'privacylaws.com',
    'technologylawdispatch.com',
    'techlawinsight.com',
    'fpf.org',                  # Future of Privacy Forum
    'cdt.org',                  # Center for Democracy & Technology
    'eff.org',                  # Electronic Frontier Foundation
    # Wire services / Business news
    'reuters.com',
    'bloomberg.com',
    'ft.com',                   # Financial Times
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
    # Anti-corruption, compliance, and regional coverage
    'regulationasia.com',       # Asia regulatory news
    'conventuslaw.com',         # Asia legal news
    'asialaw.com',              # Asia law portal
    'globalcompliancenews.com', # Global compliance
    'fcpablog.com',             # Anti-corruption (FCPA Blog)
    'corruptionwatch.org',      # Anti-corruption
]

# Court and tribunal databases by jurisdiction
COURT_SOURCES = {
    'AU': [
        'federalcourt.gov.au',      # Federal Court of Australia
        'hcourt.gov.au',            # High Court of Australia
        'austlii.edu.au',           # Legal Information Institute
        'aat.gov.au',               # Administrative Appeals Tribunal
        'judgments.fedcourt.gov.au',
    ],
    'SG': [
        'judiciary.gov.sg',         # Singapore Judiciary
        'supremecourt.gov.sg',
        'statecourts.gov.sg',
        'sicc.gov.sg',              # Singapore International Commercial Court
    ],
    'JP': [
        'courts.go.jp',             # Courts of Japan
    ],
    'IN': [
        'sci.gov.in',               # Supreme Court of India
        'indiankanoon.org',         # Indian case law database
        'delhihighcourt.nic.in',
    ],
    'KR': [
        'scourt.go.kr',             # Supreme Court of Korea
    ],
    'HK': [
        'judiciary.hk',             # Hong Kong Judiciary
        'legalref.judiciary.hk',
    ],
    'NZ': [
        'courtsofnz.govt.nz',       # Courts of New Zealand
        'nzlii.org',                # NZ Legal Information Institute
    ],
    'ID': [
        'mahkamahagung.go.id',      # Supreme Court of Indonesia
    ],
    'PH': [
        'sc.judiciary.gov.ph',      # Supreme Court of Philippines
    ],
    'VN': [
        'toaan.gov.vn',             # Supreme People's Court
    ],
    'MY': [
        'kehakiman.gov.my',         # Malaysian Judiciary
        'federalcourt.gov.my',      # Federal Court of Malaysia
    ],
    'TW': [
        'judicial.gov.tw',          # Judicial Yuan
    ],
    'TH': [
        'coj.go.th',                # Courts of Justice
    ],
}

# Industry associations and tech bodies
INDUSTRY_ASSOCIATIONS = [
    # Australia
    'aiia.com.au',              # Australian Information Industry Association
    'acs.org.au',               # Australian Computer Society
    'digi.org.au',              # Digital Industry Group
    'tech.gov.au',              # Digital Transformation Agency
    # Singapore
    'sgtech.org.sg',            # SGTech
    'aisingapore.org',          # AI Singapore
    'imda.gov.sg',              # IMDA (also regulatory)
    # Japan
    'jisa.or.jp',               # Japan Information Service Industry Association
    'jipdec.or.jp',             # Japan Institute for Promotion of Digital Economy
    'jnsa.org',                 # Japan Network Security Association
    # India
    'nasscom.in',               # National Association of Software Companies
    'dsci.in',                  # Data Security Council of India
    # Korea
    'kosa.or.kr',               # Korea Software Industry Association
    'kait.or.kr',               # Korea Association for IT Industry
    # Hong Kong
    'hkitf.org.hk',             # HK Information Technology Federation
    'hkcs.org.hk',              # HK Computer Society
    # Regional / International
    'apec.org',                 # APEC
    'asean.org',                # ASEAN
    'bsa.org',                  # BSA | The Software Alliance
    'itechlaw.org',             # International Technology Law Association
    'techuk.org',               # techUK
    'digiteurope.org',          # Digital Europe
    'accesspartnership.com',    # Access Partnership (policy advisory)
]

# Think tanks and policy research organizations
THINK_TANKS = [
    # Privacy/Tech focused
    'fpf.org',                  # Future of Privacy Forum
    'cdt.org',                  # Center for Democracy & Technology
    'eff.org',                  # Electronic Frontier Foundation
    'accessnow.org',            # Access Now
    'privacyinternational.org', # Privacy International
    # General policy think tanks
    'brookings.edu',            # Brookings Institution
    'cfr.org',                  # Council on Foreign Relations
    'carnegieendowment.org',    # Carnegie Endowment
    'rand.org',                 # RAND Corporation
    'adb.org',                  # Asian Development Bank
    'worldbank.org',            # World Bank
    'oecd.org',                 # OECD
    # Regional think tanks
    'lowyinstitute.org',        # Lowy Institute (Australia)
    'aspi.org.au',              # Australian Strategic Policy Institute
    'iseas.edu.sg',             # ISEAS-Yusof Ishak Institute (Singapore)
    'rsis.edu.sg',              # S. Rajaratnam School (Singapore)
    'jri.co.jp',                # Japan Research Institute
    'rieti.go.jp',              # Research Institute of Economy, Trade and Industry
    'nippon.com',               # Nippon Communications Foundation
    'orfonline.org',            # Observer Research Foundation (India)
    'kdi.re.kr',                # Korea Development Institute
    # AI/Tech specific research
    'ainowinstitute.org',       # AI Now Institute
    'partnershiponai.org',      # Partnership on AI
    'cset.georgetown.edu',      # Center for Security and Emerging Technology
    'hai.stanford.edu',         # Stanford HAI
    'oxfordmartin.ox.ac.uk',    # Oxford Martin School
]

# Domain blocklist - sources that should never appear
DOMAIN_BLOCKLIST = [
    'wikipedia.org', 'reddit.com', 'quora.com', 'medium.com', 'youtube.com',
    'twitter.com', 'x.com', 'facebook.com', 'tiktok.com', 'pinterest.com',
    'linkedin.com', 'deepstrike.io', 'insurancebusinessmag.com',
]

# All sources flattened for easy searching
ALL_REGULATOR_SITES = []
for sites in REGULATOR_SOURCES.values():
    ALL_REGULATOR_SITES.extend(sites)

ALL_COURT_SITES = []
for sites in COURT_SOURCES.values():
    ALL_COURT_SITES.extend(sites)

# Build comprehensive set of all approved domains
ALL_APPROVED_DOMAINS = set(
    ALL_REGULATOR_SITES
    + ALL_COURT_SITES
    + LAW_FIRM_SOURCES
    + LEGAL_PUBLICATIONS
    + INDUSTRY_ASSOCIATIONS
    + THINK_TANKS
)

# Story selection limits — dynamic volume
MIN_STORIES = 6
DEFAULT_MAX_STORIES = 12
BUSY_WEEK_MAX_STORIES = 18
TIER1_MAX_PER_JURISDICTION = 4
TIER2_MAX_STORIES = 5
EXTRA_MAX_STORIES = 2
MATERIALITY_EXPANSION_THRESHOLD = 0.5  # stories scoring above this qualify for expansion

# Word limits
MAX_TOTAL_WORDS = 2500
MAX_INSIGHTS_WORDS = 200
MAX_HEADLINE_WORDS = 12

# Content exclusion keywords
EXCLUDE_TOPICS = [
    'criminal law', 'murder', 'assault', 'theft',
    'wills and estates', 'probate', 'inheritance', 'testament',
    'family law', 'divorce', 'custody',
    'personal injury', 'tort claim',
    # Exclude incident reports (not about law/regulation)
    'ransomware attack', 'hacking incident', 'phishing attack',
    'malware attack', 'DDoS attack', 'cyber attack on',
    'hackers stole', 'hackers breached',
]

# Content inclusion topics (focus areas)
INCLUDE_TOPICS = {
    # --- CORE TECHNOLOGY LAW ---
    'AI/ML': ['artificial intelligence', 'machine learning', 'AI', 'ML', 'neural network', 'deep learning',
              'generative AI', 'AI governance', 'AI regulation', 'algorithmic', 'foundation model', 'LLM'],
    'Data Privacy': ['data privacy', 'data protection', 'GDPR', 'personal data', 'privacy law', 'PDPA', 'PDPC',
                     'cross-border data', 'data localization', 'data residency', 'data transfer', 'privacy notice',
                     'consent management', 'data subject rights', 'data breach notification'],
    'Cybersecurity': ['cybersecurity', 'cyber security', 'data breach', 'ransomware', 'hacking',
                      'information security', 'security incident', 'cyber resilience', 'critical infrastructure',
                      'security standards', 'penetration testing', 'vulnerability disclosure'],
    'Cloud': ['cloud computing', 'cloud service', 'SaaS', 'PaaS', 'IaaS', 'cloud provider',
              'software licensing', 'subscription services', 'API regulation', 'software as a service',
              'cloud sovereignty', 'multi-tenancy'],

    # --- DIGITAL TRANSACTIONS ---
    'eSignature': ['electronic signature', 'e-signature', 'digital signature', 'digital identity',
                   'electronic contract', 'electronic transaction', 'electronic record', 'remote notarization',
                   'digital authentication', 'biometric verification'],
    'E-commerce': ['e-commerce', 'online marketplace', 'platform regulation', 'digital services act',
                   'online terms', 'distance selling', 'digital contract', 'click-wrap', 'browse-wrap'],

    # --- CONTRACTS & COMMERCIAL ---
    'Contract Law': ['contract law', 'commercial contract', 'contractual', 'agreement', 'standard terms',
                     'limitation of liability', 'indemnification', 'auto-renewal', 'terms of service',
                     'force majeure', 'service level agreement', 'SLA'],

    # --- COMPETITION & MARKETS ---
    'Competition': ['competition law', 'antitrust', 'anti-trust', 'monopoly', 'market dominance', 'cartel',
                    'digital markets', 'platform regulation', 'gatekeeper', 'self-preferencing', 'bundling',
                    'abuse of dominance', 'merger control'],

    # --- CONSUMER & PLATFORM ---
    'Consumer Protection': ['consumer protection', 'consumer rights', 'consumer law', 'unfair practice',
                            'unfair contract terms', 'consumer guarantee', 'digital consumer', 'dark patterns',
                            'subscription traps', 'drip pricing'],
    'Platform Liability': ['platform liability', 'intermediary liability', 'content moderation', 'safe harbor',
                           'notice and takedown', 'illegal content', 'harmful content', 'online safety',
                           'digital services', 'hosting provider'],

    # --- CORPORATE & GOVERNANCE ---
    'Corporate Governance': ['corporate governance', 'director duties', 'shareholders', 'board', 'ESG',
                             'sustainability reporting', 'climate disclosure', 'supply chain due diligence'],

    # --- FINANCIAL SERVICES ---
    'Fintech': ['fintech', 'financial technology', 'digital payment', 'cryptocurrency', 'blockchain',
                'digital wallet', 'open banking', 'payment services', 'digital assets', 'stablecoin', 'CBDC'],
    'AML': ['anti-money laundering', 'AML', 'money laundering', 'financial crime', 'sanctions', 'KYC',
            'customer due diligence', 'beneficial ownership'],
    'Anti-Bribery': ['anti-bribery', 'anti-corruption', 'bribery', 'corruption', 'FCPA', 'foreign corrupt'],

    # --- EMPLOYMENT & WORKFORCE ---
    'Employment': ['employment law', 'remote work', 'work from home', 'gig economy', 'platform worker',
                   'independent contractor', 'employee classification', 'right to disconnect',
                   'algorithmic management', 'workplace AI', 'employment AI'],

    # --- INTELLECTUAL PROPERTY ---
    'IP': ['intellectual property', 'patent', 'copyright', 'trademark', 'trade secret', 'software patent',
           'open source', 'licensing', 'IP infringement', 'standard essential patent', 'SEP', 'FRAND'],

    # --- TAX & OUTSOURCING ---
    'Tax': ['digital services tax', 'withholding tax', 'transfer pricing', 'tax treaty',
            'permanent establishment', 'VAT digital', 'GST digital', 'tax compliance', 'Pillar One', 'Pillar Two',
            'global minimum tax'],
    'Outsourcing': ['outsourcing', 'vendor management', 'third party', 'service provider',
                    'subcontracting', 'offshore', 'BPO', 'subprocessor', 'supply chain'],

    # --- TELECOMMUNICATIONS ---
    'Telecom': ['telecommunications', 'telecom regulation', 'spectrum', 'net neutrality',
                'internet service provider', 'ISP', 'communications law', '5G regulation'],
}

# Search topic categories for comprehensive coverage
SEARCH_TOPICS = {
    'core_tech': [
        'data privacy law',
        'cybersecurity regulation',
        'artificial intelligence law',
        'digital regulation',
        'technology regulation',
    ],
    'enforcement': [
        'privacy enforcement penalty fine',
        'data protection enforcement action',
        'regulatory penalty technology',
        'investigation compliance order undertaking infringement notice',
    ],
    'consultations': [
        'draft legislation technology',
        'public consultation digital',
        'proposed regulation technology',
        'regulatory consultation privacy AI',
    ],
    'platform': [
        'platform regulation liability',
        'content moderation law',
        'online safety regulation',
        'digital services regulation',
    ],
    'commercial': [
        'fintech regulation',
        'e-commerce law',
        'electronic signature law',
        'digital contract regulation',
    ],
    'employment': [
        'gig economy worker classification',
        'remote work employment law',
        'platform worker regulation',
    ],
    'ip': [
        'AI copyright intellectual property',
        'software patent technology',
        'open source licensing regulation',
    ],
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
    'VN': 'Vietnam {topic} law technology regulation site:gov.vn OR site:vn',
    'MY': 'Malaysia {topic} law technology regulation site:gov.my OR site:my',
    'TW': 'Taiwan {topic} law technology regulation site:gov.tw OR site:tw',
    'TH': 'Thailand {topic} law technology regulation site:go.th OR site:th',
    'ASEAN': 'ASEAN {topic} digital economy regulation'
}

# =============================================================================
# COMPREHENSIVE SEARCH CONFIGURATION
# =============================================================================
# This defines the complete search matrix for digest generation.
# When generating a digest, Claude should run ALL keyword searches
# for ALL jurisdictions to ensure comprehensive coverage.

# All jurisdictions to search (12 jurisdictions + 1 regional)
DIGEST_JURISDICTIONS = [
    'AU',   # Australia
    'SG',   # Singapore
    'JP',   # Japan
    'KR',   # South Korea
    'HK',   # Hong Kong
    'IN',   # India
    'ID',   # Indonesia
    'VN',   # Vietnam
    'NZ',   # New Zealand
    'MY',   # Malaysia
    'PH',   # Philippines
    'TW',   # Taiwan
    'TH',   # Thailand
    'ASEAN' # Regional ASEAN
]

# All keyword topics to search per jurisdiction (16 keyword categories)
DIGEST_SEARCH_KEYWORDS = [
    # Existing core topics
    'privacy data protection law',
    'cybersecurity law regulation',
    'AI artificial intelligence regulation',
    'fintech digital assets crypto regulation',
    'platform regulation online safety',
    'enforcement penalty fine data privacy',
    'technology law digital economy',
    # New topic areas
    'electronic signature e-signature digital identity law',
    'anti-corruption anti-bribery enforcement',
    'consumer protection unfair contract terms dark patterns',
    'competition antitrust digital markets',
    'employment law gig economy platform workers',
    'corporate governance ESG sustainability reporting',
    'copyright intellectual property AI',
    'digital services tax transfer pricing',
    'contract law commercial SaaS cloud subscription',
]

# Extraterritorial / cross-border search keywords (searched without jurisdiction prefix)
EXTRATERRITORIAL_KEYWORDS = [
    'EU AI Act extraterritorial Asia Pacific impact',
    'GDPR enforcement Asia Pacific cross-border',
    'UK Online Safety Act Asia impact',
    'US executive order AI regulation Asia Pacific',
]

# Total expected searches: 14 jurisdictions × 16 keywords + 4 extraterritorial = ~228 searches
# This ensures comprehensive coverage across all topics and regions

# Ranking weights
MATERIALITY_WEIGHT = 0.6
JURISDICTION_WEIGHT = 0.4
