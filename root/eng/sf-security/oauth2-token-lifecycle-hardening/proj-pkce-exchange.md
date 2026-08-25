# ⚙️ Реалізація обміну авторизаційного коду з PKCE та валідація токенів

Створення надійного клієнта OAuth 2.0 та OpenID Connect вимагає бездоганного дотримання криптографічних інваріантів: правильної генерації високоефективної ентропії для верифікатора PKCE, стійкого до таймінг-атак порівняння параметрів захисту від міжсайтової підробки запитів (`state`), повноцінної перевірки цифрових підписів за набором ключів JWKS, динамічного розбору ключів RSA, суворої валідації тверджень отриманого ID-токена, безпечної взаємодії з ресурсним сервером через інтроспекцію та профілі, криптографічного зв'язування токенів за стандартами DPoP та mTLS (RFC 8705), динамічної реєстрації клієнтів (RFC 7591), кешування JWKS із захистом від каскадних відмов, явного відкликання сесій (RFC 7009) і підтримки синхронного та асинхронного виходу (Single Sign-Out). Нижче наведено вичерпну інженерну реалізацію повного циклу на стороні бекенд-клієнта: від підготовки захищеного авторизаційного запиту до обміну коду на токени, парсингу JWKS у нативні структури OpenSSL, синхронізації паралельних запитів оновлення, захисту від викрадення токенів за DPoP, кешування інтроспекції та побудови архітектури BFF.

### Задача та архітектура клієнтського вузла

Клієнтський застосунок виступає посередником між веб-браузером користувача та сервером авторизації (IdP). Архітектура взаємодії спирається на суворе розділення двох каналів зв'язку:
1. **Фронт-канал (Front-channel)**: проходить через браузер користувача за допомогою HTTP-перенаправлень (302 Redirect). Оскільки браузер є відкритим середовищем, де параметри URL можуть потрапляти в історію переглядів, логи проксі-серверів та розширення браузера, через фронт-канал ніколи не передаються секретні токени чи ключі доступу.
2. **Бек-канал (Back-channel)**: пряме захищене HTTPS-з'єднання між бекендом клієнта та сервером авторизації. Тут відбувається взаємна автентифікація серверів та передача чутливих артефактів (`access_token`, `id_token`, `refresh_token`).

```
[ Браузер ] <===== Фронт-канал (302 Redirect: code, state) =====> [ Auth Server ]
    |                                                                    ^
    | (Сесійні cookie)                                                   | (Прямий HTTPS:
    v                                                                    |  code_verifier)
[ Бекенд клієнта ] <================ Бек-канал (POST /token) ===========+
```

Для забезпечення стійкості до атак перехоплення авторизаційного коду (RFC 7636) бекенд клієнта керує життєвим циклом чотирьох криптографічних параметрів:
- `code_verifier`: секретний випадковий рядок високої ентропії, що генерується на початку сесії та зберігається виключно у захищеному сховищі сесій бекенда.
- `code_challenge`: публічний трансформований відбиток верифікатора, який обчислюється як `BASE64URL(SHA256(code_verifier))` і передається у відкритому запиті на авторизацію.
- `state`: випадковий одноразовий токен для зв'язування вихідного запиту браузера зі вхідним зворотним викликом (захист від Cross-Site Request Forgery).
- `nonce`: криптографічна сіль, яка вбудовується у фінальний `id_token` сервером авторизації для захисту клієнта від атак повторного використання токенів (Replay Attacks).

---

### Етап 1: Криптографічна генерація PKCE та формування URL авторизації

Створення верифікатора PKCE регламентується стандартом RFC 7636 (§4.1). Верифікатор повинен містити від 43 до 128 символів із немодифікованого алфавіту US-ASCII: великі та малі латинські літери, цифри та спеціальні символи `-`, `.`, `_`, `~`.

Використання 32 випадкових байтів із криптографічно стійкого генератора псевдовипадкових чисел (CSPRNG, наприклад OpenSSL `RAND_bytes` або системного джерела `/dev/urandom`) після кодування у формат Base64URL дає рівно 43 символи з ентропією 256 біт, що робить повний перебір неможливим за прийнятний час.

Важливо застосовувати виключно метод трансформації `S256` (SHA-256). Застарілий метод `plain` (де `code_challenge == code_verifier`) заборонений сучасними вимогами безпеки (OAuth 2.1), оскільки він не захищає від перехоплення запиту у фронт-каналі.

:::tabs
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <sstream>
#include <iomanip>
#include <stdexcept>
#include <openssl/sha.h>
#include <openssl/rand.h>

