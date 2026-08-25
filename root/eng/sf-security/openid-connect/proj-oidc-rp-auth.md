# ⚙️ Побудова Relying Party: автентифікація через OpenID Connect і валідація ID-токена

Цей проект реалізує промисловий вузол автентифікації на стороні сервера клієнта (Relying Party, RP) без використання важких магічних бібліотек-обгорток. Мета проекту — розібрати кожен механізм протоколу до найнижчого рівня: динамічне виявлення конфігурації провайдера, генерацію криптографічних параметрів захисту (PKCE, state, nonce), безпечний обмін коду на токени через захищений бек-канал, потокобезпечне кешування публічних ключів JWKS із підтримкою безшовної ротації, покрокову криптографічну та семантичну перевірку ID-токена, отримання даних із кінцевої точки UserInfo та коректне завершення федеративної сесії.

## Архітектурний дизайн та потоки даних

Клієнтський бекенд діє як посередник між ненадійним середовищем браузера користувача (User Agent) та авторитетним сервером ідентифікації (OpenID Provider, OP). Щоб виключити будь-яку можливість підробки особи або перехоплення сесії, система ділиться на чотири ізольовані компоненти:

1. **Менеджер конфігурації та ключів (Discovery & JWKS Cache).** Завантажує документ метаданих `/.well-known/openid-configuration`, кешує URL-адреси кінцевих точок (`authorization_endpoint`, `token_endpoint`, `userinfo_endpoint`, `end_session_endpoint`) та утримує в пам'яті розібрані публічні ключі провайдера. Менеджер підтримує лімітоване оновлення на вимогу (on-demand cache-bust) при появі нових ключів.
2. **Маршрут ініціалізації входу (`/auth/login`).** Створює транзитний криптографічний контекст для конкретного запиту: криптографічну сіль `state`, випадковий `nonce` та пару для розширення PKCE (`code_verifier` і `code_challenge`). Записує ці значення в короткоживучий шифрований стан (або сесійний Redis) і перенаправляє браузер на `authorization_endpoint`.
3. **Маршрут зворотного виклику (`/auth/callback`).** Отримує одноразовий код авторизації від провайдера через браузер, перевіряє `state`, здійснює прямий HTTP POST-запит до `token_endpoint` з передачею `code_verifier`, витягує `id_token` та `access_token`, проганяє ID-токен через повний конвеєр перевірки й створює внутрішню сесію користувача.
4. **Конвеєр сесійної автентифікації та виходу (`/auth/logout`).** Очищає локальні сесійні кукі та формує запит на федеративний вихід через `end_session_endpoint` провайдера з передачею раніше збереженого `id_token_hint`.

```
+--------------------------------------------------------------------------------------------------+
|                                    Relying Party (Backend)                                       |
|                                                                                                  |
|   /auth/login ---------> 1. Генерація PKCE (verifier + S256 challenge), state, nonce             |
|                             Формування 302 Redirect на Authorization Endpoint                    |
|                                                                                                  |
|   /auth/callback ------> 2. Валідація отриманого state із сесійного сховища                      |
|                             3. Прямий POST /token (code + code_verifier + client credentials)     |
|                             4. Отримання JSON: { id_token, access_token, refresh_token }         |
|                             5. Валідація підпису ID-токена через JWKS Manager (kid -> PubKey)    |
|                             6. Семантична перевірка claims: iss, aud, exp, iat, nonce, at_hash   |
|                             7. Опційний запит GET /userinfo (Bearer access_token)                |
|                             8. Створення постійної httpOnly Secure Cookie сесії для клієнта      |
|                                                                                                  |
|   JWKS Manager --------> Фоновий та on-demand кеш публічних ключів із захистом від DoS            |
+--------------------------------------------------------------------------------------------------+
```

## Крок 1. Генерація параметрів захисту та формування запиту авторизації

Безпека всього протоколу OpenID Connect тримається на неможливості передбачити або підробити три параметри:

* **`state`** — випадкова послідовність високої ентропії (128 біт), яка передається провайдеру і повертається ним без змін на маршрут `/callback`. Звірка `state` гарантує, що відповідь прийшла у відповідь саме на той запит, який ініціював цей конкретний користувач у цьому браузері, запобігаючи атакам CSRF та підкиданню авторизаційного коду зловмисника.
* **`nonce`** — криптографічна сіль, яку провайдер зобов'язаний скопіювати в корисне навантаження ID-токена (`claims["nonce"]`). Коли клієнт отримує токен, він звіряє це поле з локально збереженим значенням. Це захищає від атаки повторного відтворення (replay attack): зловмисник не може повторно використати раніше перехоплений чужий ID-токен у новому сеансі входу.
* **`code_verifier` та `code_challenge` (PKCE, RFC 7636)** — пара ключів для захисту коду авторизації. `code_verifier` генерується як рядок випадкових байтів довжиною від 43 до 128 символів. На сервер авторизації надсилається лише його односторонній відбиток `code_challenge`:

```
code_challenge = Base64URL( SHA-256( ASCII( code_verifier ) ) )
```

Коли клієнт обмінює код на токен на кроці 3, він надсилає сирий `code_verifier`. Провайдер повторно рахує SHA-256 і переконується, що за токенами прийшов саме той клієнт, який ініціював вхід, а не зловмисник, що перехопив код авторизації в браузері.

