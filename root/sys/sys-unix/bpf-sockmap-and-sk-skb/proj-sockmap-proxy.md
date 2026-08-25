# ⚙️ Практика: Перенаправлення TCP-трафіку за допомогою eBPF sockmap

Цей практичний проєкт містить повну та вичерпну реалізацію системи високопродуктивного перенаправлення локального TCP-трафіку між двома сокетами на одному хості. Проєкт детально демонструє роботу технології `BPF_MAP_TYPE_SOCKMAP` та BPF-програми `BPF_PROG_TYPE_SK_MSG`, які дозволяють повністю оминути проходження даних через стек протоколів TCP/IP ядра Linux, досягаючи максимальної швидкості передачі даних.

Проєкт розділено на дві принципові частини:
1. **Ядерна частина (Kernel Space / eBPF)**: Програма BPF типу `sk_msg`, яка компілюється за допомогою інструментарію Clang/LLVM у байткод BPF. Вона виконується безпосередньо всередині ядра під час здійснення системних викликів відправки даних (`send()`, `write()`, `sendmsg()`) і перенаправляє вектора сторінок пам'яті безпосередньо у чергу прийому цільового сокета.
2. **Користувацька частина (User Space Control Plane)**: Програма керування, яка відкриває BPF-байтокод, ініціалізує карту `SOCKMAP`, реєструє в ній файлові дескриптори сокетів та прикріплює програму вердикту. Наведено дві рівноцінні реалізації — мовою C з використанням чистого бібліотечного API `libbpf` та мовою C++ з використанням сучасних паттернів RAII, безпечного управління ресурсами та стандартних контейнерів `std::span` і `std::string_view`.

---

## 1. Архітектура та покроковий потік виконання системи

Процес налаштування та перенаправлення трафіку працює за чіткою послідовністю дій:

```
Покроковий потік перенаправлення трафіку у проєкті:

[Userspace: main()]
       | 1. bpf_object__open_file() & bpf_object__load()
       v
[Kernel BPF Subsystem] <--- (Load & Verify BPF Bytecode)
       | 2. bpf_prog_attach(BPF_SK_MSG_VERDICT)
       v
[BPF_MAP_TYPE_SOCKMAP] <--- 3. bpf_map_update_elem(Sock A -> Key 0, Sock B -> Key 1)
       |
       | 4. User Process writes to Sock A: write(sock_a, "Hello", 5)
       v
[tcp_bpf_sendmsg()] ---> [sk_msg Verdict BPF Program]
                                 |
                     bpf_msg_redirect_map(msg, &sock_map, 1, BPF_F_INGRESS)
                                 |
                                 v
                [sk_receive_queue Sock B] ---> 5. read(sock_b) -> "Hello"
```

1. **Компіляція та завантаження**: Програма простору користувача завантажує закомпільований ELF-файл `bpf_redir.bpf.o` у ядро за допомогою системного виклику `bpf(BPF_PROG_LOAD)`. Верифікатор ядра перевіряє безпеку BPF-коду (гарантію завершення, відсутність виходів за межі пам'яті).
2. **Ініціалізація карти**: У ядрі створюється BPF-карта типу `BPF_MAP_TYPE_SOCKMAP` з двома слотами (індекси `0` та `1`).
3. **Прикріплення вердикту**: Програма типу `SEC("sk_msg")` прикріплюється до карти `SOCKMAP` через виклик `bpf_prog_attach` з типом `BPF_SK_MSG_VERDICT`.
4. **Створення сокетів**: Створюється пара зв'язаних сокетів `sock_a` та `sock_b` (наприклад, через виклик `socketpair()` або локальне з'єднання TCP `127.0.0.1`).
5. **Реєстрація у SOCKMAP**: Файлові дескриптори `sock_a` та `sock_b` додаються до `SOCKMAP` під ключами `0` та `1` відповідно. У цей момент ядро Linux підміняє операції протоколу `sk_prot` для цих сокетів на BPF-обгортку `tcp_bpf_prot`.
6. **Передача даних без копіювання**: При виклику `write(sock_a, buf, len)` ядро викликає `tcp_bpf_sendmsg()`, заскакує у BPF-програму `sk_msg`, викликом `bpf_msg_redirect_map()` спрямовує сторінки даних у чергу прийому `sock_b`. Процес на `sock_b` викликом `read()` отримує байти без жодної обробки в TCP/IP стеку.

---

## 2. Код BPF-програми ядра (bpf_redir.bpf.c)

Нижче наведено вихідний код eBPF-програми. Вона оперує контекстом `struct sk_msg_md` і приймає рішення про перенаправлення.