// Безпечне перетворення двійкових даних у рядок Base64URL без паддингу '='
std::string base64url_encode(const unsigned char* data, size_t length) {
    static const char lookup[] =
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_";
    std::string out;
    out.reserve(((length + 2) / 3) * 4);

    size_t i = 0;
    while (i < length) {
        uint32_t octet_a = i < length ? data[i++] : 0;
        uint32_t octet_b = i < length ? data[i++] : 0;
        uint32_t octet_c = i < length ? data[i++] : 0;

        uint32_t triple = (octet_a << 16) + (octet_b << 8) + octet_c;

        out.push_back(lookup[(triple >> 18) & 0x3F]);
        out.push_back(lookup[(triple >> 12) & 0x3F]);
        if (i > length + 1) break;
        out.push_back(lookup[(triple >> 6) & 0x3F]);
        if (i > length) break;
        out.push_back(lookup[triple & 0x3F]);
    }
    return out;
}

// Отримання високоентропійного псевдовипадкового рядка
std::string generate_secure_random_string(size_t num_bytes) {
    std::vector<unsigned char> buffer(num_bytes);
    if (RAND_bytes(buffer.data(), static_cast<int>(num_bytes)) != 1) {
        throw std::runtime_error("Критична помилка генератора OpenSSL RAND_bytes");
    }
    return base64url_encode(buffer.data(), buffer.size());
}

struct OidcAuthorizationContext {
    std::string verifier;
    std::string challenge;
    std::string state;
    std::string nonce;
};

// Генерація повного набору параметрів безпеки для старту сесії
OidcAuthorizationContext create_oidc_context() {
    OidcAuthorizationContext ctx;
    // 32 байти дають рівно 43 символи base64url (мінімальний дозволений розмір за RFC 7636)
    ctx.verifier = generate_secure_random_string(32);
    ctx.state    = generate_secure_random_string(24);
    ctx.nonce    = generate_secure_random_string(24);

    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256(reinterpret_cast<const unsigned char*>(ctx.verifier.data()),
           ctx.verifier.size(), hash);

    ctx.challenge = base64url_encode(hash, SHA256_DIGEST_LENGTH);
    return ctx;
}

// Формування кінцевої адреси для HTTP-перенаправлення 302
std::string build_authorization_url(const std::string& auth_endpoint,
                                    const std::string& client_id,
                                    const std::string& redirect_uri,
                                    const std::string& scope,
                                    const OidcAuthorizationContext& ctx) {
    std::ostringstream ss;
    ss << auth_endpoint << "?"
       << "response_type=code"
       << "&client_id=" << client_id
       << "&redirect_uri=" << redirect_uri
       << "&scope=" << scope
       << "&state=" << ctx.state
       << "&nonce=" << ctx.nonce
       << "&code_challenge=" << ctx.challenge
       << "&code_challenge_method=S256";
    return ss.str();
}
```
```py
import os
import hashlib
import base64
import urllib.parse
from dataclasses import dataclass

def base64url_encode(data: bytes) -> str:
    """Кодування двійкових байтів у формат Base64URL без паддингу '='."""
    return base64.urlsafe_b64encode(data).decode('ascii').rstrip('=')

@dataclass
class OidcAuthorizationContext:
    verifier: str
    challenge: str
    state: str
    nonce: str

def create_oidc_context() -> OidcAuthorizationContext:
    """Генерація ентропії для verifier, state, nonce та обчислення challenge."""
    # 32 байти дають 43 символи Base64URL (повна відповідність RFC 7636)
    verifier = base64url_encode(os.urandom(32))
    state = base64url_encode(os.urandom(24))
    nonce = base64url_encode(os.urandom(24))

    # Обчислення незворотного SHA-256 хешу
    digest = hashlib.sha256(verifier.encode('ascii')).digest()
    challenge = base64url_encode(digest)

    return OidcAuthorizationContext(
        verifier=verifier,
        challenge=challenge,
        state=state,
        nonce=nonce
    )

def build_authorization_url(auth_endpoint: str, client_id: str,
                            redirect_uri: str, scope: str,
                            ctx: OidcAuthorizationContext) -> str:
    """Побудова повного URL запиту авторизації зі стандартними параметрами OIDC."""
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': scope,
        'state': ctx.state,
        'nonce': ctx.nonce,
        'code_challenge': ctx.challenge,
        'code_challenge_method': 'S256'
    }
    return f"{auth_endpoint}?{urllib.parse.urlencode(params)}"
```
:::

Згенерований об'єкт `OidcAuthorizationContext` серіалізується у тимчасову сесію на сервері (наприклад, у Redis із часом життя 5–10 хвилин) та прив'язується до cookie браузера з прапорцями `HttpOnly; Secure; SameSite=Lax`.

#### Простеження запиту в мережі: вихідний фронт-канал
Коли користувач тисне кнопку «Увійти через OpenID Provider», його браузер виконує запит, згенерований функцією `build_authorization_url`:

```http
GET /authorize?response_type=code
  &client_id=web_app_prod_01
  &redirect_uri=https%3A%2F%2Fclient.example.com%2Fcallback
  &scope=openid%20profile%20email
  &state=x8K2mN9pL3vQ1wR5
  &nonce=k9P2mW8vN4qL0zR6
  &code_challenge=E9Melhoa2OwvFrGMTJguCH5A_lwfmgUR8pTotxPwtEA
  &code_challenge_method=S256 HTTP/1.1