:::tabs
```py
import os
import base64
import hashlib
import urllib.parse

def b64url_encode(data: bytes) -> str:
    """Кодування сирих байтів у безпечний рядок Base64URL без знаків '='."""
    return base64.urlsafe_b64encode(data).decode('ascii').rstrip('=')

def generate_pkce_pair() -> tuple[str, str]:
    """Генерація випадкового code_verifier та розрахунок code_challenge (S256)."""
    verifier_bytes = os.urandom(32) # 256 біт ентропії
    code_verifier = b64url_encode(verifier_bytes)
    
    digest = hashlib.sha256(code_verifier.encode('ascii')).digest()
    code_challenge = b64url_encode(digest)
    return code_verifier, code_challenge

def create_authorization_url(
    authorization_endpoint: str,
    client_id: str,
    redirect_uri: str,
    scope: str = "openid profile email"
) -> dict:
    state = b64url_encode(os.urandom(24))
    nonce = b64url_encode(os.urandom(24))
    code_verifier, code_challenge = generate_pkce_pair()
    
    params = {
        "client_id": client_id,
        "response_type": "code",
        "scope": scope,
        "redirect_uri": redirect_uri,
        "state": state,
        "nonce": nonce,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "response_mode": "query"
    }
    
    query_string = urllib.parse.urlencode(params)
    auth_url = f"{authorization_endpoint}?{query_string}"
    
    return {
        "auth_url": auth_url,
        "state": state,
        "nonce": nonce,
        "code_verifier": code_verifier,
    }
```
```ts
import crypto from 'crypto';

function b64urlEncode(buffer: Buffer): string {
  return buffer.toString('base64url');
}

export function generatePkcePair(): { codeVerifier: string; codeChallenge: string } {
  const verifierBytes = crypto.randomBytes(32);
  const codeVerifier = b64urlEncode(verifierBytes);
  
  const hash = crypto.createHash('sha256').update(codeVerifier, 'ascii').digest();
  const codeChallenge = b64urlEncode(hash);
  
  return { codeVerifier, codeChallenge };
}

export function createAuthorizationUrl(
  authorizationEndpoint: string,
  clientId: string,
  redirectUri: string,
  scope: string = 'openid profile email'
) {
  const state = b64urlEncode(crypto.randomBytes(24));
  const nonce = b64urlEncode(crypto.randomBytes(24));
  const { codeVerifier, codeChallenge } = generatePkcePair();

  const url = new URL(authorizationEndpoint);
  url.searchParams.set('client_id', clientId);
  url.searchParams.set('response_type', 'code');
  url.searchParams.set('scope', scope);
  url.searchParams.set('redirect_uri', redirectUri);
  url.searchParams.set('state', state);
  url.searchParams.set('nonce', nonce);
  url.searchParams.set('code_challenge', codeChallenge);
  url.searchParams.set('code_challenge_method', 'S256');
  url.searchParams.set('response_mode', 'query');

  return {
    authUrl: url.toString(),
    state,
    nonce,
    codeVerifier,
  };
}
```
:::

## Крок 2. Потокобезпечний менеджер ключів JWKS з обробкою ротації

Сервери авторизації підписують ID-токени закритим ключем пари RSA або ECDSA. Публічна частина публікується як JSON-масив ключів за адресою `jwks_uri`.

Під час експлуатації виникає критична інженерна вимога: **провайдери регулярно оновлюють ключі підпису**. Якщо сервіс жорстко зашиє ключ або завантажить його лише раз під час старту програми, при першій же плановій або екстреній ротації всі вхідні токени почнуть відхилятися через невідомий `kid`.

Менеджер відкритих ключів повинен реалізувати таку логіку:
1. Зберігати розібрані публічні ключі в пам'яті разом із позначкою часу завантаження та TTL (наприклад, 24 години).
2. При виклику `get_key(kid)` шукати ключ у локальному словнику.
3. Якщо ключ із запитаним `kid` відсутній, не панікувати одразу, а виконати повторний запит до `jwks_uri` для підтягування свіжих ключів.
4. Встановити мінімальний інтервал між позачерговими оновленнями (`min_refresh_interval = 10 секунд`), щоб зловмисник не міг організувати DoS-атаку на наш бекенд, надсилаючи підроблені токени з нескінченно різними випадковими `kid`.

:::tabs
```py
import json
import time
import urllib.request
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

class JwksManager:
    def __init__(self, jwks_uri: str, ttl_seconds: int = 86400):
        self.jwks_uri = jwks_uri
        self.ttl = ttl_seconds
        self.keys: dict[str, rsa.RSAPublicKey] = {}
        self.last_fetched: float = 0.0
        self.min_refresh_interval: float = 10.0

    @staticmethod
    def _b64url_decode(s: str) -> bytes:
        rem = len(s) % 4
        if rem > 0:
            s += "=" * (4 - rem)
        return base64.urlsafe_b64decode(s.encode('ascii'))

    def _fetch_keys(self) -> None:
        req = urllib.request.Request(
            self.jwks_uri,
            headers={"User-Agent": "OIDC-RelyingParty-Engine/1.0", "Accept": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status != 200:
                raise RuntimeError(f"Помилка завантаження JWKS: HTTP {response.status}")
            raw_data = response.read().decode('utf-8')
            data = json.loads(raw_data)
            
        new_keys = {}
        for key_data in data.get("keys", []):
            if key_data.get("kty") == "RSA" and key_data.get("use", "sig") == "sig":
                kid = key_data.get("kid")
                if not kid:
                    continue
                # Витягуємо параметри модуля n та експоненти e
                n_bytes = self._b64url_decode(key_data["n"])
                e_bytes = self._b64url_decode(key_data["e"])
                n_int = int.from_bytes(n_bytes, byteorder='big')
                e_int = int.from_bytes(e_bytes, byteorder='big')
                
                pub_num = rsa.RSAPublicNumbers(e_int, n_int)
                pub_key = pub_num.public_key(default_backend())
                new_keys[kid] = pub_key

        self.keys = new_keys
        self.last_fetched = time.time()

    def get_key(self, kid: str) -> rsa.RSAPublicKey:
        now = time.time()
        # Планове оновлення, якщо кеш застарів або ще порожній
        if now - self.last_fetched > self.ttl or not self.keys:
            self._fetch_keys()

        # Якщо kid новий (можлива ротація) — робимо одиночне форсоване оновлення
        if kid not in self.keys:
            if now - self.last_fetched > self.min_refresh_interval:
                self._fetch_keys()
                
        if kid not in self.keys:
            raise KeyError(f"Публічний ключ із kid='{kid}' не знайдено в JWKS провайдера")
            
        return self.keys[kid]
```
```ts
import crypto from 'crypto';

interface JwkKey {
  kty: string;
  use?: string;
  kid?: string;
  alg?: string;
  n: string;
  e: string;
}

export class JwksManager {
  private jwksUri: string;
  private ttlMs: number;
  private keys: Map<string, crypto.KeyObject> = new Map();
  private lastFetched: number = 0;
  private minIntervalMs: number = 10000;

  constructor(jwksUri: string, ttlSeconds: number = 86400) {
    this.jwksUri = jwksUri;
    this.ttlMs = ttlSeconds * 1000;
  }

  private async fetchKeys(): Promise<void> {
    const res = await fetch(this.jwksUri, {
      headers: { 'User-Agent': 'OIDC-RelyingParty-Engine/1.0', Accept: 'application/json' },
    });
    if (!res.ok) throw new Error(`Помилка отримання JWKS: HTTP ${res.status}`);
    const data = (await res.json()) as { keys: JwkKey[] };

    const newMap = new Map<string, crypto.KeyObject>();
    for (const key of data.keys || []) {
      if (key.kty === 'RSA' && (key.use === undefined || key.use === 'sig')) {
        const jwkObj: crypto.JsonWebKey = {
          kty: 'RSA',
          n: key.n,
          e: key.e,
        };
        const keyObject = crypto.createPublicKey({ key: jwkObj, format: 'jwk' });
        if (key.kid) {
          newMap.set(key.kid, keyObject);
        }
      }
    }
    this.keys = newMap;
    this.lastFetched = Date.now();
  }

  public async getKey(kid: string): Promise<crypto.KeyObject> {
    const now = Date.now();
    if (now - this.lastFetched > this.ttlMs || this.keys.size === 0) {
      await this.fetchKeys();
    }

    if (!this.keys.has(kid)) {
      if (now - this.lastFetched > this.minIntervalMs) {
        await this.fetchKeys();
      }
    }

    const key = this.keys.get(kid);
    if (!key) throw new Error(`Відкритий ключ kid='${kid}' відсутній у наборі JWKS`);
    return key;
  }
}
```
:::

