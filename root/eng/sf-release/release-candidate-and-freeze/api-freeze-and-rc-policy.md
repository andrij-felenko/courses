# 📋 Специфікація політик заморозки коду та критеріїв релізного шлюзу

Ця специфікація встановлює формальний контракт для керування стадіями стабілізації кодової бази, конфігурації автоматизованих шлюзів перевірки (Quality Gates) та верифікації вихідних критеріїв (Exit Criteria). Вона призначена для системних архітекторів, інженерів випуску та розробників вбудованого програмного забезпечення, які налаштовують конвеєри безперервної інтеграції (CI/CD) для апаратних платформ та високонадійних сервісів.

---

## 1. Фази життєвого циклу релізу та матриця дозволених операцій

Перехід між фазами стабілізації релізу в системі контролю версій змінює правила доступу до релізної гілки `release/vX.Y` та набір обов'язкових перевірок для кожного запиту на злиття (Pull Request / Merge Request).

### Семантична матриця допустимих змін

| Тип інженерної операції | Normal Dev | Feature Freeze (FF) | ABI/String Freeze | Code Freeze (CF) | Release Candidate (RC) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Новий модуль / Драйвер периферії | Дозволено | **Заборонено** | **Заборонено** | **Заборонено** | **Заборонено** |
| Структурний рефакторинг логіки | Дозволено | **Заборонено** | **Заборонено** | **Заборонено** | **Заборонено** |
| Зміна публічних C/C++ сигнатур | Дозволено | Дозвіл техліда | **Заборонено** | **Заборонено** | **Заборонено** |
| Модифікація NVM / Flash карти | Дозволено | Дозвіл архітектора | **Заборонено** | **Заборонено** | **Заборонено** |
| Додавання / Зміна рядків UI | Дозволено | Дозволено | **Заборонено** | **Заборонено** | **Заборонено** |
| Виправлення P2 / P3 (Minor баги) | Дозволено | Дозволено | Дозволено | **Заборонено** | **Заборонено** |
| Виправлення P0 / P1 (Blocker баги) | Дозволено | Дозволено | Дозволено | Дозвіл Bug Council | Cherry-Pick + Релізний лід |
| Оновлення тестів HIL та документації | Дозволено | Дозволено | Дозволено | Дозволено | Дозвіл Release Lead |

### Опис стадій та інваріантів

1. **Фаза вільної розробки (Normal Development)**:
   - Відкрита для будь-яких функціональних змін у гілці `main`.
   - Інваріант: проходження базового набору модульних тестів і статичного аналізу (Clang-Tidy, Cppcheck).
2. **Фаза заморозки функціональності (Feature Freeze)**:
   - Вводиться за 3–4 тижні до планового релізу відсіканням гілки `release/vX.Y`.
   - Інваріант: обсяг скомпільованого коду (секція `.text`) більше не збільшується за рахунок нових алгоритмів; заборонено додавати нові системні виклики та команди керування.
3. **Фаза фіксації інтерфейсів та ресурсів (ABI & String Freeze)**:
   - Вводиться за 2 тижні до релізу.
   - Інваріант: двійкова сумісність структур даних, збережених у енергонезалежній пам'яті (Flash/EEPROM), залишається незмінною; усі текстові ресурси передані в бюро технічних перекладів та орган сертифікації.
4. **Фаза повної заморозки коду (Code Freeze)**:
   - Вводиться за 1 тиждень до релізу або після готовності кандидата `RC1`.
   - Інваріант: жоден рядок коду не змінюється без санкції Релізного комітету (Bug Council); дозволяються тільки точкові виправлення з нульовим радіусом побічного впливу.
5. **Фаза кваліфікації реліз-кандидата (Release Candidate Phase)**:
   - Формування підписаного бінарного артефакту та виконання 100% програми апаратної верифікації на стендах HIL.
   - Інваріант: двійкова ідентичність кандидата, який успішно пройшов усі тести, фіксується як фінальний релізний образ (Golden Master).

---

## 2. Машинно-зчитувана конфігурація шлюзу (`release-gate.yaml`)

Файл конфігурації `release-gate.yaml` розміщується в каталозі `.ci/` репозиторію. Автоматизовані агенти конвеєра зчитують його перед виконанням збірки для перевірки відповідності відкритих запитів на злиття та зібраних артефактів встановленим лімітам.

