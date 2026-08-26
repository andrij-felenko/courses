# 📋 Інтерфейси ядра Linux: тиск пам'яті, PSI та лічильники робочої множини

Керування пам'яттю та моніторинг робочої множини в ядрі Linux спираються на набір інтерфейсів системних викликів, віртуальних файлових систем `procfs` та `cgroupfs`. Ці інтерфейси забезпечують спостереження за напруженістю дефіциту кадрів і дозволяють процесам простору користувача вчасно реагувати на деградацію продуктивності до спрацювання механізму аварійного завершення (OOM Killer).

Нижче наведено специфікацію ключових точок взаємодії, форматів даних та інваріантів підсистеми керування пам'яттю.

## 1. Метрики тиску на ресурси: PSI (/proc/pressure/memory)

Інтерфейс **Pressure Stall Information (PSI)** оцінює частку процесорного часу, втраченого через очікування звільнення пам'яті, підкачування сторінок або обробку сторінкових збоїв.

### Формат файлу `/proc/pressure/memory`

Файл містить два рядки агрегованої статистики:

```
some avg10=0.00 avg60=0.00 avg300=0.00 total=0
full avg10=0.00 avg60=0.00 avg300=0.00 total=0
```

- **`some`:** Частка часу (у відсотках), протягом якого *принаймні один* активний потік виконання був заблокований в очікуванні пам'яті (наприклад, виконання прямого вивільнення сторінок або зчитування даних зі свопу), тоді як інші потоки могли виконувати корисну роботу на CPU.
- **`full`:** Частка часу, протягом якого *усі* активні потоки виконання системи були одночасно заблоковані на операціях пам'яті. У цьому стані процесор простоює без корисної роботи (пряма ознака трішингу).
- **`avg10`, `avg60`, `avg300`:** Експоненційно зважені ковзні середні за останні 10, 60 та 300 секунд відповідно.
- **`total`:** Сумарний абсолютний час простою потоків у мікросекундах від моменту завантаження системи.

### Асинхронне спостереження за порогом тиску (PSI Triggers)

Процес простору користувача може зареєструвати тригер, який генерує подію готовності для `epoll()` або `poll()`, коли рівень тиску перевищує заданий поріг за вказане вікно спостереження.

**Синтаксис рядка конфігурації тригера:**
`"<some|full> <поріг_мкс> <вікно_мкс>"`

- Приклад: `"some 150000 1000000"` генерує подію, якщо сумарний час очікування пам'яті перевищує 150 мс (15%) протягом ковзного вікна в 1 секунду (1 000 000 мкс).

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/epoll.h>
#include <errno.h>

/*
 * Реєстрація та очікування сповіщення про перевантаження пам'яті через PSI.
 */
