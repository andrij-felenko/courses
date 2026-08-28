# 📋 Специфікація машиночитних сповіщень: CSAF 2.0, OpenVEX та схема звітування CSIRT

Сучасні законодавчі акти з кібербезпеки — зокрема Європейський регламент про кіберстійкість (*Cyber Resilience Act*, CRA) та Директива NIS 2 — встановили безпрецедентно стислі строки для звітування про вразливості та операційні інциденти. Традиційний підхід, за якого компанія публікувала текстовий пресреліз або надсилала бюлетень безпеки у форматі PDF електронною поштою, повністю вичерпав себе: ручна обробка документів сторонніми організаціями та регуляторами створює критичні затримки, через які атаковані суб'єкти не встигають закрити дірки до появи масових ботнетів.

Стандартом індустрії став автоматизований обмін структурованими машиночитними даними. Сьогодні безпекова екосистема спирається на три взаємодоповнюючі формати:
1. **Єдина схема сповіщення CSIRTs Network та ENISA:** Мінімалістичний типізований формат для передачі термінових 24-годинних та 72-годинних звітів до європейської платформи координації.
2. **Специфікація OpenVEX (*Vulnerability Exploitability eXchange*):** Легковагий JSON-LD формат для швидкого інформування клієнтів та партнерів про реальну експлуатабельність знайдених вразливостей у виробі.
3. **Стандарт CSAF 2.0 (*Common Security Advisory Framework*):** Комплексний стандарт консорціуму OASIS для публікації повнорозмірних безпекових бюлетенів із детальним описом компонентів, векторів атак та процедур оновлення.

```
+--------------------------------------------------------------------------------------------------+
| Екосистема машиночитних форматів сповіщення про вразливості                                      |
+--------------------------------------------------------------------------------------------------+
| 1. CSAF 2.0 (OASIS)    -> Повний бюлетень: дерево продуктів, CVSS-метрики, виправлення, remediation|
| 2. OpenVEX             -> Швидка декларація експлуатабельності (affected / not_affected + justification)|
| 3. ENISA/CSIRT Payload -> Регуляторне раннє сповіщення за Статтею 14 CRA / Статтею 23 NIS 2     |
+--------------------------------------------------------------------------------------------------+
```

## 1. Схема раннього сповіщення CSIRTs Network / ENISA (JSON Schema)

