# ⚙️ Реалізація клієнта OAuth 2.0 з перевіркою PKCE та ротацією токенів

Створення надійного клієнта OAuth 2.0 вимагає суворого дотримання послідовності кроків, правильної криптографічної генерації одноразових параметрів та акуратної обробки життєвого циклу токенів. Будь-яка помилка у валідації стану, нехтування похибкою системних годинників або неправильне збереження секретів перетворює систему авторизації на вразливість.

Цей практичний розбір містить покроковий інженерний аналіз, вичерпний опис мережевих протокольних логів, архітектуру автоматизованого тестування, стратегії повторних спроб (Retry Strategy), шаблон проміжного ПЗ (Middleware) та закінчену реалізацію клієнтського рушія за протоколом **Authorization Code Flow із захистом PKCE (RFC 7636)** та автоматичною **ротацією токенів оновлення (Refresh Token Rotation)**.

```
+─────────────────────────────────────────────────────────────────────────────+
|               АРХІТЕКТУРА КЛІЄНТСЬКОГО ДВИГУНА OAUTH 2.0                     |
|                                                                             |
|  [ 1. Ініціалізація та криптографія ]                                       |
|   ├── Генерація криптографічного code_verifier (43-128 символів)            |
|   ├── Обчислення code_challenge = BASE64URL( SHA256(verifier) )             |
|   ├── Генерація анти-CSRF state (>= 128 біт випадковості)                   |
|   └── Формування URL перенаправлення на /authorize                          |
|                                                                             |
|  [ 2. Обробка зворотного виклику (Callback) ]                               |
|   ├── Постійно-часова перевірка збігу state (захист від CSRF)               |
|   ├── Вилучення короткоживучого authorization_code                          |
|   └── Бек-канал: POST /token { code, code_verifier, redirect_uri }          |
|                                                                             |
|  [ 3. Керування сесією та автоматичне оновлення ]                           |
|   ├── Збереження пари (access_token, refresh_token) і часу життя            |
|   ├── Випереджальне оновлення за 60 секунд до настання exp                  |
|   └── Захист від гонитви (In-Flight Promise) при паралельних викликах       |
+─────────────────────────────────────────────────────────────────────────────+
```

---

## 1. Покроковий розбір фаз роботи рушія

Робота клієнтського модуля розбита на три чітко розмежовані фази: криптографічна підготовка та запуск перенаправлення, обробка відповіді сервера авторизації у зворотному виклику (Callback) та довготривале керування життєвим циклом токенів під час виконання бізнес-запитів до API.

### Фаза 1: Криптографічна ініціалізація та генерація URL

Перед тим як перенаправити користувача на сторінку сервера авторизації, клієнт формує захисний криптографічний контекст поточної транзакції.

1. **Генерація PKCE `code_verifier`:** Клієнт генерує послідовність із 64 випадкових байтів за допомогою системного криптографічного генератора (CSPRNG). 64 байти забезпечують 512 бітів ентропії, що повністю унеможливлює атаку повним перебором (Brute-Force). Отримані байти кодуються у формат Base64url, що дає рядок довжиною 86 символів. Цей рядок задовольняє сувору вимогу RFC 7636 (довжина від 43 до 128 символів із нерезервованого набору `[A-Z, a-z, 0-9, "-", ".", "_", "~"]`). Верифікатор залишається виключно в пам'яті клієнта і не передається у фронт-каналі.
2. **Обчислення PKCE `code_challenge`:** Клієнт обчислює криптографічний геш SHA-256 від рядка `code_verifier`. Отриманий бінарний дайджест (32 байти) кодується у формат Base64url без символів паддингу `=`. Оскільки SHA-256 є незворотною односторонньою функцією, знання `code_challenge` не дозволяє зловмиснику відновити оригінальний `code_verifier`.
3. **Генерація анти-CSRF параметра `state`:** Клієнт генерує 32 байти випадкових даних і кодує їх у Base64url. Цей рядок зв'язується з поточною сесією браузера (наприклад, зберігається в зашифрованій сесійній куці або тимчасовому сховищі бекенда).
4. **Формування посилання на `/authorize`:** Клієнт конструює адресу перенаправлення, додаючи параметри `response_type=code`, `client_id`, `redirect_uri`, `scope`, `state`, `code_challenge` та `code_challenge_method=S256`. Браузер перенаправляється за цією адресою через HTTP-відповідь `302 Found`.

### Фаза 2: Обробка Callback та бек-канал обміну на токени

