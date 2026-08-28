# 📋 Специфікація схеми структурованих нотаток випуску

Коли парк промислових контролерів, телеметричних модулів або розподілених серверів налічує тисячі одиниць, текстовий файл у форматі Markdown перестає бути достатнім носієм інформації. Сервер доставки оновлень через радіоефір (англ. *Over-The-Air*, OTA), система оркестрації парку та автоматизовані сканери вразливостей не можуть надійно розбирати довільний людський текст регулярними виразами. Будь-яка друкарська помилка в описі версії бутлоадера або зміні назви поля призводить до збою автоматизованого сценарію оновлення.

Для машинної взаємодії нотатки випуску пакуються в уніфікований структурований формат `release-manifest.json` або бінарний підписаний метаблок, що додається на початку образу прошивки. Цей документ є суворим контрактом між конвеєром збірки ([CI/CD](root:sf-release/ci-cd)) та сервером розгортання.

## Призначення та архітектурні рівні схеми

Специфікація машиночитабельних нотаток випуску розв'язує чотири фундаментальні задачі автоматизованого конвеєра:

1. **Валідація апаратної сумісності (Hardware Gatekeeping):** Сервер OTA перед відправкою двійкового файлу опитує пристрій про його фізичну ревізію друкованої плати (PCB Revision). Якщо ревізія відсутня у списку `supported_pcb_revisions`, доставка блокується на рівні сервера, запобігаючи фізичному пошкодженню вхідних кіл приладу несумісними налаштуваннями портів вводу-виводу.
2. **Перевірка ланцюжка завантаження (Bootloader Pre-flight Check):** Якщо новий образ скомпільовано під нову карту пам'яті (Memory Map), що вимагає зміненого стеку завантажувача, маніфест визначає мінімально допустиму версію завантажувача. Сервер OTA в такому разі формує двоетапний сценарій: спершу завантажується та прошивається новий бутлоадер, пристрій перезавантажується, і лише після підтвердження нового статусу завантажується основний образ.
3. **Автоматизований контроль відкату (Rollback Feasibility Check):** У разі невдалого старту або збою самотестування пристрій перевіряє поле `rollback_policy.allowed`. Якщо прапорець `nvm_migration_irreversible` встановлено у значення `true`, автоматичний відкат на попередні версії блокується, оскільки стара прошивка зіпсує перетворені структури конфігурації у Flash-пам'яті. Замість цього прилад переходить у захищений режим відновлення (*Recovery Mode*).
4. **Машинна обробка безпеки (Vulnerability Ingestion):** Корпоративні сканери безпеки автоматично зчитують блок `security_advisories`, парсять ідентифікатори CVE та векторні рядки CVSS, зіставляють їх із корпоративним реєстром активів і закривають відкриті інциденти безпеки без участі людини.

## Формальна специфікація JSON Schema

