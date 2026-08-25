# 📋 Специфікація X/Open XA: інтерфейс менеджера транзакцій та ресурсів

Специфікація X/Open XA (англ. *eXtended Architecture*) — це відкритий промисловий стандарт, розроблений консорціумом The Open Group у 1991 році в межах архітектури розподіленої обробки транзакцій (англ. *Distributed Transaction Processing*, DTP).

Стандарт визначає точний програмний контракт між двома ключовими компонентами розподіленої системи:
1. **Менеджер транзакцій (Transaction Manager, TM):** зовнішній координатор, який керує глобальним життєвим циклом транзакції, призначає глобальні ідентифікатори та координує фази двофазного коміту (2PC).
2. **Менеджер ресурсів (Resource Manager, RM):** система керування даними (реляційна СУБД, документоорієнтоване сховище, брокер повідомлень або транзакційна черга), яка надає доступ до спільних ресурсів і володіє власним локальним журналом відновлення (WAL).

## Структури даних ідентифікації

Головною структурою для відстеження розподіленої транзакції є `XID` (англ. *Transaction Identifier*). Вона містить глобальний ідентифікатор транзакції та кваліфікатор конкретної гілки, що дозволяє одному бізнес-процесу охоплювати кілька незалежних ресурсів.

:::tabs
```c
#define XIDDATASIZE 128 /* максимальний розмір буфера даних */
#define MAXGTRIDSIZE 64 /* максимальний розмір глобального ID */
#define MAXBQUALSIZE 64 /* максимальний розмір кваліфікатора гілки */

struct xid_t {
    long formatID;          /* формат ідентифікатора (-1 = null, 0 = OSI CCR, >0 = вендор) */
    long gtrid_length;      /* довжина глобального ідентифікатора транзакції (1..64) */
    long bqual_length;      /* довжина кваліфікатора гілки транзакції (1..64) */
    char data[XIDDATASIZE]; /* масив байтів: gtrid + bqual */
};
typedef struct xid_t XID;
```
```cpp
#include <cstdint>
#include <string_view>
#include <span>
#include <array>

struct TransactionId {
    static constexpr size_t kMaxDataSize = 128;
    static constexpr size_t kMaxGtridSize = 64;
    static constexpr size_t kMaxBqualSize = 64;

    int64_t format_id{-1};
    int64_t gtrid_length{0};
    int64_t bqual_length{0};
    std::array<std::byte, kMaxDataSize> data{};

    [[nodiscard]] std::span<const std::byte> global_transaction_id() const noexcept {
        return std::span<const std::byte>(data.data(), static_cast<size_t>(gtrid_length));
    }

    [[nodiscard]] std::span<const std::byte> branch_qualifier() const noexcept {
        return std::span<const std::byte>(data.data() + gtrid_length, static_cast<size_t>(bqual_length));
    }
};
```
:::

## Таблиця функцій ресурсного менеджера (`xa_switch_t`)

Кожна бібліотека доступу до бази даних (клієнт Oracle, PostgreSQL, IBM DB2, MySQL) експортує глобальну структуру `xa_switch_t`. Менеджер транзакцій під час запуску отримує вказівник на цю структуру й викликає її методи для керування транзакціями:

:::tabs
```c
struct xa_switch_t {
    char name[32];          /* ім'я RM (наприклад, "PostgreSQL_XA", "Oracle_XA") */
    long flags;             /* прапорці можливостей (TMNOFLAGS, TMREGISTER тощо) */
    long version;           /* версія інтерфейсу (константа 0) */
    int (*xa_open_entry)(char *xa_info, int rmid, long flags);
    int (*xa_close_entry)(char *xa_info, int rmid, long flags);
    int (*xa_start_entry)(XID *xid, int rmid, long flags);
    int (*xa_end_entry)(XID *xid, int rmid, long flags);
    int (*xa_rollback_entry)(XID *xid, int rmid, long flags);
    int (*xa_prepare_entry)(XID *xid, int rmid, long flags);
    int (*xa_commit_entry)(XID *xid, int rmid, long flags);
    int (*xa_recover_entry)(XID *xids, long count, int rmid, long flags);
    int (*xa_forget_entry)(XID *xid, int rmid, long flags);
    int (*xa_complete_entry)(int *handle, int *retval, int rmid, long flags);
};
```
```cpp
#include <string_view>
#include <span>
#include <expected>

class IResourceManager {
public:
    virtual ~IResourceManager() = default;

    virtual std::expected<void, int> open(std::string_view info, int rm_id, int64_t flags) = 0;
    virtual std::expected<void, int> close(std::string_view info, int rm_id, int64_t flags) = 0;
    virtual std::expected<void, int> start(const TransactionId& xid, int rm_id, int64_t flags) = 0;
    virtual std::expected<void, int> end(const TransactionId& xid, int rm_id, int64_t flags) = 0;
    virtual std::expected<int, int> prepare(const TransactionId& xid, int rm_id, int64_t flags) = 0;
    virtual std::expected<void, int> commit(const TransactionId& xid, int rm_id, int64_t flags) = 0;
    virtual std::expected<void, int> rollback(const TransactionId& xid, int rm_id, int64_t flags) = 0;
    virtual std::expected<size_t, int> recover(std::span<TransactionId> xids, int rm_id, int64_t flags) = 0;
    virtual std::expected<void, int> forget(const TransactionId& xid, int rm_id, int64_t flags) = 0;
};
```
:::

## Скінченний автомат станів транзакційної гілки в XA

У межах кожного ресурсного менеджера транзакційна гілка проходить через чітко визначений життєвий цикл станів:

1. **`NON-EXISTENT` (Не існує):** початковий стан до першого виклику `xa_start()`.
2. **`ACTIVE` (Активна):** стан після успішного виклику `xa_start()`. Робочий потік застосунку виконує запити до бази даних (INSERT, UPDATE, DELETE). Усі зміни асоціюються з відповідним `XID`.
3. **`IDLE` (Очікування / Завершена робота):** стан після виклику `xa_end()`. Потік відв'язується від гілки. Нові SQL-запити більше не приймаються, але транзакція готова до голосування.
4. **`PREPARED` (Підготовлена / In-Doubt):** стан після виклику `xa_prepare()`. Ресурсний менеджер скинув усі undo/redo журнали на диск через `fsync()` і заблокував ресурси. Учасник втрачає автономію.
5. **`COMMITTED` / `ABORTED` (Термінальні стани):** стан після виклику `xa_commit()` або `xa_rollback()`. Усі замки знято, ресурси звільнено.

## Детальний опис функцій інтерфейсу XA

| Функція | Призначення | Ключові прапорці | Коди повернення |
| :--- | :--- | :--- | :--- |
| `xa_open()` | Встановлює зв'язок між TM та RM (відкриває пули з'єднань, автентифікує клієнта). | `TMNOFLAGS`, `TMASYNC` | `XA_OK`, `XAER_RMERR`, `XAER_INVAL` |
| `xa_close()` | Коректно закриває сесію взаємодії з ресурсним менеджером. | `TMNOFLAGS`, `TMASYNC` | `XA_OK`, `XAER_RMERR`, `XAER_PROTO` |
| `xa_start()` | Асоціює поточний робочий потік із транзакційною гілкою `XID`. Усі наступні SQL-запити виконуються в межах цієї гілки. | `TMNOFLAGS` (нова гілка), `TMJOIN` (приєднання до існуючої), `TMRESUME` (відновлення призупиненої) | `XA_OK`, `XAER_DUPID`, `XAER_OUTSIDE`, `XAER_PROTO` |
| `xa_end()` | Завершує асоціацію потоку з транзакційною гілкою. Після цього запити не можуть додаватися в транзакцію. | `TMSUCCESS` (успішне завершення гілки), `TMFAIL` (помилка, транзакція має бути відкочена), `TMSUSPEND` (тимчасове призупинення) | `XA_OK`, `XAER_NOTA`, `XAER_PROTO`, `XAER_RMFAIL` |
| `xa_prepare()` | **Перша фаза 2PC:** перевіряє цілісність, захоплює транзакційні замки, скидає стан у WAL на диск (`fsync`). | `TMNOFLAGS` | `XA_OK` (готовий до коміту), `XA_RDONLY` (транзакція тільки читала дані), `XAER_NOTA`, `XAER_RMERR` |
| `xa_commit()` | **Друга фаза 2PC:** остаточно фіксує підготовлену гілку на диску й знімає блокування ресурсів. | `TMNOFLAGS` (двофазний коміт), `TMONEPHASE` (оптимізація однофазного коміту, якщо RM єдиний) | `XA_OK`, `XA_HEURCOM`, `XA_HEURRB`, `XA_HEURMIX`, `XAER_NOTA` |
| `xa_rollback()` | **Друга фаза 2PC (відкат):** скасовує всі зміни транзакції за журналом undo-записів і знімає замки. | `TMNOFLAGS` | `XA_OK`, `XA_HEURCOM`, `XA_HEURRB`, `XA_HEURMIX`, `XAER_NOTA` |
| `xa_recover()` | Запитує у RM список транзакцій, які перебувають у підвішеному стані `In-Doubt` після аварійного перезапуску. | `TMSTARTRSCAN` (почати сканування), `TMENDRSCAN` (завершити сканування), `TMNOFLAGS` | Кількість знайдених транзакцій (>= 0), `XAER_RMERR` |
| `xa_forget()` | Дозволяє ресурсному менеджеру видалити з пам'яті та журналу інформацію про евристично завершену транзакцію. | `TMNOFLAGS` | `XA_OK`, `XAER_NOTA`, `XAER_RMERR` |