Коли користувач проходить автентифікацію на сервері авторизації та підтверджує запитані права (Consent), сервер повертає браузер назад на вказаний `redirect_uri`.

1. **Перевірка помилок:** Якщо користувач натиснув «Скасувати» або сталася помилка конфігурації, запит міститиме параметри `error` та `error_description`. Клієнт перериває потік і викидає відповідне виключення.
2. **Анти-CSRF валідація параметра `state`:** Клієнт порівнює отриманий у query string рядок `state` із тим значенням, яке було збережено в сесії на кроці ініціалізації. Порівняння **обов'язково виконується за алгоритмом сталого часу (Constant-Time Comparison)**, щоб унеможливити атаки за часом відгуку (Timing Attacks). Якщо значення не збігаються або сесійний стан порожній, транзакція негайно відхиляється як потенційна атака підробки міжсайтового запиту.
3. **Прямий POST-запит до `/token` (Бек-канал):** Клієнт виконує прямий захищений HTTP POST-запит безпосередньо зі свого бекенда до сервера авторизації, минаючи браузер. У тілі форми `application/x-www-form-urlencoded` передаються `grant_type=authorization_code`, отриманий `code`, ідентичний `redirect_uri`, `client_id` та оригінальний секретний `code_verifier`. Якщо клієнт є конфіденційним, додається заголовок `Authorization: Basic` із секретом застосунку.
4. **Перевірка сервером та збереження сесії:** Сервер авторизації знаходить збережений на кроці 1 челендж для цього коду, самостійно обчислює `SHA256(отриманий code_verifier)` і перевіряє точний збіг. Переконавшись у дійсності коду та автентичності клієнта, сервер видає JSON-відповідь із парою `access_token` і `refresh_token`. Клієнт зберігає токени та обчислює точний момент закінчення дії: `expires_at = time() + expires_in`.

### Фаза 3: Випереджальне оновлення та захист від гонитви (In-Flight Refresh)

Токен доступу має обмежений час життя (зазвичай від 15 до 60 хвилин). Під час виконання бізнес-запитів до API клієнт перевіряє стан токена.

1. **Буфер часової похибки (Clock Skew Buffer):** Клієнт не чекає моменту повного вичерпання строку дії токена. Оновлення ініціюється автоматично, якщо до моменту `expires_at` залишається менше 60 секунд. Це гарантує, що запит не зазнає збою `401 Unauthorized` під час передачі пакета через мережу.
2. **Блокування паралельних оновлень (In-Flight Promise Pattern):** Якщо у високонавантаженому додатку одночасно надходить кілька паралельних запитів на отримання токена, система не повинна надсилати 5 паралельних запитів на оновлення до сервера авторизації. Це критично важливо, оскільки при ввімкненій ротації токенів перший запит оновить `refresh_token`, а решта 4 надішлють уже застарілий токен, що призведе до блокування всієї сесії користувача. Клієнт запускає один спільний мережевий виклик оновлення, а всі паралельні запити очікують завершення єдиного результату.

---

## 2. Реалізація клієнта (Python, TypeScript, C++)

Нижче наведено робочий код клієнтського рушія з повною підтримкою стандарту PKCE S256, постійно-часовою перевіркою валідності стану та випереджальним керуванням сесією.

