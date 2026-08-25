# ⚙️ Реалізація верифікатора WebAuthn і Passkeys на бекенді

Практична реалізація повного серверного циклу верифікації церемоній реєстрації та автентифікації WebAuthn / Passkeys без використання сторонніх «чорних скриньок». Розбирає низькорівневе двійкове розпакування буфера `authData`, декодування та імпорт відкритих ключів формату COSE, конструювання структур ASN.1 SPKI для криптографічних бібліотек, перевірку цифрових підписів ECDSA P-256, роботу з Discoverable Credentials та захист від атак повтору й клонування токенів.

## 1. Архітектура та модель даних

Для надійної підтримки ключів доступу (Passkeys) бекенд відокремлює сутність облікового запису користувача від конкретних пристроїв автентифікації. У класичній схемі з паролями один користувач має один пароль (або його хеш). У безпарольній моделі на базі асиметричної криптографії один обліковий запис володіє набором зареєстрованих ключів: наприклад, Touch ID на робочому ноутбуці, Face ID на особистому телефоні та апаратний USB-ключ YubiKey як надійний резерв.

Кожен зареєстрований ключ характеризується унікальним ідентифікатором `credentialId`, відкритим ключем у форматі SubjectPublicKeyInfo (SPKI), поточним значенням лічильника підписів `signCount` та прапорцями підтримки хмарної синхронізації (`BE` та `BS`).

### Схема бази даних (PostgreSQL)

```sql
-- Таблиця користувачів (сутність облікового запису)
CREATE TABLE users (
    id VARCHAR(64) PRIMARY KEY,          -- Сталий бінарний ID (Base64URL), стійкий до колізій
    email VARCHAR(255) UNIQUE NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Таблиця зареєстрованих ключів доступу (Passkeys)
CREATE TABLE passkey_credentials (
    id VARCHAR(255) PRIMARY KEY,          -- credentialId (Base64URL)
    user_id VARCHAR(64) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    public_key_spki BYTEA NOT NULL,       -- Відкритий ключ у форматі DER SubjectPublicKeyInfo
    algorithm INT NOT NULL DEFAULT -7,    -- COSE ідентифікатор алгоритму (-7 = ES256)
    sign_count BIGINT NOT NULL DEFAULT 0,    -- Лічильник підписів для виявлення клонів
    aaguid VARCHAR(36) NOT NULL,          -- Модель автентифікатора (UUID)
    backup_eligible BOOLEAN NOT NULL,     -- Прапорець BE (можливість синхронізації)
    backup_state BOOLEAN NOT NULL,        -- Прапорець BS (синхронізовано у брелок)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP WITH TIME ZONE
);

-- Тимчасова таблиця сесійних викликів (челенджів)
CREATE TABLE auth_challenges (
    challenge VARCHAR(64) PRIMARY KEY,    -- Base64URL випадковий рядок (32 байти)
    user_id VARCHAR(64),                  -- NULL для безпарольного входу (Discoverable)
    ceremony_type VARCHAR(16) NOT NULL,   -- 'registration' або 'authentication'
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL
);
```