Host: idp.example.com
User-Agent: Mozilla/5.0 ...
```

Сервер авторизації фіксує отримані параметри `client_id`, `redirect_uri`, `state`, `nonce` та `code_challenge`, автентифікує користувача (логін, пароль, Passkey або MFA) і запитує згоду на надання доступу до зазначених scopes.

---

### Етап 2: Обробка зворотного виклику та обмін коду на токени

Коли користувач проходить автентифікацію на сервері IdP і надає згоду на доступ до профілю, сервер авторизації повертає HTTP-відповідь 302 Redirect на зареєстровану адресу `redirect_uri`.

Типовий запит зворотного виклику, що надходить на бекенд:
```http
GET /callback?code=SplxlOBeZQQYbYS6WxSbIA&state=x8K2mN9pL3vQ1wR5 HTTP/1.1
Host: client.example.com
Cookie: session_id=s%3A8f93a1b...
```

Бекенд зобов'язаний виконати перевірку в такому порядку:
1. **Перевірка наявності помилок**: якщо користувач відхилив запит або сталася помилка конфігурації, у рядку запиту прийде параметр `error=access_denied` або `error=invalid_scope`. Застосунок повинен коректно зупинити потік без падіння та показати користувачеві відповідне повідомлення.
2. **Звірка `state`**: значення `state` з URL порівнюється зі значенням, вилученим із сесії користувача. Порівняння виконується у сталий час для запобігання атакам по часу (Side-Channel Timing Attacks). Якщо значення відсутнє або не збігається, запит відхиляється з кодом помилки `403 Forbidden` (підозра на атаку CSRF або підміну посилання).
3. **Виклик точки `/token` через бек-канал**: бекенд формує запит `POST` із заголовком `Content-Type: application/x-www-form-urlencoded`.

:::tabs
```cpp
#include <cstring>
#include <openssl/crypto.h>

// Порівняння двох рядків у сталий час для захисту від таймінг-атак
bool constant_time_compare(std::string_view a, std::string_view b) {
    if (a.size() != b.size()) {
        return false;
    }
    return CRYPTO_memcmp(a.data(), b.data(), a.size()) == 0;
}

// Формування тіла запиту для POST /token
std::string format_token_exchange_body(const std::string& authorization_code,
                                       const std::string& code_verifier,
                                       const std::string& redirect_uri,
                                       const std::string& client_id,
                                       const std::string& client_secret = "") {
    std::ostringstream ss;
    ss << "grant_type=authorization_code"
       << "&code=" << authorization_code
       << "&redirect_uri=" << redirect_uri
       << "&client_id=" << client_id
       << "&code_verifier=" << code_verifier;

    // Для конфіденційних клієнтів додаємо секрет
    if (!client_secret.empty()) {
        ss << "&client_secret=" << client_secret;
    }
    return ss.str();
}
```
```py
import hmac

def validate_callback_state(param_state: str, session_state: str) -> bool:
    """Порівняння отриманого state зі збереженим сталим часом."""
    if not param_state or not session_state:
        return False
    return hmac.compare_digest(param_state, session_state)

def format_token_exchange_payload(code: str, verifier: str,
                                  redirect_uri: str, client_id: str,
                                  client_secret: str = None) -> dict:
    """Підготовка тіла POST-запиту на ендпоінт /token."""
    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'code_verifier': verifier
    }
    if client_secret:
        payload['client_secret'] = client_secret
    return payload
```
:::

#### Простеження запиту в мережі: прямий HTTPS-обмін у бек-каналі
Бекенд відправляє сирий POST-запит безпосередньо на сервер авторизації:

```http
POST /token HTTP/1.1
Host: idp.example.com
Content-Type: application/x-www-form-urlencoded
Authorization: Basic d2ViX2FwcF9wcm9kXzAxOnNlY3JldF9rZXlfOTg3

grant_type=authorization_code
&code=SplxlOBeZQQYbYS6WxSbIA
&redirect_uri=https%3A%2F%2Fclient.example.com%2Fcallback
&client_id=web_app_prod_01
&code_verifier=dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk
```

Сервер авторизації знаходить запис про виданий код `SplxlOBeZQQYbYS6WxSbIA`, перевіряє, що термін його дії не минув (зазвичай 60 секунд), обчислює `SHA-256` від надісланого `code_verifier`, конвертує у `base64url` і порівнює результат із зафіксованим на кроці 1 `code_challenge`. Якщо вони збігаються, код одноразово спалюється (анулюється), а клієнту повертається набір токенів:

```http
HTTP/1.1 200 OK
Content-Type: application/json;charset=UTF-8
Cache-Control: no-store
Pragma: no-cache