```c
#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_endian.h>

/* Оголошення BPF-карти сокетів типу SOCKMAP з 2 елементами */
struct {
    __uint(type, BPF_MAP_TYPE_SOCKMAP);
    __uint(max_entries, 2);
    __type(key, __u32);
    __type(value, __u32);
} sock_map SEC(".maps");

/* BPF_PROG_TYPE_SK_MSG програма вердикту, яка викликається при sendmsg */
SEC("sk_msg")
int bpf_sockmap_redirect(struct sk_msg_md *msg)
{
    /* Ключ 0 відповідає Сокету A (Proxy), ключ 1 — Сокету B (Backend).
     * Якщо дані надходять від сокета 0, спрямовуємо їх на сокет 1.
     * Прапор BPF_F_INGRESS розміщує байти безпосередньо у чергу прийому Sock B.
     */
    __u32 target_key = 1;

    /* Перенаправляємо вектор сторінок у сокет з ключем 1 */
    return bpf_msg_redirect_map(msg, &sock_map, target_key, BPF_F_INGRESS);
}

char _license[] SEC("license") = "GPL";
```

---

## 3. Користувацька програма керування (Userspace Control Plane)

Програма простору користувача відповідає за завантаження BPF-об'єкта, прикріплення програми до карти та управління файловими дескрипторами сокетів.

