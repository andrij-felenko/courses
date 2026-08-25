# ⚙️ Практична реалізація RDMA Ping-Pong та Write/Read на C та C++

Ця вставка містить повноцінний навчально-виробничий проєкт передачі даних між сервером та клієнтом за допомогою односторонньої операції **RDMA Write** з використанням бібліотек `librdmacm` та `libibverbs`. 

Перед запуском безпосереднього одностороннього запису в пам'ять (1-sided RDMA Write) програма виконує початкову фазу узгодження: вузли встановлюють з'єднання через `librdmacm`, передають один одному параметри зареєстрованих буферів (`R_Key` та віддалену віртуальну адресу `remote_addr`) за допомогою двосторонньої операції `Send/Receive`, після чого клієнт здійснює прямий запис у пам'ять сервера без залучення його центрального процесора.

---

## 1. Архітектура та етапи виконання проєкту

Проєкт складається з п'яти послідовних фаз, які відображають стандартний паттерн розробки високопродуктивних RDMA-застосунків у Linux:

1. **Ініціалізація менеджерів з'єднань (Connection Setup):** Створення `rdma_event_channel` та ідентифікаторів `rdma_cm_id`. Сервер викликає `rdma_bind_addr()` та `rdma_listen()`, а клієнт виконує `rdma_resolve_addr()` та `rdma_resolve_route()`.
2. **Алокація та реєстрація пам'яті (Memory Registration):** Сервер та клієнт виділяють вирівняні буфери в RAM та викликають `ibv_reg_mr()`. Ядро закликає `pin_user_pages()`, фіксуючи сторінки в пам'яті та створюючи локальний `L_Key` і віддалений `R_Key`.
3. **Створення апаратних черг (QP & CQ Creation):** Створення черги завершень `ibv_create_cq()` та черги пар `rdma_create_qp()` типу Reliable Connection (`IBV_QPT_RC`).
4. **Початковий обмін метаданими (Out-Of-Band Exchange):** Сервер надсилає структуру `RdmaBufferExchange` клієнту через двосторонню операцію `IBV_WR_SEND`. Клієнт приймає її у свій попередньо опублікований буфер прийому `IBV_WR_RECV`.
5. **Виконання RDMA Write та очікування завершення:** Клієнт формує `ibv_send_wr` з операцією `IBV_WR_RDMA_WRITE`, вказуючи отримані `remote_addr` та `rkey`. Мережева карта клієнта записує дані безпосередньо в RAM сервера через PCIe DMA.

### 1.1 Деталізація подій Communication Manager (CM Events)

При роботі через бібліотеку `librdmacm` встановлення з'єднання відбуваються асинхронно через канал подій `rdma_event_channel`. Застосунок послідовно обробляє наступні типи подій:
- `RDMA_CM_EVENT_ADDR_RESOLVED`: Підсистема визначила локальний пристрій RDMA, який має маршрут до вказаної IP-адреси.
- `RDMA_CM_EVENT_ROUTE_RESOLVED`: Ядро розпізнало параметри L2/L3 маршрутизації (LID, GID, VLAN, ECN) до цільового вузла. На цьому етапі розробник може створювати Queue Pair (`rdma_create_qp`).
- `RDMA_CM_EVENT_CONNECT_REQUEST`: Надішов вхідний запит на з'єднання від клієнта. Сервер отримує новий `client_id` і може прийняти виклик за допомогою `rdma_accept()`.
- `RDMA_CM_EVENT_ESTABLISHED`: З'єднання успішно встановлено, апаратні черги QP з обох боків переведені у стан RTS (Ready to Send).

---

## 2. Реалізація клієнта та сервера

