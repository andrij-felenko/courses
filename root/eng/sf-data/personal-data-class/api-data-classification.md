# 📋 Специфікація схеми класифікації даних та політик обробки

Для декларативного управління життєвим циклом, динамічним маскуванням та аудитом доступу до персональних даних у розподілених сховищах схема кожної сутності розширюється машиночитними метаданими класифікації. Політики обробки інтерпретуються шлюзами доступу (Data Gateway), каталогами даних (DataHub, OpenMetadata), механізмами розмежування прав (Apache Ranger, Immuta) та аналітичними конвеєрами обробки.

## 1. Схема анотації полів (JSON Schema Specification)

Нижче наведено специфікацію метаданих `privacy-contract-v1.json`, яка вбудовується в описи схем таблиць реляційних баз, топіків Kafka або контрактів даних (Data Contracts).

Кожне поле обов'язково декларує свій клас ідентифікованості, рівень конфіденційності, регуляторне охоплення, політику маскування за замовчуванням та правила утримання (retention).

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "FieldPrivacyClassification",
  "type": "object",
  "required": [
    "classification",
    "sensitivity_level",
    "retention",
    "masking_policy"
  ],
  "properties": {
    "classification": {
      "type": "string",
      "enum": [
        "DIRECT_IDENTIFIER",
        "QUASI_IDENTIFIER",
        "SENSITIVE_PERSONAL_DATA",
        "INTERNAL_OPERATIONAL",
        "PUBLIC"
      ],
      "description": "Таксономічний клас атрибута за його ідентифікуючою силою"
    },
    "sensitivity_level": {
      "type": "string",
      "enum": ["L0_PUBLIC", "L1_INTERNAL", "L2_CONFIDENTIAL", "L3_RESTRICTED", "L4_CRITICAL"],
      "description": "Рівень захищеності та вимоги до криптографічного захисту"
    },
    "regulatory_scope": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": ["GDPR_ART_6", "GDPR_ART_9", "HIPAA_18", "PCI_DSS", "CCPA"]
      },
      "description": "Перелік міжнародних та галузевих стандартів регулювання"
    },
    "masking_policy": {
      "type": "object",
      "required": ["default_action"],
      "properties": {
        "default_action": {
          "type": "string",
          "enum": [
            "PASS_THROUGH",
            "FULL_REDACTION",
            "PARTIAL_MASK",
            "TOKENIZE_DETERMINISTIC",
            "TOKENIZE_VAULT",
            "BUCKET_INTERVAL",
            "GENERALIZE_PREFIX"
          ],
          "description": "Базова дія шлюзу вибірки для непривілейованих запитувачів"
        },
        "mask_format": {
          "type": "string",
          "description": "Шаблон підстановки: наприклад, '****-****-****-{last4}' або '{first1}***@{domain}'"
        },
        "bucket_size": {
          "type": "integer",
          "description": "Крок інтервалу для числових полів (наприклад, 10 для віку 10–19, 20–29)"
        },
        "prefix_preserve_length": {
          "type": "integer",
          "description": "Кількість збережених провідних символів для поштових індексів або кодів"
        }
      }
    },
    "retention": {
      "type": "object",
      "required": ["max_ttl_days", "crypto_shredding"],
      "properties": {
        "max_ttl_days": {
          "type": "integer",
          "description": "Максимальний термін зберігання у днях (-1 для необмеженого)"
        },
        "crypto_shredding": {
          "type": "boolean",
          "description": "Чи шифрується поле персональним ключем користувача для стирання через знищення ключа"
        },
        "key_derivation_path": {
          "type": "string",
          "description": "Шлях виведення ключа в KMS/HSM (наприклад, 'kdf/users/{user_id}/pii')"
        }
      }
    }
  }
}
```

## 2. Семантика таксономічних класів та рівнів чутливості

Система управління даними інтерпретує поля схеми за чіткими інженерними інваріантами:

- **`DIRECT_IDENTIFIER` (Прямий ідентифікатор):** атрибут із високою унікальною ентропією (номер паспорта, email, банківська картка). Заборонено зберігати у відкритому вигляді в аналітичних шарах. Вимагає обов'язкової токенізації через HMAC або ізольоване сховище токенів. Будь-який прямий запит без прав адміністратора повертає або синтетичний токен, або частково замаскований рядок.
- **`QUASI_IDENTIFIER` (Квазі-ідентифікатор):** непрямий атрибут (поштовий індекс, дата народження, стать, посада). Окремо не ідентифікує особу, проте в комбінації дозволяє виконати атаку зведенням (Linkage Attack). При експорті для аналітики вимагає перевірки на виконання інваріанту `k`-анонімності (`|E| ≥ k`) та автоматичного застосування операцій генералізації (наприклад, `GENERALIZE_PREFIX` для індексів та `BUCKET_INTERVAL` для віку).
- **`SENSITIVE_PERSONAL_DATA` (Спеціальні категорії):** стан здоров'я, біометрія, релігійні переконання (GDPR Art. 9). Вимагає роздільного шифрування на рівні окремих записів із підтримкою миттєвого криптографічного стирання (`crypto_shredding: true`). Доступ до цих полів аудитується в реальному часі зі створенням незмінного запису в журналі безпеки.
- **`INTERNAL_OPERATIONAL` (Внутрішні технічні дані):** технічні ідентифікатори систем, трасування запитів, системні прапорці. Не містять відомостей про людину і не підпадають під регуляторні обмеження.
- **`PUBLIC` (Публічна інформація):** довідники валют, публічні тарифи, географічні назви міст. Доступ надається без фільтрації, маскування чи аудиту.

Рівні чутливості (`sensitivity_level`) визначають суворість криптографічного захисту:
- `L0_PUBLIC` — відкриті дані без шифрування.
- `L1_INTERNAL` — захист під час передачі мережею (TLS 1.3), шифрування носія за замовчуванням.
- `L2_CONFIDENTIAL` — обов'язкове шифрування на рівні сховища (AES-256-GCM), маскування в логах сервісів.
- `L3_RESTRICTED` — токенізація прямих ідентифікаторів, ізоляція ключів у хмарному KMS.
- `L4_CRITICAL` — обов'язковий апаратний модуль HSM, підготовка до криптографічного стирання за протоколом Crypto-Shredding, суворий аудит кожного звернення.

## 3. Детальний опис дій політики маскування (Masking Actions)

Шлюз динамічного маскування виконує трансформацію полів на основі задекларованої дії `default_action`:

1. **`PASS_THROUGH` (Пропуск без змін):** поле передається споживачеві у первинному вигляді. Застосовується для публічних та неідентифіковних атрибутів, а також для користувачів із найвищою роллю адміністратора безпеки.
2. **`FULL_REDACTION` (Повна супресія):** значення поля повністю замінюється статичним маркером `[REDACTED]` або значенням `NULL`. Застосовується для чутливих діагнозів, релігійних поглядів та фінансових залишків при зверненні аудиторів або зовнішніх інтеграцій.
3. **`PARTIAL_MASK` (Часткове маскування):** частина символів замінюється символами `*` зі збереженням структури формату (наприклад, перша та остання літери email і домен, або останні чотири цифри платіжної картки). Застосовується для інтерфейсів технічної підтримки клієнтів.
4. **`TOKENIZE_DETERMINISTIC` (Детермінована токенізація):** обчислення стійкого HMAC-SHA256 хешу з використанням секретного перцю. Дозволяє аналітикам виконувати операції `COUNT(DISTINCT email_token)` та `JOIN` між таблицями без розкриття самого email.
5. **`TOKENIZE_VAULT` (Токенізація зі сховищем):** заміна значення на випадковий UUID із записом пари у захищену ізольовану базу даних. Забезпечує повний захист від частотного аналізу ціною додаткового мережевого звернення при детокенізації.
6. **`BUCKET_INTERVAL` (Інтервальна бакетізація):** числовий атрибут (вік, дохід) ділиться на фіксований крок `bucket_size` та перетворюється на діапазонний рядок (наприклад, `43` перетворюється на `40–49` при кроці 10).
7. **`GENERALIZE_PREFIX` (Префіксна генералізація):** збереження лише перших `prefix_preserve_length` символів рядка, тоді як решта замінюється символом `*` (наприклад, поштовий індекс `02138` стає `021**`).

## 4. Матриця відповідності категорій та дій обробки

| Класифікація | Приклади атрибутів | Рівень чутливості | Регуляторна база | Типова політика маскування | Механізм видалення |
|---|---|---|---|---|---|
| `DIRECT_IDENTIFIER` | Номер паспорта, ІПН, Email, Номер телефону, IBAN | `L3_RESTRICTED` | GDPR Art. 6, CCPA, HIPAA-18 | `TOKENIZE_VAULT` або `PARTIAL_MASK` | Знищення запису або Crypto-Shredding |
| `QUASI_IDENTIFIER` | Поштовий індекс, Дата народження, Стать, Посада | `L2_CONFIDENTIAL` | GDPR (Recital 26), HIPAA Safe Harbor | `BUCKET_INTERVAL` (вік) / `GENERALIZE_PREFIX` (ZIP) | Узагальнення або супресія рядка |
| `SENSITIVE_PERSONAL_DATA` | Діагноз, Генетичний профіль, Біометрія, Расова приналежність | `L4_CRITICAL` | GDPR Art. 9, HIPAA Safe Harbor | `FULL_REDACTION` або `TOKENIZE_DETERMINISTIC` | Негайне занулення або шифрування з TTL |
| `INTERNAL_OPERATIONAL` | UUID сесії, Логи балансувальника, ID внутрішнього сервера | `L1_INTERNAL` | — | `PASS_THROUGH` | Автоматичне витіснення за ротацією логів |
| `PUBLIC` | Каталог товарів, Публічні оферти, Назви міст | `L0_PUBLIC` | — | `PASS_THROUGH` | Без обмежень |

## 5. Приклад декларативного опису схеми таблиці

Нижче наведено практичний опис схеми медичної сутності у форматі метаданих каталогу даних:

```yaml
table_name: "patient_encounters"
schema_version: "2.4.0"
owner_team: "health-core"
fields:
  - name: "encounter_id"
    type: "uuid"
    privacy:
      classification: "INTERNAL_OPERATIONAL"
      sensitivity_level: "L1_INTERNAL"
      masking_policy:
        default_action: "PASS_THROUGH"
      retention:
        max_ttl_days: 2555 # 7 років за медичним стандартом
        crypto_shredding: false

  - name: "patient_email"
    type: "string"
    privacy:
      classification: "DIRECT_IDENTIFIER"
      sensitivity_level: "L3_RESTRICTED"
      regulatory_scope: ["GDPR_ART_6", "HIPAA_18"]
      masking_policy:
        default_action: "TOKENIZE_DETERMINISTIC"
        mask_format: "{first1}***@{domain}"
      retention:
        max_ttl_days: 1095
        crypto_shredding: true
        key_derivation_path: "kms://health/patients/{patient_id}/enc"

  - name: "postal_code"
    type: "string"
    privacy:
      classification: "QUASI_IDENTIFIER"
      sensitivity_level: "L2_CONFIDENTIAL"
      regulatory_scope: ["HIPAA_18"]
      masking_policy:
        default_action: "GENERALIZE_PREFIX"
        prefix_preserve_length: 3 # Збереження перших 3 цифр (021**)
      retention:
        max_ttl_days: 2555
        crypto_shredding: false

  - name: "icd10_diagnosis_code"
    type: "string"
    privacy:
      classification: "SENSITIVE_PERSONAL_DATA"
      sensitivity_level: "L4_CRITICAL"
      regulatory_scope: ["GDPR_ART_9", "HIPAA_18"]
      masking_policy:
        default_action: "FULL_REDACTION"
      retention:
        max_ttl_days: 2555
        crypto_shredding: true
        key_derivation_path: "kms://health/patients/{patient_id}/medical"
