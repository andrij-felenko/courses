import base64, hashlib, hmac, os, re, time

_ITEM = re.compile(r'''
    \s*(?:,\s*)*                        # роздільники й порожні місця
    (?P<key>[A-Za-z][A-Za-z0-9_.-]*)    # назва схеми АБО ім'я поля
    (?:\s*=\s*(?:                       # значення — необов'язкове!
          "(?P<q>(?:[^"\\]|\\.)*)"      # у лапках: кома всередині — не роздільник
        | (?P<t>[^\s,]*) ))?            # або голий токен
''', re.VERBOSE)


def _items(header):
    """Заголовок → потік (ім'я, значення). Значення None ⇒ це назва схеми."""
    pos = 0
    while True:
        m = _ITEM.match(header, pos)
        if not m or m.end() == pos:
            return
        pos = m.end()
        q, t = m.group('q'), m.group('t')
        yield m.group('key').lower(), (re.sub(r'\\(.)', r'\1', q) if q is not None else t)


def parse_challenges(header):
    """WWW-Authenticate → виклики в тому порядку, як їх дала служба."""
    out = []
    for key, value in _items(header):
        if value is None:
            out.append({'scheme': key, 'params': {}})   # слово без «=» → нова схема
        elif out:
            out[-1]['params'][key] = value
    return out


def parse_params(header):
    """Authentication-Info і подібні — самі поля, без назви схеми."""
    return {k: v for k, v in _items(header) if v is not None}


ALGORITHMS = {                            # назва в заголовку → (ім'я в hashlib, сила)
    'SHA-512-256': ('sha512_256', 3),     # це SHA-512/256 з FIPS 180-4,
    'SHA-256':     ('sha256',     2),     # а НЕ обрізаний sha512
    'MD5':         ('md5',        1),
}


def split_alg(name):
    sess = name.upper().endswith('-SESS')
    return (name[:-5] if sess else name).upper(), sess


def pick(challenges):
    """Найсильніший Digest-виклик із тих, що ми вміємо: порядок у заголовку не захищений."""
    best, best_strength = None, 0
    for ch in challenges:
        if ch['scheme'] != 'digest':
            continue
        known = ALGORITHMS.get(split_alg(ch['params'].get('algorithm', 'MD5'))[0])
        if known and known[1] > best_strength:
            best, best_strength = ch, known[1]
    return best