```yaml
version: "1.0"
release_target: "v2.4.0"
branch_pattern: "^release/v[0-9]+\\.[0-9]+$"

# Політики контролю запитів на злиття за фазами
phases:
  feature_freeze:
    enforce_labels: true
    blocked_labels:
      - "type:feature"
      - "type:refactoring"
      - "type:optimization"
    required_reviewers_count: 2
    allow_direct_push: false

  abi_string_freeze:
    check_abi_diff: true
    abi_baseline_tag: "v2.3.0"
    forbidden_modified_paths:
      - "include/abi/**/*.h"
      - "drivers/registers/**/*.h"
      - "resources/locale/**/*.json"
      - "schema/nvm_layout.xml"
      - "proto/**/*.proto"

  code_freeze:
    require_bug_council_approval: true
    allowed_labels:
      - "severity:p0-blocker"
      - "severity:p1-critical"
      - "type:qualification-fix"
    mandatory_pr_fields:
      - "root_cause_analysis"
      - "regression_risk_assessment"
      - "hardware_verification_steps"
      - "rollback_plan"

# Набір числових критеріїв виходу для промоції в GA
exit_criteria:
  defect_thresholds:
    max_open_p0: 0
    max_open_p1: 0
    max_open_p2_unmitigated: 0
    max_unverified_fixes: 0

  hardware_in_the_loop:
    minimum_test_runs: 10
    required_pass_rate_percent: 100.0
    allowed_flaky_tests_count: 0
    prohibited_system_events:
      - "HARD_FAULT"
      - "WATCHDOG_TIMEOUT_RESET"
      - "BROWNOUT_RESET"
      - "STACK_OVERFLOW_TRAP"
      - "RTOS_MUTEX_DEADLOCK"
      - "BUS_FAULT_PRECISE"

  resource_budgets:
    flash_rom_bytes_max: 8912896          # 8.5 MiB (85% ліміт від 10 MiB загального обсягу)
    ram_bss_data_bytes_max: 393216        # 384 KiB (75% ліміт від 512 KiB доступного SRAM)
    stack_watermark_free_bytes_min: 4096    # Мінімум 4 KiB недоторканого простору у найглибшому стеку
    cold_boot_time_ms_max: 250            # Час від зняття апаратного Reset до першого кадру
    deep_sleep_current_microamps_max: 15.0 # Максимальний середній струм у режимі сну
    active_tx_current_milliamps_max: 120.0 # Піковий струм радіотрансивера під час передачі

  soak_testing:
    device_farm_units_min: 50
    duration_hours_min: 72.0
    ambient_temperature_cycles:
      min_celsius: -20
      max_celsius: 70
      cycles_count: 6
    allowed_node_reboots: 0
    allowed_dropped_frames_percent: 0.0
```

---

## 3. Схема метаданих реліз-кандидата (`rc-manifest.json`)

Кожна збірка кандидата утворює цифровий сертифікат готовності у форматі JSON Schema. Цей документ містить підтвердження всіх вимірювань і підписується закритим ключем релізного контуру.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "ReleaseCandidateManifest",
  "type": "object",
  "required": [
    "schema_version",
    "release_tag",
    "rc_iteration",
    "commit_sha",
    "build_timestamp_utc",
    "artifacts",
    "verification_report",
    "decision"
  ],
  "properties": {
    "schema_version": {
      "type": "string",
      "enum": ["1.0"]
    },
    "release_tag": {
      "type": "string",
      "pattern": "^v[0-9]+\\.[0-9]+\\.[0-9]+$"
    },
    "rc_iteration": {
      "type": "integer",
      "minimum": 1
    },
    "commit_sha": {
      "type": "string",
      "pattern": "^[a-f0-9]{40}$"
    },
    "build_timestamp_utc": {
      "type": "string",
      "format": "date-time"
    },
    "artifacts": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["filename", "target_architecture", "sha256", "size_bytes"],
        "properties": {
          "filename": { "type": "string" },
          "target_architecture": { "type": "string" },
          "sha256": { "type": "string", "pattern": "^[a-f0-9]{64}$" },
          "size_bytes": { "type": "integer", "minimum": 1 }
        }
      }
    },
    "verification_report": {
      "type": "object",
      "required": [
        "hil_suite_passed",
        "total_hil_tests",
        "failed_hil_tests",
        "resource_budgets_passed",
        "measured_flash_bytes",
        "measured_ram_bytes",
        "measured_sleep_current_ua",
        "measured_boot_time_ms",
        "soak_test_passed"
      ],
      "properties": {
        "hil_suite_passed": { "type": "boolean" },
        "total_hil_tests": { "type": "integer", "minimum": 1 },
        "failed_hil_tests": { "type": "integer", "enum": [0] },
        "resource_budgets_passed": { "type": "boolean" },
        "measured_flash_bytes": { "type": "integer" },
        "measured_ram_bytes": { "type": "integer" },
        "measured_sleep_current_ua": { "type": "number" },
        "measured_boot_time_ms": { "type": "integer" },
        "soak_test_passed": { "type": "boolean" },
        "soak_duration_hours": { "type": "number", "minimum": 72.0 }
      }
    },
    "decision": {
      "type": "object",
      "required": ["status", "evaluated_by", "signature"],
      "properties": {
        "status": {
          "type": "string",
          "enum": ["PROMOTED_TO_GA", "REJECTED", "UNDER_QUALIFICATION"]
        },
        "evaluated_by": { "type": "string" },
        "signature": { "type": "string" }
      }
    }
  }
}
```

---

## 4. Інтерфейс утиліти командного рядка (`rc-arbiter`)

Утиліта `rc-arbiter` автоматизує всі кроки перевірки та інтегрується в сценарії CI/CD (GitHub Actions, GitLab CI, Jenkins).

### Синтаксис та опис команд

```bash
# 1. Валідація метаданих Pull Request на відповідність фазі Code Freeze
rc-arbiter validate-pr \
  --policy .ci/release-gate.yaml \
  --pr-metadata pr-1042.json \
  --diff patch.diff