```

## 6. Контракт інтерфейсу політик шлюзу (Gateway Policy Contract)

Шлюз динамічного маскування під час обробки клієнтських SQL або HTTP-запитів аналізує роль клієнта, здійснює підміну колонок у дереві запиту (AST Rewrite) та додає діагностичні заголовки для аудиту:

```
Заголовки відповіді шлюзу:
X-Privacy-Applied-Rules: DIRECT_ID_TOKENIZED, QUASI_ID_BUCKETED
X-Privacy-Suppressed-Fields: icd10_diagnosis_code
X-Privacy-Entropy-Loss-Score: 0.142

Коди помилок авторизації політик:
403 PRIVACY_RESTRICTED_FIELD_ACCESS
    Тіло помилки:
    {
      "error": "ACCESS_DENIED",
      "field": "icd10_diagnosis_code",
      "required_role": "ROLE_MEDICAL_OFFICER",
      "caller_role": "ROLE_DATA_ANALYST",
      "policy_id": "GDPR-ART9-RESTRICTION"
    }

422 INSUFFICIENT_ANONYMITY_BUDGET
    Тіло помилки:
    {
      "error": "ANONYMITY_VIOLATION",
      "min_k_required": 5,
      "calculated_k": 2,
      "message": "Вибірка не задовольняє інваріант k-анонімності"
    }
