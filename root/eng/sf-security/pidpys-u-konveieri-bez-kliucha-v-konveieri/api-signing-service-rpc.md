# 📋 Інтерфейс та протокол служби віддаленого підписання: RPC-контракт, OIDC клейми та схема аудиту

Служба віддаленого підписання (англ. *Remote Signing Service*) забезпечує криптографічне засвідчення скомпільованих бінарних файлів, образів контейнерів та прошивок без передавання закритого ключа в незахищене середовище конвеєра CI/CD. Раннер збірки взаємодіє зі службою через строго типізований інтерфейс віддаленого виклику процедур (gRPC / Protocol Buffers) або захищений REST API, передаючи винятково 32-байтовий або 64-байтовий криптографічний геш артефакту та короткоживучий OIDC-токен автентифікації. Ця специфікація описує протокольний контракт, структуру клеймів ідентичності, декларативні правила політики допуску та схему незмінного журналу аудиту.

---

### Призначення та архітектурні інваріанти інтерфейсу

Інтерфейс віддаленого підписання спроєктовано за принципом мінімальних привілеїв та нульової довіри до клієнта. Головна мета API полягає в тому, щоб надати раннеру конвеєра можливість отримати валідний цифровий підпис артефакту без прямого доступу до апаратного модуля безпеки (HSM) або закритого ключа.

Протокол базується на п'яти фундаментальних інваріантах:
1. **Інваріант фіксованого розміру повідомлення:** Клієнт ніколи не передає тіло артефакту через мережу. Незалежно від того, чи має вихідний файл розмір у 10 кілобайтів (завантажувач мікроконтролера) чи 50 гігабайтів (образ віртуальної машини), корисне навантаження запиту завжди обмежене фіксованим 32-байтовим дайджестом для SHA-256 або 64-байтовим для SHA-512. Це усуває проблему пропускної здатності каналу та запобігає атакам на вичерпання пам'яті шлюзу.
2. **Інваріант одноразової ідентичності:** Кожен виклик мусить супроводжуватися свіжим токеном OIDC ID Token, згенерованим CI-провайдером для конкретного кроку збірки. Повторне використання токенів із попередніх запусків або використання статичних API-ключів категорично заборонено.
3. **Інваріант суворої типізації та бінарної сумісності:** Транспортний рівень використовує Protocol Buffers v3 та gRPC поверх HTTP/2. Це гарантує ефективну серіалізацію, мультиплексування запитів в одному TCP-з'єднанні та захист від помилок розбору текстових форматів.
4. **Інваріант повної аудитованості:** Жодна криптографічна операція в HSM не виконується без попередньої успішної фіксації контексту запиту в незмінному журналі аудиту. Якщо підсистема аудиту недоступна, сервіс повертає помилку `INTERNAL` і блокує підпис (принцип Fail-Close).
5. **Інваріант декларативного контролю:** Рішення про допуск до підпису ухвалюється не клієнтом і не апаратним HSM, а проміжним рушієм політик (Policy Engine), який зіставляє OIDC-клейми токена з правилами доступу до конкретного слота ключа.

---

### Специфікація Protocol Buffers (v3)

Взаємодія між клієнтом у раннері та шлюзом підпису стандартизована у вигляді сервісу `SigningAuthorityService`. Усі бінарні поля передаються у сирому байтовому вигляді або у форматі Base64 у разі використання JSON-транспорту через gRPC-Gateway.