# 2. Оцінка розмірів секцій скомпільованого бінарника за мапою лінкера
rc-arbiter evaluate-budgets \
  --policy .ci/release-gate.yaml \
  --map-file build/firmware.map \
  --elf-file build/firmware.elf

# 3. Комплексна верифікація звітів тестування та генерація маніфесту
rc-arbiter verify-candidate \
  --policy .ci/release-gate.yaml \
  --hil-report test-results/hil-summary.json \
  --soak-report test-results/soak-72h.json \
  --artifact build/firmware.bin \
  --out-manifest build/rc-manifest.json

# 4. Промоція кандидата у фінальний Golden Master через криптографічний HSM-модуль
rc-arbiter promote-to-ga \
  --manifest build/rc-manifest.json \
  --hsm-slot 1 \
  --key-alias "prod-firmware-signing-2026" \
  --output-package dist/firmware-v2.4.0-GA.tar.gz
```

### Коди завершення процесу (CLI Exit Codes)

Утиліта повертає детерміновані коди завершення, що використовуються конвеєром для зупинки або продовження виконання задач:

| Код | Символічна назва | Детальний опис причини зупинки |
| :--- | :--- | :--- |
| `0` | `GATE_PASS_PROMOTED` | Усі критерії виходу виконано, артефакт підтверджено та схвалено. |
| `1` | `GATE_FAIL_OPEN_BLOCKERS` | Знайдено відкриті P0/P1 дефекти або апаратні скидання в логах. |
| `2` | `GATE_FAIL_BUDGET_OVERRUN` | Перевищено ліміти Flash ROM, SRAM, струму сну або часу старту. |
| `3` | `GATE_FAIL_HIL_REGRESSION` | Рівень успішності проходження тестів на стендах HIL менше 100%. |
| `4` | `GATE_FAIL_POLICY_VIOLATION` | Порушено правила заморозки (несанкціонована зміна ABI, відсутній RCA). |
| `5` | `GATE_FAIL_CHECKSUM_MISMATCH` | Контрольна сума SHA-256 не збігається із зафіксованою в маніфесті. |

---

## 5. Аудит безпеки та вимоги до відтворюваності збірки (Hermetic & Reproducible Builds)

Для забезпечення принципу бінарної ідентичності конвеєр збірки кандидатів зобов'язаний гарантувати відтворюваність (Reproducibility). Якщо два незалежні агенти збирають один і той самий коміт, отримані двійкові файли повинні збігатися побайтово.

### Обов'язкові прапорці компіляції та лінкування

```makefile
# Видалення абсолютних шляхів файлової системи хоста з налагоджувальних секцій DWARF
CFLAGS += -ffile-prefix-map=$(WORKSPACE_DIR)=.
CFLAGS += -fmacro-prefix-map=$(WORKSPACE_DIR)=.
CFLAGS += -fdebug-prefix-map=$(WORKSPACE_DIR)=.

# Заборона використання недетермінованих макросів часу та дати
CFLAGS += -Werror=date-time

