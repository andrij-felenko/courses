# ⚙️ Практична реалізація фіксації затримок через PM QoS та керування P-станами у користувацькому просторі

Налаштування параметрів живлення та затримок процесора у користувацькому просторі є критично важливим завданням при розробці систем реального часу (Real-Time Linux), високонавантажених мережевих обробників та алгоритмів високочастотної торгівлі (HFT). Для забезпечення гарантованого мінімального часу реакції на зовнішні події програма повинна послідовно виконати кілька операцій:
1. Фіксувати максимальну робочу частоту CPU шляхом вибору регулятора `performance` у `sysfs`.
2. Заборонити перехід ядер у глибокі стани простою (C3/C6) шляхом утримання відкритого файлового дескриптора `/dev/cpu_dma_latency` із записом порогу затримки `0` мікросекунд.
3. Проконтролювати реальний апаратний коефіцієнт частоти через зчитування системних регістрів MSR.

При розробці системного програмного забезпечення на рівні користувача критично важливо розуміти відмінності між сирим системним підходом C та сучасними об'єктно-орієнтованими абстракціями C++. 

Нижче наведено приклади повноцінних робочих модулів обома мовами, які демонструють взаємодію з ядром Linux.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/stat.h>

#define PM_QOS_SYSFS_PATH "/dev/cpu_dma_latency"
#define CPUFREQ_GOV_PATH  "/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor"
#define MSR_DEV_PATH      "/dev/cpu/0/msr"
#define IA32_PERF_STATUS  0x198

/* Запит на фіксацію максимальної затримки через PM QoS */
int set_pm_qos_latency(int32_t target_latency_us) {
    int fd = open(PM_QOS_SYSFS_PATH, O_WRONLY);
    if (fd < 0) {
        fprintf(stderr, "Помилка відкриття %s: %s\n", PM_QOS_SYSFS_PATH, strerror(errno));
        return -1;
    }

    if (write(fd, &target_latency_us, sizeof(target_latency_us)) != sizeof(target_latency_us)) {
        fprintf(stderr, "Помилка запису в PM QoS: %s\n", strerror(errno));
        close(fd);
        return -1;
    }

    printf("[PM QoS] Успішно встановлено ліміт затримки: %d мкс (fd=%d)\n", target_latency_us, fd);
    return fd; /* Дескриптор має залишатися відкритим під час виконання роботи */
}

/* Зміна регулятора cpufreq через sysfs */
int set_cpufreq_governor(const char *governor_name) {
    int fd = open(CPUFREQ_GOV_PATH, O_WRONLY);
    if (fd < 0) {
        fprintf(stderr, "Помилка відкриття %s: %s\n", CPUFREQ_GOV_PATH, strerror(errno));
        return -1;
    }

    ssize_t len = strlen(governor_name);
    if (write(fd, governor_name, len) != len) {
        fprintf(stderr, "Помилка перемикання регулятора на %s: %s\n", governor_name, strerror(errno));
        close(fd);
        return -1;
    }

    close(fd);
    printf("[cpufreq] Встановлено регулятор: %s\n", governor_name);
    return 0;
}

/* Зчитати поточний множник частоти з MSR-регістра x86 */
int read_cpu_msr_ratio(void) {
    int fd = open(MSR_DEV_PATH, O_RDONLY);
    if (fd < 0) {
        /* Припускаємо, що модуль msr не завантажено або немає привілеїв root */
        return -1;
    }

    uint64_t msr_val = 0;
    if (pread(fd, &msr_val, sizeof(msr_val), IA32_PERF_STATUS) != sizeof(msr_val)) {
        close(fd);
        return -1;
    }

    close(fd);
    uint32_t ratio = (msr_val >> 8) & 0xFF;
    return (int)ratio;
}

