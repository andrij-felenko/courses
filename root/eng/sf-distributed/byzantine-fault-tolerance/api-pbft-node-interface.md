# 📋 Довідник структур повідомлень та інтерфейсу вузла PBFT

У протоколі PBFT (Practical Byzantine Fault Tolerance) взаємодія між клієнтами, первинним вузлом (Primary) та резервними репліками (Backups) регламентується суворим двійковим протоколом обміну повідомленнями, векторизацією криптографічних доказів та детермінованим автоматом переходів між станами.

Цей довідник описує формати повідомлень протоколу, криптографічні контракти автентифікації, структуру журналів репліки, мережевий контракт передачі даних, таблицю переходів станів та коди повернення функцій обробки подій.

## Формати та двійкові структури повідомлень

Усі повідомлення в системі містять номер поточного виду `v`, порядковий номер операції `n`, 256-бітний криптографічний дайджест `d` та цифровий підпис або вектор кодів автентифікації повідомлень (MAC).

| Тип повідомлення | Відправник | Одержувачі | Призначення в протоколі | Обов'язкові двійкові поля |
|---|---|---|---|---|
| `REQUEST` | Клієнт `c` | Первинний вузол `p` | Ініціація виконання операції `o` | `<REQUEST, o, t, c>_sigma_c` (тіло `o`, мітка часу `t`, ідентифікатор `c`, підпис клієнта) |
| `PRE-PREPARE` | Первинний вузол `p` | Усі репліки | Фіксація слота `n` у виді `v` | `<PRE-PREPARE, v, n, d>_sigma_p, m` (вид `v`, слот `n`, дайджест `d`, підпис лідера, тіло `m`) |
| `PREPARE` | Репліка `i` | Усі репліки | Перехресне підтвердження слота | `<PREPARE, v, n, d, i>_sigma_i` (вид `v`, слот `n`, дайджест `d`, номер репліки `i`, підпис) |
| `COMMIT` | Репліка `i` | Усі репліки | Підтвердження готовності до фіксації | `<COMMIT, v, n, d, i>_sigma_i` (вид `v`, слот `n`, дайджест `d`, номер репліки `i`, підпис) |
| `REPLY` | Репліка `i` | Клієнт `c` | Повернення результату виконання `r` | `<REPLY, v, t, c, i, r>_sigma_i` (вид `v`, мітка `t`, ідентифікатор `c`, репліка `i`, результат `r`) |
| `CHECKPOINT` | Репліка `i` | Усі репліки | Фіксація стабільного зрізу стану `n` | `<CHECKPOINT, n, d_state, i>_sigma_i` (номер слота `n`, дайджест стану `d_state`, підпис репліки `i`) |
| `VIEW-CHANGE` | Репліка `i` | Усі репліки | Ініціація процедури скидання лідера | `<VIEW-CHANGE, v+1, n, C, P, i>_sigma_i` (новий вид `v+1`, чекпойнт `n`, доказ `C`, сертифікати `P`) |
| `NEW-VIEW` | Новий лідер `p'` | Усі репліки | Встановлення нового стабільного виду | `<NEW-VIEW, v+1, V, O>_sigma_p'` (новий вид `v+1`, набір з `2f` View-Change `V`, набір Pre-Prepare `O`) |

### Деталізація полів службових повідомлень

1. **Повідомлення `CHECKPOINT`:**
   * `n` (uint64_t) — порядковий номер останньої транзакції, яка увійшла до знімка стану;
   * `d_state` (uint8_t[32]) — криптографічний хеш-корінь дерева стану автомата (Merkle Root);
   * `i` (uint32_t) — унікальний ідентифікатор репліки;
   * `signature` — цифровий підпис репліки.
2. **Повідомлення `VIEW-CHANGE`:**
   * `v + 1` (uint32_t) — номер нового виду, до якого переходить репліка;
   * `n` (uint64_t) — номер останнього стабільного чекпойнта, відомого репліці;
   * `C` (struct) — набір із `2f + 1` валідних повідомлень `CHECKPOINT` для слота `n`;
   * `P` (struct[]) — множина підготовлених сертифікатів для транзакцій зі слотами `n' > n`;
   * `i` (uint32_t) — ідентифікатор репліки.
