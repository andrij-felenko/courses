# ⚙️ Спільне використання eBPF-мапи через bpffs між незалежними процесами

Даний практичний проект демонструє реалізацію механізму міжпроцесної взаємодії та збереження стану у просторі ядра Linux за допомогою фіксації eBPF-мап у віртуальній файловій системі `bpffs`.

Архітектура проекту складається з двох повністю автономних програм простору користувача, які не мають спільної пам'яті (shared memory IPC), не пов'язані відносинами батьківство-нащадок (`fork()`) і не використовують керувальні сокети IPC для передачі файлових дескрипторів:

1. **Програма-Виробник (Producer):** Виконує виклик `bpf_map_create()`, створюючи хеш-мапу типу `BPF_MAP_TYPE_HASH` у пам'яті ядра. Після цього за допомогою `bpf_obj_pin()` мапа фіксується за шляхом `/sys/fs/bpf/shared_stats_map`. Виробник записує початкові метрики, закриває свій файловий дескриптор та завершує виконання.
2. **Програма-Споживач (Consumer):** Запускається пізніше (або в окремому контейнері). Вона виконує виклик `bpf_obj_get()`, запитуючи дескриптор за зафіксованим шляхом `/sys/fs/bpf/shared_stats_map`. Отримавши власний дескриптор, Споживач зчитує записані Виробником дані, здійснює їхню модифікацію та виводить оновлені значення.

---

## Передумови, компіляція та запуск проекту

Для збірки та запуску проектів потрібні встановлені заголовки ядра Linux, компілятори `gcc` і `g++` (з підтримкою C++20), а також бібліотека `libbpf` (`libbpf-dev` у Ubuntu/Debian або `libbpf-devel` у Fedora/RHEL).

Компіляція здійснюється наступними командами:

```bash
# Збірка версії мовою C
gcc -Wall -O2 producer.c -o producer -lbpf
gcc -Wall -O2 consumer.c -o consumer -lbpf

# Збірка версії мовою C++20
g++ -std=c++20 -Wall -O2 producer.cpp -o producer_cpp -lbpf
g++ -std=c++20 -Wall -O2 consumer.cpp -o consumer_cpp -lbpf
```

Оскільки за замовчуванням точка монтування `/sys/fs/bpf` має права `0700` і належить `root`, запуск програм вимагає привілеїв суперкористувача або наявності капабіліті `CAP_BPF` та `CAP_SYS_ADMIN`:

```bash
# 1. Запуск виробника C++
sudo ./producer_cpp

# 2. Перевірка наявності файла у bpffs
ls -l /sys/fs/bpf/shared_stats_map

# 3. Запуск споживача C++
sudo ./consumer_cpp
```

---

## Вихідний код та реалізація програм

Нижче наведено паралельні реалізації обох компонентів мовами C та C++. Реалізація мовою C++ базується на ідіомі RAII (англ. *Resource Acquisition Is Initialization*) для автоматичного закриття файлових дескрипторів та стандартних винятках `std::system_error` для обробки помилок системних викликів.

### Програма 1: Створення, фіксація та запис у мапу (Producer)