## Крок 3. Обмін авторизаційного коду на токени (Бек-канал)

Після того, як користувач успішно автентифікувався на сторінці провайдера, браузер отримує редирект на наш `/auth/callback` із двома параметрами: `code` та `state`.

Клієнт негайно звіряє отриманий `state` зі збереженим у сесійній пам'яті. У разі збігу сервер виконує прямий, зашифрований через TLS POST-запит до `token_endpoint`. Цей запит іде в обхід браузера (Back-channel), тому токени не потрапляють в історію перегляду чи заголовки Referer.

:::tabs
```py
def exchange_code_for_tokens(
    token_endpoint: str,
    client_id: str,
    client_secret: str | None,
    code: str,
    code_verifier: str,
    redirect_uri: str
) -> dict:
    payload_data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "code_verifier": code_verifier,
    }
    if client_secret:
        payload_data["client_secret"] = client_secret
        
    encoded_data = urllib.parse.urlencode(payload_data).encode('ascii')
    req = urllib.request.Request(
        token_endpoint,
        data=encoded_data,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "User-Agent": "OIDC-RelyingParty-Engine/1.0"
        },
        method="POST"
    )
    
    with urllib.request.urlopen(req, timeout=10) as response:
        if response.status != 200:
            raise RuntimeError(f"Помилка обміну токенів: HTTP {response.status}")
        return json.loads(response.read().decode('utf-8'))
```
```ts
export async function exchangeCodeForTokens(
  tokenEndpoint: string,
  clientId: string,
  clientSecret: string | null,
  code: string,
  codeVerifier: string,
  redirectUri: string
): Promise<{ id_token: string; access_token: string; refresh_token?: string; expires_in: number }> {
  const body = new URLSearchParams();
  body.set('grant_type', 'authorization_code');
  body.set('code', code);
  body.set('redirect_uri', redirectUri);
  body.set('client_id', clientId);
  body.set('code_verifier', codeVerifier);
  if (clientSecret) {
    body.set('client_secret', clientSecret);
  }

  const res = await fetch(tokenEndpoint, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      Accept: 'application/json',
      'User-Agent': 'OIDC-RelyingParty-Engine/1.0',
    },
    body: body.toString(),
  });

  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`Помилка обміну коду на токени: HTTP ${res.status} - ${errText}`);
  }

  return res.json();
}
```
:::

## Крок 4. Повний конвеєр криптографічної та логічної валідації ID-токена

Отриманий `id_token` розбирається та перевіряється за суворим чеклістом із восьми обов'язкових пунктів.

### Послідовність перевірок

1. **Розбір формату JWS:** Токен розбивається на три частини за символом крапки: `header_b64.payload_b64.signature_b64`.
2. **Верифікація заголовка:**
   * Алгоритм `alg` зобов'язаний бути виключно в білому списку асиметричних алгоритмів (наприклад, `RS256`).
   * Заборонені алгоритми `"none"` та симетричні `HS256` (якщо клієнт не налаштований спеціально на симетричний спільний секрет).
   * Витягується ідентифікатор ключа `kid`.
3. **Криптографічна верифікація цифрового підпису:**
   * Завантажується публічний ключ провайдера за його `kid`.
   * За допомогою відкритого ключа перевіряється, що `signature` є дійсним цифровим підписом байтів ASCII-рядка `header_b64 + "." + payload_b64`.
4. **Звірка емітента (`iss`):** Значення поля `iss` у токені має символ-у-символ збігатися з офіційною URL-адресою видавця провайдера.
5. **Звірка аудиторії (`aud`):** Поле `aud` зобов'язане містити `client_id` нашого клієнтського додатку. Якщо в `aud` перелічено кілька клієнтів (масив), токен зобов'язаний містити поле `azp` (Authorized Party), рівне нашому `client_id`.
6. **Перевірка часових меж (`exp`, `iat`):**
   * Час закінчення дії `exp` має бути більшим за поточний системний час (`exp + skew > now`).
   * Час випуску `iat` не може випереджати поточний час (`iat - skew <= now`).
7. **Звірка солі `nonce`:** Значення `payload["nonce"]` зобов'язане точно збігатися з `nonce`, згенерованим перед редиректом.
8. **Верифікація хешу токена доступу (`at_hash`):** Якщо у відповіді надійшов `access_token` і в ID-токені присутнє твердження `at_hash`, клієнт самостійно обчислює хеш від отриманого access-токена та порівнює його через функцію порівняння сталого часу.

### Розрахунок `at_hash` для RS256:

```
х = SHA-256( ASCII( access_token ) )
половина = ліві 16 байтів х (128 біт)
очікуваний_at_hash = Base64URL( половина )
перевірка: constant_time_equals( payload["at_hash"], очікуваний_at_hash )
```

Погляньмо на реалізацію валідатора:

:::tabs
```py
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
import hmac

def validate_id_token(
    id_token_raw: str,
    expected_issuer: str,
    expected_client_id: str,
    expected_nonce: str,
    jwks_manager: JwksManager,
    access_token_raw: str | None = None,
    clock_skew_sec: int = 60
) -> dict:
    parts = id_token_raw.split('.')
    if len(parts) != 3:
        raise ValueError("Некоректний формат JWT: очікується рівно три частини")
        
    header_b64, payload_b64, sig_b64 = parts
    
    # 1. Розбір та перевірка заголовка
    header_bytes = JwksManager._b64url_decode(header_b64)
    header = json.loads(header_bytes.decode('utf-8'))
    
    alg = header.get("alg")
    if alg != "RS256":
        raise ValueError(f"Недозволений алгоритм підпису: {alg}. Очікується RS256")
        
    kid = header.get("kid")
    if not kid:
        raise ValueError("У заголовку JWT відсутнє обов'язкове поле kid")
        
    # 2. Отримання відкритого ключа та перевірка підпису
    public_key = jwks_manager.get_key(kid)
    signed_payload = f"{header_b64}.{payload_b64}".encode('ascii')
    signature = JwksManager._b64url_decode(sig_b64)
    
    try:
        public_key.verify(
            signature,
            signed_payload,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
    except Exception as exc:
        raise ValueError("Цифровий підпис ID-токена не пройшов верифікацію!") from exc
        
    # 3. Розбір навантаження (claims)
    payload_bytes = JwksManager._b64url_decode(payload_b64)
    payload = json.loads(payload_bytes.decode('utf-8'))
    now = time.time()
    
    # 4. Перевірка видавця (iss)
    if payload.get("iss") != expected_issuer:
        raise ValueError(f"Невідповідність iss: очікувалось {expected_issuer}, отримано {payload.get('iss')}")
        
    # 5. Перевірка аудиторії (aud)
    aud = payload.get("aud")
    if isinstance(aud, str):
        if aud != expected_client_id:
            raise ValueError(f"Невідповідність aud: {aud} != {expected_client_id}")
    elif isinstance(aud, list):
        if expected_client_id not in aud:
            raise ValueError(f"client_id {expected_client_id} відсутній у списку aud: {aud}")
        if len(aud) > 1 and payload.get("azp") != expected_client_id:
            raise ValueError("Для множинного aud значення azp має дорівнювати client_id")
    else:
        raise ValueError("Відсутнє або некоректне поле aud")
        
    # 6. Перевірка часових міток (exp, iat)
    exp = payload.get("exp")
    if not exp or (exp + clock_skew_sec) < now:
        raise ValueError("Термін дії ID-токена сплив (exp)")
        
    iat = payload.get("iat")
    if iat and (iat - clock_skew_sec) > now:
        raise ValueError("Токен випущено в майбутньому (iat)")
        
    # 7. Звірка Nonce
    if payload.get("nonce") != expected_nonce:
        raise ValueError("Порушення nonce: токен не відповідає початковому запиту входу")
        
    # 8. Звірка at_hash
    if access_token_raw and "at_hash" in payload:
        digest = hashlib.sha256(access_token_raw.encode('ascii')).digest()
        half_len = len(digest) // 2
        expected_at_hash = b64url_encode(digest[:half_len])
        if not hmac.compare_digest(payload["at_hash"], expected_at_hash):
            raise ValueError("Невідповідність at_hash: access_token підмінено!")
            
    return payload
```
```ts
import crypto from 'crypto';

export async function validateIdToken(
  idTokenRaw: string,
  expectedIssuer: string,
  expectedClientId: string,
  expectedNonce: string,
  jwksManager: JwksManager,
  accessTokenRaw?: string,
  clockSkewSec: number = 60
): Promise<Record<string, any>> {
  const parts = idTokenRaw.split('.');
  if (parts.length !== 3) throw new Error('Некоректний формат JWT');
  const [headerB64, payloadB64, sigB64] = parts;

  // 1. Розбір заголовка
  const header = JSON.parse(Buffer.from(headerB64, 'base64url').toString('utf8'));
  if (header.alg !== 'RS256') throw new Error(`Недозволений алгоритм: ${header.alg}`);
  if (!header.kid) throw new Error('У заголовку токена відсутній kid');

  // 2. Верифікація підпису
  const publicKey = await jwksManager.getKey(header.kid);
  const verify = crypto.createVerify('RSA-SHA256');
  verify.update(`${headerB64}.${payloadB64}`, 'ascii');
  const sigBuffer = Buffer.from(sigB64, 'base64url');
  
  const isValid = verify.verify(publicKey, sigBuffer);
  if (!isValid) throw new Error('Цифровий підпис ID-токена недійсний');

  // 3. Розбір навантаження
  const payload = JSON.parse(Buffer.from(payloadB64, 'base64url').toString('utf8'));
  const now = Math.floor(Date.now() / 1000);

  // 4. Перевірка iss
  if (payload.iss !== expectedIssuer) {
    throw new Error(`Невідповідність iss: ${payload.iss} !== ${expectedIssuer}`);
  }

  // 5. Перевірка aud
  if (typeof payload.aud === 'string') {
    if (payload.aud !== expectedClientId) throw new Error(`Невідповідність aud: ${payload.aud}`);
  } else if (Array.isArray(payload.aud)) {
    if (!payload.aud.includes(expectedClientId)) throw new Error('client_id відсутній в aud');
    if (payload.aud.length > 1 && payload.azp !== expectedClientId) {
      throw new Error('azp не збігається з client_id для множинного aud');
    }
  } else {
    throw new Error('Некоректне поле aud у токені');
  }

  // 6. Перевірка часу
  if (!payload.exp || payload.exp + clockSkewSec < now) throw new Error('Токен протерміновано (exp)');
  if (payload.iat && payload.iat - clockSkewSec > now) throw new Error('Токен із майбутнього (iat)');

  // 7. Перевірка nonce
  if (payload.nonce !== expectedNonce) throw new Error('Невідповідність nonce');

  // 8. Перевірка at_hash
  if (accessTokenRaw && payload.at_hash) {
    const hash = crypto.createHash('sha256').update(accessTokenRaw, 'ascii').digest();
    const half = hash.subarray(0, hash.length / 2);
    const expectedAtHash = half.toString('base64url');
    if (payload.at_hash !== expectedAtHash) {
      throw new Error('at_hash не відповідає access_token');
    }
  }

  return payload;
}
```
:::

## Крок 5. Запит профілю з кінцевої точки UserInfo та створення сесії

ID-токен зазвичай містить лише базові поля автентифікації (`sub`, `iss`, `aud`, `exp`). Якщо клієнт замовив розширені скоупи (наприклад, `profile`, `email`, `address`), актуальні персональні дані отримуються через авторизований запит до `userinfo_endpoint`:

:::tabs
```py
def fetch_userinfo(userinfo_endpoint: str, access_token: str) -> dict:
    req = urllib.request.Request(
        userinfo_endpoint,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "User-Agent": "OIDC-RelyingParty-Engine/1.0"
        }
    )
    with urllib.request.urlopen(req, timeout=5) as response:
        if response.status != 200:
            raise RuntimeError(f"Помилка UserInfo: HTTP {response.status}")
        return json.loads(response.read().decode('utf-8'))
```
```ts
export async function fetchUserInfo(
  userinfoEndpoint: string,
  accessToken: string
): Promise<Record<string, any>> {
  const res = await fetch(userinfoEndpoint, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
      Accept: 'application/json',
      'User-Agent': 'OIDC-RelyingParty-Engine/1.0',
    },
  });

  if (!res.ok) {
    throw new Error(`Помилка отримання UserInfo: HTTP ${res.status}`);
  }

  return res.json();
}
```
:::

Після успішного отримання профілю бекенд клієнта знаходить користувача в локальній базі за незмінним ідентифікатором `sub` (або створює новий запис) і встановлює локальну сесію з прапорцями безпеки: `HttpOnly`, `Secure`, `SameSite=Lax`.

## Крок 6. Федеративний вихід користувача (RP-Initiated Logout)

Просте видалення локальної сесійної кукі у браузері не завершує сесію на боці сервера ідентифікації. Якщо користувач знову натисне «Увійти через OpenID», провайдер виявить активну SSO-сесію і миттєво впустить його без запиту пароля.

Щоб реалізувати повний вихід із системи, клієнт формує редирект на `end_session_endpoint` провайдера відповідно до специфікації OpenID Connect RP-Initiated Logout 1.0. Запит містить два обов'язкових параметри:
* `id_token_hint` — збережений під час входу ID-токен (служить криптографічним доказом того, що саме цей клієнт ініціює вихід саме цього користувача);
* `post_logout_redirect_uri` — адреса нашого сервісу, куди провайдер поверне користувача після очищення сесії.

:::tabs
```py
def create_logout_url(
    end_session_endpoint: str,
    id_token_hint: str,
    post_logout_redirect_uri: str,
    state: str | None = None
) -> str:
    params = {
        "id_token_hint": id_token_hint,
        "post_logout_redirect_uri": post_logout_redirect_uri,
    }
    if state:
        params["state"] = state
    return f"{end_session_endpoint}?{urllib.parse.urlencode(params)}"
```
```ts
export function createLogoutUrl(
  endSessionEndpoint: string,
  idTokenHint: string,
  postLogoutRedirectUri: string,
  state?: string
): string {
  const url = new URL(endSessionEndpoint);
  url.searchParams.set('id_token_hint', idTokenHint);
  url.searchParams.set('post_logout_redirect_uri', postLogoutRedirectUri);
  if (state) {
    url.searchParams.set('state', state);
  }
  return url.toString();
}
```
:::

## Крок 7. Повний серверний контур та обробка маршрутів

Об'єднаймо всі попередні кроки у завершений сервіс на базі FastAPI (Python) та Express (TypeScript). Сервіс обслуговує три публічні маршрути автентифікації:
* `GET /auth/login` — старт процесу, генерація параметрів захисту та редирект;
* `GET /auth/callback` — прийом коду, обмін, валідація та видача сесійного cookie;
* `POST /auth/logout` — знищення локальної сесії та формування редиректу на завершення сесії в провайдера;
* `GET /api/me` — захищений ресурс, що повертає профіль автентифікованого користувача.

:::tabs
```py
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

# Ініціалізація глобальних параметрів клієнта
CLIENT_ID = "my-saas-client-id"
CLIENT_SECRET = "super-secret-key-123"
ISSUER = "https://accounts.example.com"
DISCOVERY_URL = f"{ISSUER}/.well-known/openid-configuration"
REDIRECT_URI = "https://my-app.com/auth/callback"

# Локальні сховища стану (у продакшені — Redis із TTL)
pending_states = {} # state -> { nonce, code_verifier, created_at }
user_sessions = {}  # session_id -> { sub, email, name }

# Завантажуємо JWKS URI з discovery
jwks_mgr = JwksManager(jwks_uri=f"{ISSUER}/.well-known/jwks.json")

class OidcAuthServer(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)
        
        if path == "/auth/login":
            # 1. Створення параметрів та редирект
            ctx = create_authorization_url(
                authorization_endpoint=f"{ISSUER}/authorize",
                client_id=CLIENT_ID,
                redirect_uri=REDIRECT_URI
            )
            # Зберігаємо транзитний стан на 5 хвилин
            pending_states[ctx["state"]] = {
                "nonce": ctx["nonce"],
                "code_verifier": ctx["code_verifier"],
                "created_at": time.time()
            }
            self.send_response(302)
            self.send_header("Location", ctx["auth_url"])
            self.end_headers()
            
        elif path == "/auth/callback":
            # 2. Обробка повернення з провайдера
            state = query.get("state", [None])[0]
            code = query.get("code", [None])[0]
            error = query.get("error", [None])[0]
            
            if error:
                self.send_error(400, f"Помилка авторизації: {error}")
                return
                
            if not state or state not in pending_states:
                self.send_error(403, "Недійсний або протермінований параметр state (CSRF захист)")
                return
                
            saved_ctx = pending_states.pop(state)
            
            try:
                # 3. Обмін коду на токени
                token_res = exchange_code_for_tokens(
                    token_endpoint=f"{ISSUER}/token",
                    client_id=CLIENT_ID,
                    client_secret=CLIENT_SECRET,
                    code=code,
                    code_verifier=saved_ctx["code_verifier"],
                    redirect_uri=REDIRECT_URI
                )
                
                # 4. Валідація ID-токена
                claims = validate_id_token(
                    id_token_raw=token_res["id_token"],
                    expected_issuer=ISSUER,
                    expected_client_id=CLIENT_ID,
                    expected_nonce=saved_ctx["nonce"],
                    jwks_manager=jwks_mgr,
                    access_token_raw=token_res.get("access_token")
                )
                
                # 5. Отримання профілю
                profile = {}
                if "access_token" in token_res:
                    profile = fetch_userinfo(f"{ISSUER}/userinfo", token_res["access_token"])
                    
                # 6. Створення локальної сесії
                session_id = b64url_encode(os.urandom(32))
                user_sessions[session_id] = {
                    "sub": claims["sub"],
                    "email": profile.get("email", claims.get("email", "")),
                    "name": profile.get("name", claims.get("name", "")),
                    "id_token": token_res["id_token"]
                }
                
                self.send_response(302)
                self.send_header("Set-Cookie", f"session_id={session_id}; Path=/; HttpOnly; Secure; SameSite=Lax")
                self.send_header("Location", "/dashboard")
                self.end_headers()
                
            except Exception as e:
                self.send_error(401, f"Автентифікація не вдалася: {str(e)}")
```
```ts
import express, { Request, Response } from 'express';
import cookieParser from 'cookie-parser';
import crypto from 'crypto';

const app = express();
app.use(cookieParser());
app.use(express.urlencoded({ extended: true }));

const CLIENT_ID = 'my-saas-client-id';
const CLIENT_SECRET = 'super-secret-key-123';
const ISSUER = 'https://accounts.example.com';
const REDIRECT_URI = 'https://my-app.com/auth/callback';

const pendingStates = new Map<string, { nonce: string; codeVerifier: string; createdAt: number }>();
const userSessions = new Map<string, { sub: string; email: string; name: string; idToken: string }>();

const jwksMgr = new JwksManager(`${ISSUER}/.well-known/jwks.json`);

app.get('/auth/login', (req: Request, res: Response) => {
  const ctx = createAuthorizationUrl(`${ISSUER}/authorize`, CLIENT_ID, REDIRECT_URI);
  pendingStates.set(ctx.state, {
    nonce: ctx.nonce,
    codeVerifier: ctx.codeVerifier,
    createdAt: Date.now(),
  });
  res.redirect(ctx.authUrl);
});

app.get('/auth/callback', async (req: Request, res: Response) => {
  const state = req.query.state as string;
  const code = req.query.code as string;
  const error = req.query.error as string;

  if (error) {
    return res.status(400).send(`Помилка провайдера: ${error}`);
  }

  if (!state || !pendingStates.has(state)) {
    return res.status(403).send('Недійсний або відсутній state');
  }

  const savedCtx = pendingStates.get(state)!;
  pendingStates.delete(state);

  try {
    const tokenRes = await exchangeCodeForTokens(
      `${ISSUER}/token`,
      CLIENT_ID,
      CLIENT_SECRET,
      code,
      savedCtx.codeVerifier,
      REDIRECT_URI
    );

    const claims = await validateIdToken(
      tokenRes.id_token,
      ISSUER,
      CLIENT_ID,
      savedCtx.nonce,
      jwksMgr,
      tokenRes.access_token
    );

    let profile: Record<string, any> = {};
    if (tokenRes.access_token) {
      profile = await fetchUserInfo(`${ISSUER}/userinfo`, tokenRes.access_token);
    }

    const sessionId = crypto.randomBytes(32).toString('base64url');
    userSessions.set(sessionId, {
      sub: claims.sub,
      email: profile.email || claims.email || '',
      name: profile.name || claims.name || '',
      idToken: tokenRes.id_token,
    });

    res.cookie('session_id', sessionId, {
      httpOnly: true,
      secure: true,
      sameSite: 'lax',
      path: '/',
    });
    res.redirect('/dashboard');
  } catch (err: any) {
    res.status(401).send(`Помилка валідації OIDC: ${err.message}`);
  }
});
```
:::

