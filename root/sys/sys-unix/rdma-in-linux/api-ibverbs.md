# 📋 Інтерфейс libibverbs та librdmacm

Програмний стек RDMA у просторі користувача Linux спирається на дві основні бібліотеки з пакета `rdma-core`: низькорівневий інтерфейс **`libibverbs`** (реалізація специфікації InfiniBand Verbs API) та високорівневу бібліотеку управління з'єднаннями **`librdmacm`** (RDMA Communication Manager).

Цей довідник описує об'єкти, виклики API, прапорці доступу, машини станів та послідовності викликів для побудови високопродуктивних мережевих застосунків.

---

## 1. Фундаментальні об'єкти та структури даних `libibverbs`

Всі об'єкти у `libibverbs` мають чітко визначену ієрархію володіння та життєвого циклу. Створення кожного об'єкта вимагає вказівника на батьківський контекст, а знищення має відбуватися у зворотному порядку, щоб уникнути витоків ресурсів або невизначеної поведінки апаратури. Заголовочний файл — `<infiniband/verbs.h>`.

### 1.1 `struct ibv_context`
Контекст відкритого пристрою RDMA (HCA / RNIC). Повертається функцією `ibv_open_device()`. Об'єкт зберігає вказівник на таблицю методів апаратного провайдера (наприклад `libmlx5`), дескриптор пристрою ядра та загальні характеристики адаптера (кількість портів, максимальний розмір QP, підтримка атомних операцій).

### 1.2 `struct ibv_pd` (Protection Domain)
Домен безпеки (Protection Domain) слугує ізоляційним контейнером. Він пов'язує між собою об'єкти `ibv_mr` (Memory Region), `ibv_qp` (Queue Pair), `ibv_ah` (Address Handle) та `ibv_srq` (Shared Receive Queue). Апаратна частина HCA відхиляє будь-яку спробу виконати операцію над буфером MR через QP, якщо вони були створені у різних Protection Domain.

:::tabs
```c
// Створення та звільнення PD у C
struct ibv_device **dev_list = ibv_get_device_list(NULL);
struct ibv_context *ctx = ibv_open_device(dev_list[0]);
ibv_free_device_list(dev_list);

struct ibv_pd *pd = ibv_alloc_pd(ctx);
if (!pd) {
    perror("ibv_alloc_pd failed");
    return -1;
}

// ... використання ...
ibv_dealloc_pd(pd);
ibv_close_device(ctx);
```
```cpp
// Ідіоматична RAII-обгортка для PD у C++20
#include <infiniband/verbs.h>
#include <memory>
#include <stdexcept>

struct IbvContextDeleter {
    void operator()(ibv_context* ctx) const noexcept {
        if (ctx) ibv_close_device(ctx);
    }
};

struct IbvPdDeleter {
    void operator()(ibv_pd* pd) const noexcept {
        if (pd) ibv_dealloc_pd(pd);
    }
};

using UniqueContext = std::unique_ptr<ibv_context, IbvContextDeleter>;
using UniquePd      = std::unique_ptr<ibv_pd, IbvPdDeleter>;

UniquePd make_protection_domain(ibv_context* ctx) {
    ibv_pd* pd = ibv_alloc_pd(ctx);
    if (!pd) {
        throw std::runtime_error("Не вдалося виділити Protection Domain");
    }
    return UniquePd(pd);
}
```
:::

### 1.3 `struct ibv_mr` (Memory Region) та права доступу
Описує зареєстровану та закріплену в оперативній пам’яті ділянку віртуальної адреси процесу. Під час реєстрації ядро закликає `pin_user_pages()`, забороняючи операційній системі вивантажувати сторінки у swap, та завантажує віртуально-фізичні адреси в апаратну TPT-таблицю адаптера.

Основні поля структури:
- `void *addr`: Початкова віртуальна адреса локального буфера.
- `size_t length`: Розмір зареєстрованого регіону в байтах.
- `uint32_t lkey`: Локальний ключ доступу (Local Key), який передається у локальних `ibv_sge` для підтвердження прав локального DMA.
- `uint32_t rkey`: Віддалений ключ доступу (Remote Key), який передається по мережі віддаленому вузлу для підтвердження прав прямого одностороннього доступу RDMA Read/Write.