:::tabs
```c
/* producer.c — Створення eBPF-мапи та її фіксація у bpffs */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <bpf/bpf.h>
#include <bpf/libbpf.h>

#define PIN_PATH "/sys/fs/bpf/shared_stats_map"

int main(void) {
    uint32_t key = 42;
    uint64_t initial_value = 1000;

    /* Створення eBPF-мапи HASH: ключ 4 байти, значення 8 байтів, макс 1024 елементи */
    int map_fd = bpf_map_create(BPF_MAP_TYPE_HASH, "shared_stats", sizeof(key), sizeof(initial_value), 1024, NULL);
    if (map_fd < 0) {
        fprintf(stderr, "Помилка створення eBPF мапи: %s\n", strerror(errno));
        return EXIT_FAILURE;
    }

    /* Якщо раніше створена мапа вже існує у bpffs, видаляємо її перед фіксацією */
    unlink(PIN_PATH);

    /* Фіксація мапи у bpffs */
    if (bpf_obj_pin(map_fd, PIN_PATH) < 0) {
        fprintf(stderr, "Помилка фіксації мапи у %s: %s\n", PIN_PATH, strerror(errno));
        close(map_fd);
        return EXIT_FAILURE;
    }

    printf("[Producer] Мапу успішно створено та зафіксовано у %s\n", PIN_PATH);

    /* Запис початкового значення */
    if (bpf_map_update_elem(map_fd, &key, &initial_value, BPF_ANY) < 0) {
        fprintf(stderr, "Помилка запису в мапу: %s\n", strerror(errno));
        bpf_obj_unpin(map_fd, PIN_PATH);
        close(map_fd);
        return EXIT_FAILURE;
    }

    printf("[Producer] Записано ключ %u зі значенням %lu. Закриваємо FD та виходимо.\n", key, initial_value);
    
    /* Закриваємо FD. Мапа не знищується, бо вона зафіксована у bpffs! */
    close(map_fd);
    return EXIT_SUCCESS;
}
```
```cpp
// producer.cpp — Ідіоматичний C++20 варіант створення та фіксації eBPF-мапи
#include <iostream>
#include <string_view>
#include <system_error>
#include <cstdint>
#include <unistd.h>
#include <bpf/bpf.h>
#include <bpf/libbpf.h>

namespace ebpf {

class AutoFd {
public:
    explicit AutoFd(int fd = -1) noexcept : fd_(fd) {}
    ~AutoFd() { reset(); }

    AutoFd(const AutoFd&) = delete;
    AutoFd& operator=(const AutoFd&) = delete;

    AutoFd(AutoFd&& other) noexcept : fd_(other.release()) {}
    AutoFd& operator=(AutoFd&& other) noexcept {
        if (this != &other) {
            reset(other.release());
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

    int release() noexcept {
        int old = fd_;
        fd_ = -1;
        return old;
    }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }

private:
    int fd_{-1};
};

} // namespace ebpf

constexpr std::string_view kPinPath = "/sys/fs/bpf/shared_stats_map";

int main() {
    constexpr uint32_t key = 42;
    constexpr uint64_t initial_value = 1000;

    int raw_fd = ::bpf_map_create(BPF_MAP_TYPE_HASH, "shared_stats", sizeof(key), sizeof(initial_value), 1024, nullptr);
    if (raw_fd < 0) {
        std::cerr << "Помилка створення eBPF мапи: " 
                  << std::system_error(errno, std::generic_category()).what() << '\n';
        return EXIT_FAILURE;
    }

    ebpf::AutoFd map_fd(raw_fd);

    ::unlink(kPinPath.data());

    if (::bpf_obj_pin(map_fd.get(), kPinPath.data()) < 0) {
        std::cerr << "Помилка фіксації мапи: " 
                  << std::system_error(errno, std::generic_category()).what() << '\n';
        return EXIT_FAILURE;
    }

    std::cout << "[Producer C++] Мапу зафіксовано за шляхом " << kPinPath << '\n';

    if (::bpf_map_update_elem(map_fd.get(), &key, &initial_value, BPF_ANY) < 0) {
        std::cerr << "Помилка оновлення елемента: " 
                  << std::system_error(errno, std::generic_category()).what() << '\n';
        return EXIT_FAILURE;
    }

    std::cout << "[Producer C++] Успішно записано ключ " << key 
              << " зі значенням " << initial_value << ". Вихід (RAII закриє FD).\n";

    return EXIT_SUCCESS;
}
```
:::

---

### Програма 2: Отримання зафіксованої мапи та читання даних (Consumer)