:::tabs
```py
import os
import time
import base64
import hashlib
import secrets
import hmac
import urllib.parse
import json
import urllib.request
from typing import Optional, Dict, Any, Tuple

class OAuthClient:
    def __init__(
        self,
        auth_server_url: str,
        client_id: str,
        redirect_uri: str,
        client_secret: Optional[str] = None,
        clock_skew_seconds: int = 60
    ):
        self.auth_server_url = auth_server_url.rstrip("/")
        self.authorize_endpoint = f"{self.auth_server_url}/oauth/authorize"
        self.token_endpoint = f"{self.auth_server_url}/oauth/token"
        
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.clock_skew = clock_skew_seconds
        
        # Сховище токенів поточної сесії
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.expires_at: float = 0.0
        self.granted_scopes: str = ""
        
        # Тимчасовий стан між перенаправленням і callback
        self._pending_verifier: Optional[str] = None
        self._pending_state: Optional[str] = None

    @staticmethod
    def _base64url_encode(data: bytes) -> str:
        """Кодування байтів у рядок Base64URL без знаків паддингу '='."""
        return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")

    def generate_pkce_pair(self) -> Tuple[str, str]:
        """Генерує випадковий code_verifier і відповідний SHA256 code_challenge."""
        # 64 випадкові байти дають 86 символів у base64url (у межах норми 43..128)
        raw_bytes = secrets.token_bytes(64)
        verifier = self._base64url_encode(raw_bytes)
        
        digest = hashlib.sha256(verifier.encode("ascii")).digest()
        challenge = self._base64url_encode(digest)
        return verifier, challenge

    def create_authorization_url(self, scopes: list[str]) -> str:
        """Створює повний URL для перенаправлення браузера користувача."""
        verifier, challenge = self.generate_pkce_pair()
        state = self._base64url_encode(secrets.token_bytes(32))
        
        self._pending_verifier = verifier
        self._pending_state = state
        
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(scopes),
            "state": state,
            "code_challenge": challenge,
            "code_challenge_method": "S256"
        }
        return f"{self.authorize_endpoint}?{urllib.parse.urlencode(params)}"

    def handle_callback(self, query_params: Dict[str, str]) -> Dict[str, Any]:
        """Обробляє параметри повернення браузера та обмінює код на токени."""
        if "error" in query_params:
            err = query_params.get("error")
            desc = query_params.get("error_description", "Немає опису")
            raise PermissionError(f"Сервер авторизації відхилив запит: {err} ({desc})")
        
        returned_state = query_params.get("state", "")
        if not self._pending_state or not hmac.compare_digest(self._pending_state, returned_state):
            raise SecurityError("Атака підробки запиту: параметр state не збігається!")
            
        code = query_params.get("code")
        if not code:
            raise ValueError("Відповідь авторизації не містить коду (code)")
            
        if not self._pending_verifier:
            raise RuntimeError("Втрачено стан PKCE verifier для цієї сесії")
            
        # Бек-канал: прямий обмін на токени
        tokens = self._exchange_code_for_tokens(code, self._pending_verifier)
        
        # Очищення тимчасового стану після успішного використання
        self._pending_verifier = None
        self._pending_state = None
        
        return tokens

    def _exchange_code_for_tokens(self, code: str, verifier: str) -> Dict[str, Any]:
        """Надсилає HTTP POST на /token для обміну code на токени."""
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "code_verifier": verifier
        }
        return self._send_token_request(data)

    def refresh_access_token(self) -> Dict[str, Any]:
        """Використовує refresh_token для отримання нової пари токенів."""
        if not self.refresh_token:
            raise ValueError("Відсутній refresh_token для оновлення сесії")
            
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": self.client_id
        }
        return self._send_token_request(data)

    def _send_token_request(self, form_data: Dict[str, str]) -> Dict[str, Any]:
        """Виконує прямий мережевий POST-запит до ендпоінта видачі токенів."""
        encoded_data = urllib.parse.urlencode(form_data).encode("utf-8")
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }
        
        # Автентифікація конфіденційного клієнта через заголовок Basic Auth
        if self.client_secret:
            auth_str = f"{self.client_id}:{self.client_secret}"
            b64_auth = base64.b64encode(auth_str.encode("utf-8")).decode("utf-8")
            headers["Authorization"] = f"Basic {b64_auth}"
            
        req = urllib.request.Request(self.token_endpoint, data=encoded_data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            raise RuntimeError(f"Помилка ендпоінта /token [{e.code}]: {err_body}") from e
            
        # Збереження отриманих токенів у пам'яті клієнта
        self.access_token = payload["access_token"]
        # При ротації токенів сервер видає новий refresh_token
        if "refresh_token" in payload:
            self.refresh_token = payload["refresh_token"]
            
        expires_in = payload.get("expires_in", 3600)
        self.expires_at = time.time() + float(expires_in)
        self.granted_scopes = payload.get("scope", "")
        
        return payload

    def get_valid_access_token(self) -> str:
        """Повертає дійсний access_token, автоматично оновлюючи його за потреби."""
        # Оновлюємо заздалегідь (за clock_skew секунд до фактичного закінчення)
        if time.time() >= (self.expires_at - self.clock_skew):
            if self.refresh_token:
                self.refresh_access_token()
            else:
                raise PermissionError("Access token протерміновано, а refresh_token відсутній")
                
        if not self.access_token:
            raise PermissionError("Клієнт ще не пройшов авторизацію")
            
        return self.access_token
```
```ts
import crypto from "crypto";

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  refresh_token?: string;
  scope?: string;
}

export class OAuthClient {
  private readonly authServerUrl: string;
  private readonly authorizeEndpoint: string;
  private readonly tokenEndpoint: string;
  private readonly clientId: string;
  private readonly clientSecret?: string;
  private readonly redirectUri: string;
  private readonly clockSkewSeconds: number;

  private accessToken: string | null = null;
  private refreshToken: string | null = null;
  private expiresAt: number = 0;

  private pendingVerifier: string | null = null;
  private pendingState: string | null = null;
  private refreshPromise: Promise<TokenResponse> | null = null;

  constructor(options: {
    authServerUrl: string;
    clientId: string;
    redirectUri: string;
    clientSecret?: string;
    clockSkewSeconds?: number;
  }) {
    this.authServerUrl = options.authServerUrl.replace(/\/+$/, "");
    this.authorizeEndpoint = `${this.authServerUrl}/oauth/authorize`;
    this.tokenEndpoint = `${this.authServerUrl}/oauth/token`;
    this.clientId = options.clientId;
    this.clientSecret = options.clientSecret;
    this.redirectUri = options.redirectUri;
    this.clockSkewSeconds = options.clockSkewSeconds ?? 60;
  }

  private static base64UrlEncode(buffer: Buffer): string {
    return buffer
      .toString("base64")
      .replace(/\+/g, "-")
      .replace(/\//g, "_")
      .replace(/=+$/, "");
  }

  public generatePkcePair(): { verifier: string; challenge: string } {
    const verifier = OAuthClient.base64UrlEncode(crypto.randomBytes(64));
    const hash = crypto.createHash("sha256").update(verifier, "ascii").digest();
    const challenge = OAuthClient.base64UrlEncode(hash);
    return { verifier, challenge };
  }

  public createAuthorizationUrl(scopes: string[]): string {
    const { verifier, challenge } = this.generatePkcePair();
    const state = OAuthClient.base64UrlEncode(crypto.randomBytes(32));

    this.pendingVerifier = verifier;
    this.pendingState = state;

    const params = new URLSearchParams({
      response_type: "code",
      client_id: this.clientId,
      redirect_uri: this.redirectUri,
      scope: scopes.join(" "),
      state,
      code_challenge: challenge,
      code_challenge_method: "S256"
    });

    return `${this.authorizeEndpoint}?${params.toString()}`;
  }

  public async handleCallback(queryParams: Record<string, string>): Promise<TokenResponse> {
    if (queryParams.error) {
      throw new Error(`Сервер відхилив авторизацію: ${queryParams.error} (${queryParams.error_description ?? ""})`);
    }

    const state = queryParams.state ?? "";
    if (!this.pendingState || !crypto.timingSafeEqual(Buffer.from(this.pendingState), Buffer.from(state))) {
      throw new Error("Атака підробки міжсайтового запиту: параметр state не збігається");
    }

    const code = queryParams.code;
    if (!code) {
      throw new Error("Відповідь сервера не містить коду авторизації");
    }

    if (!this.pendingVerifier) {
      throw new Error("Втрачено verifier для поточної сесії PKCE");
    }

    const tokens = await this.exchangeCodeForTokens(code, this.pendingVerifier);
    this.pendingVerifier = null;
    this.pendingState = null;
    return tokens;
  }

  private async exchangeCodeForTokens(code: string, verifier: string): Promise<TokenResponse> {
    const body = new URLSearchParams({
      grant_type: "authorization_code",
      code,
      redirect_uri: this.redirectUri,
      client_id: this.clientId,
      code_verifier: verifier
    });

    return this.sendTokenRequest(body);
  }

  public async refreshAccessToken(): Promise<TokenResponse> {
    if (!this.refreshToken) {
      throw new Error("Відсутній refresh_token для виконання оновлення");
    }

    // Запобігання гонитві: якщо запит на оновлення вже виконується, повертаємо активний проміс
    if (this.refreshPromise) {
      return this.refreshPromise;
    }

    const body = new URLSearchParams({
      grant_type: "refresh_token",
      refresh_token: this.refreshToken,
      client_id: this.clientId
    });

    this.refreshPromise = this.sendTokenRequest(body).finally(() => {
      this.refreshPromise = null;
    });

    return this.refreshPromise;
  }

  private async sendTokenRequest(body: URLSearchParams): Promise<TokenResponse> {
    const headers: Record<string, string> = {
      "Content-Type": "application/x-www-form-urlencoded",
      "Accept": "application/json"
    };

    if (this.clientSecret) {
      const basic = Buffer.from(`${this.clientId}:${this.clientSecret}`).toString("base64");
      headers["Authorization"] = `Basic ${basic}`;
    }

    const response = await fetch(this.tokenEndpoint, {
      method: "POST",
      headers,
      body: body.toString()
    });

    if (!response.ok) {
      const errText = await response.text();
      throw new Error(`Помилка запиту токенів [${response.status}]: ${errText}`);
    }

    const tokens = (await response.json()) as TokenResponse;
    this.accessToken = tokens.access_token;
    if (tokens.refresh_token) {
      this.refreshToken = tokens.refresh_token;
    }
    this.expiresAt = Date.now() + (tokens.expires_in ?? 3600) * 1000;
    return tokens;
  }

  public async getValidAccessToken(): Promise<string> {
    const now = Date.now();
    const threshold = this.expiresAt - this.clockSkewSeconds * 1000;

    if (now >= threshold) {
      if (this.refreshToken) {
        await this.refreshAccessToken();
      } else {
        throw new Error("Access token закінчився, а refresh_token відсутній");
      }
    }

    if (!this.accessToken) {
      throw new Error("Клієнт не авторизований");
    }
    return this.accessToken;
  }
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <chrono>
#include <random>
#include <stdexcept>
#include <sstream>
#include <iomanip>
#include <span>
#include <openssl/sha.h>
#include <openssl/rand.h>

class OAuthClient {
public:
    OAuthClient(std::string auth_server_url,
                std::string client_id,
                std::string redirect_uri,
                std::string client_secret = "",
                int clock_skew_seconds = 60)
        : auth_server_url_(std::move(auth_server_url))
        , client_id_(std::move(client_id))
        , redirect_uri_(std::move(redirect_uri))
        , client_secret_(std::move(client_secret))
        , clock_skew_seconds_(clock_skew_seconds)
    {
        authorize_endpoint_ = auth_server_url_ + "/oauth/authorize";
        token_endpoint_ = auth_server_url_ + "/oauth/token";
    }

    static std::string base64url_encode(std::span<const uint8_t> data) {
        static constexpr char tbl[] =
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_";
        std::string out;
        out.reserve(((data.size() + 2) / 3) * 4);

        size_t i = 0;
        while (i < data.size()) {
            uint32_t octet_a = data[i++];
            uint32_t octet_b = (i < data.size()) ? data[i++] : 0;
            uint32_t octet_c = (i < data.size()) ? data[i++] : 0;

            uint32_t triple = (octet_a << 16) + (octet_b << 8) + octet_c;

            out.push_back(tbl[(triple >> 18) & 0x3F]);
            out.push_back(tbl[(triple >> 12) & 0x3F]);
            if (i > data.size() + 1) break;
            out.push_back(tbl[(triple >> 6) & 0x3F]);
            if (i > data.size()) break;
            out.push_back(tbl[triple & 0x3F]);
        }
        return out;
    }

    std::pair<std::string, std::string> generate_pkce_pair() {
        std::vector<uint8_t> random_bytes(64);
        if (RAND_bytes(random_bytes.data(), static_cast<int>(random_bytes.size())) != 1) {
            throw std::runtime_error("CSPRNG: збій отримання випадкових байтів OpenSSL");
        }
        std::string verifier = base64url_encode(random_bytes);

        uint8_t hash[SHA256_DIGEST_LENGTH];
        SHA256(reinterpret_cast<const uint8_t*>(verifier.data()), verifier.size(), hash);
        std::string challenge = base64url_encode(std::span<const uint8_t>(hash, SHA256_DIGEST_LENGTH));

        return {verifier, challenge};
    }

    std::string create_authorization_url(const std::vector<std::string>& scopes) {
        auto [verifier, challenge] = generate_pkce_pair();
        
        std::vector<uint8_t> state_bytes(32);
        RAND_bytes(state_bytes.data(), static_cast<int>(state_bytes.size()));
        std::string state = base64url_encode(state_bytes);

        pending_verifier_ = verifier;
        pending_state_ = state;

        std::string scope_str;
        for (size_t i = 0; i < scopes.size(); ++i) {
            if (i > 0) scope_str += "+";
            scope_str += scopes[i];
        }

        std::ostringstream ss;
        ss << authorize_endpoint_
           << "?response_type=code"
           << "&client_id=" << client_id_
           << "&redirect_uri=" << redirect_uri_
           << "&scope=" << scope_str
           << "&state=" << state
           << "&code_challenge=" << challenge
           << "&code_challenge_method=S256";

        return ss.str();
    }

    bool validate_state(std::string_view returned_state) const noexcept {
        if (pending_state_.empty() || pending_state_.size() != returned_state.size()) {
            return false;
        }
        // Порівняння сталого часу для захисту від timing attacks
        int diff = 0;
        for (size_t i = 0; i < pending_state_.size(); ++i) {
            diff |= (pending_state_[i] ^ returned_state[i]);
        }
        return diff == 0;
    }

    bool is_token_expired() const noexcept {
        auto now = std::chrono::system_clock::now();
        auto threshold = expires_at_ - std::chrono::seconds(clock_skew_seconds_);
        return now >= threshold;
    }

    void set_tokens(std::string access, std::string refresh, int expires_in_sec) {
        access_token_ = std::move(access);
        refresh_token_ = std::move(refresh);
        expires_at_ = std::chrono::system_clock::now() + std::chrono::seconds(expires_in_sec);
    }

    const std::string& get_pending_verifier() const noexcept { return pending_verifier_; }
    const std::string& get_access_token() const noexcept { return access_token_; }
    const std::string& get_refresh_token() const noexcept { return refresh_token_; }

private:
    std::string auth_server_url_;
    std::string authorize_endpoint_;
    std::string token_endpoint_;
    std::string client_id_;
    std::string redirect_uri_;
    std::string client_secret_;
    int clock_skew_seconds_;

    std::string access_token_;
    std::string refresh_token_;
    std::chrono::system_clock::time_point expires_at_;

    std::string pending_verifier_;
    std::string pending_state_;
};
```
:::