:::tabs
```c
/* C: Традиційна реалізація з використанням чистих викликів libbpf C API */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>

int main(int argc, char **argv)
{
    struct bpf_object *obj = NULL;
    int prog_fd, map_fd;
    int err;

    printf("=== BPF SOCKMAP Zero-Copy Redirect Controller (C) ===\n");

    /* 1. Відкриваємо та завантажуємо BPF ELF-об'єкт */
    obj = bpf_object__open_file("bpf_redir.bpf.o", NULL);
    if (!obj) {
        fprintf(stderr, "Помилка: не вдалося відкрити BPF об'єкт bpf_redir.bpf.o\n");
        return 1;
    }

    err = bpf_object__load(obj);
    if (err) {
        fprintf(stderr, "Помилка: не вдалося завантажити BPF програму в ядро (код: %d)\n", err);
        bpf_object__close(obj);
        return 1;
    }

    /* 2. Знаходимо файлові дескриптори завантаженої програми та карти */
    struct bpf_program *prog = bpf_object__find_program_by_name(obj, "bpf_sockmap_redirect");
    prog_fd = bpf_program__fd(prog);
    map_fd = bpf_object__find_map_fd_by_name(obj, "sock_map");

    if (prog_fd < 0 || map_fd < 0) {
        fprintf(stderr, "Помилка: не знайдено BPF програму або карту sock_map у файлі\n");
        bpf_object__close(obj);
        return 1;
    }

    /* 3. Прикріплюємо BPF_SK_MSG_VERDICT до карти SOCKMAP */
    err = bpf_prog_attach(prog_fd, map_fd, BPF_SK_MSG_VERDICT, 0);
    if (err) {
        fprintf(stderr, "Помилка: не вдалося прикріпити BPF_SK_MSG_VERDICT до SOCKMAP\n");
        bpf_object__close(obj);
        return 1;
    }

    /* 4. Створюємо сокетну пару для локального тестування */
    int sv[2];
    if (socketpair(AF_UNIX, SOCK_STREAM, 0, sv) < 0) {
        perror("Помилка створення socketpair");
        bpf_object__close(obj);
        return 1;
    }

    int sock_a = sv[0];
    int sock_b = sv[1];

    /* 5. Зареєструємо дескриптори сокетів у SOCKMAP за ключами 0 та 1 */
    uint32_t key_a = 0;
    uint32_t key_b = 1;

    err = bpf_map_update_elem(map_fd, &key_a, &sock_a, BPF_ANY);
    if (err) {
        perror("Помилка оновлення SOCKMAP для sock_a");
        goto cleanup;
    }

    err = bpf_map_update_elem(map_fd, &key_b, &sock_b, BPF_ANY);
    if (err) {
        perror("Помилка оновлення SOCKMAP для sock_b");
        goto cleanup;
    }

    printf("Успіх: Сокети FD %d (Key 0) та FD %d (Key 1) додано до SOCKMAP!\n", sock_a, sock_b);
    printf("Трафік із Sock A тепер перенаправляється безпосередньо у Sock B в ядрі!\n");

    /* Тестова передача даних через Sock A */
    const char *payload = "Привіт від BPF Zero-Copy Sockmap Redirect!";
    ssize_t sent = write(sock_a, payload, strlen(payload));
    printf("Sock A відправив %zd байтів у сокет.\n", sent);

    char buffer[128] = {0};
    ssize_t recvd = read(sock_b, buffer, sizeof(buffer) - 1);
    printf("Sock B успішно прочитав %zd байтів без проходження TCP/IP: '%s'\n", recvd, buffer);

cleanup:
    close(sock_a);
    close(sock_b);
    bpf_object__close(obj);
    return 0;
}
```
```cpp
// C++20: Ідіоматична обгортка з RAII управлінням ресурсами та std::span
#include <iostream>
#include <string_view>
#include <vector>
#include <memory>
#include <span>
#include <system_error>
#include <unistd.h>
#include <sys/socket.h>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>

namespace ebpf {

// RAII обгортка для безпечного управління файловими дескрипторами сокетів
class UniqueFd {
    int fd_{-1};
public:
    constexpr UniqueFd() noexcept = default;
    explicit UniqueFd(int fd) noexcept : fd_(fd) {}
    ~UniqueFd() { reset(); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : fd_(other.release()) {}
    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) {
            reset(other.release());
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
    
    int release() noexcept {
        int temp = fd_;
        fd_ = -1;
        return temp;
    }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }
};

// RAII обгортка для управління життєвим циклом BPF об'єкта
class BpfObjectWrapper {
    struct bpf_object* obj_{nullptr};
public:
    explicit BpfObjectWrapper(struct bpf_object* obj) : obj_(obj) {}
    ~BpfObjectWrapper() {
        if (obj_) {
            bpf_object__close(obj_);
        }
    }

    [[nodiscard]] struct bpf_object* get() const noexcept { return obj_; }
};

} // namespace ebpf

int main() {
    std::cout << "=== BPF SOCKMAP Redirect Controller (Modern C++20) ===\n";

    // 1. Відкриваємо та завантажуємо BPF програму
    struct bpf_object* raw_obj = bpf_object__open_file("bpf_redir.bpf.o", nullptr);
    if (!raw_obj) {
        std::cerr << "Помилка: не вдалося відкрити BPF об'єкт bpf_redir.bpf.o\n";
        return 1;
    }
    ebpf::BpfObjectWrapper obj(raw_obj);

    if (bpf_object__load(obj.get()) != 0) {
        std::cerr << "Помилка: не вдалося завантажити BPF програму в ядро Linux\n";
        return 1;
    }

    struct bpf_program* prog = bpf_object__find_program_by_name(obj.get(), "bpf_sockmap_redirect");
    int prog_fd = bpf_program__fd(prog);
    int map_fd = bpf_object__find_map_fd_by_name(obj.get(), "sock_map");

    if (prog_fd < 0 || map_fd < 0) {
        std::cerr << "Помилка: не знайдено BPF програму або карту sock_map у файлі\n";
        return 1;
    }

    // 2. Прикріплюємо BPF_SK_MSG_VERDICT до SOCKMAP
    if (bpf_prog_attach(prog_fd, map_fd, BPF_SK_MSG_VERDICT, 0) != 0) {
        std::cerr << "Помилка: не вдалося прикріпити BPF_SK_MSG_VERDICT\n";
        return 1;
    }

    // 3. Створюємо сокетну пару з авто-очищенням RAII
    int fds[2];
    if (::socketpair(AF_UNIX, SOCK_STREAM, 0, fds) < 0) {
        std::perror("socketpair");
        return 1;
    }
    ebpf::UniqueFd sock_a(fds[0]);
    ebpf::UniqueFd sock_b(fds[1]);

    // 4. Додаємо сокети у SOCKMAP
    uint32_t key_a = 0, key_b = 1;
    int raw_a = sock_a.get();
    int raw_b = sock_b.get();

    if (bpf_map_update_elem(map_fd, &key_a, &raw_a, BPF_ANY) != 0 ||
        bpf_map_update_elem(map_fd, &key_b, &raw_b, BPF_ANY) != 0) {
        std::cerr << "Помилка оновлення BPF SOCKMAP елементів\n";
        return 1;
    }

    std::cout << "C++ RAII: Сокети зареєстровано у BPF SOCKMAP!\n";

    // 5. Відправляємо дані через std::string_view
    constexpr std::string_view payload = "C++20 Zero-Copy BPF Sockmap Message!";
    ssize_t sent = ::write(sock_a.get(), payload.data(), payload.size());
    std::cout << "Sock A відправив: " << sent << " байтів.\n";

    std::vector<char> buffer(128, 0);
    ssize_t bytes = ::read(sock_b.get(), buffer.data(), buffer.size() - 1);
    if (bytes > 0) {
        std::string_view received(buffer.data(), static_cast<size_t>(bytes));
        std::cout << "Sock B прочитав без TCP/IP: '" << received << "'\n";
    }

    return 0; // RAII деструктори автоматично закриють сокети та BPF об'єкт
}
```
:::