```protobuf
syntax = "proto3";

package security.signing.v1;

option go_package = "github.com/company/security/signing/v1;signingv1";
option java_multiple_files = true;
option java_package = "com.company.security.signing.v1";

// Головний сервіс криптографічного засвідчення артефактів
service SigningAuthorityService {
  // Запит на підписання криптографічного дайджесту
  rpc SignDigest(SignDigestRequest) returns (SignDigestResponse);

  // Отримання публічного сертифіката та ланцюжка довіри
  rpc GetCertificateChain(GetCertificateChainRequest) returns (GetCertificateChainResponse);

  // Перевірка чинності підпису та відповідності політиці аудиту
  rpc VerifySignature(VerifySignatureRequest) returns (VerifySignatureResponse);
}

// Алгоритми цифрового підпису, що підтримуються апаратним HSM
enum SignatureAlgorithm {
  SIGNATURE_ALGORITHM_UNSPECIFIED = 0;
  SIGNATURE_ALGORITHM_ECDSA_P256_SHA256 = 1;
  SIGNATURE_ALGORITHM_ECDSA_P384_SHA384 = 2;
  SIGNATURE_ALGORITHM_ED25519 = 3;
  SIGNATURE_ALGORITHM_RSA_PSS_2048_SHA256 = 4;
  SIGNATURE_ALGORITHM_RSA_PSS_4096_SHA512 = 5;
}

// Запит на підписання дайджесту
message SignDigestRequest {
  // Криптографічний дайджест артефакту (рівно 32 байти для SHA-256 або 64 байти для SHA-512)
  bytes digest = 1;

  // Бажаний алгоритм цифрового підпису
  SignatureAlgorithm algorithm = 2;

  // Ефемерний OIDC ID Token у форматі JWT, виданий провайдером CI/CD
  string oidc_token = 3;

  // Логічний ідентифікатор або аліас ключа в апаратному модулі HSM (наприклад, "release-firmware-v2")
  string key_alias = 4;

  // Додаткові метадані збірки для фіксації в журналі аудиту
  map<string, string> build_metadata = 5;
}

// Відповідь із цифровим підписом та криптографічним сертифікатом
message SignDigestResponse {
  // Сирий бінарний цифровий підпис (у форматі IEEE P1363 [r || s] або DER для ECDSA)
  bytes signature = 1;

  // Повний ланцюжок сертифікатів X.509 у бінарному форматі DER (від сертифіката підписувача до кореня)
  repeated bytes certificate_chain_der = 2;

  // Унікальний криптографічний ідентифікатор транзакції у журналі аудиту (UUID v4 або Merkle Leaf Hash)
  string audit_record_id = 3;

  // Криптографічний штамп часу (RFC 3161 Time-Stamp Token), згенерований довіреним сервером TSA
  bytes timestamp_token = 4;

  // Unix-час створення підпису в наносекундах
  int64 signed_at_unix_nano = 5;
}

// Запит на отримання публічного ланцюжка сертифікатів
message GetCertificateChainRequest {
  string key_alias = 1;
}

message GetCertificateChainResponse {
  repeated bytes certificate_chain_der = 1;
  SignatureAlgorithm algorithm = 2;
  int64 not_before_unix = 3;
  int64 not_after_unix = 4;
}

// Запит на перевірку підпису
message VerifySignatureRequest {
  bytes digest = 1;
  bytes signature = 2;
  string key_alias = 3;
  bytes timestamp_token = 4;
}

message VerifySignatureResponse {
  bool is_valid = 1;
  string error_message = 2;
  string audit_record_id = 3;
}
```

---

### Детальний опис полів повідомлень та семантика RPC методів

Кожен RPC-метод сервісу виконує строго визначену атомарну функцію в життєвому циклі релізу:

#### Метод SignDigest
Головна операція шлюзу. Метод приймає запит `SignDigestRequest`, що містить криптографічний дайджест артефакту, OIDC JWT токен та аліас ключа.
1. Поле `digest` містить результат виконання односторонньої криптографічної геш-функції. Довжина масиву байтів перевіряється сервером до виклику будь-яких криптографічних підсистем: якщо для алгоритму `ECDSA_P256` передано дайджест розміром, відмінним від 32 байтів, сервер негайно повертає помилку `INVALID_ARGUMENT`.
2. Поле `oidc_token` передає сирий рядок JWT токена, отриманий від середовища раннера. Сервер розбирає його заголовок, визначає ідентифікатор відкритого ключа провайдера (`kid`) і перевіряє криптографічний підпис токена.
3. Поле `key_alias` визначає, який саме апаратний ключ у слотах HSM має бути використаний для операції. Це дозволяє розділяти ключі за призначенням: наприклад, ключ для тестових внутрішніх збірок (`firmware-stage`), ключ для серійних пристроїв (`firmware-prod`) або ключ підпису завантажувача другого ступеня (`bootloader-secure`).
4. Поле `build_metadata` приймає асоціативний масив рядків (ключ-значення), де раннер може передати номер версії компілятора, цільову архітектуру (`armv7m`, `x86_64`) чи геш конфігураційного файлу збірки. Ці дані не впливають на сам підпис, але незмінно зберігаються в журналі аудиту.

