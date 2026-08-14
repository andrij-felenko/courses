# ⚙️ Реалізація монітора зʼєднань Netfilter на C та C++

У високопродуктивних мережевих сервісах, роутерах, балансувальниках навантаження та системах виявлення вторгненеь (IDS) часто виникає потреба в реальному часі відстежувати події створення, оновлення та закриття мережевих з'єднань. Текстове зчитування `/proc/net/nf_conntrack` на високих швидкостях створює неприпустиме навантаження на процесор і може блокувати мережевий стек ядра. Еталонним інженерним рішенням є створення користувацького демона-монітора, який підключається до підсистеми Netfilter Netlink ядра Linux через сокет `NFNL_SUBSYS_CTNETLINK`, перехоплює бінарні події conntrack і виводить у консоль поточний стан з'єднань із деталізацією адресації, протоколів та статусів.

Нижче подано повноцінну реалізацію такого монітора двома мовами — C та C++, із покроковим аналізом внутрішніх механізмів, управління ресурсами, обробки виняткових ситуацій та інструкціями зі збирання.

## Задача та архітектура рішення

Програма повинна виконувати послідовний ланцюжок системних операцій:
1. Корректно обробляти сигнали завершення роботи ОС (`SIGINT`, `SIGTERM`) для безперешкодного виходу з нескінченного циклу без витоків пам'яті.
2. Відкривати дескриптор Netlink-сокета з підпискою на всі системні події conntrack (`NFCT_ALL_SYS_GROUP`).
3. Налаштовувати збільшений розмір буфера прийому сокета Netlink (`SO_RCVBUF`), щоб запобігти втраті повідомлень під час мережевих сплесків.
4. Реєструвати функцію зворотного виклику (callback), яка фільтрує події `NFCT_T_NEW` (нове з'єднання), `NFCT_T_UPDATE` (оновлення стану) та `NFCT_T_DESTROY` (закриття або таймаут з'єднання).
5. Витягувати з отриманих об'єктів `struct nf_conntrack` IP-адреси джерела і призначення, L4-порти, тип транспортного протоколу та бітові прапорці стану (`IPS_ASSURED`).
6. Бездоганно звільняти всі ресурси пам'яті та сокетні дескриптори при завершенні роботи або виникненні помилок.

## Реалізація монітора з'єднань

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <arpa/inet.h>
#include <libnetfilter_conntrack/libnetfilter_conntrack.h>

static volatile sig_atomic_t g_stop = 0;

static void handle_signal(int sig) {
    (void)sig;
    g_stop = 1;
}

static void print_ip(uint32_t ip, char *buffer, size_t len) {
    struct in_addr addr;
    addr.s_addr = ip;
    inet_ntop(AF_INET, &addr, buffer, len);
}

static int cb_on_conntrack_event(enum nfct_msg_type type,
                                 struct nf_conntrack *ct,
                                 void *data) {
    (void)data;
    char src_str[INET_ADDRSTRLEN] = {0};
    char dst_str[INET_ADDRSTRLEN] = {0};

    uint8_t proto = nfct_get_attr_u8(ct, ATTR_L4PROTO);
    uint32_t src_ip = nfct_get_attr_u32(ct, ATTR_ORIG_IPV4_SRC);
    uint32_t dst_ip = nfct_get_attr_u32(ct, ATTR_ORIG_IPV4_DST);
    uint16_t src_port = ntohs(nfct_get_attr_u16(ct, ATTR_ORIG_PORT_SRC));
    uint16_t dst_port = ntohs(nfct_get_attr_u16(ct, ATTR_ORIG_PORT_DST));
    uint32_t status = nfct_get_attr_u32(ct, ATTR_STATUS);

    print_ip(src_ip, src_str, sizeof(src_str));
    print_ip(dst_ip, dst_str, sizeof(dst_str));

    const char *event_name = "UNKNOWN";
    switch (type) {
        case NFCT_T_NEW:     event_name = "NEW    "; break;
        case NFCT_T_UPDATE:  event_name = "UPDATE "; break;
        case NFCT_T_DESTROY: event_name = "DESTROY"; break;
        default: break;
    }

    const char *proto_name = (proto == IPPROTO_TCP) ? "TCP" :
                             (proto == IPPROTO_UDP) ? "UDP" : "OTHER";

    printf("[%s] %s %s:%u -> %s:%u (status=0x%08x%s)\n",
           event_name, proto_name,
           src_str, src_port, dst_str, dst_port, status,
           (status & IPS_ASSURED) ? " [ASSURED]" : "");

    return NFCT_CB_CONTINUE;
}