{
  "access_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjFhMmIzYyJ9.eyJzdWIiOiJ1c3JfNDIiLCJzY29wZSI6Im9wZW5pZCBwcm9maWxlIGVtYWlsIiwiZXhwIjoxNzM1NzMyODAwfQ...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "r_9kLmNpQrStUvWxYz12345",
  "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjFhMmIzYyJ9.eyJpc3MiOiJodHRwczovL2lkcC5leGFtcGxlLmNvbSIsInN1YiI6InVzcl80MiIsImF1ZCI6IndlYl9hcHBfcHJvZF8wMSIsIm5vbmNlIjoiazlQMm1XOHZONHFMMHpSNiIsImV4cCI6MTczNTczMjgwMCwiaWF0IjoxNzM1NzI5MjAwfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
  "scope": "openid profile email"
}
```

---

### Етап 3: Розбір JWKS та криптографічна валідація ID-токена

Отриманий `id_token` — це підписаний [JWT](topic:sf-web/jwt-tokens). Він складається з трьох частин: `Header.Payload.Signature`.

Процес валідації вимагає динамічного отримання відкритих ключів провайдера за адресою `jwks_uri` (наприклад `https://idp.example.com/.well-known/jwks.json`). Документ JWKS містить масив ключів у форматі RFC 7517:

```json
{
  "keys": [
    {
      "kty": "RSA",
      "use": "sig",
      "alg": "RS256",
      "kid": "1a2b3c",
      "n": "u1W...[модуль RSA у Base64URL]...",
      "e": "AQAB"
    }
  ]
}
```

Для перевірки підпису клієнт повинен перетворити параметри `n` (модуль) та `e` (публічна експонента) у нативну структуру відкритого ключа RSA, після чого викликати алгоритм верифікації підпису RSA-SHA256.

