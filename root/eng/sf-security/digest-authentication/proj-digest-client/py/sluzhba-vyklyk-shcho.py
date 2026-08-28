NONCE_TTL = 30.0                                     # с — скільки живе виклик
ALLOWED = 'SHA-256'                                  # рівень захисту обираємо МИ


def make_nonce(secret, etag=''):
    """Виклик, який нікуди не треба класти: мітка часу відкрито + підпис її ж."""
    stamp = '%.6f' % time.time()
    mark = hmac.new(secret, f'{stamp}:{etag}'.encode(), 'sha256').hexdigest()
    return base64.b64encode(f'{stamp}:{mark}'.encode()).decode()


def check_nonce(secret, etag, nonce, ttl=NONCE_TTL):
    """'fresh' | 'stale' | 'bad' — без жодного звертання до сховища."""
    try:
        stamp, mark = base64.b64decode(nonce, validate=True).decode().split(':', 1)
        age = time.time() - float(stamp)
    except Exception:
        return 'bad'
    want = hmac.new(secret, f'{stamp}:{etag}'.encode(), 'sha256').hexdigest()
    if not hmac.compare_digest(want, mark):
        return 'bad'                                 # не наш виклик або підроблений
    return 'fresh' if 0 <= age < ttl else 'stale'


def authenticate(secret, ha1_store, seen, method, target, header, etag=''):
    """method і target беремо З САМОГО ЗАПИТУ; заголовок — лише заявка."""
    chs = parse_challenges(header or '')
    if not chs or chs[0]['scheme'] != 'digest':
        return 'challenge'
    p = chs[0]['params']

    if p.get('uri') != target:                       # доказ порахований під інший шлях
        return 'bad-request'
    if p.get('algorithm', 'MD5').upper() != ALLOWED:
        return 'challenge'                           # зниження рівня не обговорюється

    state = check_nonce(secret, etag, p.get('nonce', ''))
    if state != 'fresh':
        return 'stale' if state == 'stale' else 'challenge'

    try:
        nc = int(p['nc'], 16)
    except (KeyError, ValueError):
        return 'challenge'
    if nc <= seen.get(p['nonce'], 0):                # номер не зріс → це повтор
        return 'challenge'

    ha1 = ha1_store.get((p.get('username'), p.get('realm'), ALLOWED))
    if ha1 is None:
        return 'challenge'                           # хто це — не пояснюємо

    H = lambda s: hashlib.new(ALGORITHMS[ALLOWED][0], s.encode('utf-8')).hexdigest()
    ha2 = H(f'{method}:{target}')                    # ← з запиту, не з p['uri']
    want = H('{}:{}:{}:{}:{}:{}'.format(ha1, p['nonce'], p['nc'],
                                        p.get('cnonce', ''), p.get('qop', ''), ha2))
    if not hmac.compare_digest(want, p.get('response', '')):
        return 'challenge'

    seen[p['nonce']] = nc                            # запам'ятовуємо ЛИШЕ підтверджений
    return 'ok'