---

## 3. Критичні пастки та крайові випадки реалізації

### 1. Стан гонитви при паралельному оновленні токенів (Token Refresh Race Condition)

Коли мобільний додаток або веб-SPA відкриває екран дашборда, він зазвичай запускає від 5 до 10 паралельних запитів до різних мікросервісів: завантаження профілю користувача, отримання списку сповіщень, перевірка балансу та зчитування налаштувань.

Якщо термін дії токена закінчився під час простою, усі ці 10 запитів майже одночасно виявлять факт застарілості токена доступу й спробують надіслати запит на ендпоінт `/token` із тим самим `refresh_token`.

При ввімкненій **ротації токенів (Refresh Token Rotation)** виникає фатальна колізія:
1. Перший запит досягає сервера авторизації, успішно обмінює `refresh_token_1` на нову пару `(access_token_2, refresh_token_2)` і погашає старий токен.
2. Решта 9 паралельних запитів надсилають серверові вже недійсний `refresh_token_1`.
3. Сервер авторизації фіксує повторне пред'явлення вже погашеного токена. Згідно з протоколом RFC 6749, це однозначний маркер **крадіжки токена** (зловмисник або легітимний клієнт скористався застарілим ключем).
4. Сервер негайно анулює всю сім'ю токенів сесії (включно зі щойно виданим `refresh_token_2`) і блокує сеанс. Користувача раптово викидає з програми посеред роботи!

