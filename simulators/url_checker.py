import re
from urllib.parse import urlparse

_SHORT_URL_HOSTS = {
    'bit.ly', 'tinyurl.com', 'goo.gl', 't.co', 'ow.ly', 'is.gd',
    'buff.ly', 'short.io', 'rb.gy', 'cutt.ly', 'tiny.cc', 'shorte.st',
}

_SUSPICIOUS_TLDS = {'.tk', '.ml', '.ga', '.cf', '.gq', '.pw', '.top', '.click', '.link'}

_BRAND_KEYWORDS = [
    'paypal', 'amazon', 'apple', 'google', 'microsoft', 'facebook',
    'instagram', 'netflix', 'ebay', 'chase', 'wellsfargo', 'citibank',
    'bankofamerica', 'linkedin', 'twitter', 'dropbox', 'icloud', 'outlook',
]

_SUSPICIOUS_PATH_TERMS = [
    'login', 'signin', 'verify', 'account', 'update', 'secure',
    'confirm', 'validate', 'credential', 'password', 'auth',
]


def analyze_url(raw_url: str) -> dict:
    indicators = []
    risk_score  = 0
    url = raw_url.strip()

    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    try:
        parsed = urlparse(url)
    except Exception:
        return _invalid_url_result()

    scheme = parsed.scheme
    domain = (parsed.netloc or '').lower()
    path   = (parsed.path or '').lower()

    if not domain:
        return _invalid_url_result()

    domain_clean = domain.split(':')[0]
    base_domain  = domain_clean.removeprefix('www.')

    # 1. HTTP — unencrypted connection
    if scheme == 'http':
        indicators.append({'severity': 'medium', 'text': 'Uses HTTP (not HTTPS) — connection is unencrypted'})
        risk_score += 2

    # 2. IP address as domain
    if re.fullmatch(r'\d{1,3}(\.\d{1,3}){3}', domain_clean):
        indicators.append({'severity': 'high', 'text': 'Domain is a raw IP address — legitimate services use named domains, not IPs'})
        risk_score += 4

    # 3. URL shortener
    if base_domain in _SHORT_URL_HOSTS:
        indicators.append({'severity': 'high', 'text': f'URL shortener detected ({base_domain}) — the real destination is hidden'})
        risk_score += 3

    # 4. Suspicious TLD
    for tld in _SUSPICIOUS_TLDS:
        if base_domain.endswith(tld):
            indicators.append({'severity': 'medium', 'text': f'Suspicious top-level domain ({tld}) — frequently abused in phishing campaigns'})
            risk_score += 2
            break

    # 5. Brand name in wrong domain position (impersonation)
    for brand in _BRAND_KEYWORDS:
        if brand in base_domain:
            legitimate = (
                base_domain in {f'{brand}.com', f'{brand}.org', f'{brand}.net', f'{brand}.co'}
                or base_domain.endswith(f'.{brand}.com')
            )
            if not legitimate:
                indicators.append({'severity': 'high', 'text': f'Domain impersonates "{brand}" — brand name placed in a suspicious position'})
                risk_score += 4
                break

    # 6. @ symbol — can spoof the visible host
    if '@' in url:
        indicators.append({'severity': 'high', 'text': 'URL contains @ symbol — can be used to hide the real destination'})
        risk_score += 3

    # 7. Excessive subdomains
    dot_count = domain_clean.count('.')
    if dot_count >= 4:
        indicators.append({'severity': 'medium', 'text': f'Excessive subdomains ({dot_count} levels) — often used to make spoofed domains look legitimate'})
        risk_score += 2

    # 8. Suspicious path keyword
    for term in _SUSPICIOUS_PATH_TERMS:
        if f'/{term}' in path:
            indicators.append({'severity': 'low', 'text': f'Path contains "/{term}" — a common pattern in credential-harvesting pages'})
            risk_score += 1
            break

    # 9. Heavy URL encoding (obfuscation)
    pct_count = url.count('%')
    if pct_count >= 5:
        indicators.append({'severity': 'medium', 'text': f'Heavy URL encoding ({pct_count} encoded sequences) — commonly used to conceal malicious content'})
        risk_score += 2

    # 10. Hyphen-heavy domain
    if domain_clean.count('-') >= 3:
        indicators.append({'severity': 'low', 'text': 'Domain contains many hyphens — a common pattern in fake "secure" or "official" domains'})
        risk_score += 1

    # 11. Very long URL
    if len(url) > 100:
        indicators.append({'severity': 'low', 'text': f'Unusually long URL ({len(url)} chars) — may be obscuring the true destination'})
        risk_score += 1

    risk_score = min(risk_score, 10)

    if risk_score >= 7:
        verdict, risk_level = 'HIGH RISK — Likely Malicious URL', 'high'
        recommendation = (
            'Do NOT visit this URL. Multiple indicators of a phishing or malware delivery page were detected. '
            'If received by message or email, report it as phishing and delete it. '
            'If already visited, run an antivirus scan and change passwords for any accounts you may have accessed.'
        )
    elif risk_score >= 4:
        verdict, risk_level = 'MEDIUM RISK — Suspicious URL', 'medium'
        recommendation = (
            'Proceed with caution. Verify the full domain before visiting. '
            'Navigate directly to the official website instead of using this link. '
            'Confirm the domain matches exactly what you expect from the sender or source.'
        )
    elif risk_score >= 1:
        verdict, risk_level = 'LOW RISK — Minor Concerns', 'low'
        recommendation = (
            'A few minor indicators detected. Confirm the URL is from a trusted source '
            'and that HTTPS is active before entering any personal information.'
        )
    else:
        verdict, risk_level = 'No Suspicious Indicators Found', 'safe'
        recommendation = (
            'No obvious red flags detected. Always verify the complete domain '
            'before entering credentials or personal information on any website.'
        )

    return {
        'verdict': verdict,
        'risk_level': risk_level,
        'risk_score': risk_score,
        'indicators': indicators[:6],
        'recommendation': recommendation,
        'formatted': _build_text_report(verdict, risk_score, indicators, recommendation),
    }


def _invalid_url_result() -> dict:
    return {
        'verdict': 'Invalid URL',
        'risk_level': 'high',
        'risk_score': 0,
        'indicators': [{'severity': 'high', 'text': 'Could not parse this URL — check formatting and try again'}],
        'recommendation': 'Ensure the URL starts with http:// or https:// and is correctly formatted.',
        'formatted': '**Invalid URL** — Could not analyze the provided URL.',
    }


def _build_text_report(verdict, risk_score, indicators, recommendation) -> str:
    sev_labels = {'high': '[High]', 'medium': '[Medium]', 'low': '[Low]'}
    lines = [
        '**URL Safety Analysis**',
        '',
        f'**Verdict:** {verdict}',
        f'**Risk Score:** {risk_score}/10',
    ]
    if indicators:
        lines += ['', '**Risk Indicators**']
        for ind in indicators[:5]:
            label = sev_labels.get(ind['severity'], '[Info]')
            lines.append(f'{label} {ind["text"]}')
    lines += ['', '**Recommendation**', recommendation]
    return '\n'.join(lines)