:::tabs
```c
/*
 * rdma_pingpong.c — Повний варіант мовою C (POSIX / libibverbs / librdmacm)
 * Збірка: gcc -O2 rdma_pingpong.c -o rdma_pingpong -lrdmacm -libverbs
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <netdb.h>
#include <rdma/rdma_cma.h>

#define TEST_BUFFER_SIZE 1024

// Власний вихідний протокол для Out-Of-Band обміну R_Key та віртуальною адресою
struct RdmaBufferExchange {
    uint64_t remote_addr;
    uint32_t rkey;
};

static void run_server(const char *port) {
    struct rdma_event_channel *ec = rdma_create_event_channel();
    struct rdma_cm_id *listen_id = NULL, *client_id = NULL;
    struct rdma_cm_event *event = NULL;

    struct addrinfo hints = { .ai_family = AF_INET, .ai_socktype = SOCK_STREAM, .ai_flags = AI_PASSIVE };
    struct addrinfo *res = NULL;
    getaddrinfo(NULL, port, &hints, &res);

    rdma_create_id(ec, &listen_id, NULL, RDMA_PS_TCP);
    rdma_bind_addr(listen_id, res->ai_addr);
    freeaddrinfo(res);
    rdma_listen(listen_id, 1);

    printf("[Server] Очікування з'єднання на порту %s...\n", port);
    rdma_get_cm_event(ec, &event);
    client_id = event->id;
    rdma_ack_cm_event(event);

    struct ibv_pd *pd = ibv_alloc_pd(client_id->verbs);
    struct ibv_cq *cq = ibv_create_cq(client_id->verbs, 10, NULL, NULL, 0);

    struct ibv_qp_init_attr qp_attr = {
        .send_cq = cq,
        .recv_cq = cq,
        .qp_type = IBV_QPT_RC,
        .cap = { .max_send_wr = 10, .max_recv_wr = 10, .max_send_sge = 1, .max_recv_sge = 1 }
    };
    rdma_create_qp(client_id, pd, &qp_attr);

    char *buffer = (char *)calloc(1, TEST_BUFFER_SIZE);
    struct ibv_mr *mr = ibv_reg_mr(pd, buffer, TEST_BUFFER_SIZE,
                                   IBV_ACCESS_LOCAL_WRITE | IBV_ACCESS_REMOTE_WRITE);

    // Готуємо Send-буфер для передачі R_Key та адреси клієнту
    struct RdmaBufferExchange ex = {
        .remote_addr = (uint64_t)buffer,
        .rkey = mr->rkey
    };
    struct ibv_mr *ex_mr = ibv_reg_mr(pd, &ex, sizeof(ex), IBV_ACCESS_LOCAL_WRITE);

    struct ibv_sge sge = { .addr = (uint64_t)&ex, .length = sizeof(ex), .lkey = ex_mr->lkey };
    struct ibv_send_wr wr = {
        .wr_id = 1, .sg_list = &sge, .num_sge = 1,
        .opcode = IBV_WR_SEND, .send_flags = IBV_SEND_SIGNALED
    }, *bad_wr = NULL;

    struct rdma_conn_param conn_param = {};
    rdma_accept(client_id, &conn_param);
    rdma_get_cm_event(ec, &event); // RDMA_CM_EVENT_ESTABLISHED
    rdma_ack_cm_event(event);

    // Надсилаємо свої ключі клієнту
    ibv_post_send(client_id->qp, &wr, &bad_wr);

    struct ibv_wc wc;
    while (ibv_poll_cq(cq, 1, &wc) == 0); // Очікування завершення Send

    printf("[Server] Метадані передано. Очікування RDMA Write від клієнта...\n");
    sleep(2); // Даємо час клієнту виконати RDMA Write безпосередньо у буфер

    printf("[Server] Вміст буфера після RDMA Write: '%s'\n", buffer);

    ibv_dereg_mr(ex_mr);
    ibv_dereg_mr(mr);
    free(buffer);
    rdma_destroy_qp(client_id);
    ibv_destroy_cq(cq);
    ibv_dealloc_pd(pd);
    rdma_destroy_id(client_id);
    rdma_destroy_id(listen_id);
    rdma_destroy_event_channel(ec);
}

static void run_client(const char *ip, const char *port) {
    struct rdma_event_channel *ec = rdma_create_event_channel();
    struct rdma_cm_id *id = NULL;
    struct rdma_cm_event *event = NULL;

    struct addrinfo hints = { .ai_family = AF_INET, .ai_socktype = SOCK_STREAM };
    struct addrinfo *res = NULL;
    getaddrinfo(ip, port, &hints, &res);

    rdma_create_id(ec, &id, NULL, RDMA_PS_TCP);
    rdma_resolve_addr(id, NULL, res->ai_addr, 2000);
    freeaddrinfo(res);

    rdma_get_cm_event(ec, &event); // EVENT_ADDR_RESOLVED
    rdma_ack_cm_event(event);

    rdma_resolve_route(id, 2000);
    rdma_get_cm_event(ec, &event); // EVENT_ROUTE_RESOLVED
    rdma_ack_cm_event(event);

    struct ibv_pd *pd = ibv_alloc_pd(id->verbs);
    struct ibv_cq *cq = ibv_create_cq(id->verbs, 10, NULL, NULL, 0);

    struct ibv_qp_init_attr qp_attr = {
        .send_cq = cq, .recv_cq = cq, .qp_type = IBV_QPT_RC,
        .cap = { .max_send_wr = 10, .max_recv_wr = 10, .max_send_sge = 1, .max_recv_sge = 1 }
    };
    rdma_create_qp(id, pd, &qp_attr);

    // Реєструємо буфер прийому метаданих
    struct RdmaBufferExchange ex = {};
    struct ibv_mr *ex_mr = ibv_reg_mr(pd, &ex, sizeof(ex), IBV_ACCESS_LOCAL_WRITE);
    struct ibv_sge recv_sge = { .addr = (uint64_t)&ex, .length = sizeof(ex), .lkey = ex_mr->lkey };
    struct ibv_recv_wr recv_wr = { .wr_id = 2, .sg_list = &recv_sge, .num_sge = 1 }, *bad_recv_wr = NULL;

    ibv_post_recv(id->qp, &recv_wr, &bad_recv_wr);

    struct rdma_conn_param conn_param = {};
    rdma_connect(id, &conn_param);
    rdma_get_cm_event(ec, &event); // ESTABLISHED
    rdma_ack_cm_event(event);

    struct ibv_wc wc;
    while (ibv_poll_cq(cq, 1, &wc) == 0); // Очікування прийому R_Key

    printf("[Client] Отримано віддалену адресу: 0x%lx, R_Key: 0x%x\n", ex.remote_addr, ex.rkey);

    // Локальний буфер з повідомленням для запису на сервер
    char *local_msg = strdup("Привіт від RDMA Клієнта через Zero-Copy Write!");
    struct ibv_mr *local_mr = ibv_reg_mr(pd, local_msg, strlen(local_msg) + 1, IBV_ACCESS_LOCAL_WRITE);

    struct ibv_sge send_sge = { .addr = (uint64_t)local_msg, .length = (uint32_t)strlen(local_msg) + 1, .lkey = local_mr->lkey };
    struct ibv_send_wr write_wr = {
        .wr_id = 3, .sg_list = &send_sge, .num_sge = 1,
        .opcode = IBV_WR_RDMA_WRITE, .send_flags = IBV_SEND_SIGNALED,
        .wr.rdma = { .remote_addr = ex.remote_addr, .rkey = ex.rkey }
    }, *bad_write_wr = NULL;

    printf("[Client] Виконання RDMA Write...\n");
    ibv_post_send(id->qp, &write_wr, &bad_write_wr);

    while (ibv_poll_cq(cq, 1, &wc) == 0); // Очікування підтвердження від HCA
    printf("[Client] RDMA Write успішно виконано в апаратурі!\n");

    ibv_dereg_mr(local_mr);
    free(local_msg);
    ibv_dereg_mr(ex_mr);
    rdma_destroy_qp(id);
    ibv_destroy_cq(cq);
    ibv_dealloc_pd(pd);
    rdma_disconnect(id);
    rdma_destroy_id(id);
    rdma_destroy_event_channel(ec);
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s server <port> OR %s client <ip> <port>\n", argv[0], argv[0]);
        return 1;
    }
    if (strcmp(argv[1], "server") == 0) {
        run_server(argv[2]);
    } else if (strcmp(argv[1], "client") == 0) {
        run_client(argv[2], argv[3]);
    }
    return 0;
}
```
```cpp
/*
 * rdma_pingpong.cpp — Ідіоматичний C++20 варіант із RAII-управлінням ресурсами
 * Збірка: g++ -std=c++20 -O2 rdma_pingpong.cpp -o rdma_pingpong -lrdmacm -libverbs
 */
#include <iostream>
#include <memory>
#include <string>
#include <string_view>
#include <vector>
#include <span>
#include <stdexcept>
#include <netdb.h>
#include <rdma/rdma_cma.h>

// RAII Кастомні делітери для C++20 smart pointers
struct RdmaDeleters {
    void operator()(rdma_event_channel* ec) const noexcept { if (ec) rdma_destroy_event_channel(ec); }
    void operator()(rdma_cm_id* id) const noexcept { if (id) rdma_destroy_id(id); }
    void operator()(ibv_pd* pd) const noexcept { if (pd) ibv_dealloc_pd(pd); }
    void operator()(ibv_cq* cq) const noexcept { if (cq) ibv_destroy_cq(cq); }
    void operator()(ibv_mr* mr) const noexcept { if (mr) ibv_dereg_mr(mr); }
};

using UniqueEventChannel = std::unique_ptr<rdma_event_channel, RdmaDeleters>;
using UniqueCmId         = std::unique_ptr<rdma_cm_id, RdmaDeleters>;
using UniquePd           = std::unique_ptr<ibv_pd, RdmaDeleters>;
using UniqueCq           = std::unique_ptr<ibv_cq, RdmaDeleters>;
using UniqueMr           = std::unique_ptr<ibv_mr, RdmaDeleters>;

struct RemoteKeys {
    uint64_t remote_addr{0};
    uint32_t rkey{0};
};

class RdmaEndpoint {
public:
    explicit RdmaEndpoint(rdma_cm_id* id) : id_(id) {
        pd_.reset(ibv_alloc_pd(id_->verbs));
        if (!pd_) throw std::runtime_error("Не вдалося виділити Protection Domain");

        cq_.reset(ibv_create_cq(id_->verbs, 16, nullptr, nullptr, 0));
        if (!cq_) throw std::runtime_error("Не вдалося створити Completion Queue");

        ibv_qp_init_attr qp_attr{};
        qp_attr.send_cq = cq_.get();
        qp_attr.recv_cq = cq_.get();
        qp_attr.qp_type = IBV_QPT_RC;
        qp_attr.cap.max_send_wr = 16;
        qp_attr.cap.max_recv_wr = 16;
        qp_attr.cap.max_send_sge = 1;
        qp_attr.cap.max_recv_sge = 1;

        if (rdma_create_qp(id_, pd_.get(), &qp_attr) != 0) {
            throw std::runtime_error("Не вдалося створити Queue Pair");
        }
    }

    ~RdmaEndpoint() noexcept {
        if (id_ && id_->qp) {
            rdma_destroy_qp(id_);
        }
    }

    [[nodiscard]] ibv_pd* pd() const noexcept { return pd_.get(); }
    [[nodiscard]] ibv_cq* cq() const noexcept { return cq_.get(); }

    void poll_completion_blocking(uint64_t expected_wr_id) {
        ibv_wc wc{};
        while (true) {
            int ret = ibv_poll_cq(cq_.get(), 1, &wc);
            if (ret > 0) {
                if (wc.status != IBV_WC_SUCCESS) {
                    throw std::runtime_error("Помилка CQ status: " + std::to_string(wc.status));
                }
                if (wc.wr_id == expected_wr_id) return;
            } else if (ret < 0) {
                throw std::runtime_error("Помилка опитування ibv_poll_cq");
            }
        }
    }

private:
    rdma_cm_id* id_{nullptr};
    UniquePd pd_{nullptr};
    UniqueCq cq_{nullptr};
};

void run_cpp_server(std::string_view port) {
    UniqueEventChannel ec(rdma_create_event_channel());
    if (!ec) throw std::runtime_error("Помилка створення event channel");

    rdma_cm_id* raw_listen_id{nullptr};
    if (rdma_create_id(ec.get(), &raw_listen_id, nullptr, RDMA_PS_TCP) != 0) {
        throw std::runtime_error("Помилка rdma_create_id");
    }
    UniqueCmId listen_id(raw_listen_id);

    addrinfo hints{.ai_family = AF_INET, .ai_socktype = SOCK_STREAM, .ai_flags = AI_PASSIVE};
    addrinfo* res{nullptr};
    getaddrinfo(nullptr, port.data(), &hints, &res);
    rdma_bind_addr(listen_id.get(), res->ai_addr);
    freeaddrinfo(res);

    rdma_listen(listen_id.get(), 1);
    std::cout << "[C++ Server] Очікування на порту " << port << "...\n";

    rdma_cm_event* event{nullptr};
    rdma_get_cm_event(ec.get(), &event);
    UniqueCmId client_id(event->id);
    rdma_ack_cm_event(event);

    RdmaEndpoint ep(client_id.get());

    std::vector<char> target_buffer(1024, 0);
    UniqueMr target_mr(ibv_reg_mr(ep.pd(), target_buffer.data(), target_buffer.size(),
                                  IBV_ACCESS_LOCAL_WRITE | IBV_ACCESS_REMOTE_WRITE));

    RemoteKeys keys{.remote_addr = reinterpret_cast<uint64_t>(target_buffer.data()), .rkey = target_mr->rkey};
    UniqueMr keys_mr(ibv_reg_mr(ep.pd(), &keys, sizeof(keys), IBV_ACCESS_LOCAL_WRITE));

    ibv_sge sge{.addr = reinterpret_cast<uint64_t>(&keys), .length = sizeof(keys), .lkey = keys_mr->lkey};
    ibv_send_wr wr{.wr_id = 100, .sg_list = &sge, .num_sge = 1, .opcode = IBV_WR_SEND, .send_flags = IBV_SEND_SIGNALED};
    ibv_send_wr* bad_wr{nullptr};

    rdma_conn_param conn_param{};
    rdma_accept(client_id.get(), &conn_param);
    rdma_get_cm_event(ec.get(), &event);
    rdma_ack_cm_event(event);

    ibv_post_send(client_id->qp, &wr, &bad_wr);
    ep.poll_completion_blocking(100);

    std::cout << "[C++ Server] Метадані передано. Очікування RDMA Write...\n";
    sleep(2);

    std::cout << "[C++ Server] Результат буфера: '" << target_buffer.data() << "'\n";
}
```
:::