3. **Повідомлення `NEW-VIEW`:**
   * `v + 1` (uint32_t) — новий активний номер виду;
   * `V` (struct[]) — набір із `2f` валідних повідомлень `VIEW-CHANGE` від різних реплік;
   * `O` (struct[]) — набір відновлених повідомлень `PRE-PREPARE`, згенерованих новим лідером.

## Мережевий протокол та двійкове пакування

Усі повідомлення передаються через надійні з'єднання TCP або TLS. Для запобігання атакам розриву потоку застосовується довжинне фреймування (Length-Prefixed Framing).

Кожен двійковий фрейм у мережі має таку структуру заголовка (усі цілі числа передаються у форматі Big-Endian / Network Byte Order):
* `magic` (uint32_t) — магічне число протоколу `0x50424654` (ASCII "PBFT");
* `msg_type` (uint16_t) — числовий код типу повідомлення (1 = Request, 2 = Pre-Prepare, 3 = Prepare, 4 = Commit, 5 = Reply, 6 = Checkpoint, 7 = View-Change, 8 = New-View);
* `payload_length` (uint32_t) — довжина корисного навантаження в байтах без урахування заголовка;
* `sender_id` (uint32_t) — числовий номер репліки або клієнта;
* `mac_vector_offset` (uint32_t) — зміщення до блоку криптографічних підписів усередині корисного навантаження.

## Криптографічний контракт та автентифікація

Кожен вузол системи має пару ключів асиметричної криптографії (публічний / приватний ключ) та набір попередньо узгоджених симетричних ключів для прямого каналу зв'язку з кожним іншим учасником кластера.

1. **Дайджест запиту (Digest):** Обчислюється як криптографічний геш SHA-256 або BLAKE3 від повного двійкового представлення клієнтського запиту: `d = Hash(m)`.
2. **Вектори MAC (Message Authentication Codes):** Для оптимізації швидкодії в межах штатного режиму (фази Pre-Prepare, Prepare, Commit) вузли використовують вектори автентифікації повідомлень на базі HMAC-SHA256 або Poly1305. Вектор містить `N - 1` окремих MAC-міток — по одній для кожної репліки-одержувача.
3. **Асиметричні цифрові підписи:** Повідомлення `VIEW-CHANGE` та `NEW-VIEW` обов'язково підписуються за допомогою асиметричних ключів (наприклад, Ed25519 або ECDSA), оскільки ці повідомлення передаються транзитивно через нового лідера й вимагають незалежної публічної верифікації кожним вузлом кластера.

## Інтерфейс функцій обробки подій вузла

Нижче наведено формальні сигнатури C-інтерфейсу обробки повідомлень та керування життєвим циклом репліки PBFT:

:::tabs
```c
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define PBFT_DIGEST_SIZE 32
#define PBFT_MAX_REPLICAS 16

typedef struct {
    uint8_t bytes[PBFT_DIGEST_SIZE];
} pbft_digest_t;

typedef enum {
    PBFT_OK                           =  0,
    PBFT_ERR_INVALID_SIGNATURE        = -1,
    PBFT_ERR_INVALID_DIGEST           = -2,
    PBFT_ERR_VIEW_MISMATCH            = -3,
    PBFT_ERR_NOT_PRIMARY              = -4,
    PBFT_ERR_EQUIVOCATION             = -5,
    PBFT_ERR_DUPLICATE_MESSAGE        = -6,
    PBFT_ERR_WATERMARK_OUT_OF_BOUNDS  = -7,
    PBFT_ERR_INSUFFICIENT_QUORUM      = -8,
    PBFT_ERR_CHECKPOINT_INVALID       = -9
} pbft_result_t;

typedef struct {
    uint32_t view;
    uint32_t seq_num;
    pbft_digest_t digest;
    const uint8_t* payload;
    size_t payload_len;
    uint32_t sender_id;
} pbft_pre_prepare_msg_t;

typedef struct {
    uint32_t view;
    uint32_t seq_num;
    pbft_digest_t digest;
    uint32_t sender_id;
} pbft_prepare_msg_t;

typedef struct {
    uint32_t view;
    uint32_t seq_num;
    pbft_digest_t digest;
    uint32_t sender_id;
} pbft_commit_msg_t;

typedef struct {
    uint32_t new_view;
    uint32_t last_checkpoint_seq;
    pbft_digest_t state_digest;
    uint32_t sender_id;
} pbft_view_change_msg_t;

/* Непрозора структура внутрішнього стану репліки */
typedef struct pbft_replica_context pbft_replica_context_t;

/* Ініціалізація контексту репліки */
pbft_result_t pbft_replica_init(pbft_replica_context_t** ctx, uint32_t node_id, uint32_t total_nodes);

/* Обробка трансляції Pre-Prepare від первинного вузла */
pbft_result_t pbft_on_pre_prepare(pbft_replica_context_t* ctx, const pbft_pre_prepare_msg_t* msg, pbft_prepare_msg_t* out_prepare);

/* Обробка підтвердження Prepare від репліки */
pbft_result_t pbft_on_prepare(pbft_replica_context_t* ctx, const pbft_prepare_msg_t* msg, pbft_commit_msg_t* out_commit);

/* Обробка повідомлення Commit від репліки */
pbft_result_t pbft_on_commit(pbft_replica_context_t* ctx, const pbft_commit_msg_t* msg, bool* out_ready_to_execute);

/* Обробка сигналу тайм-ауту та формування повідомлення View-Change */
pbft_result_t pbft_on_view_change_timer(pbft_replica_context_t* ctx, pbft_view_change_msg_t* out_vc);

/* Фіксація завершення виконання транзакції та оновлення стану */
pbft_result_t pbft_mark_executed(pbft_replica_context_t* ctx, uint32_t seq_num);
```
```cpp
#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <optional>
#include <expected>
#include <memory>

namespace pbft::api {

constexpr size_t DigestLength = 32;
using Digest = std::array<uint8_t, DigestLength>;

enum class Error : int32_t {
    InvalidSignature     = -1,
    InvalidDigest        = -2,
    ViewMismatch         = -3,
    NotPrimary           = -4,
    Equivocation         = -5,
    DuplicateMessage     = -6,
    WatermarkOutOfBounds = -7,
    InsufficientQuorum   = -8,
    CheckpointInvalid    = -9
};

struct PrePrepareMessage {
    uint32_t view{0};
    uint32_t seq_num{0};
    Digest digest{};
    std::span<const uint8_t> payload{};
    uint32_t sender_id{0};
};

struct PrepareMessage {
    uint32_t view{0};
    uint32_t seq_num{0};
    Digest digest{};
    uint32_t sender_id{0};
};

struct CommitMessage {
    uint32_t view{0};
    uint32_t seq_num{0};
    Digest digest{};
    uint32_t sender_id{0};
};

struct ViewChangeMessage {
    uint32_t new_view{0};
    uint32_t last_checkpoint_seq{0};
    Digest state_digest{};
    uint32_t sender_id{0};
};

class IReplicaEngine {
public:
    virtual ~IReplicaEngine() = default;

    virtual std::expected<PrepareMessage, Error>
    on_pre_prepare(const PrePrepareMessage& msg) = 0;

    virtual std::expected<CommitMessage, Error>
    on_prepare(const PrepareMessage& msg) = 0;

    virtual std::expected<bool, Error>
    on_commit(const CommitMessage& msg) = 0;

    virtual std::expected<ViewChangeMessage, Error>
    on_view_change_timer() = 0;

    virtual std::expected<void, Error>
    mark_executed(uint32_t seq_num) = 0;
};

std::unique_ptr<IReplicaEngine> create_replica_engine(uint32_t node_id, uint32_t total_nodes);

} // namespace pbft::api
```
:::

## Матриця станів та інваріанти переходів

Кожен слот транзакцій у журналі репліки проходить строгу послідовність станів:

```
[EMPTY] ──(Pre-Prepare)──► [PRE-PREPARED] ──(2f Prepares)──► [PREPARED] ──(2f+1 Commits)──► [COMMITTED-LOCAL] ──► [EXECUTED]
```