У відповіді `SignDigestResponse`:
1. Поле `signature` містить результат обчислення асиметричного підпису. Для кривих ECDSA (NIST P-256 / P-384) підпис за замовчуванням повертається у бінарному форматі IEEE P1363 (зчеплення координат `r` та `s`), або у форматі ASN.1 DER залежно від прапорців конфігурації.
2. Поле `certificate_chain_der` містить впорядкований список бінарних сертифікатів X.509: нульовий елемент є сертифікатом відкритого ключа, що відповідає приватному ключу підпису, наступні елементи — проміжними центрами сертифікації, а останній — кореневим сертифікатом організації.
3. Поле `audit_record_id` повертає унікальний UUID запису в журналі аудиту або геш листка у дереві Меркла. Клієнт зберігає цей ідентифікатор у супровідних документах релізу (SBOM / SLSA Provenance).
4. Поле `timestamp_token` містить бінарну криптографічну мітку часу RFC 3161 (Time-Stamp Token), створену окремим апаратним сервером часу. Це гарантує юридичну та технічну доказовість того, що підпис було створено в конкретну секунду, коли сертифікат був чинним.

---

### Специфікація OIDC клеймів (JSON Web Token)

Служба віддаленого підписання виконує криптографічну валідацію JWT-токена, отриманого з середовища раннера. Токен повинен бути підписаний асиметричним ключем довіреного провайдера ідентичності (Issuer) і містити набір стандартизованих клеймів.

| Назва поля | Тип | Опис та семантика | Приклад значення |
|---|---|---|---|
| `iss` | `string` | URL довіреного провайдера ідентичності (IdP) | `https://token.actions.githubusercontent.com` |
| `sub` | `string` | Унікальний суб'єкт контексту виконання | `repo:acme/core-os:ref:refs/tags/v1.2.0` |
| `aud` | `string` | Цільова аудиторія (Audience) шлюзу підпису | `https://signing.internal.acme.net` |
| `exp` | `integer`| Unix-час завершення дії токену (максимум 15 хв) | `1724810400` |
| `nbf` | `integer`| Unix-час початку дії токену | `1724809500` |
| `repository` | `string` | Повний шлях до репозиторію проекту | `acme-corp/firmware-platform` |
| `repository_owner` | `string` | Організація-власник репозиторію | `acme-corp` |
| `ref` | `string` | Git-посилання, на якому запущено збірку | `refs/tags/v2.4.1` |
| `ref_type` | `string` | Тип посилання: `tag` або `branch` | `tag` |
| `actor` | `string` | Обліковий запис користувача, який запустив збірку | `release-engineer-alex` |
| `sha` | `string` | 40-символьний SHA-1 або 64-символьний SHA-256 коміту | `7f8b91a2c3d4e5f60718293a4b5c6d7e8f901234` |
| `job_workflow_ref` | `string` | Повний шлях до визначення пайплайну збірки | `acme-corp/firmware-platform/.github/workflows/release.yml@refs/tags/v2.4.1` |
| `run_id` | `string` | Унікальний числовий ідентифікатор запуску CI | `10592837411` |