Прапорці доступу при реєстрації `ibv_reg_mr()`:
- `IBV_ACCESS_LOCAL_WRITE`: Дозволяє апаратному адаптеру записувати дані у цей буфер при локальному прийомі пакета або виконанні RDMA Read.
- `IBV_ACCESS_REMOTE_WRITE`: Дозволяє віддаленому вузлу виконувати запис `IBV_WR_RDMA_WRITE` у цей буфер. Вимагає також наявності `IBV_ACCESS_LOCAL_WRITE`.
- `IBV_ACCESS_REMOTE_READ`: Дозволяє віддаленому вузлу виконувати читання `IBV_WR_RDMA_READ` з цього буфера.
- `IBV_ACCESS_REMOTE_ATOMIC`: Дозволяє віддаленому вузлу виконувати атомарні операції (Compare-and-Swap, Fetch-and-Add).
- `IBV_ACCESS_MW_BIND`: Дозволяє зв'язувати з цим регіоном динамічні вікна пам'яті (Memory Windows).

:::tabs
```c
// Реєстрація пам'яті у C
char *buffer = (char *)malloc(4096);
struct ibv_mr *mr = ibv_reg_mr(pd, buffer, 4096,
                               IBV_ACCESS_LOCAL_WRITE |
                               IBV_ACCESS_REMOTE_WRITE |
                               IBV_ACCESS_REMOTE_READ);
if (!mr) {
    perror("ibv_reg_mr failed");
}
// ...
ibv_dereg_mr(mr);
free(buffer);
```
```cpp
// Ідіоматична RAII-обгортка для буфера та MR у C++20
#include <infiniband/verbs.h>
#include <memory>
#include <span>
#include <vector>
#include <stdexcept>

class RegisteredBuffer {
public:
    RegisteredBuffer(ibv_pd* pd, size_t size, int access_flags)
        : data_(size) {
        mr_ = ibv_reg_mr(pd, data_.data(), data_.size(), access_flags);
        if (!mr_) throw std::runtime_error("Помилка реєстрації пам'яті ibv_reg_mr");
    }

    ~RegisteredBuffer() noexcept {
        if (mr_) ibv_dereg_mr(mr_);
    }

    RegisteredBuffer(const RegisteredBuffer&) = delete;
    RegisteredBuffer& operator=(const RegisteredBuffer&) = delete;

    RegisteredBuffer(RegisteredBuffer&& o) noexcept
        : data_(std::move(o.data_)), mr_(o.mr_) {
        o.mr_ = nullptr;
    }

    [[nodiscard]] uint32_t lkey() const noexcept { return mr_->lkey; }
    [[nodiscard]] uint32_t rkey() const noexcept { return mr_->rkey; }
    [[nodiscard]] uint64_t remote_ptr() const noexcept {
        return reinterpret_cast<uint64_t>(data_.data());
    }
    [[nodiscard]] std::span<std::byte> bytes() noexcept {
        return std::span(reinterpret_cast<std::byte*>(data_.data()), data_.size());
    }

private:
    std::vector<char> data_;
    ibv_mr* mr_{nullptr};
};
```
:::

### 1.4 `struct ibv_mw` (Memory Window)
Вікно пам'яті (Memory Window) дозволяє динамічно надавати або відкликати права віддаленого доступу до окремих підрегіонів наявного `ibv_mr` без виконання дорогого виклику `ibv_reg_mr()`.
- **Type 1 MW:** Зв'язується з MR через `ibv_bind_mw()`.
- **Type 2 MW:** Зв'язується з конкретним QP через спеціальний Work Request `IBV_WR_BIND_MW`.

### 1.5 `struct ibv_srq` (Shared Receive Queue)
Спільна черга прийому. Дозволяє багатьом об'єктам QP типу RC використовувати єдиний спільний пул буферів прийому, що економить оперативну пам'ять на серверах із тисячами активних з'єднань.

---

## 2. Апаратні черги: `ibv_cq` та `ibv_qp`

### 2.1 Черга завершення `struct ibv_cq` (Completion Queue)
Черга `ibv_cq` накопичує елементи завершення (Work Completions, `struct ibv_wc`), які генеруються апаратним адаптером HCA після того, як операція відправки або прийому була повністю виконана.

- `ibv_create_cq(ctx, cqe_depth, cq_context, comp_channel, comp_vector)`: Створює чергу місткістю `cqe_depth`.
- `ibv_poll_cq(cq, num_entries, wc_array)`: Неблокуюча функція витягування елементів із черги CQ. Повертає кількість реально витягнутих елементів (від `0` до `num_entries`) або від'ємне число при системній помилці.