| Початковий стан | Подія (Вхідний пакет) | Необхідна умова (Precondition) | Результуючий стан | Вихідна дія репліки |
|---|---|---|---|---|
| `EMPTY` | `Pre-Prepare(v, n, d)` | `v == current_view`, `sender == primary(v)`, `n ∈ [h, H]` | `PRE-PREPARED` | Розсилка `Prepare(v, n, d, id)` усім реплікам |
| `PRE-PREPARED` | `Prepare(v, n, d, j)` | `hash == d`, накопичено `2f` підтверджень | `PREPARED` | Формування Prepared Certificate, розсилка `Commit(v, n, d, id)` |
| `PREPARED` | `Commit(v, n, d, j)` | `hash == d`, накопичено `2f + 1` підтверджень | `COMMITTED-LOCAL` | Формування Commit Certificate, виклик локального автомата станів |
| `COMMITTED-LOCAL` | Виконання операції | Усі попередні слоти `k < n` мають стан `EXECUTED` | `EXECUTED` | Надсилання результату `<REPLY, v, t, c, id, r>` клієнту |
| Будь-який стан | Спливання таймера | Лідер мовчить або прислав підроблені дані | `VIEW-CHANGE` | Зупинка виду `v`, розсилка `<VIEW-CHANGE, v+1, ...>` |

## Інваріанти переходів між станами

1. **Інваріант валідності Pre-Prepare:** Репліка `i` приймає `<PRE-PREPARE, v, n, d>` тоді й тільки тоді, коли:
   * Підпис первинного вузла валідний;
   * Номер виду `v` збігається з поточним видом репліки `current_view`;
   * Порядковий номер `n` потрапляє у вікно водяних знаків `h ≤ n ≤ H`, де `h` — номер останнього стабільного чекпойнта, а `H = h + 2·L` (`L` — розмір вікна журналу);
   * Репліка не має у своєму журналі іншого повідомлення Pre-Prepare з тим самим `(v, n)` та іншим дайджестом `d' ≠ d`.
2. **Інваріант підготовленого стану (Prepared Invariant):** Предикат `prepared(m, v, n, i)` набуває значення `true` тоді й тільки тоді, коли в журналі репліки присутній валідний запис `Pre-Prepare(v, n, d)` для `d = Hash(m)` та щонайменше `2f` підтверджених повідомлень `Prepare(v, n, d, j)` від різних реплік `j ≠ i`.
3. **Інваріант фіксації (Committed-Local Invariant):** Предикат `committed_local(m, v, n, i)` набуває значення `true` тоді й тільки тоді, коли предикат `prepared(m, v, n, i)` істинний і репліка отримала щонайменше `2f + 1` валідних повідомлень `Commit(v, n, d, j)` від різних вузлів кластера (включно з власним).
4. **Інваріант безпеки виконання (Execution Invariant):** Репліка `i` виконує транзакцію зі слота `n` над автоматом станів тоді й тільки тоді, коли `committed_local(m, v, n, i)` істинний, і всі попередні транзакції зі слотами `k < n` уже успішно виконані (строга послідовна реплікація).

## Класифікація помилок та стратегії відновлення

1. **`PBFT_ERR_EQUIVOCATION`:** Виникає, коли первинний вузол надсилає два різні дайджести для одного номера слота. Репліка негайно реєструє факт змови, відкидає повторний пакет і викликає процедуру `pbft_on_view_change_timer` для заміни скомпрометованого координатора.
2. **`PBFT_ERR_WATERMARK_OUT_OF_BOUNDS`:** Повідомлення містить номер слота `n > H` або `n < h`. Це свідчить або про запізнілий пакет із минулого, або про спробу лідера вийти за межі буфера пам'яті. Пакет відкидається без збереження.
3. **`PBFT_ERR_VIEW_MISMATCH`:** Пакет належить старішому виду `v' < current_view` або майбутньому виду. Застарілі пакети ігноруються, а пакети майбутнього виду буферизуються в окрему чергу очікування завершення зміни виду.
4. **`PBFT_ERR_INVALID_SIGNATURE`:** Відбиток відправника або MAC-мітка не проходять криптографічну перевірку. Повідомлення негайно скидається, а лічильник підозрілої активності відправника збільшується.
5. **`PBFT_ERR_INSUFFICIENT_QUORUM`:** Сигнал внутрішнього стану, який вказує, що кількість підтверджень ще не досягла необхідного порогу (`2f` для Prepare або `2f + 1` для Commit). Репліка продовжує перебувати в поточному стані та чекає на прибуття затриманих пакетів.