```json
{
  "iss": "https://token.actions.githubusercontent.com",
  "sub": "repo:acme-corp/firmware-platform:ref:refs/tags/v2.4.1",
  "aud": "https://signing.internal.acme.net",
  "exp": 1724810400,
  "nbf": 1724809500,
  "repository": "acme-corp/firmware-platform",
  "repository_owner": "acme-corp",
  "ref": "refs/tags/v2.4.1",
  "ref_type": "tag",
  "actor": "release-engineer-alex",
  "sha": "7f8b91a2c3d4e5f60718293a4b5c6d7e8f901234",
  "job_workflow_ref": "acme-corp/firmware-platform/.github/workflows/release.yml@refs/tags/v2.4.1",
  "run_id": "10592837411"
}
```

---

### Механізм перевірки OIDC токенів та управління JWKS кешем

Шлюз підпису реалізує динамічну модель перевірки криптографічних сертифікатів провайдера ідентичності:
1. **Issuer Discovery:** Під час старту сервіс зчитує конфігураційний документ за стандартом OpenID Connect Discovery за адресою `{iss}/.well-known/openid-configuration`. З отриманого документа сервіс витягує параметр `jwks_uri` (наприклад, `https://token.actions.githubusercontent.com/.well-known/jwks.json`).
2. **JWKS Кешування:** Публічні ключі провайдера завантажуються в локальну оперативну пам'ять із часом життя (TTL) 1 година. Якщо надходить токен із новим ідентифікатором ключа (`kid`), якого немає в кеші, шлюз виконує позачерговий фоновий запит до JWKS-ендпоінта для підтримки планової ротації ключів провайдером.
3. **Захист від дрейфу годинника (Clock Skew):** Перевірка полів `nbf` (Not Before) та `exp` (Expiration) враховує допустимий часовий дрейф до ±60 секунд для запобігання хибним відхиленням через незначну розсинхронізацію NTP-демонів на серверах.

---

### Схема декларативних правил політики (Policy Rules Schema)

Рушій політик (Policy Engine) оцінює запит на відповідність JSON/YAML-конфігурації перед передачею дайджесту в HSM. Конфігурація визначає, яким репозиторіям, гілкам та воркфлоу дозволено використовувати конкретний апаратний ключ.

```yaml
# Приклад схеми політики шлюзу підпису: /etc/signing-service/policies.yaml
version: "v1"
policies:
  - id: "production-firmware-policy"
    description: "Політика підписання виробничих прошивок для мікроконтролерів"
    key_alias: "hsm-slot-01-prod-firmware"
    allowed_algorithms:
      - "SIGNATURE_ALGORITHM_ECDSA_P256_SHA256"
      - "SIGNATURE_ALGORITHM_ED25519"
    conditions:
      issuer: "https://token.actions.githubusercontent.com"
      audience: "https://signing.internal.acme.net"
      repositories:
        - "acme-corp/firmware-platform"
        - "acme-corp/bootloader-core"
      allowed_ref_patterns:
        - "^refs/tags/v[0-9]+\\.[0-9]+\\.[0-9]+$"
      require_ref_type: "tag"
      allowed_workflows:
        - "acme-corp/firmware-platform/.github/workflows/release.yml@refs/tags/v*"
      allowed_actors:
        - "release-bot"
        - "lead-maintainer"
    rate_limits:
      max_requests_per_minute: 10
      max_requests_per_day: 100
    security_controls:
      require_timestamping: true
      require_audit_logging: true
```

---

### Матриця кодів помилок та статусів

Усі виклики сервісу повертають стандартизовані статуси gRPC разом із детальним кодом помилки в полі `ErrorInfo`.