**Архітектурне розв'язання:**
* Реалізація механізму **Single-Flight / In-Flight Promise**: клієнт створює глобальну чергу оновлення. Перший запит створює активний асинхронний виклик до `/token`, а всі наступні паралельні запити не виконують власних викликів, а просто підписуються на завершення цього єдиного виклику. Щойно оновлення завершується, усі запити отримують новий токен доступу й одночасно вирушають до API.

### 2. Часова похибка системних годинників (Clock Skew)

Якщо на клієнтському пристрої системний час налаштовано неточно (похибка в 30–90 секунд є типовою для смартфонів без постійної синхронізації або серверів без належного налаштування NTP), клієнт вважатиме токен валідним, тоді як сервер ресурсів уже відхилятиме його з помилкою `401 Token Expired`.

**Архітектурне розв'язання:**
* Клієнт зобов'язаний закладати захисний часовий інтервал: ініціювати оновлення токена за **60 секунд до настання значення `expires_at`**. Це повністю нівелює ризик відхилення запиту через мережеву затримку в польоті або розсинхронізацію годинників.

### 3. Атаки за часом відгуку при звірці `state` (Timing Attacks)

Звичайне порівняння рядків у мовах високого рівня (`a == b`) працює оптимізовано: воно порівнює символи по черзі й негайно зупиняється на першому незбігу. Зловмисник, надсилаючи тисячі підроблених запитів і вимірюючи час повернення HTTP-відповіді з точністю до наносекунд, може посимвольно відновити валідне значення `state`.