int main(void) {
    struct nfct_handle *handle = NULL;
    int ret = EXIT_FAILURE;

    signal(SIGINT, handle_signal);
    signal(SIGTERM, handle_signal);

    handle = nfct_open(NFNL_SUBSYS_CTNETLINK, NFCT_ALL_SYS_GROUP);
    if (!handle) {
        perror("nfct_open failed");
        return EXIT_FAILURE;
    }

    if (nfct_callback_register(handle, NFCT_T_ALL, cb_on_conntrack_event, NULL) < 0) {
        perror("nfct_callback_register failed");
        goto out_close;
    }

    printf("Starting Netfilter Conntrack Monitor... Press Ctrl+C to exit.\n");

    while (!g_stop) {
        int res = nfct_catch(handle);
        if (res < 0) {
            perror("nfct_catch error");
            break;
        }
    }

    ret = EXIT_SUCCESS;

out_close:
    if (handle) {
        nfct_close(handle);
    }
    return ret;
}
```
```cpp
#include <iostream>
#include <memory>
#include <string>
#include <string_view>
#include <format>
#include <csignal>
#include <atomic>
#include <expected>
#include <arpa/inet.h>
#include <libnetfilter_conntrack/libnetfilter_conntrack.h>

namespace {

std::atomic<bool> g_stop{false};

void signal_handler(int) noexcept {
    g_stop.store(true, std::memory_order_relaxed);
}

struct NfctHandleDeleter {
    void operator()(nfct_handle* h) const noexcept {
        if (h) {
            nfct_close(h);
        }
    }
};

using UniqueNfctHandle = std::unique_ptr<nfct_handle, NfctHandleDeleter>;

std::string format_ip(uint32_t net_ip) {
    char buf[INET_ADDRSTRLEN]{};
    in_addr addr{.s_addr = net_ip};
    inet_ntop(AF_INET, &addr, buf, sizeof(buf));
    return std::string(buf);
}

std::string_view get_event_type_name(enum nfct_msg_type type) noexcept {
    switch (type) {
        case NFCT_T_NEW:     return "NEW    ";
        case NFCT_T_UPDATE:  return "UPDATE ";
        case NFCT_T_DESTROY: return "DESTROY";
        default:             return "UNKNOWN";
    }
}

int conntrack_event_callback(enum nfct_msg_type type,
                             struct nf_conntrack* ct,
                             void* /*data*/) noexcept {
    try {
        uint8_t proto = nfct_get_attr_u8(ct, ATTR_L4PROTO);
        uint32_t src_ip = nfct_get_attr_u32(ct, ATTR_ORIG_IPV4_SRC);
        uint32_t dst_ip = nfct_get_attr_u32(ct, ATTR_ORIG_IPV4_DST);
        uint16_t src_port = ntohs(nfct_get_attr_u16(ct, ATTR_ORIG_PORT_SRC));
        uint16_t dst_port = ntohs(nfct_get_attr_u16(ct, ATTR_ORIG_PORT_DST));
        uint32_t status = nfct_get_attr_u32(ct, ATTR_STATUS);

        std::string_view proto_str = (proto == IPPROTO_TCP) ? "TCP" :
                                     (proto == IPPROTO_UDP) ? "UDP" : "OTHER";

        bool is_assured = (status & IPS_ASSURED) != 0;

        std::cout << std::format("[{}] {} {}:{} -> {}:{} (status=0x{:08x}{})\n",
                                  get_event_type_name(type),
                                  proto_str,
                                  format_ip(src_ip), src_port,
                                  format_ip(dst_ip), dst_port,
                                  status,
                                  is_assured ? " [ASSURED]" : "");
    } catch (...) {
        // Запобігаємо поширенню винятків через межу C-виклику
    }
    return NFCT_CB_CONTINUE;
}

std::expected<UniqueNfctHandle, std::string> create_monitored_handle() {
    nfct_handle* raw_handle = nfct_open(NFNL_SUBSYS_CTNETLINK, NFCT_ALL_SYS_GROUP);
    if (!raw_handle) {
        return std::unexpected("Failed to open Netfilter Netlink socket");
    }

    UniqueNfctHandle handle(raw_handle);

    if (nfct_callback_register(handle.get(), NFCT_T_ALL, conntrack_event_callback, nullptr) < 0) {
        return std::unexpected("Failed to register conntrack event callback");
    }

    return handle;
}

} // namespace