Відповідно до Статті 14 Регламенту CRA, виробник цифрового продукту зобов'язаний надіслати раннє попередження про активно експлуатовану вразливість протягом 24 годин. На цьому етапі виправлення зазвичай ще не створене, тому головна мета схеми — зафіксувати факт атаки, позначити уражені версії виробу та надати попередні інструкції з обмеження доступу без розкриття деталей, які могли б допомогти іншим хакерам створити робочий експлойт.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "ENISA_CRA_EarlyWarning_v1",
  "type": "object",
  "required": [
    "notification_id",
    "timestamp_utc",
    "notification_phase",
    "manufacturer",
    "affected_product",
    "exploit_status"
  ],
  "properties": {
    "notification_id": {
      "type": "string",
      "format": "uuid"
    },
    "timestamp_utc": {
      "type": "string",
      "format": "date-time"
    },
    "notification_phase": {
      "type": "string",
      "enum": ["EARLY_WARNING_24H", "VULNERABILITY_NOTICE_72H", "FINAL_REPORT"]
    },
    "manufacturer": {
      "type": "object",
      "required": ["name", "contact_email", "country_code"],
      "properties": {
        "name": { "type": "string" },
        "contact_email": { "type": "string", "format": "email" },
        "country_code": { "type": "string", "pattern": "^[A-Z]{2}$" }
      }
    },
    "affected_product": {
      "type": "object",
      "required": ["cpe_uri", "product_name", "firmware_version"],
      "properties": {
        "cpe_uri": { "type": "string", "pattern": "^cpe:2\\.3:[aho]:.*" },
        "product_name": { "type": "string" },
        "firmware_version": { "type": "string" }
      }
    },
    "exploit_status": {
      "type": "string",
      "enum": [
        "IN_THE_WILD_CONFIRMED",
        "PUBLIC_POC_AVAILABLE",
        "SUSPECTED_TARGETED_ATTACK"
      ]
    },
    "cross_border_impact": {
      "type": "boolean"
    },
    "initial_mitigation_instructions": {
      "type": "string"
    }
  }
}
```

У цій схемі критично важливим є поле `cpe_uri`, яке містить стандартизований ідентифікатор виробу за номенклатурою NIST Common Platform Enumeration. Це дозволяє центральному координаційному хабу автоматично зіставити звіт виробника із записами національних баз даних та ідентифікувати критичну інфраструктуру, де розгорнуто вразливі пристрої.

Якщо поле `cross_border_impact` має значення `true`, єдина платформа ENISA негайно транслює знеособлені індикатори компрометації (IoC) до мережі національних команд реагування (CSIRTs Network) усіх 27 держав-членів ЄС, що унеможливлює раптовий спалах атак у сусідніх країнах.

## 2. Специфікація OpenVEX: статус експлуатабельності компонентів

Сучасні пристрої містять сотні сторонніх бібліотек з відкритим вихідним кодом. Сканери безпеки знаходять у специфікаціях програмних матеріалів (SBOM) десятки відомих вразливостей (CVE). Проте у переважній більшості випадків вразливий код або взагалі не викликається в прошивці, або ізольований апаратними механізмами захисту пам'яті. Без машинного підтвердження статусу клієнти стикаються з лавиною помилкових тривог (*alert fatigue*).

Формат **OpenVEX** вирішує цю проблему, надаючи лаконічні та однозначні твердження виробника про реальний статус вразливості:

```json
{
  "@context": "https://openvex.dev/ns/v0.2.0",
  "@id": "https://vendor.example.com/vex/2026-08-CRA-0042",
  "author": "PSIRT Secure Systems Inc.",
  "role": "Coordinator",
  "timestamp": "2026-08-28T03:00:00Z",
  "version": 1,
  "statements": [
    {
      "vulnerability": {
        "name": "CVE-2026-9999",
        "description": "Buffer overflow in legacy packet parser daemon"
      },
      "products": [
        "pkg:generic/industrial-controller-firmware@4.2.1"
      ],
      "status": "affected",
      "action_statement": "Disable port 502/TCP until patch v4.2.2 is applied via secure OTA"
    },
    {
      "vulnerability": {
        "name": "CVE-2026-8888",
        "description": "Information disclosure in debug interface"
      },
      "products": [
        "pkg:generic/industrial-controller-firmware@4.2.1"
      ],
      "status": "not_affected",
      "justification": "vulnerable_code_not_present",
      "impact_statement": "Debug build flag is disabled in production release artifacts"
    }
  ]
}
```

### Семантика статусів та обґрунтувань за стандартом OpenVEX

Кожне твердження у форматі OpenVEX спирається на сувору логічну класифікацію:

- **`not_affected` (Не зазнає впливу):** Виробник стверджує, що вразливість не може бути експлуатована в цьому виробі. Статус обов'язково супроводжується одним із п'яти нормативних обґрунтувань:
  - `component_not_present` — вразливий модуль взагалі відсутній у збірці;
  - `vulnerable_code_not_present` — код бібліотеки включено частково, і сам вразливий метод вирізано компілятором під час оптимізації;
  - `vulnerable_code_not_in_execute_path` — функція присутня в бінарному файлі, але в конфігурації пристрою немає жодного шляху виконання, який би викликав цю функцію;
  - `vulnerable_code_cannot_be_controlled_by_adversary` — вхідні параметри функції є жорстко зашитими константами і не залежать від мережевого чи користувацького вводу;
  - `inline_mitigations_already_exist` — експлуатація фізично заблокована зовнішнім захисним контуром (наприклад, апаратним модулем MPU, фільтром seccomp або перевіркою цифрового підпису).
- **`affected` (Зазнає впливу):** Уразливість підтверджена. Виробник зобов'язаний надати поле `action_statement` із чітким описом тимчасових захисних заходів для оператора.
- **`fixed` (Виправлено):** Уразливість усунуто в зазначеній версії програмного продукту.
- **`under_investigation` (Досліджується):** Тимчасовий статус, який використовується під час активної роботи інженерів у межах 72-годинного вікна тріажу.

## 3. Профіль CSAF 2.0 Security Advisory (Повний бюлетень)

Коли виправлення готове до релізу, виробник публікує фінальний бюлетень безпеки за стандартом CSAF 2.0. Цей документ містить повну історію версій, криптографічні контрольні суми, метрики оцінки небезпеки за шкалою CVSS, посилання на класифікатор слабкостей CWE та прямі інструкції щодо оновлення:

```json
{
  "document": {
    "category": "csaf_security_advisory",
    "csaf_version": "2.0",
    "title": "Security Advisory: Denial of Service in Secure Mesh Router",
    "tracking": {
      "id": "SEC-ADV-2026-0801",
      "current_release_date": "2026-08-28T03:00:00Z",
      "initial_release_date": "2026-08-28T03:00:00Z",
      "status": "final",
      "version": "1.0.0"
    },
    "publisher": {
      "category": "vendor",
      "name": "Network Hardware Ltd",
      "namespace": "https://nwhardware.example.com"
    }
  },
  "product_tree": {
    "branches": [
      {
        "category": "product_name",
        "name": "EdgeRouter Pro",
        "product": {
          "name": "EdgeRouter Pro Firmware 3.1",
          "product_id": "CSAFPID-0001"
        }
      }
    ]
  },
  "vulnerabilities": [
    {
      "cve": "CVE-2026-12345",
      "cwe": {
        "id": "CWE-120",
        "name": "Buffer Copy without Checking Size of Input ('Classic Buffer Overflow')"
      },
      "scores": [
        {
          "cvss_v3": {
            "version": "3.1",
            "vectorString": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
            "baseScore": 9.8,
            "baseSeverity": "CRITICAL"
          }
        }
      ],
      "product_status": {
        "fixed": ["CSAFPID-0001"]
      },
      "remediations": [
        {
          "category": "vendor_fix",
          "details": "Upgrade firmware to version 3.1.2 via administrative portal",
          "product_ids": ["CSAFPID-0001"],
          "url": "https://nwhardware.example.com/downloads/firmware-3.1.2.bin"
        }
      ]
    }
  ]
}
```

## Інтеграція, автоматичний прийом та перевірка автентичності

Щоб гарантувати захист від підробки та маніпуляцій з боку зловмисників, усі машиночитні документи безпеки повинні публікуватися за стандартними правилами цілісності:

1. **Фіксовані точки публікації:** Файли CSAF та VEX розміщуються на захищеному веб-сервері за стандартним шляхом виявлення провайдера, наприклад `https://vendor.example.com/.well-known/csaf/provider-metadata.json`. Цей файл містить перелік усіх випущених бюлетенів, хеші SHA-256 та відкриті криптографічні ключі організації.
2. **Цифровий підпис документів:** Кожен JSON-маніфест обов'язково супроводжується від'єднаним цифровим підписом у форматі OpenPGP (`.asc`) або Minisign (`.sig`). Сканери безпеки перевіряють автентичність підпису перед імпортом тверджень у внутрішню базу.
3. **Автоматизований конвеєр оновлення:** Системи управління вразливостями клієнтів (OpenVAS, Trivy, Dependency-Track, Snyk) у фоновому режимі опитують репозиторії виробників. Отримавши новий VEX-документ зі статусом `not_affected`, сканер автоматично знижує пріоритет тривоги, звільняючи час аналітиків для реагування на справжні загрози.
4. **Процедура відкликання та анулювання:** Якщо додатковий аналіз виявив обхід мітигації, виробник випускає нову версію VEX із підвищеним номером `version` та оновленим полем `timestamp`. Сканери відстежують монотонне зростання версій і негайно скасовують попереднє твердження про безпеку виробу.