**Архітектурне розв'язання:**
* Для перевірки `state` завжди використовується функція порівняння сталого часу (`hmac.compare_digest` у Python, `crypto.timingSafeEqual` у Node.js, бітове XOR-порівняння в C++).

---

## 4. Безпечне зберігання токенів за типами середовища

Місце зберігання отриманих токенів визначається моделлю загроз конкретної платформи:

1. **Браузерні додатки (SPA / Frontend):**
   * *Антипатерн:* Зберігання в `localStorage` чи `sessionStorage`. Будь-яка вразливість міжсайтового скриптингу (XSS) дозволяє сторонньому скрипту прочитати сховище й викрасти `refresh_token`.
   * *Правильне рішення:* Архітектурний патерн **Backend for Frontend (BFF)**. Браузер спілкується з власним легким бекендом через захищені сесійні куки з прапорцями `HttpOnly`, `Secure` та `SameSite=Lax/Strict`. Сам `refresh_token` зберігається виключно на бекенді BFF і ніколи не потрапляє в середовище JavaScript браузера.
2. **Мобільні та настільні додатки (iOS, Android, Desktop):**
   * Використання апаратних захищених сховищ операційної системи: **iOS Keychain**, **Android EncryptedSharedPreferences / Keystore**, **Windows Credential Manager**. Токени шифруються апаратними ключами пристрою і захищені біометрією (FaceID / Fingerprint).
