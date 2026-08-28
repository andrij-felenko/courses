# 📋 Специфікація маніфесту кампанії оновлення парку (Campaign Specification)

Декларативний контракт оркестрації кампанії оновлення визначає правила сегментації пристроїв, параметри поетапних хвиль, обмеження одночасності передачі даних та критичні порогові значення метрик якості, за яких спрацьовує автоматичний аварійний переривач (Stop-the-Line). Специфікація використовується контролерами розгортання, серверами автентифікації та агентами управління парком для узгодженого керування життєвим циклом випуску на тисячах розподілених вузлів.

---

## Архітектурний контракт специфікації

Маніфест кампанії розглядається як незмінний (immutable) документ, що публікується в розподіленому сховищі конфігурацій перед початком будь-яких активних дій над парком. Кожна зміна параметрів кампанії (наприклад, коригування лімітів або ручне призупинення) породжує нову ревізію специфікації з фіксацією автора, часу та аудиторського сліду.

Специфікація вирішує чотири ключові завдання управління розподіленим парком:
1. **Ідентифікація та криптографічна цілісність:** зв'язує цільову версію мікропрограми з криптографічним хешем SHA-256 та цифровим підписом відкритого ключа, що унеможливлює підміну пакета на рівні проміжних мереж чи серверів доставки контенту.
2. **Селекція сумісності (Eligibility):** формує предикати апаратної відповідності, перевіряючи ревізії апаратних плат, мінімальний залишок енергії акумулятора, обсяг вільної енергонезалежної пам'яті та дозволені типи мережевих інтерфейсів.
3. **Регулювання пропускної здатності (Pacing):** обмежує пікове навантаження на інфраструктуру видачі за допомогою алгоритму маркерного кошика (Token Bucket) та максимальної кількості одночасних операцій.
4. **Статистичний арбітраж надійності:** формалізує допустимі бюджети помилок, апаратних відкатів та втрати зв'язку, перевищення яких викликає миттєве блокування конвеєра та захищає решту парку від пошкодження.

---

## Декларативна схема маніфесту (YAML)

Маніфест кампанії описує повний життєвий цикл розгортання випуску у вигляді структурованого документа:

```yaml
apiVersion: fleet.release.engine/v1alpha1
kind: FleetCampaign
metadata:
  campaignId: "cmp-2026-q3-firmware-v2.4.0"
  title: "Планове оновлення мікропрограми шлюзів телеметрії"
  createdAt: "2026-08-28T04:00:00Z"
  priority: High
spec:
  targetPackage:
    version: "2.4.0"
    artifactUrl: "https://cdn.firmware.internal/packages/gw-v2.4.0.pkg"
    sha256: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    signature: "MEUCIQDxv48mK1...crypto_sig...z9vL7b"
    minimumSourceVersion: "2.2.0"
    maximumSourceVersion: "2.3.9"
    securityPatchLevel: 20260815

  eligibility:
    hardwareRevisions:
      - "REV-B2"
      - "REV-C1"
    requiredTags:
      environment: "production"
      region: "eu-central"
    constraints:
      minBatteryPct: 60
      requireExternalPower: false
      minFreeStorageBytes: 134217728 # 128 MB
      allowedNetworks:
        - "ethernet"
        - "wifi"
        - "lte-m"

  concurrency:
    globalMaxInFlight: 2500
    tokenBucketRatePerSec: 50.0
    tokenBucketCapacity: 200
    leaseTimeoutSeconds: 1800

  stopTheLinePolicy:
    minSampleSize: 100
    heartbeatTimeoutSeconds: 3600
    evaluationWindowSeconds: 7200
    thresholds:
      maxFailureRatePct: 1.0
      maxRollbackRatePct: 0.5
      maxSilenceRatePct: 0.2
    actionOnBreach: "PauseAndAlert"

  waves:
    - name: "ring-0-dogfood"
      targetPercentage: 0.5
      maxInFlight: 50
      soakDurationSeconds: 43200     # 12 годин
      allowedTimeWindow:
        utcHourStart: 1
        utcHourEnd: 5

    - name: "ring-1-canary"
      targetPercentage: 5.0
      maxInFlight: 200
      soakDurationSeconds: 86400     # 24 години
      allowedTimeWindow:
        utcHourStart: 0
        utcHourEnd: 24

    - name: "ring-2-expansion"
      targetPercentage: 25.0
      maxInFlight: 1000
      soakDurationSeconds: 172800    # 48 годин
      allowedTimeWindow:
        utcHourStart: 0
        utcHourEnd: 24

    - name: "ring-3-global"
      targetPercentage: 100.0
      maxInFlight: 2500
      soakDurationSeconds: 0
      allowedTimeWindow:
        utcHourStart: 0
        utcHourEnd: 24
```