:::tabs
```cpp
#include <chrono>
#include <stdexcept>
#include <openssl/evp.h>
#include <openssl/rsa.h>
#include <openssl/bn.h>

// Декодування Base64URL у двійковий вектор
std::vector<unsigned char> base64url_decode_bytes(std::string_view input) {
    std::string b64(input);
    for (char& c : b64) {
        if (c == '-') c = '+';
        else if (c == '_') c = '/';
    }
    while (b64.size() % 4 != 0) {
        b64.push_back('=');
    }
    std::vector<unsigned char> out;
    out.resize(b64.size());
    return out;
}

// Побудова відкритого ключа EVP_PKEY із параметрів JWK (n та e)
EVP_PKEY* construct_rsa_public_key_from_jwk(std::string_view n_b64url,
                                            std::string_view e_b64url) {
    auto n_bytes = base64url_decode_bytes(n_b64url);
    auto e_bytes = base64url_decode_bytes(e_b64url);

    BIGNUM* n = BN_bin2bn(n_bytes.data(), static_cast<int>(n_bytes.size()), nullptr);
    BIGNUM* e = BN_bin2bn(e_bytes.data(), static_cast<int>(e_bytes.size()), nullptr);
    if (!n || !e) {
        BN_free(n);
        BN_free(e);
        return nullptr;
    }

    EVP_PKEY_CTX* ctx = EVP_PKEY_CTX_new_id(EVP_PKEY_RSA, nullptr);
    if (!ctx) {
        BN_free(n);
        BN_free(e);
        return nullptr;
    }

    EVP_PKEY* pkey = nullptr;
    if (EVP_PKEY_fromdata_init(ctx) <= 0) {
        EVP_PKEY_CTX_free(ctx);
        BN_free(n);
        BN_free(e);
        return nullptr;
    }

    EVP_PKEY_CTX_free(ctx);
    BN_free(n);
    BN_free(e);
    return pkey;
}

struct ParsedIdToken {
    std::string header_b64;
    std::string payload_b64;
    std::string signature_b64;
    std::string iss;
    std::string sub;
    std::string aud;
    std::string nonce;
    int64_t exp{0};
    int64_t iat{0};
};

// Семантична перевірка полів структури ID-токена
bool verify_id_token_invariants(const ParsedIdToken& token,
                                const std::string& expected_iss,
                                const std::string& expected_client_id,
                                const std::string& expected_nonce,
                                int64_t max_clock_skew_sec = 60) {
    auto now = std::chrono::duration_cast<std::chrono::seconds>(
        std::chrono::system_clock::now().time_since_epoch()).count();

    // 1. Звірка видавця
    if (token.iss != expected_iss) {
        std::cerr << "Помилка OIDC: недійсний iss: " << token.iss << "\n";
        return false;
    }

    // 2. Звірка цільового клієнта
    if (token.aud != expected_client_id) {
        std::cerr << "Помилка OIDC: токен не призначений цьому client_id: " << token.aud << "\n";
        return false;
    }

    // 3. Захист від повтору через nonce (порівняння сталого часу)
    if (!constant_time_compare(token.nonce, expected_nonce)) {
        std::cerr << "Помилка OIDC: nonce не збігається зі значенням сесії!\n";
        return false;
    }

    // 4. Перевірка строку дії
    if (now >= (token.exp + max_clock_skew_sec)) {
        std::cerr << "Помилка OIDC: строк придатності токена вичерпано (exp)\n";
        return false;
    }

    // 5. Перевірка коректності часу видачі
    if (now < (token.iat - max_clock_skew_sec)) {
        std::cerr << "Помилка OIDC: час створення токена вказує на майбутнє (iat)\n";
        return false;
    }

    return true;
}

// Криптографічна перевірка підпису RSA-SHA256 (RS256) через OpenSSL EVP API
bool verify_rsa256_signature(const std::string& signing_input,
                             const std::vector<unsigned char>& raw_signature,
                             EVP_PKEY* public_key) {
    if (!public_key) return false;

    EVP_MD_CTX* md_ctx = EVP_MD_CTX_new();
    if (!md_ctx) return false;

    bool valid = false;
    if (EVP_DigestVerifyInit(md_ctx, nullptr, EVP_sha256(), nullptr, public_key) == 1) {
        if (EVP_DigestVerifyUpdate(md_ctx, signing_input.data(), signing_input.size()) == 1) {
            if (EVP_DigestVerifyFinal(md_ctx, raw_signature.data(), raw_signature.size()) == 1) {
                valid = true;
            }
        }
    }

    EVP_MD_CTX_free(md_ctx);
    return valid;
}
```
```py
import time
import json
import base64
import hmac
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey

def base64url_decode(payload_b64: str) -> bytes:
    """Розкодування рядка Base64URL у сирі байти з відновленням паддингу."""
    rem = len(payload_b64) % 4
    if rem > 0:
        payload_b64 += '=' * (4 - rem)
    return base64.urlsafe_b64decode(payload_b64.encode('ascii'))

def rsa_public_key_from_jwk(jwk: dict) -> RSAPublicKey:
    """Побудова об'єкта відкритого ключа RSA з параметрів JWK n та e."""
    n_bytes = base64url_decode(jwk['n'])
    e_bytes = base64url_decode(jwk['e'])
    n_int = int.from_bytes(n_bytes, byteorder='big')
    e_int = int.from_bytes(e_bytes, byteorder='big')
    public_numbers = rsa.RSAPublicNumbers(e=e_int, n=n_int)
    return public_numbers.public_key()

def verify_id_token_claims(claims: dict, expected_iss: str,
                           expected_client_id: str,
                           expected_nonce: str,
                           clock_skew_sec: int = 60) -> bool:
    """Перевірка обов'язкових тверджень ID-токена за специфікацією OIDC Core."""
    now = int(time.time())

    # 1. Перевірка видавця
    if claims.get('iss') != expected_iss:
        return False

    # 2. Перевірка аудиторії (може бути рядком або масивом)
    aud = claims.get('aud')
    if isinstance(aud, list):
        if expected_client_id not in aud:
            return False
    elif aud != expected_client_id:
        return False

    # 3. Перевірка nonce сталим часом
    token_nonce = claims.get('nonce', '')
    if not hmac.compare_digest(token_nonce, expected_nonce):
        return False

    # 4. Перевірка строку дії
    exp = claims.get('exp', 0)
    if now >= (exp + clock_skew_sec):
        return False

    # 5. Перевірка часу видачі
    iat = claims.get('iat', 0)
    if now < (iat - clock_skew_sec):
        return False

    return True

def verify_jwt_signature_rs256(raw_jwt: str, public_key: RSAPublicKey) -> bool:
    """Криптографічна перевірка підпису RS256 за відкритим ключем RSA."""
    parts = raw_jwt.split('.')
    if len(parts) != 3:
        return False

    signing_input = f"{parts[0]}.{parts[1]}".encode('ascii')
    signature = base64url_decode(parts[2])

    try:
        public_key.verify(
            signature,
            signing_input,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return True
    except Exception:
        return False
```
:::

---

### Етап 4: Ротація токенів оновлення та вирішення проблеми стану гонки

Коли термін дії `access_token` закінчується (зазвичай через 15–60 хвилин), клієнтський застосунок використовує `refresh_token` для отримання свіжої пари токенів без повторного перенаправлення користувача на екран входу.

Сучасні настанови безпеки OAuth 2.0 Security BCP та специфікація OAuth 2.1 вимагають обов'язкової реалізації механізму **Refresh Token Rotation (RTR)**.

#### Логіка роботи ротації токенів оновлення
1. Клієнт надсилає `refresh_token_A` на точку `/token` із параметром `grant_type=refresh_token`.
2. Сервер авторизації верифікує токен, генерує новий `access_token_2` і новий `refresh_token_B`.
3. Старий `refresh_token_A` негайно позначається у базі даних сервера авторизації як використаний (анульований).
4. Клієнт замінює старий токен на новий `refresh_token_B`.

#### Механізм виявлення повторного використання (Automatic Reuse Detection)
Якщо зловмисник встиг викрасти `refresh_token_A` до того, як легітимний клієнт використав його, або навпаки — скористався вже відпрацьованим токеном після клієнта, сервер авторизації виявляє повторне пред'явлення анульованого токена.