Нижче наведено повну схему валідації маніфесту нотаток випуску згідно зі стандартом JSON Schema Draft 2020-12:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "DeviceReleaseNotesSchema",
  "type": "object",
  "required": [
    "version",
    "release_date",
    "target_platform",
    "hardware_compatibility",
    "bootloader_requirements",
    "rollback_policy",
    "changes",
    "artifacts"
  ],
  "properties": {
    "version": {
      "type": "string",
      "pattern": "^(0|[1-9]\\d*)\\.(0|[1-9]\\d*)\\.(0|[1-9]\\d*)(?:-((?:0|[1-9]\\d*|\\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\\.(?:0|[1-9]\\d*|\\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\\+([0-9a-zA-Z-]+(?:\\.[0-9a-zA-Z-]+)*))?$",
      "description": "Версія випуску у форматі SemVer 2.0.0"
    },
    "release_date": {
      "type": "string",
      "format": "date",
      "description": "Дата публікації релізу (ISO 8601, YYYY-MM-DD)"
    },
    "target_platform": {
      "type": "string",
      "description": "Ідентифікатор архітектури чи родини мікроконтролера (наприклад, stm32h7-dualcore, esp32s3)"
    },
    "hardware_compatibility": {
      "type": "object",
      "required": ["supported_pcb_revisions", "deprecated_pcb_revisions"],
      "properties": {
        "supported_pcb_revisions": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Список підтримуваних апаратних ревізій друкованої плати"
        },
        "deprecated_pcb_revisions": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Ревізії плат, підтримку яких буде припинено у наступному мажорному випуску"
        }
      }
    },
    "bootloader_requirements": {
      "type": "object",
      "required": ["min_version", "mandatory_update"],
      "properties": {
        "min_version": {
          "type": "string",
          "description": "Мінімальна версія первинного завантажувача (Bootloader), необхідна для запуску цього образу"
        },
        "mandatory_update": {
          "type": "boolean",
          "description": "Чи вимагає цей реліз попереднього оновлення завантажувача перед прошивкою основного додатку"
        }
      }
    },
    "rollback_policy": {
      "type": "object",
      "required": ["allowed", "min_rollback_version", "nvm_migration_irreversible"],
      "properties": {
        "allowed": {
          "type": "boolean",
          "description": "Чи дозволено безпечний автоматичний відкат (даунгрейд) на попередню версію"
        },
        "min_rollback_version": {
          "type": "string",
          "description": "Найнижча версія прошивки, до якої можливий відкат без втрати даних калібрування"
        },
        "nvm_migration_irreversible": {
          "type": "boolean",
          "description": "Чи зазнала схема Flash/EEPROM незворотної міграції, що унеможливлює відкат"
        }
      }
    },
    "changes": {
      "type": "object",
      "required": ["breaking_changes", "security_advisories", "features", "fixes"],
      "properties": {
        "breaking_changes": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["scope", "summary", "action_required", "migration_guide_url"],
            "properties": {
              "scope": { "type": "string" },
              "summary": { "type": "string" },
              "action_required": { "type": "string" },
              "migration_guide_url": { "type": "string", "format": "uri" }
            }
          }
        },
        "security_advisories": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["cve_id", "cvss_v3_score", "cvss_v3_vector", "cwe_id", "summary", "mitigation"],
            "properties": {
              "cve_id": { "type": "string", "pattern": "^CVE-\\d{4}-\\d{4,}$" },
              "cvss_v3_score": { "type": "number", "minimum": 0.0, "maximum": 10.0 },
              "cvss_v3_vector": { "type": "string" },
              "cwe_id": { "type": "string", "pattern": "^CWE-\\d+$" },
              "summary": { "type": "string" },
              "mitigation": { "type": "string" }
            }
          }
        },
        "features": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["scope", "summary"],
            "properties": {
              "scope": { "type": "string" },
              "summary": { "type": "string" }
            }
          }
        },
        "fixes": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["scope", "summary"],
            "properties": {
              "scope": { "type": "string" },
              "summary": { "type": "string" }
            }
          }
        }
      }
    },
    "artifacts": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["filename", "artifact_type", "sha256", "size_bytes"],
        "properties": {
          "filename": { "type": "string" },
          "artifact_type": { "type": "string", "enum": ["firmware_binary", "bootloader", "elf_symbols", "sbom", "test_report"] },
          "sha256": { "type": "string", "pattern": "^[a-fA-F0-9]{64}$" },
          "size_bytes": { "type": "integer", "minimum": 1 }
        }
      }
    }
  }
}
```

## Опис полів та правила валідації

Кожна секція маніфесту має чіткі семантичні обмеження, які валідуються на етапі створення релізного пакету:

### Метадані та апаратний профіль
- `version`: Рядок обов'язково відповідає синтаксису SemVer 2.0.0. Будь-які префікси на кшталт `v` видаляються під час формування маніфесту (`3.2.0`, а не `v3.2.0`).
- `target_platform`: Ідентифікатор процесорної архітектури або цільового чипа. Запобігає випадковій спробі прошити бінарний образ для мікроконтролера ARM Cortex-M4 у пристрій на базі RISC-V.
- `hardware_compatibility.supported_pcb_revisions`: Масив рядків з іменами ревізій. Пристрій порівнює значення свого внутрішнього апаратного регістру або байтів OTP-пам'яті з цим масивом.
- `hardware_compatibility.deprecated_pcb_revisions`: Список ревізій, для яких цей реліз є останнім або передостаннім. Дозволяє системі моніторингу формувати звіт про необхідність планової апаратної модернізації об'єктів.

### Вимоги до завантажувача та правила відкату
- `bootloader_requirements.min_version`: Мінімальна версія завантажувача. Якщо локальний завантажувач старіший, оновлення основного образу суворо блокується.
- `bootloader_requirements.mandatory_update`: Прапорець, що змушує систему спершу виконати оновлення самого завантажувача.
- `rollback_policy.allowed`: Булевий прапорець, що дозволяє або забороняє автоматичне повернення на попередню версію при виникненні аварійних ситуацій (Watchdog reset, Kernel Panic).
- `rollback_policy.nvm_migration_irreversible`: Критичний параметр. Якщо він дорівнює `true`, клієнтський завантажувач ні за яких обставин не повинен завантажувати старіший образ із резервного банку пам'яті (Slot B), оскільки структури даних у EEPROM/Flash зазнали незворотних змін.

### Секції змін та безпеки
- `changes.breaking_changes`: Кожен запис обов'язково містить поле `action_required` (що саме оператор має зробити руками) та `migration_guide_url` (посилання на покрокову інструкцію).
- `changes.security_advisories`: Кожен безпековий пункт містить номер `cve_id`, числовий бал `cvss_v3_score` (від 0.0 до 10.0), повний векторний рядок `cvss_v3_vector` (наприклад, `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H`), ідентифікатор слабкості `cwe_id` та обов'язковий опис тимчасових компенсаційних заходів `mitigation`.

## Двобанкова пам'ять та верифікація цифрового підпису

У сучасних вбудованих системах реалізується схема двоетапного оновлення через спарені банки пам'яті (A/B Partitioning). Флеш-пам'ять мікроконтролера розділена на два незалежні слоти: активний слот `Slot A`, з якого виконується поточна прошивка, та резервний слот `Slot B`, куди записується завантажений образ.

Під час отримання маніфесту пристрій здійснює послідовну перевірку:
1. **Перевірка підпису маніфесту:** Маніфест супроводжується криптографічним підписом за алгоритмом Ed25519 або ECDSA (NIST P-256). Завантажувач перевіряє підпис маніфесту за допомогою публічного ключа виробника, зашитого в захищену область пам'яті (eFuse / OTP ROM).
2. **Перевірка сумісності ревізії:** Завантажувач зчитує апаратний ідентифікатор друкованої плати та переконується, що поточна ревізія присутня в масиві `supported_pcb_revisions`.
3. **Завантаження та звірка гешу:** Образ прошивки записується у `Slot B`. Після завершення запису обчислюється контрольна сума SHA-256 і звіряється з полем `artifacts[...].sha256`.
4. **Пробний старт (Trial Boot):** Завантажувач перемикає прапорець запуску на `Slot B` і передає керування новому ядру. Якщо протягом заданого тайм-ауту (наприклад, 30 секунд) нова прошивка не підтверджує успішну ініціалізацію датчиків та зв'язку викликом `system_confirm_boot()`, апаратний таймер Watchdog перезавантажує мікроконтролер, і завантажувач автоматично повертається до стабільного образу в `Slot A`.

## Приклад робочого маніфесту випуску

Нижче наведено зразок повністю заповненого файлу `release-manifest.json` для промислового телеметричного вузла:

```json
{
  "version": "3.2.0",
  "release_date": "2026-08-28",
  "target_platform": "stm32h743-rev-b",
  "hardware_compatibility": {
    "supported_pcb_revisions": ["HW-2.1", "HW-2.2", "HW-3.0"],
    "deprecated_pcb_revisions": ["HW-2.0"]
  },
  "bootloader_requirements": {
    "min_version": "1.4.0",
    "mandatory_update": false
  },
  "rollback_policy": {
    "allowed": false,
    "min_rollback_version": "3.2.0",
    "nvm_migration_irreversible": true
  },
  "changes": {
    "breaking_changes": [
      {
        "scope": "can-protocol",
        "summary": "Перехід на кадр CAN-FD з бітрейтом даних 2 Мбіт/с",
        "action_required": "Оновити шлюз телеметрії до версії 2.0 перед увімкненням живлення контролера",
        "migration_guide_url": "https://docs.telemetry.internal/migration/can-fd-3.2"
      }
    ],
    "security_advisories": [
      {
        "cve_id": "CVE-2026-4412",
        "cvss_v3_score": 8.1,
        "cvss_v3_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H",
        "cwe_id": "CWE-120",
        "summary": "Переповнення вхідного кільцевого буфера при обробці некоректних кадрів Modbus TCP",
        "mitigation": "Увімкнути фільтрацію пакетів на внутрішньому міжмережевому екрані або заблокувати порт TCP 502 для зовнішніх підмереж"
      }
    ],
    "features": [
      {
        "scope": "sensors",
        "summary": "Додано динамічну температурну компенсацію датчиків тиску 4-20 мА"
      }
    ],
    "fixes": [
      {
        "scope": "adc",
        "summary": "Усунено зміщення нульового рівня при низьких температурах навколишнього середовища (-20 C)"
      }
    ]
  },
  "artifacts": [
    {
      "filename": "firmware-v3.2.0.bin",
      "artifact_type": "firmware_binary",
      "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "size_bytes": 524288
    },
    {
      "filename": "sbom-v3.2.0.cdx.json",
      "artifact_type": "sbom",
      "sha256": "4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a",
      "size_bytes": 45120
    }
  ]
}
```

## Інтеграція в процес валідації та доставки

У конвеєрі неперервного постачання цей маніфест проходить автоматичну валідацію лінтером схеми перед підписанням релізних артефактів. Якщо у файлі відсутній геш хоча б одного бінарного файлу або не заповнено обов'язкове поле `action_required` для ламкої зміни, конвеєр перериває публікацію випуску з помилкою валідації. Це гарантує, що жоден пристрій у полі не отримає неповної або некоректно оформленої інструкції оновлення.