---

## Структури даних у програмному коді

Для впровадження специфікації в низькорівневі сервіси та контролери парку використовуються типізовані структури мовами C та C++.

:::tabs
@tab C
```c
#include <stdint.h>
#include <stdbool.h>

#define MAX_NAME_LEN 64
#define MAX_URL_LEN 256
#define MAX_SHA256_HEX 65
#define MAX_SIG_LEN 128
#define MAX_HW_REVS 8
#define MAX_WAVES 8

typedef enum {
    CAMPAIGN_STATUS_DRAFT = 0,
    CAMPAIGN_STATUS_SCHEDULED,
    CAMPAIGN_STATUS_IN_PROGRESS,
    CAMPAIGN_STATUS_SOAKING,
    CAMPAIGN_STATUS_PAUSED_STOP_THE_LINE,
    CAMPAIGN_STATUS_ABORTED,
    CAMPAIGN_STATUS_COMPLETED
} CampaignStatus;

typedef enum {
    BREACH_ACTION_PAUSE_AND_ALERT = 0,
    BREACH_ACTION_EMERGENCY_ROLLBACK,
    BREACH_ACTION_ABORT
} BreachAction;

typedef struct {
    char version[MAX_NAME_LEN];
    char artifact_url[MAX_URL_LEN];
    char sha256[MAX_SHA256_HEX];
    char signature[MAX_SIG_LEN];
    char min_source_version[MAX_NAME_LEN];
    char max_source_version[MAX_NAME_LEN];
    uint32_t security_patch_level;
} TargetPackageSpec;

typedef struct {
    char hw_revisions[MAX_HW_REVS][MAX_NAME_LEN];
    uint32_t hw_revisions_count;
    uint32_t min_battery_pct;
    bool require_external_power;
    uint64_t min_free_storage_bytes;
} EligibilitySpec;

typedef struct {
    uint32_t min_sample_size;
    uint32_t heartbeat_timeout_sec;
    uint32_t evaluation_window_sec;
    double max_failure_rate_pct;
    double max_rollback_rate_pct;
    double max_silence_rate_pct;
    BreachAction action_on_breach;
} StopTheLinePolicy;

typedef struct {
    char name[MAX_NAME_LEN];
    double target_percentage;
    uint32_t max_in_flight;
    uint32_t soak_duration_sec;
    uint8_t utc_hour_start;
    uint8_t utc_hour_end;
} WaveSpec;

typedef struct {
    char campaign_id[MAX_NAME_LEN];
    char title[MAX_NAME_LEN * 2];
    uint64_t created_at_unix;
    TargetPackageSpec package;
    EligibilitySpec eligibility;
    StopTheLinePolicy stop_policy;
    WaveSpec waves[MAX_WAVES];
    uint32_t waves_count;
    uint32_t global_max_in_flight;
    double token_bucket_rate;
    uint32_t lease_timeout_sec;
} FleetCampaignSpec;
```
@tab C++
```cpp
#include <string>
#include <vector>
#include <chrono>
#include <cstdint>
#include <optional>

namespace fleet::release {

enum class CampaignStatus {
    Draft,
    Scheduled,
    InProgress,
    Soaking,
    PausedStopTheLine,
    Aborted,
    Completed
};

enum class BreachAction {
    PauseAndAlert,
    EmergencyRollback,
    Abort
};

struct TargetPackageSpec {
    std::string version;
    std::string artifactUrl;
    std::string sha256;
    std::string signature;
    std::string minSourceVersion;
    std::string maxSourceVersion;
    uint32_t securityPatchLevel{0};
};

struct EligibilitySpec {
    std::vector<std::string> hardwareRevisions;
    uint32_t minBatteryPct{50};
    bool requireExternalPower{false};
    uint64_t minFreeStorageBytes{64 * 1024 * 1024};
    std::vector<std::string> allowedNetworks;
};

struct StopTheLinePolicy {
    uint32_t minSampleSize{100};
    std::chrono::seconds heartbeatTimeout{3600};
    std::chrono::seconds evaluationWindow{7200};
    double maxFailureRatePct{1.0};
    double maxRollbackRatePct{0.5};
    double maxSilenceRatePct{0.2};
    BreachAction actionOnBreach{BreachAction::PauseAndAlert};
};

struct WaveSpec {
    std::string name;
    double targetPercentage{0.0};
    uint32_t maxInFlight{100};
    std::chrono::seconds soakDuration{0};
    uint8_t utcHourStart{0};
    uint8_t utcHourEnd{24};
};

struct FleetCampaignSpec {
    std::string campaignId;
    std::string title;
    std::chrono::system_clock::time_point createdAt;
    TargetPackageSpec package;
    EligibilitySpec eligibility;
    StopTheLinePolicy stopPolicy;
    std::vector<WaveSpec> waves;
    uint32_t globalMaxInFlight{1000};
    double tokenBucketRatePerSec{50.0};
    std::chrono::seconds leaseTimeout{1800};
};

} // namespace fleet::release
```
:::