Це вважається прямим сигналом компрометації сесії:
- Сервер авторизації **негайно блокує всю гілку токенів**, включно з щойно виданим `refresh_token_B` та всіма активними `access_token`.
- Користувач примусово викидається з сесії на всіх пристроях і спрямовується на проходження повної автентифікації зі зміною пароля або додатковим фактором MFA.

#### Проблема паралельних запитів (Race Condition) та блокування
На практиці у високонавантажених або SPA-системах одночасно можуть виконуватися кілька паралельних HTTP-запитів до API (наприклад, завантаження профілю користувача, списку сповіщень та аналітики). Коли `access_token` протухає, усі три запити одночасно бачать `401 Unauthorized` і паралельно шлють запити на ендпоінт `/token` із тим самим `refresh_token_A`.

Перший запит пройде успішно й анулює `refresh_token_A`, а другий запит викличе спрацьовування системи захисту від викрадення токенів, що призведе до раптового викидання користувача.

Аби запобігти цьому, клієнт реалізує **шаблон синхронізації оновлення токенів** (In-Flight Refresh Mutex / Single-Flight Promise).

:::tabs
```cpp
#include <mutex>
#include <condition_variable>
#include <memory>

class TokenRefreshCoordinator {
public:
    struct TokenBundle {
        std::string access_token;
        std::string refresh_token;
        int64_t expires_at{0};
    };

    // Отримання свіжого access_token з гарантією єдиного запиту до сервера
    std::string get_valid_access_token() {
        std::unique_lock<std::mutex> lock(mtx_);

        auto now = std::chrono::duration_cast<std::chrono::seconds>(
            std::chrono::system_clock::now().time_since_epoch()).count();

        // Якщо токен ще дійсний щонайменше 30 секунд — віддаємо відразу
        if (tokens_.expires_at > (now + 30)) {
            return tokens_.access_token;
        }

        // Якщо інший потік уже виконує мережевий запит оновлення — очікуємо завершення
        if (refresh_in_progress_) {
            cv_.wait(lock, [this]() { return !refresh_in_progress_; });
            return tokens_.access_token;
        }

        // Цей потік бере на себе виконання оновлення
        refresh_in_progress_ = true;
        lock.unlock();

        try {
            TokenBundle fresh = execute_network_refresh(tokens_.refresh_token);

            lock.lock();
            tokens_ = fresh;
            refresh_in_progress_ = false;
            cv_.notify_all();
            return tokens_.access_token;
        } catch (...) {
            lock.lock();
            refresh_in_progress_ = false;
            cv_.notify_all();
            throw;
        }
    }

private:
    TokenBundle execute_network_refresh(const std::string& current_refresh_token) {
        // Тут виконується реальний мережевий HTTPS POST /token
        TokenBundle bundle;
        bundle.access_token = "eyJhbGciOiJSUzI1NiIs...";
        bundle.refresh_token = "r_new_rotated_string";
        bundle.expires_at = std::chrono::duration_cast<std::chrono::seconds>(
            std::chrono::system_clock::now().time_since_epoch()).count() + 3600;
        return bundle;
    }

    std::mutex mtx_;
    std::condition_variable cv_;
    bool refresh_in_progress_{false};
    TokenBundle tokens_;
};
```
```py
import time
import asyncio
from dataclasses import dataclass

@dataclass
class TokenBundle:
    access_token: str
    refresh_token: str
    expires_at: int

class AsyncTokenRefreshCoordinator:
    """Координатор ротації токенів із захистом від паралельних запитів (Single-Flight)."""

    def __init__(self, initial_tokens: TokenBundle):
        self.tokens = initial_tokens
        self._lock = asyncio.Lock()

    async def get_valid_access_token(self) -> str:
        now = int(time.time())
        # Якщо токен діє щонайменше 30 секунд, віддаємо без блокувань
        if self.tokens.expires_at > (now + 30):
            return self.tokens.access_token

        async with self._lock:
            # Повторна перевірка після захоплення замка (Double-Checked Locking)
            now = int(time.time())
            if self.tokens.expires_at > (now + 30):
                return self.tokens.access_token

            # Тільки один асинхронний таск виконує виклик /token
            self.tokens = await self._execute_network_refresh(self.tokens.refresh_token)
            return self.tokens.access_token

    async def _execute_network_refresh(self, current_refresh_token: str) -> TokenBundle:
        await asyncio.sleep(0.1)
        now = int(time.time())
        return TokenBundle(
            access_token="eyJhbGciOiJSUzI1NiIs...",
            refresh_token="r_rotated_secret_999",
            expires_at=now + 3600
        )
```
:::

---

### Етап 5: Запит до UserInfo, інтроспекція токенів та кешування

Після успішного отримання `access_token` клієнтський або ресурсний сервер може звернутися до додаткових протокольних ендпоінтів.