int main(void) {
    const char *psi_path = "/proc/pressure/memory";
    int psi_fd = open(psi_path, O_RDWR | O_NONBLOCK);
    if (psi_fd < 0) {
        perror("Не вдалося відкрити /proc/pressure/memory");
        return EXIT_FAILURE;
    }

    /* Налаштування тригера: 100 мс простою у вікні 1 с */
    const char *trigger_spec = "some 100000 1000000";
    if (write(psi_fd, trigger_spec, strlen(trigger_spec)) < 0) {
        perror("Не вдалося записати тригер у PSI");
        close(psi_fd);
        return EXIT_FAILURE;
    }

    int epoll_fd = epoll_create1(0);
    if (epoll_fd < 0) {
        perror("epoll_create1 failed");
        close(psi_fd);
        return EXIT_FAILURE;
    }

    struct epoll_event ev;
    ev.events = EPOLLPRI; /* PSI генерує подію виняткового стану EPOLLPRI */
    ev.data.fd = psi_fd;

    if (epoll_ctl(epoll_fd, EPOLL_CTL_ADD, psi_fd, &ev) < 0) {
        perror("epoll_ctl failed");
        close(psi_fd);
        close(epoll_fd);
        return EXIT_FAILURE;
    }

    printf("Очікування подій Memory Pressure через PSI (поріг 10%% за 1 с)...\n");

    struct epoll_event events[1];
    int n = epoll_wait(epoll_fd, events, 1, 10000); /* Таймаут 10 секунд */

    if (n < 0) {
        perror("epoll_wait failed");
    } else if (n == 0) {
        printf("За 10 секунд поріг тиску пам'яті не перевищено (система стабільна).\n");
    } else {
        if (events[0].events & EPOLLPRI) {
            printf("УВАГА: Зафіксовано високий рівень тиску на пам'ять! Потрібне скидання кешів.\n");
        }
    }

    close(psi_fd);
    close(epoll_fd);
    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <system_error>
#include <fcntl.h>
#include <unistd.h>
#include <sys/epoll.h>

class PsiMemoryMonitor {
public:
    PsiMemoryMonitor(std::string_view trigger_spec = "some 100000 1000000") {
        psi_fd_ = ::open("/proc/pressure/memory", O_RDWR | O_NONBLOCK);
        if (psi_fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "open(/proc/pressure/memory) failed");
        }

        if (::write(psi_fd_, trigger_spec.data(), trigger_spec.size()) < 0) {
            ::close(psi_fd_);
            throw std::system_error(errno, std::generic_category(), "write PSI trigger failed");
        }

        epoll_fd_ = ::epoll_create1(0);
        if (epoll_fd_ < 0) {
            ::close(psi_fd_);
            throw std::system_error(errno, std::generic_category(), "epoll_create1 failed");
        }

        struct epoll_event ev{};
        ev.events = EPOLLPRI;
        ev.data.fd = psi_fd_;

        if (::epoll_ctl(epoll_fd_, EPOLL_CTL_ADD, psi_fd_, &ev) < 0) {
            ::close(psi_fd_);
            ::close(epoll_fd_);
            throw std::system_error(errno, std::generic_category(), "epoll_ctl failed");
        }
    }

    ~PsiMemoryMonitor() noexcept {
        if (psi_fd_ >= 0) ::close(psi_fd_);
        if (epoll_fd_ >= 0) ::close(epoll_fd_);
    }

    PsiMemoryMonitor(const PsiMemoryMonitor&) = delete;
    PsiMemoryMonitor& operator=(const PsiMemoryMonitor&) = delete;

    [[nodiscard]] bool wait_event(int timeout_ms = 5000) {
        struct epoll_event events[1];
        int nfds = ::epoll_wait(epoll_fd_, events, 1, timeout_ms);
        if (nfds < 0) {
            throw std::system_error(errno, std::generic_category(), "epoll_wait failed");
        }
        return (nfds > 0 && (events[0].events & EPOLLPRI));
    }

private:
    int psi_fd_{-1};
    int epoll_fd_{-1};
};