---

## Протокол взаємодії та життєвий цикл маркера лізингу

Для запобігання перевантаженню інфраструктури видачі оновлень клієнтські пристрої не можуть починати завантаження бінарного пакета спонтанно. Взаємодія будується на основі протоколу тимчасових дозволів (лізингу маркерів).

Клієнтський агент, отримавши сповіщення про наявність нової версії в межах поточної хвилі, надсилає запит на отримання слота завантаження. Серверний контролер перевіряє ліміт одночасності та наявність вільних маркерів у кошику. Якщо ліміт не вичерпано, пристрою надається підписаний тимчасовий маркер із часом життя `leaseTimeoutSeconds` (наприклад, 30 хвилин).

Протягом цього інтервалу пристрій здійснює завантаження артефакту частинами. Якщо через повільний або нестабільний зв'язок процес затягується, клієнт зобов'язаний надіслати запит на продовження лізингу. Якщо пристрій раптово втрачає живлення чи зв'язок під час завантаження, сервер після завершення інтервалу таймауту автоматично повертає маркер у глобальний пул, запобігаючи «витоку» слотів одночасності.

```text
МЕХАНІКА ЛІЗИНГУ МАРКЕРА ЗАВАНТАЖЕННЯ:
Пристрій ──► Запит маркера ──► Серверний контролер (Token Bucket)
                             ├── Якщо квота є ──► Маркер видано (Таймаут 30 хв)
                             └── Якщо вичерпано ──► Відмова (Повторити через Retry-After)
Пристрій ──► Завантаження ──► Фіксація успіху / Звільнення маркера в пул
```

---

## Протокол звітування станів пристрою

Під час виконання оновлення кожен пристрій зобов'язаний надсилати події зміни стану в чергу телеметрії сервера оркестрації. Формат повідомлення визначає поточну фазу оновлення та діагностичний контекст:

```json
{
  "deviceId": "gw-eu-849201",
  "campaignId": "cmp-2026-q3-firmware-v2.4.0",
  "timestamp": "2026-08-28T04:15:32Z",
  "state": "REBOOTING",
  "sourceVersion": "2.3.8",
  "targetVersion": "2.4.0",
  "activeSlot": "SLOT_B",
  "errorCode": 0,
  "errorMessage": "",
  "batteryPct": 88,
  "rssiDbm": -67
}
```

### Перелік термінальних та проміжних станів

* `ASSIGNED` — пристрій отримав призначення на хвилю, але ще не запитав маркер завантаження.
* `DOWNLOADING` — пристрій утримує активний лізинг маркера і стягує бінарний образ через CDN.
* `VERIFYING` — виконується перевірка SHA-256 та криптографічного підпису Ed25519 перед записом у неактивний слот A/B.
* `FLASHING` — прямий запис блоків у флеш-пам'ять другого слота.
* `REBOOTING` — встановлено прапорець завантажувача на новий слот, ініційовано перезавантаження мікроконтролера.
* `SUCCEEDED` — пристрій успішно завантажився з нового слота, пройшов самодіагностику та надіслав перший робочий heartbeat.
* `FAILED` — відмова на етапі завантаження, верифікації або запису у флеш. Пристрій залишається на старій робочій версії.
* `ROLLED_BACK` — пристрій спробував завантажитися з нового слота, зазнав паніки ядра або спрацювання Watchdog і автоматично повернувся у попередній слот.
* `SILENCED` — обчислюваний стан на стороні сервера: минув інтервал `heartbeatTimeoutSeconds` після події `REBOOTING`, а новий heartbeat так і не надійшов.

---

## Статистичне обчислення замовклих пристроїв (Silence Detection)

Показник замовклих пристроїв є найбільш критичним індикатором стану кампанії, оскільки сигналізує про втрату керування та апаратне окрипічення. На відміну від явних відмов, де пристрій самостійно надсилає код помилки, стан мовчання виявляється виключно на стороні сервера шляхом безперервного зіставлення очікуваних і фактичних часових міток.

Коли пристрій надсилає подію `REBOOTING`, серверний планувальник реєструє відкладений таймер очікування тривалістю `heartbeatTimeoutSeconds`. Якщо до настання граничного часу від пристрою надходить валідний звіт зі станом `SUCCEEDED` або `ROLLED_BACK`, таймер скасовується. Якщо ж інтервал вичерпується без жодного повідомлення, пристрій автоматично переводиться у стан `SILENCED`, а лічильник мовчання поточної хвилі інкрементується.

