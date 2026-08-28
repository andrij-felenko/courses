# Специфікація маніфесту довготривалого архіву (LTS-Manifest)

Маніфест довготривалого архіву (`archive-manifest.json` або `archive-manifest.yaml`) — це стандартизований структурований документ, що криптографічно зв'язує докупи всі артефакти релізу вбудованої системи: вихідний код, заморожене середовище збірки, апаратні креслення, сервісну документацію, конфігурацію захисту та еталонні бінарні образи.

Маніфест розміщується в корені архівного тому, містить контрольні суми SHA-256 та SHA-512 для кожного вкладеного файлу та засвідчується кількома цифровими підписами відповідальних інженерів і офіцерів безпеки. Цей документ слугує юридичним і технічним контрактом між первинною командою розробників і будь-яким інженером чи регуляторним аудитором, який відкриє архів через 10–20 років.

## Призначення та архітектурні інваріанти

Головне завдання маніфесту — усунути будь-яку двозначність щодо того, які саме файли, інструменти, налаштування та ключі формують офіційний реліз. Під час тривалого зберігання окремі файли можуть зазнати пошкодження, бути випадково перейменовані або підмінені. Маніфест забезпечує математичний доказ автентичності кожного байта.

Специфікація встановлює такі обов'язкові інваріанти:
1. **Канонізація формату (RFC 8785 / JCS):** Перед накладанням цифрового підпису документ маніфесту обов'язково проходить процедуру канонізації JSON (сортування ключів за алфавітом, нормалізація пробілів і кодувань). Це гарантує, що різні парсери через десятиліття згенерують однаковий байтовий потік для перевірки підпису.
2. **Подвійне хешування (SHA-256 + SHA-512):** Кожен бінарний артефакт хешується двома незалежними криптографічними функціями. Якщо на горизонті 15 років в алгоритмі SHA-256 буде знайдено практичні колізії, захист спиратиметься на SHA-512.
3. **Герметичність шляхів:** Усі шляхи до файлів (`file_path`, `path`) вказуються відносно кореня архівного каталогу з використанням прямого слеша `/` незалежно від операційної системи. Заборонено використання абсолютних шляхів, дисків (C:, D:) або переходів вище кореня (`../`).
4. **Незмінність схеми (Schema Evolution):** Поле `schema_version` визначає семантичну версію формату маніфесту. Будь-які майбутні розширення схеми зобов'язані підтримувати зворотну сумісність: парсер новішої версії повинен коректно інтерпретувати маніфести версії 1.x без втрати валідаційних інваріантів.

## Структура документа та схема полів

Документ організовано у сім логічних секцій:

```json
{
  "schema_version": "1.2.0",
  "archive_uuid": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "created_at_utc": "2026-08-28T10:00:00Z",
  "epoch_timestamp": 1787911200,
  "project_metadata": {
    "device_name": "Autonomous telemetry node",
    "part_number": "ATN-400-REV-C",
    "firmware_release_tag": "v3.4.2-lts",
    "regulatory_standard": "ISO 26262 ASIL-B / IEC 62304 Class B",
    "archival_lifespan_years": 15,
    "planned_eol_date": "2041-08-28"
  },
  "golden_binaries": [
    {
      "file_path": "bin/firmware_app_v3.4.2.bin",
      "target_mcu": "STM32F429ZIT6",
      "target_memory_base": "0x08020000",
      "size_bytes": 394240,
      "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "sha512": "cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce47d0d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927da3e",
      "signature_algorithm": "Ed25519",
      "signature_file": "bin/firmware_app_v3.4.2.sig",
      "signing_key_fingerprint": "9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b"
    }
  ],
  "toolchain_environment": {
    "container_image_digest": "sha256:d82e2e88a38c2c19e59d9c25608d4b3b1f52b662d5e2e861d856d56214150be8",
    "container_archive_file": "env/toolchain_builder_rhel8_arm_gcc10.tar.gz",
    "vm_raw_image_file": "env/qemu_build_appliance_v1.0.qcow2",
    "compiler_tuple": "arm-none-eabi-gcc",
    "compiler_version_raw": "10.3.1 20210824 (release)",
    "host_os_baseline": "Debian 11.8 (Bullseye) / Linux kernel 5.10.0-28",
    "build_command_invoked": "cmake -B build -G Ninja -DSOURCE_DATE_EPOCH=1787911200 -DCMAKE_BUILD_TYPE=Release && ninja -C build",
    "environment_variables": {
      "SOURCE_DATE_EPOCH": "1787911200",
      "LC_ALL": "C",
      "TZ": "UTC",
      "CFLAGS": "-O2 -fdebug-prefix-map=/src=. -ffile-prefix-map=/src=."
    }
  },
  "source_repositories": {
    "primary_repository_bundle": "src/main_firmware_git_bundle_v3.4.2.bundle",
    "git_commit_sha": "a1b2c3d4e5f60718293a4b5c6d7e8f9012345678",
    "git_tree_hash": "b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1",
    "submodules": [
      {
        "name": "vendor_hal",
        "path": "drivers/stm32f4_hal",
        "bundle_file": "src/submodules/stm32f4_hal.bundle",
        "commit_sha": "f1e2d3c4b5a697887766554433221100ffeeddcc"
      },
      {
        "name": "freertos_kernel",
        "path": "rtos/freertos",
        "bundle_file": "src/submodules/freertos_v10.4.6.bundle",
        "commit_sha": "1234567890abcdef1234567890abcdef12345678"
      }
    ]
  },
  "hardware_documentation": {
    "schematic_pdf": {
      "path": "hw/schematics_v3.4.pdf",
      "sha256": "4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a"
    },
    "gerber_manufacturing_archive": {
      "path": "hw/gerber_production_panel_rev_c.zip",
      "sha256": "ef2d127de37b942baad06145e54b0c619a1f22327b2ebbcfbec78f5564afe39d"
    },
    "bill_of_materials": {
      "path": "hw/bom_full_component_specs.csv",
      "sha256": "c8038b34005b8a0d9e9c9a2961d1573c0919f85c1598f48dfc4f1c1f5139a04a"
    },
    "datasheets_archive": {
      "path": "docs/datasheets_and_silicon_errata.tar.gz",
      "sha256": "9b71d224bd62f3785d96d46ad3ea3d73319bfbc2890caadae2dff72519673ca7"
    },
    "test_jig_specifications": {
      "path": "hw/test_jig_pogo_pin_mapping_and_test_firmware.zip",
      "sha256": "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
    }
  },
  "key_escrow_manifest": {
    "escrow_protocol": "Shamir Secret Sharing (k=3 of n=5)",
    "public_signing_key_pem": "keys/firmware_release_public.pem",
    "key_algorithm": "Ed25519",
    "key_purpose": "Secure Boot OTA update verification",
    "shares_distribution": [
      {"share_id": 1, "holder": "Chief Security Officer", "vault_location": "Kyiv Offline Safe #1"},
      {"share_id": 2, "holder": "VP of Engineering", "vault_location": "Lviv Offline Safe #2"},
      {"share_id": 3, "holder": "External Legal Escrow Agent", "vault_location": "Zurich Bank Depository"},
      {"share_id": 4, "holder": "Lead Firmware Architect", "vault_location": "Hardware Token #4 (Air-gapped)"},
      {"share_id": 5, "holder": "Quality Assurance Director", "vault_location": "Hardware Token #5 (Air-gapped)"}
    ]
  },
  "signatures": [
    {
      "signer_role": "Lead Firmware Architect",
      "signer_name": "Oleksandr Petrenko",
      "public_key_fingerprint": "11223344556677889900aabbccddeeff00112233",
      "timestamp_utc": "2026-08-28T10:15:00Z",
      "signature_base64": "MEQCIG7...34A="
    },
    {
      "signer_role": "Chief Quality & Compliance Officer",
      "signer_name": "Iryna Kovalenko",
      "public_key_fingerprint": "aabbccddeeff0011223344556677889900112233",
      "timestamp_utc": "2026-08-28T10:30:00Z",
      "signature_base64": "MEUCIQ...99B="
    }
  ]
}
```

## Детальний опис секцій та контрактів валідації

### 1. `project_metadata` (Метадані проєкту)
Ця секція визначає базовий контекст виробу:
- `device_name`: текстова назва лінійки виробів.
- `part_number`: точний заводський шифр плати чи модуля з ревізією (наприклад, `ATN-400-REV-C`). Зміна ревізії вимагає заведення нового архіву, оскільки може змінюватися розпіновка, трасування або номінали компонентів.
- `regulatory_standard`: перелік галузевих нормативів (ISO 26262, IEC 62304, DO-178C), які вимагають збереження доказової бази та регулярної верифікації.
- `archival_lifespan_years`: нормативний строк зберігання (типово 10, 15 або 20 років), від якого відраховуються регламентні цикли скрабінгу.
- `planned_eol_date`: дата офіційного завершення експлуатації та сервісного контракту виробу.

### 2. `golden_binaries` (Еталонні прошивки)
Масив описів усіх випущених бінарних файлів, що прошиваються на заводі або доставляються через OTA. Кожен запис містить:
- `target_mcu`: точне маркування цільового мікроконтролера чи процесора (включно зі степінгом кремнію).
- `target_memory_base`: базова фізична адреса завантаження у Flash-пам'ять (наприклад, `0x08020000` для сектору додатку після завантажувача).
- `size_bytes`: точний розмір файлу в байтах. Будь-яке зміщення розміру свідчить про пошкодження або недетерміноване додавання паддингу.
- `sha256` та `sha512`: контрольні суми еталонного бінарного образу.
- `signature_algorithm` та `signature_file`: алгоритм підпису (Ed25519, ECDSA P-256) та шлях до бінарного файлу підпису, який перевіряє Secure Boot.