:::tabs
```c
/* consumer.c — Відкриття зафіксованої у bpffs мапи та зчитування даних */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <bpf/bpf.h>

#define PIN_PATH "/sys/fs/bpf/shared_stats_map"

int main(void) {
    uint32_t key = 42;
    uint64_t value = 0;

    /* Отримання FD зафіксованої у bpffs мапи */
    int map_fd = bpf_obj_get(PIN_PATH);
    if (map_fd < 0) {
        fprintf(stderr, "Помилка отримання мапи з %s: %s\n", PIN_PATH, strerror(errno));
        return EXIT_FAILURE;
    }

    printf("[Consumer] Успішно отримано FD %d з %s\n", map_fd, PIN_PATH);

    /* Пошук значення за ключем */
    if (bpf_map_lookup_elem(map_fd, &key, &value) < 0) {
        fprintf(stderr, "Помилка зчитування елемента з ключем %u: %s\n", key, strerror(errno));
        close(map_fd);
        return EXIT_FAILURE;
    }

    printf("[Consumer] Прочитано з зафіксованої мапи: ключ %u -> значення %lu\n", key, value);

    /* Інкремент значення у спільній мапі */
    value += 500;
    if (bpf_map_update_elem(map_fd, &key, &value, BPF_EXIST) < 0) {
        fprintf(stderr, "Помилка оновлення значення: %s\n", strerror(errno));
        close(map_fd);
        return EXIT_FAILURE;
    }

    printf("[Consumer] Нове значення для ключа %u успішно оновлено на %lu\n", key, value);

    close(map_fd);
    return EXIT_SUCCESS;
}
```
```cpp
// consumer.cpp — Ідіоматичний C++20 варіант отримання та читання зафіксованої мапи
#include <iostream>
#include <string_view>
#include <system_error>
#include <cstdint>
#include <unistd.h>
#include <bpf/bpf.h>

namespace ebpf {

class AutoFd {
public:
    explicit AutoFd(int fd = -1) noexcept : fd_(fd) {}
    ~AutoFd() { reset(); }

    AutoFd(const AutoFd&) = delete;
    AutoFd& operator=(const AutoFd&) = delete;

    AutoFd(AutoFd&& other) noexcept : fd_(other.release()) {}
    AutoFd& operator=(AutoFd&& other) noexcept {
        if (this != &other) {
            reset(other.release());
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

    int release() noexcept {
        int old = fd_;
        fd_ = -1;
        return old;
    }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }

private:
    int fd_{-1};
};

} // namespace ebpf

constexpr std::string_view kPinPath = "/sys/fs/bpf/shared_stats_map";

int main() {
    constexpr uint32_t key = 42;
    uint64_t value = 0;

    int raw_fd = ::bpf_obj_get(kPinPath.data());
    if (raw_fd < 0) {
        std::cerr << "Помилка відкриття " << kPinPath << ": " 
                  << std::system_error(errno, std::generic_category()).what() << '\n';
        return EXIT_FAILURE;
    }

    ebpf::AutoFd map_fd(raw_fd);

    std::cout << "[Consumer C++] Успішно отримано дескриптор мапи (FD " << map_fd.get() << ")\n";

    if (::bpf_map_lookup_elem(map_fd.get(), &key, &value) < 0) {
        std::cerr << "Помилка пошуку ключа " << key << ": "
                  << std::system_error(errno, std::generic_category()).what() << '\n';
        return EXIT_FAILURE;
    }

    std::cout << "[Consumer C++] Прочитане значення для ключа " << key << ": " << value << '\n';

    value += 500;
    if (::bpf_map_update_elem(map_fd.get(), &key, &value, BPF_EXIST) < 0) {
        std::cerr << "Помилка запису нового значення: "
                  << std::system_error(errno, std::generic_category()).what() << '\n';
        return EXIT_FAILURE;
    }

    std::cout << "[Consumer C++] Нове оновлене значення: " << value << '\n';

    return EXIT_SUCCESS;
}
```
:::

---

## Детальний розбір механізму виконання та роботи з ресурсами

Аналіз поведінки системи під час послідовного виконання двох програм розкриває важливі особливості управління пам'яттю ядра Linux:

### 1. Етап створення мапи та фіксації у Виробнику

Виклик `bpf_map_create()` повертає ціле число `map_fd` (наприклад, `3`). У цей момент у ядра створено об'єкт `struct bpf_map` із лічильником посилань `refcnt = 1`.

Далі програма викликає `bpf_obj_pin(3, "/sys/fs/bpf/shared_stats_map")`. Драйвер `bpffs` створює VFS-інод у пам'яті за цією адресою і збільшує `refcnt` об'єкта до `2`.

Після запису ключа 42 зі значенням 1000 Виробник виконує `close(map_fd)` (у C++ це робить деструктор `AutoFd`). Таблиця `files_struct` Виробника більше не містить дескриптора `3`. Лічильник `refcnt` зменшується з `2` до `1`.

Оскільки `refcnt == 1` (завдяки VFS-іноду у `bpffs`), ядро **не викликає** деструктор звільнення пам'яті. Виробник повністю завершує роботу і зникає зі списку процесів (`ps aux`), але створена ним мапа продовжує жити у пам'яті ядра!

### 2. Етап відновлення та модифікації у Споживачі

Споживач запускається як абсолютно новий процес із новим PID. Він не має жодних успадкованих дескрипторів від Виробника.

Споживач викликає `bpf_obj_get("/sys/fs/bpf/shared_stats_map")`. Ядро резолвить шлях у VFS, перевіряє права доступу інода, зчитує покажчик `i_private`, виділяє новий дескриптор (наприклад, `fd = 3` у таблиці Споживача) та збільшує `refcnt` мапи з `1` до `2`.