Для запобігання хибним спрацьовуванням контролер застосовує фільтрацію за якістю зв'язку: якщо пристрій працює через ненадійний супутниковий чи стільниковий канал із високим рівнем втрати пакетів, для нього може застосовуватися динамічний коефіцієнт масштабування таймауту.

---

## Таблиця полів та правила валідації специфікації

| Поле | Тип | Обов'язкове | Опис та семантичні обмеження |
|---|---|---|---|
| `campaignId` | Рядок | Так | Унікальний ідентифікатор кампанії в розподіленій базі метаданих. |
| `targetPackage.version` | Рядок (SemVer) | Так | Цільова версія випуску. Повинна бути строго вищою за поточну базову. |
| `targetPackage.sha256` | Рядок (Hex) | Так | 64-символьний контрольний дайджест бінарного пакета для перевірки цілісності. |
| `targetPackage.signature` | Рядок (Base64) | Так | Криптографічний підпис відкритого ключа випуску (Ed25519 або ECDSA P-256). |
| `targetPackage.minimumSourceVersion` | Рядок (SemVer) | Так | Найстаріша версія, з якої дозволено прямий перехід без проміжних кроків міграції. |
| `eligibility.hardwareRevisions` | Масив рядків | Так | Список сумісних ревізій друкованих плат. Пристрої інших ревізій відсікаються на етапі планування. |
| `eligibility.minBatteryPct` | Ціле число (0–100) | Ні | Мінімальний залишок заряду акумулятора перед початком прошивки (захист від знеструмлення). |
| `eligibility.minFreeStorageBytes` | Ціле число | Так | Мінімальний обсяг вільного місця у файловій системі для збереження тимчасового пакета. |
| `concurrency.globalMaxInFlight` | Ціле число | Так | Абсолютна стеля одночасних завантажень на всі CDN-вузли та сервери видачі. |
| `concurrency.tokenBucketRatePerSec` | Дійсне число | Так | Швидкість поповнення пулу дозволів на завантаження (маркерів за секунду). |
| `concurrency.leaseTimeoutSeconds` | Ціле число | Так | Час життя виданого маркера. Після таймауту маркер повертається в пул, якщо клієнт зник. |
| `stopTheLinePolicy.minSampleSize` | Ціле число | Так | Мінімальна кількість опрацьованих пристроїв для активації статистичного арбітражу SLI. |
| `stopTheLinePolicy.heartbeatTimeoutSeconds` | Ціле число | Так | Граничний інтервал очікування телеметрії після старту перезавантаження пристрою. |
| `stopTheLinePolicy.thresholds.maxFailureRatePct` | Дійсне число | Так | Допустимий поріг явних помилок інсталяції (`Failed / Assigned * 100`). |
| `stopTheLinePolicy.thresholds.maxRollbackRatePct` | Дійсне число | Так | Допустимий поріг апаратних повернень у старий A/B слот (`RolledBack / Assigned * 100`). |
| `stopTheLinePolicy.thresholds.maxSilenceRatePct` | Дійсне число | Так | Допустимий поріг замовклих пристроїв (`Silenced / Assigned * 100`). |
| `waves[].targetPercentage` | Дійсне число | Так | Накопичувальний відсоток парку, який охоплюється цією хвилею (строго зростаюча послідовність). |
| `waves[].soakDurationSeconds` | Ціле число | Так | Тривалість вікна спостереження за когортою до переходу на наступну хвилю. |
| `waves[].allowedTimeWindow` | Об'єкт | Ні | Дозволені години доби (UTC) для старту оновлення з урахуванням місцевого часу користувачів. |

---

## Інваріанти валідації маніфесту перед запуском

Контролер оркестрації виконує набір обов'язкових структурних перевірок перед переведенням кампанії у стан `SCHEDULED`:
1. **Монотонність хвиль:** значення `targetPercentage` у кожній наступній хвилі повинно бути строго більшим за попереднє, а фінальна хвиля обов'язково має дорівнювати 100.0%.
2. **Ненульовий час витримки для початкових кілець:** для хвиль з охопленням менше 50% значення `soakDurationSeconds` не може бути меншим за 14 400 секунд (4 години), що гарантує отримання перших репрезентативних даних моніторингу за добовим циклом.
3. **Валідація безпеки відкату:** поріг `maxSilenceRatePct` завжди повинен бути меншим за `maxFailureRatePct`, оскільки втрата зв'язку з пристроєм є критично небезпечнішим збоєм, ніж штатна відмова з поверненням коду помилки.
4. **Консистентність лімітів одночасності:** значення `maxInFlight` окремої хвилі не може перевищувати глобальний ліміт `globalMaxInFlight`.