## Коди повернення та обробка евристичних помилок

### Нормальні статуси
* **`XA_OK` (`0`):** операція завершилася успішно.
* **`XA_RDONLY` (`3`):** важлива оптимізація *Read-Only*. Ресурсний менеджер виявив, що транзакція виконувала лише операції читання (SELECT) і не змінювала стан таблиць. RM негайно звільняє всі спільні замки читання й повідомляє координатору, що викликати `xa_commit()` для нього не потрібно.

### Евристичні винятки (Heuristic Hazard)
Евристичні стани виникають, коли вузол-учасник через тривалу втрату зв'язку з координатором або через пряму команду системного адміністратора самовільно виходить зі стану `PREPARED`:
* **`XA_HEURCOM` (`7`):** учасник самовільно зафіксував транзакцію (Heuristic Commit).
* **`XA_HEURRB` (`6`):** учасник самовільно відкотив транзакцію (Heuristic Rollback).
* **`XA_HEURMIX` (`5`):** найважча аварія розриву атомарності (Heuristic Mixed). Частина ресурсів транзакції виявилася зафіксованою, а інша частина — відкоченою. Вимагає ручного втручання та аудиту даних.
* **`XA_HEURHAZ` (`8`):** стан транзакції невизначений (Heuristic Hazard).

### Системні коди помилок (`XAER_*`)
* **`XAER_ASYNC` (`-2`):** асинхронна операція ще триває.
* **`XAER_RMERR` (`-3`):** критичний збій ресурсного менеджера (наприклад, пошкодження дискового накопичувача).
* **`XAER_NOTA` (`-4`):** вказаний `XID` не існує або вже завершений.
* **`XAER_INVAL` (`-5`):** передано неприпустимі параметри або некоректні прапорці.
* **`XAER_PROTO` (`-6`):** помилка послідовності протоколу (наприклад, виклик `xa_commit()` для транзакції, яка не пройшла `xa_prepare()`).
* **`XAER_RMFAIL` (`-7`):** менеджер ресурсів став недоступним через обрив зв'язку або падіння процесу.

## Процедура відновлення завислих транзакцій (`xa_recover`)

Коли Менеджер транзакцій (координатор) перезапускається після аварійного відключення або відновлює зв'язок з базою даних, він запускає процедуру очищення підвислих транзакцій:

1. **Сканування:** TM викликає `xa_recover()` із прапорцем `TMSTARTRSCAN`. Ресурсний менеджер повертає масив структур `XID`, які наразі перебувають у стані `PREPARED` (In-Doubt).
2. **Звірка з журналом TM:** для кожного отриманого `XID` координатор перевіряє свій власний журнал:
   - якщо в журналі координатора для цього `XID` знайдено запис `COMMIT`, координатор негайно викликає `xa_commit(xid, TMNOFLAGS)`;
   - якщо в журналі координатора знайдено запис `ABORT` (або запис про транзакцію взагалі відсутній — правило Presumed Abort), координатор викликає `xa_rollback(xid, TMNOFLAGS)`.