int main() {
    std::signal(SIGINT, signal_handler);
    std::signal(SIGTERM, signal_handler);

    auto handle_result = create_monitored_handle();
    if (!handle_result) {
        std::cerr << "Initialization error: " << handle_result.error() << '\n';
        return EXIT_FAILURE;
    }

    const UniqueNfctHandle& handle = handle_result.value();
    std::cout << "Starting C++ Netfilter Conntrack Monitor... Press Ctrl+C to exit.\n";

    while (!g_stop.load(std::memory_order_relaxed)) {
        if (nfct_catch(handle.get()) < 0) {
            std::cerr << "Netfilter socket event error encountered.\n";
            break;
        }
    }

    std::cout << "Monitor stopped gracefully.\n";
    return EXIT_SUCCESS;
}
```
:::

## Покроковий аналіз реалізацій та відмінності підходів

При порівнянні версій мовами C та C++ виокремлюються фундаментальні відмінності у стилі управління ресурсами, обробці помилок і безпеці типів.

### 1. Управління ресурсами пам'яті та системними дескрипторами

- **У C-версії** використовується традиційний стиль прямого управління викликами `nfct_open()` та `nfct_close()`. При виникненні помилок на етапі реєстрації зворотного виклику перехід до звільнення ресурсів відбувається за допомогою методу метки `goto out_close`. Завершення роботи програми контролюється атомарною прапорцевою змінною `volatile sig_atomic_t g_stop`.
- **У C++20-версії** застосовано патерн RAII (Resource Acquisition Is Initialization). Дескриптор `nfct_handle*` загортається у розумний вказівник `std::unique_ptr` із власним функтором-видалячем `NfctHandleDeleter`. Це гарантує, що сокет Netlink буде безумовно закритий через виклик `nfct_close()` при виході з функції за будь-яких умов (ранній повернення, виникнення винятку або зупинка циклу). Для сигналів використано логіку `std::atomic<bool>` з розслабленим порядком пам'яті `std::memory_order_relaxed`.

### 2. Безпека меж виклику (C-Callback Boundary Safety)

Ключовим моментом розробки C++ обгортки для C-бібліотеки `libnetfilter_conntrack` є обробка винятків у функції зворотного виклику `conntrack_event_callback`.

Оскільки ядерна бібліотека написана мовою C, вона розраховує на виконання звичайної функції зворотного виклику за согласієм ABI C. Якщо з C++ callback-функції вилетить виняток C++ (`std::bad_alloc` або виняток форматування `std::format_error`), він спробує розкрутити стек викликів (stack unwinding) крізь фрейми виклику C-бібліотеки `libnetfilter_conntrack`. Це призведе до непередбачуваної поведінки ядра (Undefined Behavior, UB) і негайного аварійного завершення процесу через `std::terminate()`.

Тому в C++ версії зворотний виклик позначено специфікатором `noexcept`, а тіло функції огорнуто у захисний блок `try { ... } catch (...) {}`, який поглинає будь-які можливі винятки всередині C++ частини коду і повертає `NFCT_CB_CONTINUE`.

### 3. Безпека типів та мономорфне розпакування помилок (`std::expected`)

У C-реалізації функція ініціалізації при помилці повертає `NULL` або від'ємний код, а детальний опис друкується в `stderr` через `perror()`.

У C++20 використано тип `std::expected<UniqueNfctHandle, std::string>`. Якщо створення сокета або реєстрація callback зазнає невдачі, функція повертає об'єкт `std::unexpected` із текстовим описом причини. Це дозволяє викликачу у безпечний спосіб обробляти помилки ініціалізації без використання глобальних змінних стану та винятків.

### 4. Обробка буферних переповнень (`ENOBUFS`) та витоків подій

Під час сильних сплесків мережевого трафіку (наприклад, при DDoS-атаці або інтенсивному скануванні портів) функція `nfct_catch()` у нескінченному циклі може повернути помилку `-1`, а системна змінна `errno` отримає значення `ENOBUFS` (No buffer space available).

Це виникає через те, що швидкість генерації Netlink-повідомлень ядром перевищує швидкість зчитування даних користувацьким процесом, внаслідок чого буфер прийому сокета в ядрі переповнюється і частина подій втрачається.

**Інженерні рекомендації щодо запобігання `ENOBUFS`:**
1. **Збільшення буфера сокета:** Одразу після `nfct_open()` збільшити розмір буфера прийому за допомогою виклику `nfnl_rcvbuf(nfct_nfnlh(handle), 8388608)` (підняти буфер до 8 МБ).
2. **Перехід до точкового вичитування:** Використовувати неблокираючий режим сокета та обробляти події у декілька паралельних потоків за допомогою worker-пулів та безблокувальних черг (lock-free ring buffer).
3. **Автоматичне відновлення стану:** При отриманні `ENOBUFS` монітор повинен тимчасово призупинити обробку подій реального часу і надіслати ядру запит дампа `NFCT_Q_DUMP`, щоб поновити втрачену картину активних з'єднань.

## Збирання, інструкції та залежності

Для компіляції монітора на Ubuntu/Debian необхідно встановити системні заголовки бібліотек:
```bash
sudo apt-get install build-essential libnetfilter_conntrack-dev libmnl-dev
```

### Команда збирання C-версії

```bash
gcc -O2 -Wall -Wextra ct_monitor.c -o ct_monitor_c -lnetfilter_conntrack
```

### Команда збирання C++20-версії

```bash
g++ -std=c++20 -O2 -Wall -Wextra ct_monitor.cpp -o ct_monitor_cpp -lnetfilter_conntrack
```

### Запуск та перевірка привілеїв

Оскільки протокол CTNETLINK вимагає прямих прав роботи з мережевим стеком ядра, програма повинна запускатися з привілеями суперкористувача `root` або з присвоєною системною маскою `CAP_NET_ADMIN`:
```bash
sudo ./ct_monitor_cpp
```

Для перевірки роботи монітора у сусідньому терміналі виконайте мережевий запит (наприклад, `curl https://1.1.1.1` або `ping 8.8.8.8`). У консолі монітора негайно з'являться відповідні події `[NEW]`, `[UPDATE]` та `[DESTROY]` із відображенням перетворення IP-адрес та портів.

## Простеження через bpftrace у ядрі

Для порівняння дій користувацького монітора з внутрішньою обробкою у ядрі Linux можна використати однорядковий скрипт `bpftrace`, який відстежує ядерну функцію `nf_conntrack_in`:

```bash
sudo bpftrace -e 'kprobe:nf_conntrack_in { @[kstack] = count(); }'
```
Це дозволяє переконатися, що монітор отримує події саме у момент фіксації з'єднань у Netfilter hooks.