int main(void) {
    printf("=== Налаштування параметрів живлення та затримок CPU (C API) ===\n");

    /* 1. Встановлюємо регулятор performance */
    if (set_cpufreq_governor("performance") != 0) {
        fprintf(stderr, "Увага: не вдалося змінити регулятор. Перевірте права root.\n");
    }

    /* 2. Блокуємо C-стани через PM QoS (затримка 0 мкс) */
    int qos_fd = set_pm_qos_latency(0);
    if (qos_fd < 0) {
        fprintf(stderr, "Не вдалося заблокувати затримку через PM QoS.\n");
        return EXIT_FAILURE;
    }

    /* 3. Зчитуємо поточний апаратний множник */
    int ratio = read_cpu_msr_ratio();
    if (ratio > 0) {
        printf("[MSR] Поточний множник частоти CPU: x%d\n", ratio);
    } else {
        printf("[MSR] Зчитування MSR недоступне (потрібно: modprobe msr).\n");
    }

    printf("Виконання критичної секції роботи з низькою затримкою...\n");
    sleep(2); /* Імуляція роботи системи під навантаженням */

    /* Закриваємо дескриптор, звільняючи PM QoS */
    close(qos_fd);
    printf("[PM QoS] Ліміт затримки знято.\n");

    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <fstream>
#include <filesystem>
#include <system_error>
#include <string_view>
#include <expected>
#include <cstdint>
#include <fcntl.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>

namespace fs = std::filesystem;

/*
 * RAII-обгортка для управління дескриптором PM QoS (/dev/cpu_dma_latency).
 * Автоматично вивільняє ресурси та знімає обмеження C-станів при виході з області видимості.
 */
class pm_qos_latency_lock {
public:
    explicit pm_qos_latency_lock(std::int32_t target_latency_us) {
        fd_ = ::open("/dev/cpu_dma_latency", O_WRONLY);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити /dev/cpu_dma_latency");
        }

        if (::write(fd_, &target_latency_us, sizeof(target_latency_us)) != sizeof(target_latency_us)) {
            ::close(fd_);
            fd_ = -1;
            throw std::system_error(errno, std::generic_category(), "Помилка запису в PM QoS");
        }

        std::cout << "[PM QoS RAII] Фіксація затримки на " << target_latency_us << " мкс активована.\n";
    }

    ~pm_qos_latency_lock() noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
            std::cout << "[PM QoS RAII] Дескриптор закрито, обмеження C-станів знято.\n";
        }
    }

    pm_qos_latency_lock(const pm_qos_latency_lock&) = delete;
    pm_qos_latency_lock& operator=(const pm_qos_latency_lock&) = delete;

    pm_qos_latency_lock(pm_qos_latency_lock&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    pm_qos_latency_lock& operator=(pm_qos_latency_lock&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

private:
    int fd_{-1};
};

/* Клас для керування політиками cpufreq через C++20 iostreams та filesystem */
class cpufreq_manager {
public:
    static std::expected<void, std::string> set_governor(std::size_t cpu_index, std::string_view governor) {
        fs::path path = fs::path("/sys/devices/system/cpu") / ("cpu" + std::to_string(cpu_index)) / "cpufreq/scaling_governor";

        if (!fs::exists(path)) {
            return std::unexpected("Шлях sysfs не існує: " + path.string());
        }

        std::ofstream sysfs_file(path);
        if (!sysfs_file.is_open()) {
            return std::unexpected("Помилка відкриття файлу для запису: " + path.string());
        }

        sysfs_file << governor;
        if (sysfs_file.fail()) {
            return std::unexpected("Помилка запису регулятора у sysfs");
        }

        std::cout << "[cpufreq C++] Регулятор для CPU " << cpu_index << " змінено на: " << governor << "\n";
        return {};
    }
};

int main() {
    std::cout << "=== Налаштування параметрів живлення та затримок CPU (C++20 API) ===\n";

    /* 1. Встановлюємо регулятор performance через C++ manager */
    auto result = cpufreq_manager::set_governor(0, "performance");
    if (!result) {
        std::cerr << "Помилка cpufreq: " << result.error() << "\n";
    }

    try {
        /* 2. Створюємо RAII об'єкт засувки PM QoS */
        pm_qos_latency_lock qos_lock(0);

        std::cout << "Виконання високонавантаженої обчисливальної задачі без затримок...\n";
        ::sleep(2);

    } catch (const std::exception& ex) {
        std::cerr << "Виняток PM QoS: " << ex.what() << "\n";
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
```
:::

## Аналіз архітектурних розбіжностей та механізмів обробки

При порівнянні реалізацій мовами C та C++ проявляються ключові особливості проектирування системного коду для ядра Linux:

1. **Управління ресурсами та паттерн RAII**:
   * У версії мовою C виклики `open()` та `close()` обробляються вручну. Якщо програма передчасно виходить із функції у разі виникнення помилки, не закривши дескриптор `qos_fd`, обмеження PM QoS залишатиметься діючим до кінця життя процесу.
   * У реалізації C++ використовується паттерн RAII (Resource Acquisition Is Initialization). Клас `pm_qos_latency_lock` гарантує, що при виконанні конструктора відкриється дескриптор `/dev/cpu_dma_latency`, а деструктор примусово викличе `close()`, навіть якщо в обчисливальному блоці буде згенеровано виняток (exception). Для запобігання дублюванню виклику `close()` конструктор копіювання заблоковано (`delete`), а переміщення (move semantics) правильно передає володіння дескриптором.

2. **Обробка помилок та синтаксис C++20**:
   * Реалізація C спирається на повернення від'ємних кодів помилок та перевірку глобальної змінної `errno` через `strerror()`.
   * Реалізація C++ застосовує тип `std::expected<void, std::string>`, доступний у C++23/C++20, що дозволяє явно розділити результат успішного виконання від контекстного опису помилки без необхідності кидати винятки на гарячих шляхах виконання.

3. **Взаємодія з файловою системою**:
   * Взаємодія з `sysfs` у C реалізована через низькорівневі системні виклики POSIX `open()` та `write()`, що забезпечує мінімальні накладні витрати пам'яті.
   * У C++ використовується об'єктна бібліотека `std::filesystem::path` та файлові потоки `std::ofstream`, які забезпечують кросплатформову безпеку формування шляхів та абстрагують форматування даних.

## Багатопотоковість, ядерні підсистеми та привілеї

При застосуванні PM QoS у багатопотокових високонавантажених застосунках необхідно враховувати особливості ядра Linux:

1. **Глобальний характер PM QoS**: Запит на затримку у `/dev/cpu_dma_latency` є глобальним для всієї системи або для відповідної QoS-групи. Запис значення `0` одним застосунком впливає на поведінку сплячих ядер у всій системі, що збільшує загальне споживання електроенергії серверної стійки.
2. **Багатопотокова синхронізація**: Якщо кілька потоків усередині одного процесу намагаються незалежно керувати PM QoS, кожен із них повинен відкривати власний файловий дескриптор `/dev/cpu_dma_latency`. Ядро Linux автоматично вибере найменше значення затримки серед усіх відкритих файлових дескрипторів у системі.
3. **Патч Real-Time (PREEMPT_RT)**: На ядрах із патчем реального часу `PREEMPT_RT` затримки перемикання C-станів можуть призводити до зриву дедлайнів тактів таймера. Застосування `pm_qos_latency_lock` є обов'язковою практикою для циклів обробки переривань реального часу.

## Простеження та верифікація через ftrace й perf

Для верифікації роботи засувки PM QoS у реальному часі можна використовувати підсистему трасування ядра `ftrace` та утиліту `perf`:

1. **Трасування оновлень PM QoS**:
   Підсистема ядра генерує події трасування при зміні списку вимог затримки. Їх можна перевірити через файлову систему `tracefs`:
   ```bash
   echo 1 > /sys/kernel/tracing/events/power/pm_qos_update/enable
   cat /sys/kernel/tracing/trace_pipe
   ```
   При запуску нашої програми ftrace виведе системну подію оновлення списку constraints із новим мінімальним значенням `0` мкс.

2. **Вимірювання розподілу C-станів через perf stat**:
   Для перевірки того, що процесор дійсно припинив входити у глибокі C-стани під час роботи програми, використовують команду:
   ```bash
   perf stat -e power:cpu_idle -a -- sleep 2
   ```
   У режимі активного блокування PM QoS лічильник подій входу в C-стани `state > 1` залишатиметься дорівнювати нулю.

## Часті пастки при практичному налаштуванні

1. **Недостатні права доступу**: Запис у `/dev/cpu_dma_latency` та атрибути `sysfs` вимагає привілеїв суперкористувача (`CAP_SYS_ADMIN` або `root`). Спроба відкриття файлів від імені звичайного користувача поверне помилку `EACCES` або `EPERM`.
2. **Аварійне закриття дескриптора PM QoS**: Якщо програма зберігає дескриптор у локальній змінній функції, яка завершується, дескриптор закриється автоматично, і ядро відновить перехід процесора у глибокі C-стани. Об'єкт `pm_qos_latency_lock` повинен жити протягом усього часу виконання критичного коду.
3. **Конфлікт драйвера intel_pstate**: При роботі `intel_pstate` у режимі `active` традиційні регулятори на кшталт `ondemand` виключені зі списку доступних. Перемикання можливе лише між `performance` та `powersave`.