### 2.2 Структура елемента завершення `struct ibv_wc` (Work Completion)
Містить детальний звіт апаратури про стан виконаного запиту:
- `uint64_t wr_id`: Значення ідентифікатора запиту, яке програма задала у полі `wr_id` під час публікації.
- `enum ibv_wc_status status`: Апаратний код стану (див. детальний довідник у Розділі 6). Значення `IBV_WC_SUCCESS` (0) означає успішну доставку.
- `enum ibv_wc_opcode opcode`: Тип завершеної операції (`IBV_WC_SEND`, `IBV_WC_RECV`, `IBV_WC_RDMA_WRITE`, `IBV_WC_RDMA_READ`, `IBV_WC_COMP_SWAP`).
- `uint32_t byte_len`: Кількість переданих або отриманих байтів.
- `uint32_t qp_num`: Номер локального QP, який згенерував цей елемент.
- `uint32_t src_qp`: Номер QP віддаленого вузла (для непідключених каналів UD).

---

## 3. Запити на роботу: Work Requests (WR) та Scatter/Gather Elements (SGE)

Операції передачі та прийому відправляються до апаратного адаптера шляхом формування зв'язаних списків запитів (Work Requests).

### 3.1 `struct ibv_sge` (Scatter/Gather Element)
Вказує апаратній карті на локальний буфер для зчитування (Scatter) або запису (Gather):
- `uint64_t addr`: Віртуальна адреса локального буфера (повинна бути приведена до `uint64_t`).
- `uint32_t length`: Довжина даних у байтах.
- `uint32_t lkey`: Локальний ключ доступу (Local Key) відповідного зареєстрованого `ibv_mr`.

### 3.2 `struct ibv_send_wr` (Send Work Request)
Запит на відправку, який публікується у Send Queue за допомогою виклику `ibv_post_send()`.

:::tabs
```c
// Формування та публікація RDMA Write у C
struct ibv_sge sge = {
    .addr = (uint64_t)local_buffer,
    .length = 1024,
    .lkey = mr->lkey
};

struct ibv_send_wr wr = {
    .wr_id = 1001,
    .next = NULL,
    .sg_list = &sge,
    .num_sge = 1,
    .opcode = IBV_WR_RDMA_WRITE,
    .send_flags = IBV_SEND_SIGNALED | IBV_SEND_INLINE,
    .wr.rdma = {
        .remote_addr = remote_target_addr,
        .rkey = remote_rkey
    }
};

struct ibv_send_wr *bad_wr = NULL;
int ret = ibv_post_send(qp, &wr, &bad_wr);
if (ret != 0) {
    fprintf(stderr, "Помилка ibv_post_send: %d\n", ret);
}
```
```cpp
// Опублікування RDMA Write у C++20 з безпечною перевіркою типом
#include <infiniband/verbs.h>
#include <expected>
#include <cstdint>

std::expected<void, int> post_rdma_write_cpp(ibv_qp* qp, uint64_t wr_id,
                                             uint64_t local_addr, uint32_t len, uint32_t lkey,
                                             uint64_t remote_addr, uint32_t rkey) {
    ibv_sge sge{
        .addr = local_addr,
        .length = len,
        .lkey = lkey
    };

    ibv_send_wr wr{};
    wr.wr_id = wr_id;
    wr.next = nullptr;
    wr.sg_list = &sge;
    wr.num_sge = 1;
    wr.opcode = IBV_WR_RDMA_WRITE;
    wr.send_flags = IBV_SEND_SIGNALED;
    wr.wr.rdma.remote_addr = remote_addr;
    wr.wr.rdma.rkey = rkey;

    ibv_send_wr* bad_wr{nullptr};
    int err = ibv_post_send(qp, &wr, &bad_wr);
    if (err != 0) {
        return std::unexpected(err);
    }
    return {};
}
```
:::

Прапорці `send_flags`:
- `IBV_SEND_SIGNALED`: Вимагає від HCA обов'язково згенерувати елемент `ibv_wc` у черзі Completion Queue після завершення цього запиту. Якщо прапорець не встановлено, запит виконується «мовчки» (Unsignaled), що прискорює роботу, але вимагає періодичної відправки Signaled-запитів для очищення внутрішнього кільцевого буфера HCA.
- `IBV_SEND_INLINE`: Вказує драйверу копіювати байти даних безпосередньо у саму структуру WQE в регістр HCA (через MMIO), минаючи механізм DMA-читання з RAM для малих пакетів.
- `IBV_SEND_FENCE`: Гарантує, що цей запит розпочнеться лише після повного завершення усіх попередніх операцій `RDMA Read`.

---

## 4. Машина станів Queue Pair (QP State Machine)

Переведення Queue Pair між станами здійснюється функцією `ibv_modify_qp()`. Жоден QP не може відправляти чи приймати дані одразу після створення.