Функція `bpf_map_lookup_elem()` знаходить записаний Виробником ключ `42` і повертає значення `1000`. Споживач збільшує його на 500 (`1500`) і викликає `bpf_map_update_elem()`. Оскільки обидва процеси працювали з однією і тією ж мапою у пам'яті ядра, ці зміни миттєво зберігаються у структурі `bpf_map`.

При виході Споживача його дескриптор закривається, і `refcnt` знову повертається до значення `1`.

---

## Простеження виконання трасувальником strace

Простежити послідовність системних викликів при виконанні Виробника можна командою `strace`:

```bash
sudo strace -e bpf,openat,close,unlink ./producer
```

У логу трасування буде видно чіткий ланцюжок системних викликів:

```text
bpf(BPF_MAP_CREATE, {map_type=BPF_MAP_TYPE_HASH, key_size=4, value_size=8, max_entries=1024, map_name="shared_stats"}, 128) = 3
unlink("/sys/fs/bpf/shared_stats_map") = -1 ENOENT (No such file or directory)
bpf(BPF_OBJ_PIN, {pathname="/sys/fs/bpf/shared_stats_map", bpf_fd=3}, 128) = 0
bpf(BPF_MAP_UPDATE_ELEM, {map_fd=3, key=0x7ffe..., value=0x7ffe..., flags=BPF_ANY}, 128) = 0
close(3) = 0
```

Цей трасирувальний лог підтверджує, що для фіксації та оновлення мапи використовується один і той самий системний виклик `bpf()` із різними значеннями першого аргументу `cmd`.

---

## Обробка крайових випадків та відмов у доступі

При розробці системних сервісів на основі фіксованих мап необхідно враховувати три основні крайові випадки:

1. **Конфлікт існуючого файла (EEXIST):** Якщо програма-Виробник не виконує `unlink()` перед фіксацією, виклик `bpf_obj_pin()` повертає помилку `EEXIST`. Для вирішення цієї ситуації програма повинна або спочатку перевіряти наявність мапи через `bpf_obj_get()`, або примусово видаляти застарілий інод через `unlink()`.
2. **Відсутність VFS-прав доступу (EACCES):** Якщо точку монтування `/sys/fs/bpf` змонтовано з опцією `mode=0700`, а Споживач виконується від непривілейованого користувача `nobody`, виклик `bpf_obj_get()` зазнає невдачі з помилкою `EACCES` ще на етапі перевірки VFS-прав доступу до директорії.
3. **Зміна схеми даних при оновленні версії:** Якщо Виробник оновився і створив мапу із розміром значення `sizeof(value) = 16`, а застарілий Споживач очікує значення розміром `8` байтів, виклик `bpf_map_lookup_elem()` поверне помилку `EINVAL` або призведе до пошкодження пам'яті у просторі користувача. Рекомендується додавати версіонування у назву файла (наприклад, `/sys/fs/bpf/shared_stats_v2`).

---

## Інспекція за допомогою системної утиліти bpftool

Перевірити статус зафіксованої мапи та переглянути її контент можна безпосередньо через системну утиліту `bpftool`:

```bash
# 1. Список усіх мап у ядрі з відображенням зафіксованих шляхів
sudo bpftool map list

# Приклад виводу:
# 42: hash  name shared_stats  flags 0x0
#     key 4B  value 8B  max_entries 1024  memlock 89344B
#     pinned /sys/fs/bpf/shared_stats_map

# 2. Дамп усього вмісту зафіксованої мапи
sudo bpftool map dump pinned /sys/fs/bpf/shared_stats_map

# Приклад виводу:
# key: 2a 00 00 00  value: dc 05 00 00 00 00 00 00
# Found 1 element
```

Значення `dc 05 00 00 00 00 00 00` у шістнадцятковому форматі little-endian відповідає десятковому числу `1500` (`0x05dc`), що підтверджує успішне виконання модифікації Споживачем.

---

## Остаточне видалення мапи (Unpinning)

Для знищення мапи та звільнення пам'яті ядра потрібно видалити зафіксований файл за допомогою виклику `unlink()` або CLI-команди `rm`:

```bash
sudo rm /sys/fs/bpf/shared_stats_map
```

Видалення файла знищує VFS-інод у `bpffs` та зменшує `refcnt` мапи до `0`. Підсистема BPF негайно поміщає об'єкт у чергу RCU-звільнення, і після завершення спокійного періоду пам'яті мапа остаточно вивільняється ядрами ЦП.