# Фіксація порядку секцій лінкером для усунення випадкових перестановок
LDFLAGS += -Wl,--sort-section=alignment
LDFLAGS += -Wl,--build-id=none
```

### Нормалізація середовища виконання

Перед запуском компілятора автоматизований раннер встановлює фіксовані параметри середовища:
- `SOURCE_DATE_EPOCH`: мітка часу Unix, зафіксована за останнім комітом у релізній гілці.
- `LC_ALL=C`: запобігає локалізованому сортуванню символів у таблицях компілятора.
- `TZ=UTC`: уніфікація часового поясу для виключення зміщень у генерованих заголовках.
- Контейнеризація: фіксація точного дайджесту образу компілятора (`gcc-arm-none-eabi@sha256:...`).

---

## 6. Регламент аварійного скасування заморозки (Emergency Unfreeze Protocol)

Якщо на стадії Code Freeze або тестування Release Candidate виявлено критичний дефект, усунення якого вимагає зміни структури даних або додавання нових модулів, застосовується регламент аварійного скасування заморозки:

1. **Ініціація**: Технічний лід або системний архітектор створює запит `RFC: Emergency Unfreeze` із описом загрози та технічним обґрунтуванням необхідності зняття блокування.
2. **Анулювання активного RC**: Усі попередньо зібрані реліз-кандидати (`RC1`, `RC2`) маркуються в реєстрі артефактів як `REVOKED` (анульовані).
3. **Повернення до Feature Freeze**: Релізна гілка тимчасово переводиться на попередній рівень контролю, де дозволені структурні модифікації за обов'язкового погодження архітектора.
4. **Внесення виправлення**: Патч вливається в `main` і переноситься через `cherry-pick` у релізну гілку.
5. **Повний перезапуск циклу кваліфікації**: Заморозка вводиться повторно, формується `RC(N+1)`, і повна 72-годинна програма тестування HIL запускається з першої секунди без зарахування попередніх результатів.

---

## 7. Шаблон заявки на внесення змін під час Code Freeze (Bug Council Change Request)

Будь-який запит на злиття в релізну гілку під час дії Code Freeze повинен містити структурований опис у тілі Pull Request за наступною обов'язковою формою:

```markdown
### Заявка на виправлення в релізній гілці (Code Freeze Exception)

- **Ідентифікатор дефекту**: ISSUE-4092 (P0 - Blocker)
- **Першопричина (Root Cause Analysis)**:
  Переповнення 16-бітного таймера апаратного лічильника при безперервній роботі понад 18 годин,
  що призводить до блокування шини I2C у стані очікування прапорця готовності.
- **Радіус побічного впливу (Blast Radius)**:
  Зміна локалізована виключно у файлі `drivers/i2c_master.c` (рядки 114–122).
  Сусідні драйвери SPI та UART не зачіпаються.
- **Оцінка ризику регресії**:
  Низький. Додано явне маскування бітів та перевірку таймауту.
- **План верифікації на залізі**:
  1. Запуск стрес-тесту `hil_i2c_wraparound_test` на стенді з 10 платами протягом 24 годин.
  2. Перевірка відсутності генерації помилкових подій I2C NACK.
- **План відкату (Rollback Strategy)**:
  Скасування коміту через `git revert` повертає поведінку до базової версії RC1.
```

---

## 8. Інтеграційний контур автоматизації у конвеєрі CI/CD

Автоматизована перевірка політик заморозки виконується як перший обов'язковий етап (Pre-merge Check) для кожного відкритого запиту на злиття в релізну гілку.

### Приклад конфігурації задачі GitHub Actions

```yaml
name: Release Gate Enforcement

on:
  pull_request:
    branches:
      - 'release/v*'

jobs:
  enforce-freeze-policy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Download rc-arbiter tool
        run: |
          curl -sSL https://artifacts.internal/tools/rc-arbiter -o /usr/local/bin/rc-arbiter
          chmod +x /usr/local/bin/rc-arbiter

      - name: Validate Pull Request against Freeze Gate
        run: |
          git diff origin/${{ github.base_ref }}...HEAD > pr-diff.patch
          rc-arbiter validate-pr \
            --policy .ci/release-gate.yaml \
            --pr-metadata "${{ toJson(github.event.pull_request) }}" \
            --diff pr-diff.patch
```

Якщо інженер створює Pull Request із міткою `type:feature` під час дії фази Feature Freeze, утиліта `rc-arbiter` повертає код завершення `4` (`GATE_FAIL_POLICY_VIOLATION`), що блокує можливість злиття коду на рівні правил захисту гілки (Branch Protection Rules) в репозиторії.