3. **Серверні бекенди (Confidential Clients):**
   * Токени зберігаються в захищених базах даних (наприклад, Redis з увімкненим TLS та авторизацією) у зашифрованому вигляді за допомогою ключів із системи керування секретами (HashiCorp Vault, AWS KMS).

---

## 5. Обробка фатальної помилки `invalid_grant` та скидання сесії

Під час оновлення токена клієнт може отримати від сервера відповідь із кодом `400 Bad Request` та тілом `{"error": "invalid_grant"}`. Ця помилка виникає у чотирьох принципових ситуаціях:
1. Користувач змінив пароль або явно натиснув «Вийти з усіх пристроїв» в особистому кабінеті.
2. Адміністратор компанії заблокував обліковий запис або відкликав права застосунку.
3. Закінчився абсолютний строк життя сесії (англ. *Max Refresh Lifetime*, наприклад 30 або 90 днів).
4. Сервер виявив спробу повторного використання старого `refresh_token` і превентивно заблокував увесь ланцюжок ротації.

**Алгоритм дій клієнта при отриманні `invalid_grant`:**
* Клієнт **не має права повторювати запит на оновлення** (це безглуздо і призведе лише до зайвого навантаження на сервер).
* Клієнт негайно видаляє збережені `access_token` та `refresh_token` зі сховища.
* Усі активні фонові запити до API скасовуються.
* Користувацький інтерфейс переводиться в стан розірваної сесії, а користувачу показується повідомлення про необхідність повторного входу з перенаправленням на початок потоку `/authorize`.

---

## 6. Мережевий протокол у дії: живий лог запитів і відповідей

Нижче наведено повний дамп HTTP-запитів і відповідей, що відбуваються під час проходження повного циклу авторизації за допомогою створеного клієнта:

### Крок 1: Браузерне перенаправлення на сервер авторизації

```http
GET /oauth/authorize?response_type=code
    &client_id=analytics-dashboard-123
    &redirect_uri=https%3A%2F%2Fapp.example.com%2Foauth%2Fcallback
    &scope=reports.read
    &state=x7K9vL2mQ8jP4wZ1
    &code_challenge=dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk
    &code_challenge_method=S256 HTTP/1.1
Host: auth.example.com
```

### Крок 2: Сервер авторизації повертає редирект із кодом

```http
HTTP/1.1 302 Found
Location: https://app.example.com/oauth/callback?code=SplxlOBeZQQYbYS6WxSbIA&state=x7K9vL2mQ8jP4wZ1
```

### Крок 3: Бекенд клієнта обмінює код на токени (бек-канал)

```http
POST /oauth/token HTTP/1.1
Host: auth.example.com
Authorization: Basic YW5hbHl0aWNzLWRhc2hib2FyZC0xMjM6c3VwZXItc2VjcmV0LWtleQ==
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code
&code=SplxlOBeZQQYbYS6WxSbIA
&redirect_uri=https%3A%2F%2Fapp.example.com%2Foauth%2Fcallback
&code_verifier=E9Melhoa2OwvFrGMTJguCH5rtx64fZqiJ405nmIjY0s
```

### Крок 4: Сервер авторизації видає першу пару токенів

```http
HTTP/1.1 200 OK
Content-Type: application/json;charset=UTF-8
Cache-Control: no-store

{
  "access_token": "at_9874102938401923",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "rt_0192830192830192",
  "scope": "reports.read"
}
```

### Крок 5: Випереджальне оновлення сесії через ротацію токенів