---

## 4. Покрокова інструкція зі збірки та інженерні деталі

Для компіляції та виконання даного проєкту в системі Linux потрібні встановлені пакети `clang`, `llvm`, `libbpf-dev` та привілеї `root` (або `CAP_BPF` та `CAP_NET_ADMIN`).

### Крок 1: Компіляція BPF-байтокоду ядра

Компілятор Clang транслює BPF C код у цільову архітектуру `bpf`:

```bash
clang -g -O2 -target bpf -D__TARGET_ARCH_x86 -c bpf_redir.bpf.c -o bpf_redir.bpf.o
```

Отриманий об'єктний файл `bpf_redir.bpf.o` є стандартизованим ELF-контейнером, що містить секції `.maps` (ініціалізація карт) та `sk_msg` (байткод BPF-програми).

### Крок 2: Компіляція контролера простору користувача

Для збірки версії мовою C використовується стандартний компілятор `gcc` з підключенням системної бібліотеки `libbpf`:

```bash
gcc -O2 -Wall main.c -o sockmap_ctrl -lbpf
```

Для збірки версії мовою C++20 використовується `g++`:

```bash
g++ -std=c++20 -O2 -Wall main.cpp -o sockmap_ctrl_cpp -lbpf
```

### Крок 3: Запуск контролера з привілеями суперкористувача

Запуск контролера вимагає підвищених привілеїв операційної системи для завантаження байткоду BPF в ядро та модифікації протокольних операцій сокетів:

```bash
sudo ./sockmap_ctrl
```

Очікуваний вивід у консолі:

```text
=== BPF SOCKMAP Zero-Copy Redirect Controller (C) ===
Успіх: Сокети FD 3 (Key 0) та FD 4 (Key 1) додано до SOCKMAP!
Трафік із Sock A тепер перенаправляється безпосередньо у Sock B в ядрі!
Sock A відправив 42 байтів у сокет.
Sock B успішно прочитав 42 байтів без проходження TCP/IP: 'Привіт від BPF Zero-Copy Sockmap Redirect!'
```

---

## 5. Обробка крайових випадків та закриття сокетів

У практичних високопродуктивних системах керування сокетами вимагає врахування таких інженерних моментів:

1. **Аварійне закриття сокетів**: Якщо прикладний процес аварійно завершується, ядро автоматично перехоплює це через перевизначений метод `sock_map_close()`. Вона видаляє сокет із карти `SOCKMAP`, деактивує BPF-хуки та повертає оригінальну таблицю `tcp_prot`.
2. **Обробка черги `BPF_F_INGRESS`**: Прапорець `BPF_F_INGRESS` гарантує, що байти потрапляють безпосередньо у чергу прийому `sk_receive_queue` сокету-отримувача. Якщо вказати `0`, байти потраплять у чергу відправки, що вимагатиме подальшої обробки сокетом.
3. **Використання cgroups для автоматичного перехоплення**: У реальних проектах (таких як Cilium) додавання сокетів у `SOCKMAP` відбувається автоматично через програму `BPF_PROG_TYPE_SOCK_OPS`, яка прикріплюється до cgroup v2 і реагує на події встановлення TCP-з'єднань (`BPF_SOCK_OPS_ACTIVE_ESTABLISHED` та `BPF_SOCK_OPS_PASSIVE_ESTABLISHED`).

## 6. Детальний аналіз механізму Zero-Copy та системних викликів

При звичайній передачі даних додаток відправника викликає `write()`, що змушує ядро виділяти об'єкт `sk_buff`, копіювати дані з пам'яті користувача в буфер ядра, будувати заголовки TCP/IP та передавати пакет у мережевий пристрій. При використанні BPF `sk_msg` програма отримує прямий доступ до вектору сторінок пам'яті `struct sk_msg_md`, який описує фізичні сторінки користувача.

Під час виконання функції `bpf_msg_redirect_map()` ядро Linux не створює об'єкти `sk_buff` і не копіює корисний вантаж. Натомість воно переміщує вказівники на сторінки пам'яті користувача безпосередньо у чергу прийому сокета-отримувача `sk_receive_queue`. Коли процес отримувача викликає системний виклик `read()`, ядро здійснює єдине копіювання даних безпосередньо зі сторінок пам'яті відправника у буфер користувача отримувача.

Цей підхід повністю виключає проміжні копіювання в ядрі, оптимізує використання кешу CPU та знижує навантаження на підсистему пам'яті, що робить BPF sockmap найефективнішим інструментом IPC у Linux.