| gRPC Status | Внутрішній код помилки | Причина виникнення | Дія клієнта |
|---|---|---|---|
| `UNAUTHENTICATED` | `OIDC_TOKEN_EXPIRED` | Термін дії JWT минув (`exp < current_time`) | Запросити новий OIDC-токен у середовищі CI |
| `UNAUTHENTICATED` | `OIDC_SIGNATURE_INVALID` | Підпис JWT не збігається з відкритими ключами JWKS | Перевірити налаштування Issuer URL |
| `UNAUTHENTICATED` | `OIDC_AUDIENCE_MISMATCH` | Поле `aud` у токені не відповідає URL служби підпису | Вказати коректний `audience` під час запиту токену |
| `PERMISSION_DENIED`| `POLICY_TAG_REJECTED` | Запит надійшов із гілки замість валідного релізного тегу | Запускати підпис лише на тегах `refs/tags/v*` |
| `PERMISSION_DENIED`| `POLICY_REPO_UNAUTHORIZED` | Репозиторій відсутній у білому списку для цього ключа | Звернутися до адміністратора безпеки |
| `PERMISSION_DENIED`| `POLICY_WORKFLOW_MUTATED` | Файл воркфлоу збірки не збігається із захищеним шаблоном | Відновити оригінальний release workflow |
| `INVALID_ARGUMENT` | `DIGEST_LENGTH_MISMATCH` | Довжина дайджесту не дорівнює 32 або 64 байтам | Перевірити алгоритм гешування (SHA-256/512) |
| `RESOURCE_EXHAUSTED`|`RATE_LIMIT_EXCEEDED` | Перевищено ліміт запитів для репозиторію | Додати експоненційну затримку перед повтором |
| `UNAVAILABLE` | `HSM_HARDWARE_OFFLINE` | Апаратний модуль HSM не відповідає через PKCS#11 | Повторити запит через резервний вузол |
| `INTERNAL` | `AUDIT_LOG_WRITE_FAILED` | Помилка фіксації транзакції в незмінному журналі | Сервіс блокує підпис (Fail-Close) |

---

### Схема незмінного запису журналу аудиту (Audit Envelope)

Для кожної операції підписання служба генерує канонічний JSON-об'єкт аудиту, який додається до незмінного ланцюжка (на основі Merkle Tree або HMAC-ланцюжка) та передається на зовнішній сервер централізованого моніторингу безпеки (SIEM).

```json
{
  "audit_record_version": "1.0",
  "record_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "timestamp_utc": "2026-08-28T03:20:00.124592Z",
  "client_ip": "10.240.12.45",
  "key_alias": "hsm-slot-01-prod-firmware",
  "algorithm": "SIGNATURE_ALGORITHM_ECDSA_P256_SHA256",
  "digest_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "signature_base64": "MEYCIQD+5rZ...xY=",
  "oidc_context": {
    "issuer": "https://token.actions.githubusercontent.com",
    "repository": "acme-corp/firmware-platform",
    "ref": "refs/tags/v2.4.1",
    "commit_sha": "7f8b91a2c3d4e5f60718293a4b5c6d7e8f901234",
    "actor": "release-engineer-alex",
    "workflow": ".github/workflows/release.yml",
    "run_id": "10592837411"
  },
  "policy_evaluation": {
    "policy_id": "production-firmware-policy",
    "verdict": "ALLOW",
    "matched_rules": [
      "VALID_ISSUER",
      "VALID_AUDIENCE",
      "REPO_ALLOWLIST",
      "TAG_REGEX_MATCH"
    ]
  },
  "hsm_metadata": {
    "slot_id": 1,
    "token_label": "PROD_CORE_HSM",
    "operation_duration_ms": 14.2
  },
  "previous_record_hash": "6a09e667f3bcc908e33045674395b28d7a124a9809ef123456789abcdef01234",
  "current_record_hash": "bf586e3557e1b5b4815a5f57f6b9c9f286828b49e3b3e34b123456789abcdef0"
}
```

---

### Криптографічне зчеплення записів аудиту та мітки часу

Цілісність журналу аудиту забезпечується структурою криптографічного ланцюга. Кожен новий запис `N` включає в себе криптографічний геш `SHA-256` від попереднього запису `N-1`. Завдяки цьому будь-яка спроба видалити компрометуючий запис про підпис стороннього бінарника чи відредагувати метадані руйнує весь подальший ланцюжок гешів.

Додатково кожні 100 записів або кожні 5 хвилин кореневий геш поточного ланцюжка відправляється на незалежний сервер штампів часу (TSA) за стандартом RFC 3161. Отримана цифрова мітка часу закріплює стан журналу аудиту в глобальному часі, що унеможливлює підміну історії навіть системними адміністраторами з найвищими привілеями доступу до бази даних.