int main() {
    try {
        std::cout << "Ініціалізація C++ PSI монітора пам'яті...\n";
        PsiMemoryMonitor monitor("some 100000 1000000");

        std::cout << "Очікування сплеску навантаження (таймаут 10 с)...\n";
        bool triggered = monitor.wait_event(10000);

        if (triggered) {
            std::cout << "ПОПЕРЕДЖЕННЯ: Тиск на оперативну пам'ять перевищив 10%!\n";
        } else {
            std::cout << "Тиск у нормі: система працює без значних затримок пам'яті.\n";
        }
    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << "\n";
        return 1;
    }
    return 0;
}
```
:::

## 2. Керування робочою множиною в Control Groups v2

У сучасній архітектурі Linux кожна контрольна група (cgroup v2) забезпечує ізоляцію та лімітування робочих множин для набору процесів.

| Файл у cgroup v2 | Призначення та поведінка |
|---|---|
| `memory.current` | Поточний загальний обсяг пам'яті (у байтах), зайнятий процесами контрольної групи (анонімна пам'ять + кеш сторінок + структури ядра). |
| `memory.min` | Жорсткий захищений мінімум. Ядро за жодних умов дефіциту пам'яті не вилучає сторінки cgroup, якщо споживання нижче цього порогу. |
| `memory.low` | М'який захищений рівень (Best-effort). Ядро витісняє сторінки лише тоді, коли не може знайти вільних кадрів у незахищених групах. |
| `memory.high` | Пороговий рівень навантаження. При його перевищенні процеси контрольної групи штучно сповільнюються (throttling) на операціях алокації, а ядро запускає інтенсивний фоновий реклейм. |
| `memory.max` | Абсолютна стеля пам'яті. Перевищення призводить до блокування викликів виділення пам'яті для проведення прямого вивільнення (Direct Reclaim); якщо пам'ять звільнити не вдається — запускається OOM Killer. |
| `memory.events` | Лічильники подій перевищення порогів: `low`, `high`, `max`, `oom`, `oom_kill`, `oom_group_kill`. |
| `memory.pressure` | Показники PSI, обчислені суто для процесів цієї контрольної групи. |

### Лічильники робочої множини у `memory.stat`

Файл `memory.stat` надає статистику алгоритму **Refault Distance** (`mm/workingset.c`):

- **`workingset_refault_anon`:** Кількість повторних сторінкових збоїв для вивантажених анонімних сторінок.
- **`workingset_refault_file`:** Кількість повторних сторінкових збоїв для витіснених сторінок файлового кешу.
- **`workingset_activate_anon` / `workingset_activate_file`:** Кількість сторінок, які під час повторного збою були визнані частиною активної робочої множини (оскільки `refault_distance ≤ active_list_size`) і переміщені безпосередньо у список `Active LRU`.
- **`workingset_restore_anon` / `workingset_restore_file`:** Сторінки, відновлені в пам'яті до того, як їхні тіньові дескриптори (shadow entries) були витіснені з дерева xarray.
- **`workingset_nodereclaim`:** Кількість випадків, коли реклейм сторінок не зміг знайти кандидатів на вивільнення у відповідному вузлі NUMA.

## 3. Системний виклик madvise() та керування локальністю

Системний виклик `madvise()` дозволяє процесу явно передати ядру інформацію про очікуваний патерн звернення до робочої множини для конкретного діапазону віртуальних адрес.

### Прапорці оптимізації робочої множини:

- **`MADV_WILLNEED`:** Ядро ініціює випереджальне неблокуюче завантаження сторінок діапазону у фізичну пам'ять (Pre-faulting). Зменшує латентність наступних звернень за рахунок розширення поточної резидентної множини.
- **`MADV_DONTNEED`:** Сповіщає ядро, що дані діапазону більше не потрібні. Для анонімних сторінок пам'ять негайно звільняється (при наступному читанні повертаються нулі); для файлових відображень сторінки вивільняються з кешу.
- **`MADV_COLD` (з Linux 5.4):** Переміщує сторінки діапазону на початок списку `Inactive LRU`. Сторінки залишаються в пам'яті, але у разі виникнення дефіциту вони будуть витіснені першими без додаткового сканування.
- **`MADV_PAGEOUT` (з Linux 5.4):** Ініціює негайне асинхронне вивантаження сторінок діапазону на диск або у своп, звільняючи фізичні кадри для інших процесів.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <unistd.h>
#include <string.h>

#define BUFFER_SIZE (16 * 1024 * 1024) /* 16 МБ */

/*
 * Демонстрація оптимізації робочої множини через madvise().
 */
int main(void) {
    char *buf = (char *)mmap(NULL, BUFFER_SIZE, PROT_READ | PROT_WRITE,
                             MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (buf == MAP_FAILED) {
        perror("mmap failed");
        return EXIT_FAILURE;
    }

    /* Заповнюємо дані (всі сторінки стають резидентними) */
    memset(buf, 0xAB, BUFFER_SIZE);
    printf("16 МБ пам'яті алоковано та заповнено даними.\n");

    /* Фаза 1: Позначаємо сторінки як холодні (MADV_COLD) */
    if (madvise(buf, BUFFER_SIZE, MADV_COLD) == 0) {
        printf("Сторінки позначено як MADV_COLD (демоція у список Inactive LRU).\n");
    }

    /* Фаза 2: Звільняємо непотрібний діапазон без munmap (MADV_DONTNEED) */
    if (madvise(buf, BUFFER_SIZE, MADV_DONTNEED) == 0) {
        printf("Діапазон скинуто через MADV_DONTNEED (фізичні кадри повернено ядру).\n");
    }

    munmap(buf, BUFFER_SIZE);
    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <vector>
#include <sys/mman.h>
#include <unistd.h>
#include <cstring>
#include <system_error>

class ManagedBuffer {
public:
    explicit ManagedBuffer(size_t size) : size_(size) {
        void* ptr = ::mmap(nullptr, size_, PROT_READ | PROT_WRITE,
                           MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
        if (ptr == MAP_FAILED) {
            throw std::system_error(errno, std::generic_category(), "mmap failed");
        }
        data_ = static_cast<std::byte*>(ptr);
    }

    ~ManagedBuffer() noexcept {
        if (data_ != nullptr) {
            ::munmap(data_, size_);
        }
    }

    void mark_cold() const {
        if (::madvise(data_, size_, MADV_COLD) != 0) {
            throw std::system_error(errno, std::generic_category(), "madvise(MADV_COLD) failed");
        }
    }

    void discard_pages() const {
        if (::madvise(data_, size_, MADV_DONTNEED) != 0) {
            throw std::system_error(errno, std::generic_category(), "madvise(MADV_DONTNEED) failed");
        }
    }

    [[nodiscard]] std::byte* data() noexcept { return data_; }
    [[nodiscard]] size_t size() const noexcept { return size_; }

private:
    std::byte* data_{nullptr};
    size_t size_{0};
};

int main() {
    constexpr size_t buffer_size = 16 * 1024 * 1024; // 16 МБ

    try {
        ManagedBuffer buffer(buffer_size);
        std::memset(buffer.data(), 0xAB, buffer.size());
        std::cout << "16 МБ пам'яті ініціалізовано.\n";

        buffer.mark_cold();
        std::cout << "MADV_COLD успішно застосовано через C++ RAII обгортку.\n";

        buffer.discard_pages();
        std::cout << "MADV_DONTNEED успішно вивільнив фізичні кадри.\n";

    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << "\n";
        return 1;
    }
    return 0;
}
```
:::