### 3. `toolchain_environment` (Середовище збірки)
Повний профіль для розгортання в ізольованому контурі:
- `container_image_digest`: унікальний SHA-256 дайджест OCI-образу контейнера. Запобігає підміні шарів образу під час імпорту.
- `container_archive_file`: шлях до експортованого монолітного `.tar.gz` архіву контейнера з усіма утилітами.
- `vm_raw_image_file`: образ повної віртуальної машини QEMU/KVM (`.qcow2`) для складних legacy-середовищ (наприклад, коли потрібна 32-бітна бібліотечна база).
- `compiler_tuple` та `compiler_version_raw`: рядок ідентифікації компілятора.
- `environment_variables`: повний набір змінних детермінізму (`SOURCE_DATE_EPOCH`, `LC_ALL`, `TZ`, прапорці `-fdebug-prefix-map`).

### 4. `source_repositories` (Вихідний код)
- `primary_repository_bundle`: шлях до автономного двійкового файлу `git bundle`, що містить усю історію репозиторію.
- `git_commit_sha` та `git_tree_hash`: точні хеші коміту та кореневого дерева об'єктів Git.
- `submodules`: масив усіх субмодулів, де кожен компонент має власний автономний `.bundle` файл та зафіксований хеш коміту.

### 5. `hardware_documentation` (Апаратний пакет)
- Креслення та схеми у векторному форматі PDF/A-1b (стандарт ISO для довготривалого збереження документів, що забороняє зовнішні шрифти).
- Повний набір шарів Gerber RS-274X та файлів свердління Excellon.
- Виробничий перелік компонентів (BOM) із зазначенням первинних артикулів (MPN) та затверджених аналогів (second-source).
- Повні оригінальні PDF-даташити на всі мікросхеми плати, включаючи офіційні листи помилок кремнію (silicon errata).
- Креслення тестового стенда (test jig), розпіновку голчастих контактів (pogo-pins) та прошивку тестового адаптера.

### 6. `key_escrow_manifest` (Депонування секретів)
- Схема розподілу ключів підпису. Заборонено зберігати відкриті приватні ключі всередині архіву. Замість цього фіксується ідентифікатор відкритого ключа, протокол розділення секрету Шаміра (*Shamir's Secret Sharing*) із зазначенням порогу `k` з `n`, перелік власників часток та фізичні локації сейфів.

### 7. `signatures` (Блок цифрових підписів)
- Масив щонайменше двох незалежних підписів під повним текстом маніфесту (за винятком самої секції `signatures`). Підписи накладаються архітектором прошивки та відповідальним офіцером служби якості.

## Схема валідації та стандартизовані коди помилок

Під час щорічного пожежного тренування або перевірки архіву аудиторська програма виконує покрокову валідацію:
1. Перевірка цілісності маніфесту за схемою JSON Schema.
2. Верифікація криптографічних підписів у секції `signatures`.
3. Повний розрахунок SHA-256 / SHA-512 для кожного файлу на носії та порівняння з маніфестом.
4. Розгортання контейнера/VM та виконання збірки з вихідних кодів у каталозі `src/`.
5. Побітове порівняння свіжозібраного файлу з образом у `golden_binaries`.

Інструмент аудиту повертає стандартизовані коди помилок:

| Код | Символічна назва | Причина виникнення та інженерна дія |
| :--- | :--- | :--- |
| `0x00` | `VALIDATION_OK` | Усі контрольні суми збіглися, підписи коректні, структура непорушна. |
| `0x01` | `ERR_MANIFEST_CORRUPT` | Синтаксична помилка JSON або порушення обов'язкової схеми полів. |
| `0x02` | `ERR_FILE_MISSING` | Файл, вказаний у маніфесті, фізично відсутній на носії (битий архів). |
| `0x03` | `ERR_CHECKSUM_MISMATCH` | Обчислений SHA-256 / SHA-512 не збігається з маніфестом (деградація носія / bit rot). |
| `0x04` | `ERR_SIGNATURE_INVALID` | Цифровий підпис маніфесту або бінарника не проходить перевірку відкритим ключем. |
| `0x05` | `ERR_NON_DETERMINISTIC_BUILD` | Прошивка, зібрана з джерел усередині VM, не збігається побітово з `golden_binaries`. |
| `0x06` | `ERR_MISSING_ESCROW_RECORD` | Відсутній обов'язковий протокол відновлення криптографічних ключів або частки секрету. |
| `0x07` | `ERR_UNRESOLVED_DEPENDENCY` | Скрипт збірки намагається виконати мережевий запит на зовнішній сервер під час збірки. |

Кожна виявлена помилка автоматично формує протокол інциденту, що зумовлює термінове відновлення пошкодженого артефакту з дублюючого носія за правилом 3-2-1.