```

## 7. Валідація схем у конвеєрі CI/CD

Для запобігання появі некласифікованих полів у продакшн-середовищі етап збірки CI/CD виконує автоматичний аудит схеми:

1. **Перевірка на повноту тегів:** кожен новий стовпець у файлах міграцій бази даних (Flyway, Liquibase) повинен мати відповідний блок `privacy` у каталозі метаданих. Якщо поле додано без класифікації, збірка завершується з кодом помилки.
2. **Евристичне сканування на PII:** статичний аналізатор перевіряє назви нових колонок за словником регулярних виразів (`*email*`, `*phone*`, `*ssn*`, `*tax_id*`, `*passport*`). Якщо виявлено поле з підозрілою назвою, яке позначено як `PUBLIC` або `INTERNAL_OPERATIONAL`, лінтер вимагає явного підтвердження від офіцера безпеки (Data Protection Officer, DPO).
3. **Контроль шляхів стирання:** якщо поле містить прапорець `crypto_shredding: true`, перевіряється наявність зареєстрованого шаблону виведення ключа в KMS. Відсутність конфігурації KDF вважається критичною помилкою конфігурації схеми.

## 8. Аудит подій доступу та інтеграція з SIEM

Усі операції демаскування (відкриття немодифікованого значення для привілейованих ролей) фіксуються в незмінному журналі аудиту безпеки.

Подія аудиту експортується у форматі CEF (Common Event Format) або структурованому JSON до системи SIEM:
- Фіксується точний ідентифікатор сесії та користувача, що здійснив запит;
- Зазначається назва таблиці та конкретний перелік прочитаних стовпців;
- Записується бізнес-обґрунтування (Ticket ID або Reason Code), що унеможливлює несанкціоноване читання даних персоналом компанії.