## Крок 8. Асинхронне завершення сесії через Back-Channel Logout

У великих розподілених системах редиректного виходу (RP-Initiated Logout) недостатньо: коли користувач тисне «Вийти» в одному корпоративному додатку або скидає сесію через службу безпеки, провайдер повинен сповістити всі інші підключені додатки.

Для цього використовується специфікація **OpenID Connect Back-Channel Logout 1.0**:
1. Сервер провайдера самостійно надсилає прямий HTTP POST-запит на кінцеву точку клієнта `/auth/backchannel-logout`.
2. Тіло запиту містить параметр `logout_token` — підписаний провайдером JWT.
3. Токен виходу містить твердження `sub` (кого вилогувати) або `sid` (конкретний ідентифікатор сесії у провайдера), а також маркер події:

```json
{
  "iss": "https://accounts.example.com",
  "sub": "usr-98124",
  "aud": "my-saas-client-id",
  "iat": 1735732800,
  "jti": "b0a23f-4e91-...",
  "events": {
    "http://schemas.openid.net/event/backchannel-logout": {}
  }
}
```

Клієнт перевіряє підпис `logout_token` через `JwksManager`, переконується у відсутності поля `nonce` (специфікація прямо забороняє `nonce` у токенах виходу, щоб унеможливити плутанину з ID-токенами), знаходить усі локальні сесії відповідного `sub` та миттєво видаляє їх зі сховища.

:::tabs
```py
def handle_backchannel_logout(
    logout_token_raw: str,
    expected_issuer: str,
    expected_client_id: str,
    jwks_manager: JwksManager
) -> str:
    """Обробка Logout Token та повернення sub користувача для інвалідації сесій."""
    parts = logout_token_raw.split('.')
    if len(parts) != 3:
        raise ValueError("Некоректний формат Logout Token")
        
    header = json.loads(JwksManager._b64url_decode(parts[0]).decode('utf-8'))
    public_key = jwks_manager.get_key(header["kid"])
    
    # Верифікація підпису
    signed_data = f"{parts[0]}.{parts[1]}".encode('ascii')
    signature = JwksManager._b64url_decode(parts[2])
    public_key.verify(signature, signed_data, padding.PKCS1v15(), hashes.SHA256())
    
    payload = json.loads(JwksManager._b64url_decode(parts[1]).decode('utf-8'))
    
    # Перевірка обов'язкових інваріантів Logout Token
    if payload.get("iss") != expected_issuer:
        raise ValueError("Невідповідність iss у Logout Token")
        
    aud = payload.get("aud")
    if aud != expected_client_id and (isinstance(aud, list) and expected_client_id not in aud):
        raise ValueError("Невідповідність aud у Logout Token")
        
    if "nonce" in payload:
        raise ValueError("Logout Token містить заборонене поле nonce!")
        
    events = payload.get("events", {})
    if "http://schemas.openid.net/event/backchannel-logout" not in events:
        raise ValueError("Відсутній обов'язковий маркер події backchannel-logout")
        
    sub = payload.get("sub")
    if not sub and not payload.get("sid"):
        raise ValueError("Logout Token зобов'язаний містити sub або sid")
        
    return sub
```
```ts
export async function handleBackchannelLogout(
  logoutTokenRaw: string,
  expectedIssuer: string,
  expectedClientId: string,
  jwksManager: JwksManager
): Promise<string> {
  const parts = logoutTokenRaw.split('.');
  if (parts.length !== 3) throw new Error('Некоректний формат Logout Token');

  const header = JSON.parse(Buffer.from(parts[0], 'base64url').toString('utf8'));
  const publicKey = await jwksManager.getKey(header.kid);

  const verify = crypto.createVerify('RSA-SHA256');
  verify.update(`${parts[0]}.${parts[1]}`, 'ascii');
  const isValid = verify.verify(publicKey, Buffer.from(parts[2], 'base64url'));
  if (!isValid) throw new Error('Підпис Logout Token недійсний');

  const payload = JSON.parse(Buffer.from(parts[1], 'base64url').toString('utf8'));

  if (payload.iss !== expectedIssuer) throw new Error('Невідповідність iss у Logout Token');
  if (payload.aud !== expectedClientId && !(Array.isArray(payload.aud) && payload.aud.includes(expectedClientId))) {
    throw new Error('Невідповідність aud у Logout Token');
  }
  if (payload.nonce) throw new Error('Logout Token не може містити nonce');
  if (!payload.events || !payload.events['http://schemas.openid.net/event/backchannel-logout']) {
    throw new Error('Відсутній маркер події backchannel-logout');
  }

  const sub = payload.sub || payload.sid;
  if (!sub) throw new Error('Logout Token не містить sub або sid');
  return sub;
}
```
:::