```text
┌───────────┐    ibv_modify_qp()     ┌───────────┐    ibv_modify_qp()     ┌───────────┐
│           │ ─────────────────────> │           │ ─────────────────────> │           │
│   RESET   │                        │   INIT    │                        │    RTR    │
│           │                        │           │                        │ (Ready to │
└───────────┘                        └───────────┘                        │  Receive) │
      ▲                                                                   └─────┬─────┘
      │                                                                         │
      │                             ┌───────────┐                               │ ibv_modify_qp()
      │     Помилка / Reset         │    RTS    │                               │
      └──────────────────────────── │ (Ready to │ <─────────────────────────────┘
                                    │   Send)   │
                                    └───────────┘
```

Послідовність станів для з'єднання типу Reliable Connection (RC):
1. **RESET:** Початковий стан після виклику `ibv_create_qp()`. Черги порожні, апаратура не обробляє запити.
2. **INIT:** Налаштовуються базові права доступу (`qp_access_flags`), номер порту HCA та P_Key (Partition Key). У цьому стані у чергу RQ вже можна публікувати `ibv_post_recv()`.
3. **RTR (Ready to Receive):** Передаються параметри віддаленого вузла: віддалений номер QP (`dest_qp_num`), віддалений LID/GID, вихідний ПАКЕНТНИЙ PSN (Packet Sequence Number) та розмір вікна прийому. Апаратура здатна приймати вхідні пакети по мережі.
4. **RTS (Ready to Send):** Задаються параметри таймаутів, кількості повторних спроб (`retry_cnt`, `rnr_retry`) та початковий локальний PSN. QP готовий виконувати операції з Send Queue (`ibv_post_send()`).
5. **ERROR:** Стан помилки, у який QP переходить при перевищенні таймаутів або апаратних збоях. Всі нереалізовані WQE скидаються у CQ зі статусом `IBV_WC_WR_FLUSH_ERR`.

---

## 5. Стек управління з'єднаннями `librdmacm`

Бібліотека `librdmacm` (заголовочний файл `<rdma/rdma_cma.h>`) автоматизує ручний обмін номерами QP, адресами GID та ключами PSN, надаючи API, схоже на стандартні POSIX-сокети.

### 5.1 Основні структури та функції `librdmacm`
- `struct rdma_cm_id`: Ідентифікатор з'єднання (аналог сокета). Зберігає вказівники на `ibv_context`, `ibv_qp` та канальний об'єкт `rdma_event_channel`.
- `rdma_create_event_channel()`: Створює канал для отримання асинхронних подій встановлення з'єднання (Connection Events).
- `rdma_create_id(channel, &id, context, ps)`: Створює об'єкт `rdma_cm_id`. Параметр `ps` вказує тип порту (наприклад `RDMA_PS_TCP` для надійних потоків).
- `rdma_bind_addr(id, addr)`: Прив'язує локальний ID до IP-адреси та порту.
- `rdma_listen(id, backlog)`: Переводить ID у стан прослуховування вхідних запитів.
- `rdma_resolve_addr(id, src_addr, dst_addr, timeout_ms)`: Визначає локальний RDMA-пристрій та маршрут до віддаленої IP-адреси.
- `rdma_resolve_route(id, timeout_ms)`: Визначає параметри L3-маршрутизації (LID/GID/VLAN) до цільового вузла.
- `rdma_connect(id, conn_param)`: Відправляє пакет запиту на з'єднання (Connection Request).
- `rdma_accept(id, conn_param)`: Приймає вхідне з'єднання на стороні сервера.
- `rdma_disconnect(id)`: Розірвання з'єднання та переведення QP у стан ERROR.
- `rdma_destroy_id(id)`: Звільнення ресурсів з'єднання.

---

## 6. Таблиця статусів виконання `enum ibv_wc_status`

| Статус | Опис та першопричина |
| :--- | :--- |
| `IBV_WC_SUCCESS` | Операція успішно виконана апаратурою HCA. |
| `IBV_WC_LOC_LEN_ERR` | Розмір локального буфера SGE менший за розмір вхідних даних. |
| `IBV_WC_LOC_PROT_ERR` | Помилка локальних прав доступу: L_Key недійсний або не збігається PD. |
| `IBV_WC_REM_ACCESS_ERR` | Віддалений вузол відхилив доступ: R_Key недійсний або відсутні прапорці `REMOTE_WRITE`/`READ`. |
| `IBV_WC_REM_RESP_ERR` | Віддалений HCA повернув невалідний транспортний пакет або не відповів (ACK timeout). |
| `IBV_WC_RETRY_EXC_ERR` | Перевищено ліміт повторних спроб (Retry Count Exceeded) через втрату пакетів або обрив фізичного лінка. |
| `IBV_WC_WR_FLUSH_ERR` | Запит скинуто з черги, оскільки QP перейшов у стан Помилки (ERROR state). |