У цій схемі поле `user.id` є незмінним бінарним дескриптором (User Handle). Специфікація W3C WebAuthn забороняє використовувати як `user.id` персональні дані (електронну пошту, ім'я чи номер телефону), оскільки це значення передається апаратному чіпу і зберігається у відкритому вигляді всередині флеш-пам'яті токена.

---

## 2. Церемонія реєстрації (Registration Ceremony)

Церемонія реєстрації складається з двох послідовних мережевих кроків:
1. **Ініціалізація (Options):** Клієнт звертається до бекенду із запитом на реєстрацію нового ключа. Сервер генерує криптографічно стійкий випадковий челендж (32 байти), фіксує його в сесії з таймаутом життя 60–120 секунд і повертає конфігураційний об'єкт `PublicKeyCredentialCreationOptions`.
2. **Верифікація (Attestation Verification):** Браузер викликає `navigator.credentials.create()`, отримує від автентифікатора пару ключів і надсилає на сервер двійкові об'єкти `clientDataJSON` та `attestationObject`. Сервер перевіряє криптографічні інваріанти, витягує відкритий ключ і зберігає його в базі даних.

### Етап 1: Генерація опцій реєстрації

Під час формування опцій реєстрації сервер вказує власний `rpId` (домен сайту), список підтримуваних криптографічних алгоритмів (`pubKeyCredParams`) та вимоги до автентифікатора. Параметр `residentKey: "required"` вказує операційній системі створити Discoverable Credential (Passkey), що дозволить у майбутньому входити в один клік без попереднього введення логіна.

:::tabs
```ts
import crypto from "node:crypto";

export interface RegistrationOptions {
  rp: { name: string; id: string };
  user: { id: string; name: string; displayName: string };
  challenge: string; // Base64URL
  pubKeyCredParams: Array<{ type: "public-key"; alg: number }>;
  timeout: number;
  authenticatorSelection: {
    residentKey: "required";
    userVerification: "preferred";
  };
}

export function generateRegistrationOptions(
  user: { id: string; email: string; displayName: string },
  rpId: string
): RegistrationOptions {
  // Генеруємо 32 байти випадкового виклику через CSPRNG
  const challengeBuffer = crypto.randomBytes(32);
  const challenge = challengeBuffer.toString("base64url");

  return {
    rp: {
      name: "Acme Cloud Platform",
      id: rpId,
    },
    user: {
      id: Buffer.from(user.id).toString("base64url"),
      name: user.email,
      displayName: user.displayName,
    },
    challenge,
    pubKeyCredParams: [
      { type: "public-key", alg: -7 },   // ES256 (ECDSA поверх NIST P-256 з SHA-256)
      { type: "public-key", alg: -8 },   // Ed25519 (EdDSA)
      { type: "public-key", alg: -257 }, // RS256 (RSA 2048 з SHA-256)
    ],
    timeout: 60000,
    authenticatorSelection: {
      residentKey: "required", // Вимагаємо створення Passkey для входу в один клік
      userVerification: "preferred",
    },
  };
}
```
```cpp
#include <string>
#include <vector>
#include <chrono>
#include <random>
#include <openssl/rand.h>

struct RegistrationOptions {
    std::string rp_id;
    std::string rp_name;
    std::string user_id_b64;
    std::string user_name;
    std::string user_display_name;
    std::string challenge_b64;
    uint32_t timeout_ms;
    std::string resident_key;
    std::string user_verification;
};

// Допоміжне кодування у Base64URL без знаків вирівнювання '='
std::string to_base64url(const unsigned char* data, size_t len) {
    static const char tbl[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_";
    std::string res;
    res.reserve(((len + 2) / 3) * 4);
    for (size_t i = 0; i < len; i += 3) {
        uint32_t b = (data[i] << 16) | 
                     ((i + 1 < len ? data[i + 1] : 0) << 8) | 
                     (i + 2 < len ? data[i + 2] : 0);
        res.push_back(tbl[(b >> 18) & 0x3F]);
        res.push_back(tbl[(b >> 12) & 0x3F]);
        if (i + 1 < len) res.push_back(tbl[(b >> 6) & 0x3F]);
        if (i + 2 < len) res.push_back(tbl[b & 0x3F]);
    }
    return res;
}

RegistrationOptions generate_registration_options(
    const std::string& user_id,
    const std::string& email,
    const std::string& display_name,
    const std::string& rp_id
) {
    unsigned char challenge_bytes[32];
    RAND_bytes(challenge_bytes, sizeof(challenge_bytes));

    RegistrationOptions opt;
    opt.rp_id = rp_id;
    opt.rp_name = "Acme Cloud Platform";
    opt.user_id_b64 = to_base64url(reinterpret_cast<const unsigned char*>(user_id.data()), user_id.size());
    opt.user_name = email;
    opt.user_display_name = display_name;
    opt.challenge_b64 = to_base64url(challenge_bytes, sizeof(challenge_bytes));
    opt.timeout_ms = 60000;
    opt.resident_key = "required";
    opt.user_verification = "preferred";
    return opt;
}
```
:::

---

### Етап 2: Верифікація реєстрації (Двійковий розбір authData)

Отримавши відповідь від клієнта, бекенд зобов'язаний розібрати сирий масив байтів `authData`. Цей буфер має жорстку бінарну структуру: перші 32 байти відведено під хеш домену `rpIdHash`, 33-й байт містить бітову маску прапорців (`flags`), байти 34–37 зберігають 32-бітний беззнаковий цілий лічильник підписів `signCount` у порядку байтів Big-Endian.

Якщо під час реєстрації було встановлено прапорець `AT` (біт 6 байта `flags`), починаючи з 37-го байта слідує секція `attestedCredentialData`:
- 16 байтів — ідентифікатор моделі автентифікатора (AAGUID);
- 2 байти — довжина ідентифікатора ключа `L` (uint16 Big-Endian);
- `L` байтів — значення `credentialId`;
- решта буфера — відкритий ключ у форматі CBOR / COSE.

:::tabs
```ts
import crypto from "node:crypto";

export interface ParsedAuthData {
  rpIdHash: Buffer;
  flags: {
    userPresent: boolean;
    userVerified: boolean;
    backupEligible: boolean;
    backupState: boolean;
    hasAttestedCredentialData: boolean;
  };
  signCount: number;
  aaguid?: string;
  credentialId?: Buffer;
  cosePublicKey?: Buffer;
}

export function parseAuthData(authData: Buffer): ParsedAuthData {
  if (authData.length < 37) {
    throw new Error("authData buffer is too small (< 37 bytes)");
  }

  const rpIdHash = authData.subarray(0, 32);
  const flagByte = authData[32];
  const signCount = authData.readUInt32BE(33);

  const flags = {
    userPresent: (flagByte & 0x01) !== 0,
    userVerified: (flagByte & 0x04) !== 0,
    backupEligible: (flagByte & 0x08) !== 0,
    backupState: (flagByte & 0x10) !== 0,
    hasAttestedCredentialData: (flagByte & 0x40) !== 0,
  };

  let offset = 37;
  let aaguid: string | undefined;
  let credentialId: Buffer | undefined;
  let cosePublicKey: Buffer | undefined;

  if (flags.hasAttestedCredentialData) {
    if (authData.length < offset + 18) {
      throw new Error("Truncated attested credential data header");
    }

    const aaguidBuf = authData.subarray(offset, offset + 16);
    aaguid = aaguidBuf.toString("hex").replace(
      /(.{8})(.{4})(.{4})(.{4})(.{12})/,
      "$1-$2-$3-$4-$5"
    );
    offset += 16;

    const credIdLen = authData.readUInt16BE(offset);
    offset += 2;

    if (authData.length < offset + credIdLen) {
      throw new Error("Truncated credentialId buffer");
    }

    credentialId = authData.subarray(offset, offset + credIdLen);
    offset += credIdLen;

    // Решта буфера містить бінарний CBOR COSE Public Key
    cosePublicKey = authData.subarray(offset);
  }

  return { rpIdHash, flags, signCount, aaguid, credentialId, cosePublicKey };
}

export function verifyRegistrationResponse(params: {
  clientDataJSON: Buffer;
  authData: Buffer;
  expectedChallenge: string;
  expectedOrigin: string;
  expectedRpId: string;
}) {
  // 1. Декодування та перевірка clientDataJSON
  const clientData = JSON.parse(params.clientDataJSON.toString("utf8"));
  if (clientData.type !== "webauthn.create") {
    throw new Error(`Invalid ceremony type: ${clientData.type}`);
  }
  if (clientData.challenge !== params.expectedChallenge) {
    throw new Error("Challenge mismatch");
  }
  if (clientData.origin !== params.expectedOrigin) {
    throw new Error(`Origin mismatch: expected ${params.expectedOrigin}, got ${clientData.origin}`);
  }

  // 2. Двійковий розбір та перевірка authData
  const parsed = parseAuthData(params.authData);

  const expectedRpIdHash = crypto.createHash("sha256").update(params.expectedRpId).digest();
  if (!parsed.rpIdHash.equals(expectedRpIdHash)) {
    throw new Error("rpIdHash does not match expected RP ID");
  }

  if (!parsed.flags.userPresent) {
    throw new Error("User Presence (UP) flag was not set");
  }
  if (!parsed.flags.hasAttestedCredentialData || !parsed.credentialId || !parsed.cosePublicKey) {
    throw new Error("Attested Credential Data is missing from registration");
  }

  return {
    credentialId: parsed.credentialId.toString("base64url"),
    cosePublicKey: parsed.cosePublicKey,
    signCount: parsed.signCount,
    aaguid: parsed.aaguid!,
    backupEligible: parsed.flags.backupEligible,
    backupState: parsed.flags.backupState,
  };
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <stdexcept>
#include <openssl/sha.h>

struct ParsedFlags {
    bool user_present;
    bool user_verified;
    bool backup_eligible;
    bool backup_state;
    bool has_attested_data;
};

struct ParsedAuthData {
    std::vector<uint8_t> rp_id_hash;
    ParsedFlags flags;
    uint32_t sign_count;
    std::string aaguid;
    std::vector<uint8_t> credential_id;
    std::vector<uint8_t> cose_public_key;
};

ParsedAuthData parse_auth_data(const std::vector<uint8_t>& buf) {
    if (buf.size() < 37) {
        throw std::runtime_error("authData too short (< 37 bytes)");
    }

    ParsedAuthData res;
    res.rp_id_hash.assign(buf.begin(), buf.begin() + 32);

    uint8_t f = buf[32];
    res.flags.user_present    = (f & 0x01) != 0;
    res.flags.user_verified   = (f & 0x04) != 0;
    res.flags.backup_eligible = (f & 0x08) != 0;
    res.flags.backup_state    = (f & 0x10) != 0;
    res.flags.has_attested_data = (f & 0x40) != 0;

    res.sign_count = (static_cast<uint32_t>(buf[33]) << 24) |
                     (static_cast<uint32_t>(buf[34]) << 16) |
                     (static_cast<uint32_t>(buf[35]) << 8)  |
                     (static_cast<uint32_t>(buf[36]));

    size_t offset = 37;
    if (res.flags.has_attested_data) {
        if (buf.size() < offset + 18) {
            throw std::runtime_error("Truncated attested credential data header");
        }

        // Форматуємо AAGUID (16 байтів) у стандартний рядок UUID
        char aaguid_hex[37];
        snprintf(aaguid_hex, sizeof(aaguid_hex),
                 "%02x%02x%02x%02x-%02x%02x-%02x%02x-%02x%02x-%02x%02x%02x%02x%02x%02x",
                 buf[offset], buf[offset+1], buf[offset+2], buf[offset+3],
                 buf[offset+4], buf[offset+5], buf[offset+6], buf[offset+7],
                 buf[offset+8], buf[offset+9], buf[offset+10], buf[offset+11],
                 buf[offset+12], buf[offset+13], buf[offset+14], buf[offset+15]);
        res.aaguid = aaguid_hex;
        offset += 16;

        uint16_t cred_id_len = (static_cast<uint16_t>(buf[offset]) << 8) | buf[offset + 1];
        offset += 2;

        if (buf.size() < offset + cred_id_len) {
            throw std::runtime_error("Truncated credential_id");
        }
        res.credential_id.assign(buf.begin() + offset, buf.begin() + offset + cred_id_len);
        offset += cred_id_len;

        // Залишок буфера — COSE Public Key
        res.cose_public_key.assign(buf.begin() + offset, buf.end());
    }

    return res;
}
```
:::

---

## 3. Перетворення COSE Key у стандартний формат SPKI DER

Для криптографічної перевірки підписів відкритий ключ необхідно імпортувати у стандартні бібліотеки (Node.js `crypto`, WebCrypto, OpenSSL). Для найпоширенішого алгоритму ES256 (ECDSA P-256) мапа COSE містить дві 32-байтні координати `X` (ключ `-2`) та `Y` (ключ `-3`).

Щоб перетворити ці координати на стандартний сертифікатний формат SubjectPublicKeyInfo (SPKI DER), виконується конкатенація:
1. **Статичний ASN.1 заголовок для P-256 (26 байтів):** SEQUENCE, що містить OID алгоритму `id-ecPublicKey` (1.2.840.10045.2.1) та OID іменованої кривої `prime256v1` / `secp256r1` (1.2.840.10045.3.1.7).
2. **Нестиснена точка еліптичної кривої (65 байтів):** Префікс `0x04` (позначка нестисненої точки) + 32 байти координати `X` + 32 байти координати `Y`.

Разом отримується 91-байтний буфер SPKI DER, який безпосередньо приймається будь-яким криптографічним рушієм.

---

## 4. Церемонія автентифікації (Assertion Verification)

Під час автентифікації клієнт повертає на сервер чотири сутності:
1. `credentialId` — ідентифікатор ключа, за яким сервер знаходить раніше збережений відкритий ключ у базі даних;
2. `clientDataJSON` — контекст операції (челендж, origin, тип `"webauthn.get"`);
3. `authenticatorData` — заголовок `authData` (37+ байтів) з прапорцями присутності та лічильником `signCount`;
4. `signature` — бінарний цифровий підпис у форматі ASN.1 DER SEQUENCE `(r, s)`.

### Формування підписуваного блоку (Signed Data)

Автентифікатор підписує не сирий JSON, а конкатенацію двох масивів байтів:

```
SignedData = authenticatorData || SHA-256(clientDataJSON)
```

Сервер обчислює 32-байтний хеш `SHA-256` від отриманого буфера `clientDataJSON`, з'єднує його з буфером `authenticatorData` і передає отриманий блок разом із підписом та відкритим ключем у функцію криптографічної перевірки.

:::tabs
```ts
import crypto from "node:crypto";

export function importCoseP256Key(xCoord: Buffer, yCoord: Buffer): crypto.KeyObject {
  // Створюємо нестиснену точку еліптичної кривої: 0x04 || X (32B) || Y (32B)
  const uncompressedPoint = Buffer.concat([Buffer.from([0x04]), xCoord, yCoord]);

  // Заголовок ANSI X9.62 / PKIX для кривої prime256v1 (P-256)
  const ecP256DerHeader = Buffer.from([
    0x30, 0x59, // SEQUENCE (89 байтів)
    0x30, 0x13, // SEQUENCE (ідентифікатор алгоритму, 19 байтів)
    0x06, 0x07, 0x2a, 0x86, 0x48, 0xce, 0x3d, 0x02, 0x01, // OID id-ecPublicKey
    0x06, 0x08, 0x2a, 0x86, 0x48, 0xce, 0x3d, 0x03, 0x01, 0x07, // OID prime256v1
    0x03, 0x42, 0x00, // BIT STRING (66 байтів, 0 невикористаних бітів)
  ]);

  const spkiDer = Buffer.concat([ecP256DerHeader, uncompressedPoint]);
  return crypto.createPublicKey({ key: spkiDer, format: "der", type: "spki" });
}

export function verifyAuthenticationAssertion(params: {
  authData: Buffer;
  clientDataJSON: Buffer;
  signature: Buffer;
  publicKeySpki: Buffer;
  storedSignCount: number;
  expectedChallenge: string;
  expectedOrigin: string;
  expectedRpId: string;
}) {
  // 1. Валідація clientDataJSON
  const clientData = JSON.parse(params.clientDataJSON.toString("utf8"));
  if (clientData.type !== "webauthn.get") {
    throw new Error(`Invalid assertion type: ${clientData.type}`);
  }
  if (clientData.challenge !== params.expectedChallenge) {
    throw new Error("Challenge mismatch");
  }
  if (clientData.origin !== params.expectedOrigin) {
    throw new Error(`Origin mismatch: expected ${params.expectedOrigin}, got ${clientData.origin}`);
  }

  // 2. Валідація authData
  const parsed = parseAuthData(params.authData);
  const expectedRpIdHash = crypto.createHash("sha256").update(params.expectedRpId).digest();
  if (!parsed.rpIdHash.equals(expectedRpIdHash)) {
    throw new Error("rpIdHash does not match RP ID");
  }
  if (!parsed.flags.userPresent) {
    throw new Error("User Presence flag is not set");
  }

  // 3. Формування підписуваного повідомлення: authData || sha256(clientDataJSON)
  const clientDataHash = crypto.createHash("sha256").update(params.clientDataJSON).digest();
  const signedData = Buffer.concat([params.authData, clientDataHash]);

  // 4. Криптографічна перевірка підпису ECDSA (ASN.1 DER)
  const publicKey = crypto.createPublicKey({
    key: params.publicKeySpki,
    format: "der",
    type: "spki",
  });

  const isSignatureValid = crypto.verify(
    "sha256",
    signedData,
    publicKey,
    params.signature
  );

  if (!isSignatureValid) {
    throw new Error("Cryptographic signature verification failed");
  }

  // 5. Перевірка лічильника підписів (signCount)
  if (parsed.signCount > 0 || params.storedSignCount > 0) {
    if (parsed.signCount <= params.storedSignCount) {
      throw new Error(
        `Cloned authenticator detected: incoming signCount (${parsed.signCount}) <= stored (${params.storedSignCount})`
      );
    }
  }

  return {
    verified: true,
    newSignCount: parsed.signCount,
  };
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <stdexcept>
#include <openssl/evp.h>
#include <openssl/sha.h>
#include <openssl/x509.h>

bool verify_ecdsa_signature(
    const std::vector<uint8_t>& auth_data,
    const std::vector<uint8_t>& client_data_json,
    const std::vector<uint8_t>& signature_der,
    const std::vector<uint8_t>& public_key_spki_der
) {
    // 1. Обчислюємо SHA-256 від clientDataJSON
    unsigned char client_hash[SHA256_DIGEST_LENGTH];
    SHA256(client_data_json.data(), client_data_json.size(), client_hash);

    // 2. Формуємо SignedData = authData || SHA-256(clientDataJSON)
    std::vector<uint8_t> signed_data = auth_data;
    signed_data.insert(signed_data.end(), client_hash, client_hash + SHA256_DIGEST_LENGTH);

    // 3. Імпортуємо відкритий ключ OpenSSL з формату DER SPKI
    const unsigned char* p = public_key_spki_der.data();
    EVP_PKEY* pkey = d2i_PUBKEY(nullptr, &p, static_cast<long>(public_key_spki_der.size()));
    if (!pkey) {
        throw std::runtime_error("Failed to decode SPKI public key");
    }

    // 4. Ініціалізуємо контекст перевірки підпису
    EVP_MD_CTX* md_ctx = EVP_MD_CTX_new();
    bool is_valid = false;

    if (EVP_DigestVerifyInit(md_ctx, nullptr, EVP_sha256(), nullptr, pkey) == 1) {
        int res = EVP_DigestVerify(
            md_ctx,
            signature_der.data(), signature_der.size(),
            signed_data.data(), signed_data.size()
        );
        is_valid = (res == 1);
    }

    EVP_MD_CTX_free(md_ctx);
    EVP_PKEY_free(pkey);
    return is_valid;
}
```
:::

---

## 5. Низькорівневе декодування CBOR без зовнішніх залежностей

У веб-розробці для парсингу `attestationObject` часто тягнуть важкі сторонні бібліотеки. Проте для розбору відкритого ключа COSE достатньо знати базові правила кодування CBOR (Concise Binary Object Representation, RFC 8949).

CBOR використовує перший байт кожного елемента (початковий байт) для визначення головного типу (старші 3 біти) та додаткової інформації (молодші 5 бітів):
- **Тип 0 (0x00..0x17):** Беззнакове ціле число. Значення від 0 до 23 кодуються прямо в молодших 5 бітах.
- **Тип 1 (0x20..0x37):** Від'ємне ціле число. Значення `n` обчислюється як `-1 - val`. Наприклад, алгоритм ES256 має код `-7`, що кодується байтом `0x26` (`-1 - 6 = -7`).
- **Тип 2 (0x40..0x57):** Байт-рядок (Byte String). За початковим байтом слідує довжина даних, а потім — сирі байти (саме так кодуються 32-байтні координати `X` та `Y`).
- **Тип 3 (0x60..0x77):** Текстовий рядок UTF-8.
- **Тип 5 (0xA0..0xB7):** Словник (Map). Молодші 5 бітів вказують кількість пар «ключ-значення». Для стандартного ключа P-256 мапа має 5 пар і починається з байта `0xA5`.

### Схема розбору мапи COSE P-256

Типовий відкритий ключ ECDSA P-256 у буфері `cosePublicKey` має вигляд:
```
A5                # Map з 5 елементів
  01 02           # 1 (kty): 2 (EC2)
  03 26           # 3 (alg): -7 (ES256)
  20 01           # -1 (crv): 1 (P-256)
  21 58 20 [32B]  # -2 (x): 32 байти координати X
  22 58 20 [32B]  # -3 (y): 32 байти координати Y
```

Простий лінійний сканер перевіряє сигнатуру `0xA5`, зчитує зміщення для ключів `0x21` (`-2`, координата X) та `0x22` (`-3`, координата Y) і витягує рівно по 32 байти для кожної координати без необхідності підключення багатотисячних бібліотек.

---

## 6. Інтеграція в HTTP-контролери та керування сесіями

Верифікатор інтегрується в типовий REST API або RPC-шар сервера. Розгляньмо типову послідовність обробки чотирьох ендпоінтів:

### 1. Ендпоінт `POST /api/auth/register/start`
- Приймає ідентифікатор користувача або пошту.
- Перевіряє, чи не перевищено ліміт запитів (Rate Limiting).
- Генерує 32 байти випадкового виклику `challenge` через CSPRNG.
- Зберігає запис `(challenge, userId, "registration", now + 2 хвилини)` у сховищі сесій (PostgreSQL або Redis).
- Повертає клієнту об'єкт `PublicKeyCredentialCreationOptions`.

### 2. Ендпоінт `POST /api/auth/register/finish`
- Приймає `clientDataJSON` та `attestationObject`.
- У межах однієї транзакції шукає виклик у базі даних і **негайно видаляє його**, запобігаючи повторній обробці.
- Викликає функцію `verifyRegistrationResponse()`.
- Зберігає отриманий `credentialId`, експортований відкритий ключ `public_key_spki`, початковий `signCount` та прапорці резервування `backup_eligible`/`backup_state` у таблицю `passkey_credentials`.
- Повертає статус успіху `201 Created`.

### 3. Ендпоінт `POST /api/auth/login/start`
- Якщо використовується безпарольний вхід за вибором ключа з браузера (Conditional UI / Discoverable Credentials), клієнт надсилає порожній запит.
- Сервер генерує 32 байти свіжого `challenge`, зберігає його із `userId = NULL` та повертає `PublicKeyCredentialRequestOptions` з порожнім масивом `allowCredentials`.

### 4. Ендпоінт `POST /api/auth/login/finish`
- Приймає `credentialId`, `clientDataJSON`, `authenticatorData`, `signature` та опційний `userHandle`.
- Знищує використаний `challenge` у сесійному сховищі.
- Знаходить запис ключа у таблиці `passkey_credentials` за `credentialId`. Якщо ключ не знайдено — повертає `401 Unauthorized`.
- Викликає функцію `verifyAuthenticationAssertion()`.
- Оновлює поле `sign_count` та `last_used_at` у базі даних.
- Створює нову авторизовану сесію для користувача `user_id` і встановлює захищені `HTTP-only`, `Secure`, `SameSite=Lax` сесійні cookie або видає JWT-токен доступу.

---

## 7. Автоматизоване тестування через Virtual Authenticators

Для інтеграційного тестування WebAuthn у CI/CD без фізичного дотику людини використовується механізм віртуальних автентифікаторів (Virtual Authenticator), стандартизований у W3C WebDriver та підтримуваний рушіями Chromium через Chrome DevTools Protocol (CDP):

```ts
import { test, expect } from "@playwright/test";

test("успішна безпарольна реєстрація та вхід через віртуальний Passkey", async ({ page }) => {
  // Створюємо сесію CDP до браузера
  const client = await page.context().newCDPSession(page);

  // Вмикаємо емуляцію середовища WebAuthn
  await client.send("WebAuthn.enable");

  // Додаємо віртуальний біометричний автентифікатор із підтримкою Passkeys
  const { authenticatorId } = await client.send("WebAuthn.addVirtualAuthenticator", {
    options: {
      protocol: "ctap2",
      transport: "internal",
      hasResidentKey: true,
      hasUserVerification: true,
      isUserVerified: true,
      automaticPresenceSimulation: true,
    },
  });

  // Відкриваємо сторінку реєстрації
  await page.goto("https://example.com/register");
  await page.fill("#email", "alice@example.com");
  await page.click("#btn-register-passkey");

  // Перевіряємо успішне створення запису в UI
  await expect(page.locator("#status-message")).toHaveText("Ключ успішно зареєстровано!");

  // Тестуємо вхід в один клік
  await page.goto("https://example.com/login");
  await page.click("#btn-login-passkey");

  // Перевіряємо авторизований стан
  await expect(page.locator("#user-profile")).toBeVisible();

  // Прибираємо віртуальний автентифікатор
  await client.send("WebAuthn.removeVirtualAuthenticator", { authenticatorId });
});
```

---

## 9. Підтримка альтернативних алгоритмів (Ed25519 та RS256)

Хоча алгоритм ES256 (ECDSA P-256) є обов'язковим для всіх клієнтів WebAuthn, деякі корпоративні апаратні токени (YubiKey з прошивкою 5.2+, Nitrokey) та сучасні операційні системи підтримують алгоритми Ed25519 (COSE `alg = -8`) та RS256 (COSE `alg = -257`).

### Обробка Ed25519 (OKP / Edwards25519)
Крива Ed25519 має суттєві переваги над ECDSA: детермінований підпис без потреби в якісному джерелі ентропії під час кожного підпису (захист від витоку закритого ключа через повтор nonce `k`), захист від атак побічними каналами за часом та вищу швидкість перевірки.

У форматі COSE відкритий ключ Ed25519 має `kty = 1` (OKP) та `crv = 6` (Ed25519). 32-байтове поле `x` (ключ `-2`) є безпосереднім відкритим ключем кривої. Для імпорту в OpenSSL чи Node.js формується SPKI DER заголовок з OID `1.3.101.112` (id-Ed25519):

```
30 2A 30 05 06 03 2B 65 70 03 21 00 [32 байти відкритого ключа]
```

Підпис Ed25519 має фіксовану довжину 64 байти (конкатенація точки `R` та скаляра `S`), без пакування в ASN.1 DER SEQUENCE.

### Обробка RS256 (RSA PKCS#1 v1.5)
Для старих смарт-карток та апаратних модулів TPM 1.2/2.0 часто використовується RSA з довжиною ключа 2048 бітів. Мапа COSE повертає два поля:
- Ключ `-2` (`n`): модуль RSA (256 байтів для 2048-бітного ключа);
- Ключ `-3` (`e`): публічна експонента (зазвичай 3 байти: `0x01, 0x00, 0x01` для 65537).

Сервер формує структуру ASN.1 `RSAPublicKey` (RFC 8017), що загортається у стандартний SPKI DER блок, і верифікує підпис методом `SHA256withRSA`.

---

## 10. Стратегія міграції з паролів на Passkeys у діючій системі

Впровадження WebAuthn у продакшн-системі з мільйонами користувачів із традиційними паролями відбувається у три послідовні фази:

### Фаза 1: Passkey як другий фактор (2FA / Step-Up Auth)
- Користувач продовжує вводити логін і пароль.
- Після перевірки хешу пароля замість SMS або TOTP-коду браузер викликає `navigator.credentials.get()`.
- Це дозволяє користувачам ознайомитися з роботою біометрії або апаратного токена без ризику втратити доступ до акаунта через зміну пристрою.

### Фаза 2: Гібридний вхід (Passwordless Upgrade)
- В особистому кабінеті користувача з'являється пропозиція: «Створити Passkey для швидкого входу без пароля».
- Після успішної реєстрації ключа на формі входу активується умовний інтерфейс (Conditional UI): у полі введення логіна браузер виводить список збережених ключів.
- Якщо користувач обирає збережений Passkey, вхід відбувається миттєво за біометрією. Якщо користувач сидить за чужим комп'ютером — залишається кнопка «Увійти за допомогою пароля та резервного коду».

### Фаза 3: Повна відмова від паролів (Pure Passwordless)
- Для нових користувачів реєстрація пароля взагалі не пропонується: акаунт створюється через введення пошти та генерацію Passkey.
- Відновлення доступу у разі втрати всіх пристроїв базується на одноразових магічних посиланнях, надісланих на верифіковану пошту, або довірених резервних контактах, а не на застарілих паролях чи вразливих «таємних питаннях».

---

## 11. Налагодження та телеметрія помилок верифікації

Діагностика помилок WebAuthn на бекенді ускладнюється тим, що клієнтська частина повертає лише загальні винятки JavaScript (`NotAllowedError`, `SecurityError`, `InvalidStateError`). Щоб швидко локалізувати збої в розподіленій системі, бекенд повинен вести структурований аудит-лог із такими полями:

```json
{
  "event": "webauthn_verification_failed",
  "reason": "origin_mismatch",
  "expected_origin": "https://example.com",
  "received_origin": "https://login.example.com",
  "rp_id": "example.com",
  "ceremony": "assertion",
  "user_id": "usr_94a8f2bc",
  "credential_id_prefix": "a1b2c3d4...",
  "client_data_type": "webauthn.get",
  "sign_count_stored": 42,
  "sign_count_received": 42,
  "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
  "ip_address_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "timestamp": "2026-08-20T10:15:30.125Z"
}
```

Зверніть увагу: IP-адреса та конфіденційні ідентифікатори хешуються або маскуються відповідно до вимог GDPR, а відкриті ключі та підписи не друкуються у відкриті логи, щоб уникнути витоку метаданих.

---

## 13. Step-Up автентифікація та примусова біометрична верифікація

Для чутливих операцій усередині застосунку (зміна фінансових реквізитів, виведення коштів, зміна прав доступу) бекенд може вимагати підтвердження операції за допомогою наявного Passkey з примусовою вимогою `userVerification: "required"`:

1. **Ініціалізація чутливої дії:** Клієнт надсилає запит на виконання операції `POST /api/account/transfer`.
2. **Генерація спеціального виклику:** Сервер створює челендж, але замість загального входу прив'язує його до конкретної транзакції (наприклад, хеш суми та отримувача платежу передається як частина челенджу).
3. **Примусова верифікація:** У `PublicKeyCredentialRequestOptions` сервер суворо вказує `userVerification: "required"` та передає конкретний `credentialId` у масиві `allowCredentials`.
4. **Перевірка біта UV:** Бекенд перевіряє не лише валідність підпису, але й те, що біт 2 (`UV`, 0x04) байта `flags` у структурі `authData` дорівнює 1. Якщо користувач просто торкнувся датчика без сканування пальця чи введення PIN-коду (біт `UV = 0`), транзакція відхиляється.

---

## 14. Безпечні дефолти та захист від типових атак

Під час впровадження власного верифікатора WebAuthn на бекенді необхідно дотримуватися обов'язкових правил безпеки:

### Одноразовість челенджу (Replay Protection)
Кожен згенерований `challenge` має бути використаний рівно один раз. Щойно надійшов запит верифікації (незалежно від того, успішно завершилася перевірка чи сталася помилка), запис виклику з бази даних або сховища Redis негайно знищується в межах тієї самої транзакції. Це гарантує неможливість повторного надсилання перехопленого пакету даних.

### Суворе порівняння походження (Origin Matching)
Рядок `clientDataJSON.origin` має порівнюватися на точний збіг (`===`). Сервер не повинен використовувати нечіткий пошук підрядка (наприклад, `origin.includes("example.com")`), оскільки зловмисник зможе пройти перевірку з фішингового домену `example.com.evil-attacker.org`.

### Обробка відсутності зростання signCount
Для апаратних фізичних токенів (YubiKey) `signCount` збільшується на одиницю при кожному натисканні кнопки. Якщо на сервер приходить значення `signCount`, що є меншим або дорівнює раніше збереженому, це свідчить про створення несанкціонованої копії (клону) фізичного чіпа. Проте для синхронізованих Passkeys (Apple Keychain, Google Password Manager) `signCount` зазвичай дорівнює 0, оскільки ключ живе на багатьох пристроях. Логіка бекенда зобов'язана активувати захист від клонування лише за умови, що обидва лічильники (вхідний та збережений) строго більші за нуль.

### Захист від викликів із чужих фреймів (Permissions Policy та Cross-Origin)
Якщо ваш сервіс дозволяє вбудовування у сторонні сторінки через `<iframe>`, зловмисник може спробувати ініціювати реєстрацію або вхід від імені жертви. За замовчуванням браузери блокують виклики `navigator.credentials` у крос-доменних фреймах, якщо батьківська сторінка явно не передала заголовок або атрибут дозволу:
```html
<iframe src="https://auth.example.com" allow="publickey-credentials-get 'self' https://auth.example.com"></iframe>
```
Сервер зобов'язаний перевіряти поле `clientDataJSON.crossOrigin`: якщо ваш застосунок не призначений для роботи всередині сторонніх фреймів, отримання `crossOrigin === true` свідчить про спробу атаки зловмисника через клікджекінг чи вбудований контекст і вимагає негайного відхилення операції.

### Захист від зловживань та перебору (Rate Limiting)
Хоча підібрати 256-бітний підпис ECDSA математично неможливо, бекенд повинен обмежувати частоту запитів до ендпоінтів `/register/start` та `/login/start` за IP-адресою та ідентифікатором користувача для захисту від вичерпання ресурсів генератора випадкових чисел та засмічення таблиці активних сесійних челенджів.