## Крок 9. Низькорівнева валідація підпису токена на C++ з OpenSSL

У високопродуктивних мікросервісних шлюзах (API Gateway) або вбудованих системах розбір і криптографічна перевірка токенів виконується на C++ без використання інтерпретованих мов.

Для цього використовується бібліотека OpenSSL (або BoringSSL). Відновлення публічного ключа RSA з компонентів `n` (модуль) та `e` (експонента), отриманих із JWKS, та верифікація підпису RS256 за допомогою універсального інтерфейсу `EVP_DigestVerify` реалізується через строгі RAII-обгортки.

:::tabs
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <memory>
#include <stdexcept>
#include <openssl/evp.h>
#include <openssl/rsa.h>
#include <openssl/bio.h>
#include <openssl/buffer.h>
#include <openssl/param_build.h>
#include <openssl/core_names.h>

// RAII-обгортки для ресурсів OpenSSL 3.0
struct EvpPkeyDeleter { void operator()(EVP_PKEY* p) const { EVP_PKEY_free(p); } };
struct EvpMdCtxDeleter { void operator()(EVP_MD_CTX* p) const { EVP_MD_CTX_free(p); } };
struct OsslParamBldDeleter { void operator()(OSSL_PARAM_BLD* p) const { OSSL_PARAM_BLD_free(p); } };
struct OsslParamDeleter { void operator()(OSSL_PARAM* p) const { OSSL_PARAM_free(p); } };

using ScopedPkey = std::unique_ptr<EVP_PKEY, EvpPkeyDeleter>;
using ScopedMdCtx = std::unique_ptr<EVP_MD_CTX, EvpMdCtxDeleter>;

// Допоміжна функція декодування Base64URL
std::vector<uint8_t> base64url_decode(std::string_view input) {
    std::string b64(input);
    for (char& c : b64) {
        if (c == '-') c = '+';
        else if (c == '_') c = '/';
    }
    while (b64.size() % 4 != 0) {
        b64.push_back('=');
    }

    std::vector<uint8_t> out(b64.size());
    BIO* bio = BIO_new_mem_buf(b64.data(), static_cast<int>(b64.size()));
    BIO* b64_filter = BIO_new(BIO_f_base64());
    BIO_set_flags(b64_filter, BIO_FLAGS_BASE64_NO_NL);
    bio = BIO_push(b64_filter, bio);

    int decoded_len = BIO_read(bio, out.data(), static_cast<int>(out.size()));
    BIO_free_all(bio);

    if (decoded_len < 0) {
        throw std::runtime_error("Помилка декодування Base64URL");
    }
    out.resize(decoded_len);
    return out;
}

// Побудова EVP_PKEY з публічних компонентів RSA (OpenSSL 3.0+)
ScopedPkey create_rsa_public_key(std::string_view n_b64url, std::string_view e_b64url) {
    auto n_bytes = base64url_decode(n_b64url);
    auto e_bytes = base64url_decode(e_b64url);

    std::unique_ptr<OSSL_PARAM_BLD, OsslParamBldDeleter> bld(OSSL_PARAM_BLD_new());
    if (!bld) throw std::runtime_error("Не вдалося створити OSSL_PARAM_BLD");

    BIGNUM* n_bn = BN_bin2bn(n_bytes.data(), static_cast<int>(n_bytes.size()), nullptr);
    BIGNUM* e_bn = BN_bin2bn(e_bytes.data(), static_cast<int>(e_bytes.size()), nullptr);

    OSSL_PARAM_BLD_push_BN(bld.get(), OSSL_PKEY_PARAM_RSA_N, n_bn);
    OSSL_PARAM_BLD_push_BN(bld.get(), OSSL_PKEY_PARAM_RSA_E, e_bn);
    BN_free(n_bn);
    BN_free(e_bn);

    std::unique_ptr<OSSL_PARAM, OsslParamDeleter> params(OSSL_PARAM_BLD_to_param(bld.get()));
    if (!params) throw std::runtime_error("Не вдалося згенерувати OSSL_PARAM");

    EVP_PKEY_CTX* ctx = EVP_PKEY_CTX_new_from_name(nullptr, "RSA", nullptr);
    if (!ctx) throw std::runtime_error("Помилка створення EVP_PKEY_CTX");

    EVP_PKEY* pkey_raw = nullptr;
    EVP_PKEY_fromdata_init(ctx);
    if (EVP_PKEY_fromdata(ctx, &pkey_raw, EVP_PKEY_PUBLIC_KEY, params.get()) <= 0) {
        EVP_PKEY_CTX_free(ctx);
        throw std::runtime_error("Помилка створення EVP_PKEY з параметрів RSA");
    }
    EVP_PKEY_CTX_free(ctx);

    return ScopedPkey(pkey_raw);
}