---

## 3. Практичні пастки, вирівнювання та системне налаштування

При практичній розробці та експлуатації RDMA-застосунків у виробничому середовищі розробники стикаються з низкою специфічних системних пасток.

### 3.1 Обмеження закріпленої пам'яті (`ulimit -l` / `RLIMIT_MEMLOCK`)
Реєстрація пам'яті (`ibv_reg_mr`) викликає в ядрі Linux внутрішню процедуру `pin_user_pages()`, яка виключає зареєстровані віртуальні сторінки з підсистеми підкачки (swap-out). У багатьох дистрибутивах за замовчуванням максимальний розмір заблокованої пам'яті для непривілейованих процесів встановлено у 64 КБ.

Спроба зареєструвати буфер більшого розміру призведе до відмови виклику `ibv_reg_mr()` з поверненням `NULL` та встановленням змінної `errno = ENOMEM`.

**Розв'язання:** Збільшення системних лімітів у конфігурації `/etc/security/limits.conf`:
```text
*    soft    memlock    unlimited
*    hard    memlock    unlimited
```

Також рекомендується налаштувати параметри ядра `sysctl` для підсистеми пам'яті `vm.max_map_count`, щоб запобігти вичерпанню ліміту регіонів VMA при реєстрації тисяч дрібних Memory Regions.