```http
POST /oauth/token HTTP/1.1
Host: auth.example.com
Authorization: Basic YW5hbHl0aWNzLWRhc2hib2FyZC0xMjM6c3VwZXItc2VjcmV0LWtleQ==
Content-Type: application/x-www-form-urlencoded

grant_type=refresh_token
&refresh_token=rt_0192830192830192
```

### Крок 6: Сервер повертає новий access_token та новий refresh_token

```http
HTTP/1.1 200 OK
Content-Type: application/json;charset=UTF-8
Cache-Control: no-store

{
  "access_token": "at_1122334455667788",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "rt_9988776655443322",
  "scope": "reports.read"
}
```

Старий `rt_0192830192830192` безповоротно знищується в базі сервера. Будь-яка наступна спроба пред'явити його призведе до негайної інвалідації щойно створеного `rt_9988776655443322`. Цей механізм гарантує максимальну криптографічну стійкість та захист призначених для користувача даних.

---

## 7. Інтеграція клієнта через HTTP Interceptor / Middleware

Для практичного використання у виробничих сервісах клієнт обгортають у проміжний шар HTTP-клієнта (англ. *HTTP Interceptor / Transport Layer*). Це звільняє бізнес-код від необхідності вручну передавати токени або обробляти помилки автентифікації.

Інтерцептор автоматично виконує такі операції:
1. Перед відправкою будь-якого бізнес-запиту викликає метод `get_valid_access_token()`, який перевіряє час життя токена та за потреби прозоро виконує оновлення через `refresh_token`.
2. Додає заголовок `Authorization: Bearer <access_token>` до вихідного HTTP-пакета.
3. Якщо сервер ресурсів повертає статус `401 Unauthorized` (наприклад, через примусове дострокове відкликання прав на стороні API), інтерцептор перехоплює помилку, ініціює одноразове примусове оновлення токена та повторює початковий запит.
4. Якщо повторний запит також зазнає збою з кодом 401 або процес оновлення повертає `invalid_grant`, інтерцептор перериває ланцюжок і сповіщає користувацький інтерфейс про необхідність повного перелогіну.
5. На мобільних клієнтах під час переходу між стільниковою мережею та Wi-Fi або під час виходу з режиму польоту інтерцептор перевіряє наявність зв'язку перед спробою оновлення, уникаючи зайвих помилок таймауту.

Така архітектура повністю ізолює протокольні деталі OAuth 2.0 від коду прикладного рівня, забезпечуючи високу надійність і стійкість додатку до мережевих збоїв.

---

## 8. Стратегія автоматизованого тестування клієнта

Тестування безпеки клієнта OAuth 2.0 вимагає перевірки не лише успішного сценарію (Happy Path), а й стресових та аварійних режимів.

Комплексний набір модульних тестів обов'язково покриває такі критичні кейси:
1. **Тест захисту від підробки State:** Симуляція повернення зловмисником випадкового або чужого `state`. Тест переконується, що клієнт викидає виключення безпеки до моменту виклику ендпоінта `/token`.
2. **Тест коректності перетворення PKCE:** Перевірка верифікатора `code_verifier` довжиною рівно 43 та 128 символів, перевірка відповідності SHA-256 хеша та відсутності знаків паддингу `=` у результуючому челенджі.
3. **Тест випереджального оновлення за Clock Skew:** Симуляція ситуації, коли до закінчення токена залишається 30 секунд. Тест перевіряє, що `get_valid_access_token()` проактивно викликає оновлення, не чекаючи фактичного настання `exp`.
4. **Тест паралельного оновлення (Race Condition Stress Test):** Одночасний запуск 50 асинхронних корутин, які запитують токен у момент його закінчення. Тест підтверджує, що до тестового мок-сервера надходить рівно **один** HTTP POST-запит на ендпоінт `/token`, а всі 50 корутин успішно отримують новий токен.
5. **Тест обробки відмови у правах (`access_denied`):** Перевірка коректної обробки редиректу з повідомленням про відхилення згоди користувачем без падіння процесу клієнта.
6. **Тест повторних спроб (Retry з експоненційним відступом):** Перевірка поведінки клієнта під час тимчасових мережевих збоїв або відповідей сервера з кодом `503 Service Unavailable`. Клієнт виконує обмежену кількість повторів із джиттером, уникаючи надлишкового навантаження на інфраструктуру.
7. **Тест явного відкликання токенів (Revocation Test):** Перевірка виклику ендпоінта `/revoke` при виході користувача з облікового запису та очищення локального кешу ключів.