## 4. Конфігурація захисту процесу від OOM Killer

Ядро призначає кожному процесу числову оцінку схильності до аварійного завершення (`oom_score`), яка варіюється від `0` (найменш вірогідна жертва) до `1000` (першочерговий кандидат на `SIGKILL`).

- **`/proc/[pid]/oom_score`:** Поточна оцінка процесу, що динамічно обчислюється ядром на основі частки споживаної оперативної пам'яті від загального обсягу RAM.
- **`/proc/[pid]/oom_score_adj`:** Значення коригування від `-1000` до `+1000`.
  - Значення `-1000` повністю вимикає OOM Killer для цього процесу (використовується для `systemd`, `sshd`, критичних баз даних).
  - Додатні значення (наприклад, `+500`) збільшують вірогідність завершення фонових задач без впливу на основний сервіс.

## 5. Інтерфейси Multi-Gen LRU (/sys/kernel/mm/lru_gen)

Починаючи з версії ядра Linux 6.1, підсистема керування пам'яттю підтримує архітектуру **Multi-Gen LRU (MGLRU)**, яка замінює традиційні подвійні списки Active/Inactive ієрархією генерацій віку сторінок (від 0 до `MAX_NR_GENS - 1`).

- **`/sys/kernel/mm/lru_gen/enabled`:** Бітова маска активації функцій MGLRU:
  - `0x0001`: Активація багатогенераційного сканування для кешу сторінок та анонімної пам'яті.
  - `0x0002`: Активація сканування таблиць сторінок через MMU accessed-біти під час оцінки віку.
  - `0x0004`: Активація оптимізації очищення кешу для вторинних NUMA вузлів.
- **`/sys/kernel/mm/lru_gen/min_ttl_ms`:** Мінімальний час життя генерації у мілісекундах. Запобігає надмірній частоті ротації генерацій при пікових сплесках короткочасних звернень, утримуючи стабільну оцінку розміру робочої множини.

## 6. Глобальні параметри sysctl для тюнінгу пам'яті

Налаштування файлів у `/proc/sys/vm/` керують поведінкою фонового демона `kswapd` та балансом між файловими й анонімними сторінками:

- **`vm.swappiness` (від 0 до 200, за замовчуванням 60):** Задає відносний пріоритет витіснення анонімної пам'яті у простір підкачки порівняно зі скиданням файлових кешів. Значення `0` мінімізує використання свопу до критичних станів; значення `100` надає рівний пріоритет; значення `>100` змушує ядро агресивно звільняти анонімні сторінки для утримання файлового кешу.
- **`vm.vfs_cache_pressure` (за замовчуванням 100):** Регулює схильність ядра вивільняти з пам'яті структури кешу метаданих VFS (dentry та inode). Збільшення понад 100 змушує ядро агресивніше повертати пам'ять, зайняту шляхами файлів.
- **`vm.watermark_scale_factor` (від 1 до 3000, за замовчуванням 10 = 0.1% пам'яті):** Визначає відстань між водяними знаками `WMARK_MIN`, `WMARK_LOW` та `WMARK_HIGH`. Збільшення параметра змушує `kswapd` прокидатися раніше, запобігаючи переходу процесів у прямий реклейм (Direct Reclaim) на сплесках виділення пам'яті.