// Верифікація підпису RS256 для підписаного блоку JWT
bool verify_rs256_signature(
    std::string_view signed_data,
    std::string_view signature_b64url,
    EVP_PKEY* public_key
) {
    auto signature = base64url_decode(signature_b64url);

    ScopedMdCtx md_ctx(EVP_MD_CTX_new());
    if (!md_ctx) return false;

    if (EVP_DigestVerifyInit(md_ctx.get(), nullptr, EVP_sha256(), nullptr, public_key) <= 0) {
        return false;
    }

    if (EVP_DigestVerifyUpdate(md_ctx.get(), signed_data.data(), signed_data.size()) <= 0) {
        return false;
    }

    int rc = EVP_DigestVerifyFinal(md_ctx.get(), signature.data(), signature.size());
    return (rc == 1);
}
```
:::

## Інженерні пастки та правила надійності

1. **Захист від підміни алгоритму (Algorithm Confusion).** Ніколи не дозволяйте вхідному токену визначати криптографічний алгоритм перевірки. Якщо очікується асиметричний підпис RSA, жорстко вимагайте `alg == "RS256"` до початку будь-яких криптографічних операцій.
2. **Контроль розсинхрону годинників (Clock Skew).** Час на сервері клієнта та сервері провайдера може відрізнятися на кілька десятків секунд через затримки NTP. Завжди застосовуйте невеликий допуск (60–120 секунд) при порівнянні `exp` та `iat`.
3. **Строга відповідність URL емітента.** Поле `iss` має порівнюватися з точністю до символу. Рядки `https://accounts.google.com` та `https://accounts.google.com/` (із кінцевим слешем) вважаються різними емітентами.
4. **Транзитний стан у сховищі.** Значення `state`, `nonce` та `code_verifier` повинні мати короткий час життя (TTL 5–10 хвилин) і автоматично видалятися відразу після одноразової перевірки на маршруті `/callback`.
5. **Запобігання витоку токенів у логах.** `access_token` та `id_token` є конфіденційними мандатами. Будь-яке логування HTTP-запитів у проміжних шарах (middleware) зобов'язане маскувати заголовки `Authorization` та тіла відповідей точки `/token`.
6. **Ротація сесійних ідентифікаторів.** Після успішного завершення OIDC-входу старий сесійний cookie (якщо він існував до логіну) має бути знищений, а новий згенерований із використанням криптографічно стійкого CSPRNG, що запобігає атакам фіксації сесії (Session Fixation).

## Стійкість до відмов: політика повторних спроб (Exponential Backoff з джитером)

У високонавантажених розподілених системах зовнішні виклики до точки `/token` провайдера можуть зазнавати тимчасових збоїв через сплески навантаження, мережеві перепідключення або перезавантаження серверів IdP (HTTP 502/503/504, TCP Reset).

Сліпе повторення однакових запитів усіма клієнтами одночасно призводить до катастрофічного ефекту «громоподібного стада» (Thundering Herd). Для запобігання цьому клієнтський рівень застосовує експоненційний відступ із випадковим розкидом (Full Jitter):

```
T_sleep = random( 0, min( T_max, T_base * 2^attempt ) )
```

### Клієнтська автентифікація через `private_key_jwt`

Для серверних додатків використання статичного пароля `client_secret` створює ризик компрометації при витоку конфігураційних файлів чи змінних оточення. Стандарт OIDC Core визначає метод `private_key_jwt` (RFC 7523):

1. Клієнт генерує власну асиметричну пару ключів (наприклад, RSA-2048).
2. Відкритий ключ публікується на публічній адресі `jwks_uri` клієнта або реєструється в кабінеті IdP.
3. При зверненні до точки `/token` клієнт створює короткоживучий (час життя 1–2 хвилини) JWT:
   * `iss`: ідентифікатор клієнта `client_id`;
   * `sub`: ідентифікатор клієнта `client_id`;
   * `aud`: URL точки `/token` провайдера;
   * `jti`: унікальний випадковий UUID (запобігає повторному відтворенню);
   * `exp`: поточний час + 60 секунд.
4. Клієнт підписує цей JWT своїм закритим ключем і передає в тілі запиту як `client_assertion` із типом `client_assertion_type=urn:ietf:params:oauth:client-assertion-type:jwt-bearer`.

Провайдер перевіряє підпис відкритим ключем клієнта і звіряє `aud` та `jti`. Навіть якщо цей токен буде перехоплений у логах проксі, він стає недійсним уже через 60 секунд і не може бути використаний повторно завдяки унікальному `jti`.

## Архітектура розподіленого сесійного сховища (Redis State Store)

У багатосерверному горизонтально масштабованому кластері клієнтські запити можуть потрапляти на різні екземпляри додатку. Збереження параметрів `state`, `nonce` та `code_verifier` в оперативній пам'яті одного процесу спричинить збій авторизації, якщо зворотний виклик `/callback` прийде на інший сервер.

Для забезпечення безвідмовної роботи в продакшені сесійний шар організовується на базі розподіленого кешу (Redis):

1. **Ініціалізація входу:**
   * Ключ: `oidc:flow:{state}`
   * Значення (JSON): `{"nonce": "...", "code_verifier": "...", "created_at": 1735732800}`
   * Час життя (TTL): 300 секунд (5 хвилин).
2. **Атомарне вилучення на маршруті `/callback`:**
   * Використовується атомарна команда `GETDEL` (Redis 6.2+) або Lua-скрипт. Це гарантує одноразове використання транзитного стану: якщо зловмисник спробує надіслати повторний запит із тим самим `state`, ключ уже буде відсутній, і спроба входу буде відхилена.
3. **Збереження активної сесії користувача:**
   * Ключ сесії: `session:{session_id}` -> дані профілю, `sub`, `exp`, `access_token`.
   * Індекс користувача: `user:sessions:{sub}` -> Redis Set із переліком активних `session_id`.
4. **Обробка Back-Channel Logout:**
   * Отримавши `logout_token` із полем `sub`, клієнтський бекенд виконує запит до `user:sessions:{sub}`, отримує всі `session_id` цього користувача та одним викликом `UNLINK` видаляє їх зі сховища, миттєво завершуючи всі паралельні сесії користувача на всіх пристроях.

## Стратегія кешування метаданих Discovery (Stale-While-Revalidate)

Документ `/.well-known/openid-configuration` містить статичні або рідко змінювані налаштування. Виконання HTTP-запиту до Discovery-ендпоінту на кожен вхід користувача створює непотрібну затримку (latency) у 50–200 мс і робить систему залежною від короткочасних мережевих коливань.

Рекомендована архітектурна стратегія для Relying Party:
* Метадані завантажуються під час ініціалізації процесу та зберігаються в локальній пам'яті з TTL 24 години;
* При настанні терміну інвалідації застосовується патерн **stale-while-revalidate**: клієнт продовжує обслуговувати поточні запити на основі наявного кешу, одночасно запускаючи фоновий асинхронний запит на оновлення метаданих;
* Якщо фоновий запит зазнає невдачі через недоступність мережі IdP, клієнт збільшує час використання застарілого кешу ще на 1 годину та реєструє попередження в системі моніторингу без переривання обслуговування користувачів.






