QUOTED = ('username', 'realm', 'nonce', 'uri', 'response', 'cnonce', 'opaque')


def _field(k, v):
    if k not in QUOTED:
        return f'{k}={v}'                 # algorithm, qop, nc — БЕЗ лапок
    return '{}="{}"'.format(k, v.replace('\\', '\\\\').replace('"', '\\"'))


class DigestClient:
    def __init__(self, username, password):
        self.username, self.password = username, password
        self._counts = {}                 # nonce → скільки запитів уже пішло
        self._sess = {}                   # nonce → (ключ сеансу, його cnonce)

    def authorization(self, ch, method, target, body=b''):
        p = ch['params']
        declared = p.get('algorithm', 'MD5')
        base, sess = split_alg(declared)
        name = ALGORITHMS[base][0]
        Hb = lambda b: hashlib.new(name, b).hexdigest()
        H = lambda s: Hb(s.encode('utf-8'))          # пароль — саме UTF-8

        nonce = p['nonce']
        self._counts[nonce] = self._counts.get(nonce, 0) + 1
        nc = '%08x' % self._counts[nonce]            # рівно 8 шістнадцяткових цифр
        cnonce = os.urandom(16).hex()                # непередбачуване, не «щоразу інше»

        secret = H(f'{self.username}:{p["realm"]}:{self.password}')
        if sess:                                     # ключ сеансу рахуємо ОДИН раз на виклик
            if nonce not in self._sess:
                self._sess[nonce] = (H(f'{secret}:{nonce}:{cnonce}'), cnonce)
            secret, cnonce = self._sess[nonce]       # і cnonce більше не міняємо

        offered = [x.strip() for x in p.get('qop', 'auth').split(',')]
        qop = 'auth' if 'auth' in offered else 'auth-int'
        a2 = f'{method}:{target}' + (f':{Hb(body)}' if qop == 'auth-int' else '')
        response = H(f'{secret}:{nonce}:{nc}:{cnonce}:{qop}:{H(a2)}')

        fields = {'username': self.username, 'realm': p['realm'], 'uri': target,
                  'algorithm': declared, 'nonce': nonce, 'nc': nc,
                  'cnonce': cnonce, 'qop': qop, 'response': response}
        if 'opaque' in p:
            fields['opaque'] = p['opaque']           # повертаємо як є, не заглядаючи
        ctx = {'H': H, 'secret': secret, 'nonce': nonce, 'nc': nc,
               'cnonce': cnonce, 'qop': qop, 'uri': target}
        return 'Digest ' + ', '.join(_field(k, v) for k, v in fields.items()), ctx

    def verify_rspauth(self, ctx, info_header):
        """Authentication-Info: чи знає співрозмовник те саме H(A1)."""
        p = parse_params(info_header)
        if 'rspauth' not in p:
            return False
        H = ctx['H']
        ha2 = H(':' + ctx['uri'])                    # ← БЕЗ методу: його обирали не ми
        want = H(f'{ctx["secret"]}:{ctx["nonce"]}:{ctx["nc"]}:{ctx["cnonce"]}:{ctx["qop"]}:{ha2}')
        return hmac.compare_digest(want, p['rspauth'])