3. **Завершення сканування:** TM викликає `xa_recover()` із прапорцем `TMENDRSCAN` для закриття курсора відновлення.
4. **Очищення евристик:** якщо ресурсний менеджер повідомив про евристичне завершення транзакції (`XA_HEURCOM` або `XA_HEURRB`), координатор записує факт аварії в системний журнал аудиту й викликає `xa_forget(xid)`, щоб дозволити базі даних остаточно стерти старий запис.

## SQL-еквіваленти в промислових СУБД

Сучасні реляційні бази даних транслюють низькорівневі виклики інтерфейсу XA у відповідні SQL-команди для ручного тестування та інтеграції:

### PostgreSQL

```sql
-- 1. Відкриття транзакції та виконання операцій
BEGIN;
UPDATE accounts SET balance = balance - 500 WHERE id = 101;

-- 2. Фаза 1: підготовка та скидання стану на диск (аналог xa_prepare)
PREPARE TRANSACTION 'global_tx_branch_pg_01';

-- 3. Перегляд списку підвислих (In-Doubt) транзакцій (аналог xa_recover)
SELECT gid, prepared, owner, database FROM pg_prepared_xacts;

-- 4. Фаза 2: остаточна фіксація або відкат (аналог xa_commit / xa_rollback)
COMMIT PREPARED 'global_tx_branch_pg_01';
-- або у разі відкату:
ROLLBACK PREPARED 'global_tx_branch_pg_01';
```

### MySQL (InnoDB)

```sql
-- 1. Початок гілки транзакції (xa_start)
XA START 'global_tx_001', 'mysql_branch_01';
UPDATE warehouse SET items_count = items_count - 1 WHERE item_id = 42;
XA END 'global_tx_001', 'mysql_branch_01';

-- 2. Фаза 1: підготовка (xa_prepare)
XA PREPARE 'global_tx_001', 'mysql_branch_01';

-- 3. Моніторинг нефіксованих транзакцій (xa_recover)
XA RECOVER;

-- 4. Фаза 2: коміт (xa_commit)
XA COMMIT 'global_tx_001', 'mysql_branch_01';
```

## Повний життєвий цикл розподіленої транзакції

Типовий сценарій виконання міжбанківського переказу між базою даних PostgreSQL (рахунок відправника) та базою даних MySQL (рахунок отримувача) під керуванням Transaction Manager складається з таких кроків:

1. **Ініціалізація:** TM викликає `xa_open()` для обох ресурсних менеджерів (RM1 та RM2).
2. **Генерація ID:** TM створює глобальний ідентифікатор `GTRID` та формує дві гілки: `XID1` (для RM1) та `XID2` (для RM2).
3. **Виконання гілки 1:** TM викликає `xa_start(XID1, TMNOFLAGS)` на RM1; застосунок виконує `UPDATE accounts SET balance = balance - 100`; TM викликає `xa_end(XID1, TMSUCCESS)`.
4. **Виконання гілки 2:** TM викликає `xa_start(XID2, TMNOFLAGS)` на RM2; застосунок виконує `UPDATE accounts SET balance = balance + 100`; TM викликає `xa_end(XID2, TMSUCCESS)`.
5. **Фаза 1 (Голосування):**
   - TM викликає `xa_prepare(XID1)`. RM1 скидає WAL на диск і повертає `XA_OK`.
   - TM викликає `xa_prepare(XID2)`. RM2 скидає WAL на диск і повертає `XA_OK`.
6. **Фаза 2 (Фіксація):**
   - Оскільки обидва RM повернули `XA_OK`, TM фіксує рішення `COMMIT` у власному журналі.
   - TM викликає `xa_commit(XID1, TMNOFLAGS)` на RM1. RM1 фіксує дані, знімає замки й повертає `XA_OK`.
   - TM викликає `xa_commit(XID2, TMNOFLAGS)` на RM2. RM2 фіксує дані, знімає замки й повертає `XA_OK`.
7. **Завершення:** TM повідомляє клієнту про успішне виконання розподіленої транзакції.