### 3.2 Пастка продуктивності: Динамічна реєстрація MR на гарячому шляху
Функція `ibv_reg_mr()` є дуже дорогою операцією, оскільки вона вимагає виконання системного виклику ядра, виклику `pin_user_pages()`, алокації внутрішніх структур та оновлення апаратної TPT-таблиці адаптера HCA. 

**Антипатерн:** Виклик `ibv_reg_mr()` безпосередньо перед кожним `ibv_post_send()` і виклик `ibv_dereg_mr()` одразу після нього. Це повністю знищує переваги Kernel Bypass, додаючи затримки у десятки мікросекунд.

**Правильний підхід:** Попередня виділення басейнів пам'яті (Buffer Pools / Slab Allocators) на етапі ініціалізації програми. Пам'ять реєструється один раз при старті, а під час передачі даних змінюються лише зміщення (offsets) всередині готового Memory Region.

### 3.3 Вирівнювання адрес (Memory Alignment)
Для досягнення максимальної пропускної здатності шини PCIe DMA буфери, що передаються у `ibv_reg_mr()`, повинні бути вирівняні по межі системної сторінки (4096 байтів) або розміру кеш-лінії CPU (64 байти). Використання звичайного `malloc()` може призводити до розщеплення DMA-транзакцій на межах сторінок.
- У мові C слід використовувати `posix_memalign(&ptr, 4096, size)`.
- У мові C++20 слід застосовувати `std::aligned_alloc(4096, size)` або специфікатор `alignas(4096)`.