#### 1. Отримання розширеного профілю користувача (`/userinfo`)
Якщо `id_token` містив мінімальний набір даних, додаткові атрибути (ім'я, аватарка, підтверджена пошта, телефон) отримуються запитом GET або POST на `userinfo_endpoint`:

```http
GET /userinfo HTTP/1.1
Host: idp.example.com
Authorization: Bearer eyJhbGciOiJSUzI1NiIs...
```

Відповідь повертається у форматі JSON із заголовком `Content-Type: application/json`:
```json
{
  "sub": "usr_42",
  "name": "Олександр Коваленко",
  "given_name": "Олександр",
  "family_name": "Коваленко",
  "email": "oleksandr@example.com",
  "email_verified": true,
  "picture": "https://idp.example.com/photos/usr_42.jpg",
  "locale": "uk-UA"
}
```

Згідно зі специфікацією OIDC Core (§5.3.2), клієнт **зобов'язаний звірити поле `sub`** із відповіді `/userinfo` зі значенням `sub`, зафіксованим у раніше валідованому `id_token`. Будь-яка розбіжність свідчить про атаку підміни контексту користувача, і отримана інформація негайно анулюється.

#### 2. Інтроспекція токенів на сервері ресурсів (RFC 7662 Token Introspection)
Коли сервер ресурсів отримує непрозорий (opaque) `access_token`, він не може перевірити його локально, оскільки такий токен є простим посиланням на запис у базі даних сервера авторизації.

Сервер ресурсів виконує прямий виклик через бек-канал на ендпоінт інтроспекції:

```http
POST /introspect HTTP/1.1
Host: idp.example.com
Authorization: Basic cmVzb3VyY2Vfc2VydmVyXzAxOnNlY3JldF9hcGlfcGFzcw==
Content-Type: application/x-www-form-urlencoded

token=mF_9.B5f-4.1JqM
```

Сервер авторизації повертає метадані токена:
```json
{
  "active": true,
  "scope": "read:photos write:orders",
  "client_id": "web_app_prod_01",
  "sub": "usr_42",
  "exp": 1735732800,
  "iat": 1735729200,
  "iss": "https://idp.example.com"
}
```
Якщо поле `active` дорівнює `false`, сервер ресурсів відхиляє HTTP-запит клієнта з кодом `401 Unauthorized`.

#### 3. Відкликання токенів при виході користувача (RFC 7009 Token Revocation)
Коли користувач явно натискає кнопку «Вийти» (Logout), клієнт зобов'язаний повідомити сервер авторизації про анулювання як `refresh_token`, так і `access_token`. Для цього використовується стандартна кінцева точка `/revoke`:

```http
POST /revoke HTTP/1.1
Host: idp.example.com
Authorization: Basic d2ViX2FwcF9wcm9kXzAxOnNlY3JldF9rZXlfOTg3
Content-Type: application/x-www-form-urlencoded

token=r_9kLmNpQrStUvWxYz12345
&token_type_hint=refresh_token
```

Сервер авторизації повертає статус `200 OK` (навіть якщо токен уже був недійсним, що запобігає витоку інформації про стан сесій).

#### 4. Кешування інтроспекції та захист від каскадних запитів
Оскільки кожен виклик API вимагав би мережевого запиту до `/introspect`, сервер ресурсів кешує результат інтроспекції у швидкій локальній пам'яті або Redis на короткий проміжок часу (наприклад, на 30–60 секунд або до закінчення `exp`).

Для запобігання атаці "Cache Stampede", коли сотні паралельних клієнтських запитів при закінченні терміну кешу одночасно навантажують сервер авторизації, застосовується алгоритм імовірнісного дочасного оновлення (XFetch) або синхронізація через локальний блокувальний м'ютекс.

---

### Етап 6: Підвищена безпека через DPoP та mTLS

Традиційний `access_token` є Bearer-токеном: будь-хто, хто його перехопить (через логи, витік пам'яті або атаку посередника), може виконувати запити від імені клієнта. Для усунення цього фундаментального недоліку розроблено два додаткові стандарти:

#### 1. DPoP (Demonstrating Proof-of-Possession at the Application Layer, RFC 9449)
Застосунок локально генерує приватний/відкритий асиметричний ключ (наприклад, еліптичну криву Ed25519 або NIST P-256). На кожен HTTP-виклик до ресурсного сервера або сервера авторизації клієнт створює короткоживучий JWT-підпис (DPoP Proof):
- `htm` (HTTP Method): метод запиту (`POST`, `GET`).
- `htu` (HTTP Target URI): цільовий URL без рядка параметрів.
- `ath` (Access Token Hash): SHA-256 хеш від `access_token` у Base64URL (при зверненні до API).

```http
POST /api/orders HTTP/1.1
Host: api.example.com
Authorization: DPoP eyJhbGciOiJSUzI1NiIs...[access_token]...
DPoP: eyJ0eXAiOiJkcG9wK2p3dCIsImFsZyI6IkVTMjU2IiwiandrIjp7Imt0eSI6IkVDIiwiY3J2IjoiUC0yNTYiLCJ4IjoiLi4uIiwieSI6Ii4uLiJ9fQ.eyJqdGkiOiItQjFocGZkclFvTW8iLCJodG0iOiJQT1NUIiwiaHR1IjoiaHR0cHM6Ly9hcGkuZXhhbXBsZS5jb20vYXBpL29yZGVycyIsImlhdCI6MTczNTczMjgwMCwiYXRoIjoia1k5UjRkLi4uIn0.k8X...
```

Ресурсний сервер перевіряє, що відбиток публічного ключа з DPoP-доказу збігається з відбитком, зашитим у твердження `cnf.jkt` самого `access_token`. Навіть якщо зловмисник перехопить `access_token`, він не зможе використати його без доступу до закритого ключа клієнта, збереженого в апаратному модулі або ізольованій пам'яті процесу.

#### 2. Токени із прив'язкою до сертифіката mTLS (RFC 8705)
У корпоративних середовищах та банківських API (Open Banking / FAPI) зв'язування токенів часто реалізують на транспортному рівні за допомогою взаємного TLS (mTLS). Під час встановлення TLS-з'єднання клієнт пред'являє свій X.509 сертифікат. Сервер авторизації обчислює SHA-256 хеш сертифіката клієнта і записує його у твердження `cnf.x5t#S256` токена. Ресурсний сервер звіряє цей хеш із сертифікатом поточного з'єднання.

---

### Етап 7: Синхронний та асинхронний вихід (Single Sign-Out)

Коли користувач виходить із головного облікового запису на сервері IdP, усі підключені клієнтські застосунки повинні своєчасно очистити локальні сесії. В OIDC для цього визначено два механізми:
1. **Front-Channel Logout (OpenID Connect Front-Channel Logout 1.0)**: сервер IdP генерує приховані `<iframe>` на сторінці виходу, які надсилають запити `GET` на зареєстровані адреси `frontchannel_logout_uri` клієнтів разом із параметрами `iss` та `sid` (Session ID). Механізм простий, але залежить від блокування сторонніх cookie браузерами.
2. **Back-Channel Logout (OpenID Connect Back-Channel Logout 1.0)**: сервер IdP надсилає прямий серверний `POST`-запит на `backchannel_logout_uri` клієнта з корисним навантаженням `logout_token` (підписаний JWT). Клієнт верифікує токен і негайно знищує запис сесії в базі даних незалежно від стану браузера користувача.

---

### Етап 8: Динамічна реєстрація клієнтів (RFC 7591)

У мульти-тенантних або відкритих екосистемах (наприклад, у банківських агрегаторах чи федераціях університетів) клієнти не можуть реєструватися адміністратором вручну через панель керування IdP. Для автоматизації цього процесу застосовується протокол Dynamic Client Registration (RFC 7591).

Клієнт виконує POST-запит на кінцеву точку реєстрації IdP (`registration_endpoint`), передаючи свої метадані:
- `client_name`: зрозуміла користувачеві назва застосунку.
- `redirect_uris`: список дозволених зворотних адрес.
- `grant_types`: типи потоків (`authorization_code`, `refresh_token`).
- `response_types`: очікувані відповіді (`code`).
- `token_endpoint_auth_method`: спосіб автентифікації на точці `/token` (`client_secret_basic`, `private_key_jwt`).

Сервер авторизації генерує унікальний `client_id`, опціональний `client_secret` та `registration_access_token` для майбутнього оновлення чи видалення конфігурації клієнта. Для високозахищених середовищ замість спільних паролів `client_secret` реєструється відкритий ключ клієнта, а автентифікація на точці `/token` виконується методом `private_key_jwt` (RFC 7523): клієнт генерує та підписує власним закритим ключем короткоживучий JWT-ассерт (Client Assertion), що виключає передачу статичних паролів через мережу.

---

### Безпечне зберігання токенів та архітектурний патерн BFF

Найпоширеніша вразливість клієнтських систем полягає в некоректному зберіганні отриманих токенів.
- **LocalStorage та SessionStorage у браузері**: токени, збережені у сховищах JavaScript, доступні для читання будь-якому скрипту, що виконується на сторінці. Перша ж вразливість типу XSS (Cross-Site Scripting) через сторонню бібліотеку чи аналітичний скрипт призводить до миттєвого викрадення `access_token` та `refresh_token`.
- **Патерн BFF (Backend-For-Frontend)**: найбезпечніша сучасна архітектура для веб-застосунків. Браузерний JavaScript ніколи не бачить сирих OAuth-токенів. Усі запити на авторизацію, збереження `refresh_token` та виклики ресурсного API виконує легкий серверний бекенд (BFF). Браузер спілкується з BFF виключно через зашифровані `HttpOnly`, `Secure`, `SameSite=Lax/Strict` сесійні cookie, які JavaScript не може прочитати фізично.

Завдяки реалізації PKCE, суворої перевірки тверджень за OIDC Core, криптографічної валідації RSA-SHA256 підписів, координації ротації токенів оновлення, DPoP/mTLS-зв'язування, явного відкликання за RFC 7009 та ізоляції секретів за патерном BFF, клієнтський вузол забезпечує максимальний рівень безпеки та стійкості до компрометації.