### 3.4 Когерентність кешу CPU та DMA-бар'єри
Під час виконання операції **RDMA Write** мережевий адаптер HCA записує дані безпосередньо у фізичні модулі DRAM через шину PCIe DMA. На архітектурах x86-64 шина PCIe підтримує механізм шинного спостереження (bus snooping / CCI), який автоматично інвалідує застарілі рядки кешу CPU (L1/L2/L3). 

Однак на деяких не-когерентних архітектурах (деякі кристали ARM64 чи RISC-V) або при використанні бафферизованого читання процесор може прочитати з кешу старі байти. Для гарантії когерентності розробник повинен використовувати явні примусові бар'єри пам’яті (`std::atomic_thread_fence(std::memory_order_acquire)`).

### 3.5 Оптимізація малих пакетів: Inline Data
При відправці малих повідомлень (розміром до 128–256 байтів) виконання DMA-читання з боку HCA створює накладні витрати на арбітраж шини PCIe. Встановлення прапорця `IBV_SEND_INLINE` у `wr.send_flags` змушує драйвер `libibverbs` скопіювати байти безпосередньо всередину команди WQE, яка записується в MMIO-регістр HCA. Це знижує затримку передачі на **200–400 наносекунд**.

### 3.6 Стратегія опитування черг Completion Queue (Busy-Wait vs Event-Driven)
Опитування черги CQ за допомогою виклику `ibv_poll_cq()` у нескінченному циклі (busy loop / spin polling) надає найнижчу затримку відгуку (латентність), але завантажує ядро процесора на 100%. Убагатьох реальних системах використовують комбіновану стратегію (Hybrid Polling): потік опитує CQ у циклі протягом 10–50 мікросекунд, і якщо нові CQE не з'являються, переходить у режим очікування події через канал комплішна `comp_channel` та системний виклик `epoll_wait()`.
