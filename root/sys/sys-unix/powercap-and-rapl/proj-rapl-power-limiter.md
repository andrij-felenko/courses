# ⚙️ Розробка системного сервісу динамічного обмеження потужності через powercap sysfs

У високонавантажених серверних кластерах, а також у мобільних робототехнічних комплексах виникає потреба динамічно обмежувати споживання енергії центральним процесором залежно від зовнішніх умов: залишкового заряду акумуляторної батареї, температури повітря у стійці або пікових тарифів на електроенергію. Цей практичний проєкт демонструє створення системного сервісу моніторингу та регулювання живлення для Linux, який сканує ієрархію зон `/sys/class/powercap/intel-rapl/`, виконує безперервний розрахунок поточної потужності сокета з урахуванням переповнення лічильника мікроджоулів та динамічно встановлює обмеження PL1/PL2.

## 1. Архітектурна ідея та робота з лічильником енергії

Для побудови надійного та енергоефективного демона керування живленням необхідно вирішити чотири ключові інженерні проблеми:

1. **Мінімізація системних накладних витрат:** Відкриття та закриття файлів sysfs у кожному циклі опитування (`open()` / `close()`) призводить до постійного виділення структур `inode` та пошуку у віртуальній файловій системі `dentry`, що створює непотрібне навантаження на процесор. Сервіс відкриває файлові дескриптори `energy_uj` один раз під час ініціалізації та утримує їх відкритими. Зчитування накопиченого значення енергії здійснюється системним викликом `pread()` із нульовим зміщенням, що дозволяє уникнути викликів `lseek()` та повторної алокації файлових дескрипторів.
2. **Обробка переповнення 32-бітного апаратного лічильника:** Апаратний лічильник MSR `0x611` скидається в нуль кожні кілька сотень секунд під високим навантаженням. Програма повинна детектувати переповнення та обчислювати дельту `ΔE` за модулем максимального діапазону.
3. **Захист від джиттеру таймера:** Використання годинника реального часу `CLOCK_REALTIME` є помилкою через можливі коригування часу службою NTP (стрибки назад або вперед). Для розрахунку потужності використовується суворо монотонний апаратний таймер `CLOCK_MONOTONIC_RAW`, що виключає вплив NTP-фазування на розрахунок похідної енергії.
4. **Асинхронне завершення та обробка сигналів:** Системний сервіс повинен коректно перехоплювати сигнали `SIGTERM` та `SIGINT`, скидати ліміти до заводських значень перед завершенням та гарантовано звільняти відкриті дескриптори.

Розрахунок середньої потужності за інтервал часу `Δt` виконується за фізичною формулою:

```text
ΔE = (E_current >= E_previous) 
     ? (E_current - E_previous) 
     : (E_current + Max_Range - E_previous)

P_avg (Вт) = (ΔE / 1 000 000) / (Δt / 1 000 000) = ΔE (мкДж) / Δt (мкс)
```

Де `Max_Range` — значення з файлу `max_energy_range_uj` (зазвичай від 262 до 655 Дж залежно від архітектури CPU).

## 2. Послідовність виконання системного виклику pread() у ядрі

Коли сервіс викликає `pread(fd_energy, buf, sizeof(buf) - 1, 0)`, у просторі ядра Linux розгортається наступна послідовність операцій:

1. **VFS та kernfs:** Системний виклик `sys_pread64` потрапляє до рівня віртуальної файлової системи VFS, яка перенаправляє запит обробнику віртуальної підсистеми `kernfs` для відповідного атрибута sysfs.
2. **Зворотний виклик powercap:** Драйвер ядра викликає функцію `powercap_zone_show()`, яка захоплює м'ютекс `zone->lock` і звертається до зареєстрованої таблиці зворотних викликів `ops->get_energy_uj`.
3. **Читання MSR/TPMI:** Драйвер `intel_rapl_msr` виконує пряме апаратне читання через інструкцію `rdmsrl_safe(MSR_PKG_ENERGY_STATUS, &val)`, масштабує отримане значення відповідно до `MSR_RAPL_POWER_UNIT` та записує результуючий текст у мікроджоулях у буфер користувача.

Завдяки збереженню дескриптора відкритим тривалість цього ланцюжка скорочується до 2–3 мікросекунд, що дозволяє виконувати високоточний моніторинг без спотворення енергетичного профілю самої системи.

## 3. Програмний контур регулювання: алгоритм динамічного лімітування

Окрім простого статичного встановлення `constraint_0_power_limit_uw`, системний сервіс може реалізовувати пропорційно-інтегральний (ПІ) регулятор для динамічного підлаштування лімітів під цільову температуру або рівень шуму вентиляторів.

Якщо фактична потужність або температура перевищує бажаний поріг `T_target`, керуюча функція сервісу обчислює помилку розбалансу `e(t) = T_actual - T_target` і знижує ліміт PL1 на величину `ΔP = K_p · e(t) + K_i · ∫ e(t) dt`. Це дозволяє утримувати систему в оптимальному тепловому режимі без різких стрибків частоти та акустичного шуму.

## 4. Реалізація сервісу моніторингу та лімітування

Нижче наведено повну реалізацію системної утиліти мовами C та C++. Обидві програми реалізують відкриття зон, періодичний вимір потужності, розрахунок дельти енергії та запис нового ліміту PL1.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <time.h>
#include <errno.h>
#include <signal.h>

#define RAPL_BASE_PATH "/sys/class/powercap/intel-rapl/intel-rapl:0"
#define BUFFER_SIZE 64

static volatile sig_atomic_t g_running = 1;

static void handle_signal(int sig) {
    (void)sig;
    g_running = 0;
}

typedef struct {
    int fd_energy;
    int fd_limit;
    uint64_t max_range_uj;
    uint64_t prev_energy_uj;
    struct timespec prev_time;
} rapl_zone_t;

/* Отримання поточного монотонного часу у мікросекундах */
static inline uint64_t get_time_us(const struct timespec *ts) {
    return (uint64_t)ts->tv_sec * 1000000ULL + (uint64_t)ts->tv_nsec / 1000ULL;
}

/* Ініціалізація дескрипторів зони керування RAPL */
int rapl_zone_init(rapl_zone_t *zone, const char *base_path) {
    char path[256];
    char buf[BUFFER_SIZE];
    
    // 1. Зчитування діапазону переповнення
    snprintf(path, sizeof(path), "%s/max_energy_range_uj", base_path);
    int fd = open(path, O_RDONLY);
    if (fd < 0) {
        perror("Помилка відкриття max_energy_range_uj");
        return -1;
    }
    ssize_t bytes = read(fd, buf, sizeof(buf) - 1);
    close(fd);
    if (bytes <= 0) return -1;
    buf[bytes] = '\0';
    zone->max_range_uj = strtoull(buf, NULL, 10);

    // 2. Відкриття файлу енергії (потрібні права root / CAP_SYS_RAWIO)
    snprintf(path, sizeof(path), "%s/energy_uj", base_path);
    zone->fd_energy = open(path, O_RDONLY);
    if (zone->fd_energy < 0) {
        perror("Помилка відкриття energy_uj (потрібен запуск із sudo)");
        return -1;
    }

    // 3. Відкриття файлу встановлення ліміту PL1
    snprintf(path, sizeof(path), "%s/constraint_0_power_limit_uw", base_path);
    zone->fd_limit = open(path, O_WRONLY);
    if (zone->fd_limit < 0) {
        perror("Помилка відкриття constraint_0_power_limit_uw");
        close(zone->fd_energy);
        return -1;
    }

    // Початкове калібрувальне читання
    bytes = pread(zone->fd_energy, buf, sizeof(buf) - 1, 0);
    if (bytes > 0) {
        buf[bytes] = '\0';
        zone->prev_energy_uj = strtoull(buf, NULL, 10);
    }
    clock_gettime(CLOCK_MONOTONIC_RAW, &zone->prev_time);
    return 0;
}

/* Розрахунок середньої потужності за інтервал у ватах */
double rapl_read_power_watts(rapl_zone_t *zone) {
    char buf[BUFFER_SIZE];
    struct timespec now;
    
    ssize_t bytes = pread(zone->fd_energy, buf, sizeof(buf) - 1, 0);
    if (bytes <= 0) return -1.0;
    buf[bytes] = '\0';
    
    clock_gettime(CLOCK_MONOTONIC_RAW, &now);
    uint64_t curr_energy = strtoull(buf, NULL, 10);

    // Розрахунок дельти енергії з урахуванням переповнення
    uint64_t delta_energy;
    if (curr_energy >= zone->prev_energy_uj) {
        delta_energy = curr_energy - zone->prev_energy_uj;
    } else {
        delta_energy = curr_energy + zone->max_range_uj - zone->prev_energy_uj;
    }

    uint64_t time_prev_us = get_time_us(&zone->prev_time);
    uint64_t time_now_us = get_time_us(&now);
    uint64_t delta_time_us = time_now_us - time_prev_us;

    zone->prev_energy_uj = curr_energy;
    zone->prev_time = now;

    if (delta_time_us == 0) return 0.0;
    // Потужність: uJ / us = Watts
    return (double)delta_energy / (double)delta_time_us;
}

/* Встановлення апаратного ліміту PL1 у ватах */
int rapl_set_power_limit_watts(rapl_zone_t *zone, double watts) {
    char buf[BUFFER_SIZE];
    uint64_t limit_uw = (uint64_t)(watts * 1000000.0);
    
    int len = snprintf(buf, sizeof(buf), "%llu\n", (unsigned long long)limit_uw);
    ssize_t bytes = pwrite(zone->fd_limit, buf, len, 0);
    return (bytes == len) ? 0 : -1;
}

void rapl_zone_close(rapl_zone_t *zone) {
    if (zone->fd_energy >= 0) close(zone->fd_energy);
    if (zone->fd_limit >= 0) close(zone->fd_limit);
}

int main(int argc, char **argv) {
    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = handle_signal;
    sigaction(SIGINT, &sa, NULL);
    sigaction(SIGTERM, &sa, NULL);

    rapl_zone_t zone;
    if (rapl_zone_init(&zone, RAPL_BASE_PATH) < 0) {
        fprintf(stderr, "Ініціалізація RAPL не вдалася. Перевірте наявність модуля intel_rapl_msr.\n");
        return 1;
    }

    printf("Моніторинг RAPL запущено для %s (Апаратна ємність: %.2f Дж)\n",
           RAPL_BASE_PATH, (double)zone.max_range_uj / 1e6);

    // Встановлення тестового ліміту потужності 45.0 Вт
    if (rapl_set_power_limit_watts(&zone, 45.0) == 0) {
        printf("Успішно встановлено ліміт PL1 = 45.00 Вт\n");
    }

    while (g_running) {
        usleep(500000); // Період опитування 500 мс
        double power = rapl_read_power_watts(&zone);
        if (power >= 0.0) {
            printf("Поточне споживання сокета: %6.2f Вт\n", power);
        }
    }

    printf("\nЗавершення роботи. Закриття дескрипторів...\n");
    rapl_zone_close(&zone);
    return 0;
}
```
```cpp
#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <chrono>
#include <thread>
#include <atomic>
#include <system_error>
#include <csignal>
#include <fcntl.h>
#include <unistd.h>

namespace {
    std::atomic<bool> g_running{true};

    void signalHandler(int) noexcept {
        g_running.store(false);
    }
}

class RaplZone {
public:
    explicit RaplZone(std::string_view basePath) 
        : basePath_(basePath), fdEnergy_(-1), fdLimit_(-1), maxRangeUj_(0), prevEnergyUj_(0) {
        init();
    }

    ~RaplZone() {
        if (fdEnergy_ >= 0) ::close(fdEnergy_);
        if (fdLimit_ >= 0) ::close(fdLimit_);
    }

    RaplZone(const RaplZone&) = delete;
    RaplZone& operator=(const RaplZone&) = delete;

    RaplZone(RaplZone&& other) noexcept 
        : basePath_(std::move(other.basePath_)),
          fdEnergy_(other.fdEnergy_),
          fdLimit_(other.fdLimit_),
          maxRangeUj_(other.maxRangeUj_),
          prevEnergyUj_(other.prevEnergyUj_),
          prevTime_(other.prevTime_) {
        other.fdEnergy_ = -1;
        other.fdLimit_ = -1;
    }

    double readPowerWatts() {
        char buf[64];
        ssize_t bytes = ::pread(fdEnergy_, buf, sizeof(buf) - 1, 0);
        if (bytes <= 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка читання energy_uj");
        }
        buf[bytes] = '\0';
        
        auto now = std::chrono::steady_clock::now();
        uint64_t currEnergy = std::stoull(buf);

        uint64_t deltaEnergy = 0;
        if (currEnergy >= prevEnergyUj_) {
            deltaEnergy = currEnergy - prevEnergyUj_;
        } else {
            deltaEnergy = currEnergy + maxRangeUj_ - prevEnergyUj_;
        }

        auto deltaUs = std::chrono::duration_cast<std::chrono::microseconds>(now - prevTime_).count();
        prevEnergyUj_ = currEnergy;
        prevTime_ = now;

        if (deltaUs == 0) return 0.0;
        return static_cast<double>(deltaEnergy) / static_cast<double>(deltaUs);
    }

    void setPowerLimitWatts(double watts) {
        uint64_t limitUw = static_cast<uint64_t>(watts * 1'000'000.0);
        std::string payload = std::to_string(limitUw) + "\n";
        
        ssize_t bytes = ::pwrite(fdLimit_, payload.data(), payload.size(), 0);
        if (bytes != static_cast<ssize_t>(payload.size())) {
            throw std::system_error(errno, std::generic_category(), "Помилка запису ліміту потужності");
        }
    }

    [[nodiscard]] uint64_t maxRangeUj() const noexcept { return maxRangeUj_; }

private:
    void init() {
        std::string rangePath = basePath_ + "/max_energy_range_uj";
        std::ifstream rangeFile(rangePath);
        if (!rangeFile.is_open()) {
            throw std::runtime_error("Не вдалося відкрити " + rangePath);
        }
        rangeFile >> maxRangeUj_;

        std::string energyPath = basePath_ + "/energy_uj";
        fdEnergy_ = ::open(energyPath.c_str(), O_RDONLY);
        if (fdEnergy_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка відкриття " + energyPath);
        }

        std::string limitPath = basePath_ + "/constraint_0_power_limit_uw";
        fdLimit_ = ::open(limitPath.c_str(), O_WRONLY);
        if (fdLimit_ < 0) {
            ::close(fdEnergy_);
            throw std::system_error(errno, std::generic_category(), "Помилка відкриття " + limitPath);
        }

        char buf[64];
        ssize_t bytes = ::pread(fdEnergy_, buf, sizeof(buf) - 1, 0);
        if (bytes > 0) {
            buf[bytes] = '\0';
            prevEnergyUj_ = std::stoull(buf);
        }
        prevTime_ = std::chrono::steady_clock::now();
    }

    std::string basePath_;
    int fdEnergy_;
    int fdLimit_;
    uint64_t maxRangeUj_;
    uint64_t prevEnergyUj_;
    std::chrono::steady_clock::time_point prevTime_;
};

int main() {
    std::signal(SIGINT, signalHandler);
    std::signal(SIGTERM, signalHandler);

    try {
        RaplZone zone("/sys/class/powercap/intel-rapl/intel-rapl:0");
        std::cout << "Ініціалізовано зону RAPL. Максимальний діапазон лічильника: " 
                  << (zone.maxRangeUj() / 1e6) << " Дж\n";

        zone.setPowerLimitWatts(45.0);
        std::cout << "Встановлено апаратний ліміт PL1 = 45.0 Вт\n";

        while (g_running.load()) {
            std::this_thread::sleep_for(std::chrono::milliseconds(500));
            double power = zone.readPowerWatts();
            std::cout << "Поточне споживання Package: " << power << " Вт\n";
        }
        std::cout << "Коректне завершення роботи.\n";
    } catch (const std::exception& ex) {
        std::cerr << "Помилка виконання сервісу: " << ex.what() << '\n';
        return 1;
    }
    return 0;
}
```
:::

## 5. Інтеграція із systemd та безпековий конфіг

Для запуску сервісу у виробничому оточенні Linux рекомендується оформити його як системну службу `systemd`. З метою дотримання принципу найменших привілеїв (Least Privilege Principle) процес не повинен працювати від облікового запису `root`. Замість цього створюється виділений користувач `power-daemon`, а службі делегується двійкова можливість ядра Linux `CAP_SYS_RAWIO`.

Файл конфігурації юніта `/etc/systemd/system/rapl-limiter.service`:

```ini
[Unit]
Description=RAPL Dynamic Power Capping Daemon
After=syslog.target network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/rapl_power_limiter
Restart=always
RestartSec=5s

# Безпека та обмеження прав
User=power-daemon
Group=power-daemon
CapabilityBoundingSet=CAP_SYS_RAWIO
AmbientCapabilities=CAP_SYS_RAWIO
NoNewPrivileges=true

# Ізоляція файлової системи
ProtectSystem=strict
ProtectHome=yes
ReadOnlyPaths=/sys/class/powercap/intel-rapl/intel-rapl:0/energy_uj
ReadWritePaths=/sys/class/powercap/intel-rapl/intel-rapl:0/constraint_0_power_limit_uw
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

## 6. Практичні підводні камені та типові помилки

Під час експлуатації системних сервісів керування живленням у виробничому середовищі слід враховувати такі особливості:

1. **Непривілейований доступ та налаштування udev:**
   Після закриття вразливості Platypus файл `energy_uj` доступний лише користувачу `root` (права `0400`). Для роботи сервісу від виділеного системного користувача слід або надати процесу `CAP_SYS_RAWIO`, або налаштувати правило `udev` для надання прав доступу групі моніторингу:
   ```bash
   # /etc/udev/rules.d/99-powercap.rules
   SUBSYSTEM=="powercap", ACTION=="add", RUN+="/bin/chmod -R g+r /sys/class/powercap/intel-rapl/"
   ```
2. **Період вибірки проти переповнення лічильника:**
   При споживанні процесора 250 Вт лічильник ємністю 262 Дж переповнюється кожну секунду (`262 / 250 ≈ 1.05 с`). Якщо період опитування демона перевищує цей час, виникає незворотна втрата інформації про спожиту енергію. Період вибірки повинен задовольняти умову: `T_sample < Max_Range / (2 · P_max)`.
3. **Багатосокетні конфігурації (NUMA):**
   У дво- та чотирисокетних серверах кожна зона `intel-rapl:0`, `intel-rapl:1` має незалежні лічильники та ліміти. Сервіс повинен ітерувати по всіх каталогах сокетів, сумувати енергію та пропорційно розподіляти загальний бюджет стійки між процесорами.
4. **Конфлікт із демонами керування енергопрофілями:**
   Системні демони `power-profiles-daemon`, `tlp` або `thermald` можуть перезаписувати значення `constraint_0_power_limit_uw` під час перемикання профілів ("Performance", "Balanced", "Power-Saver") або при переході на живлення від батареї. При впровадженні власного сервісу необхідно вимкнути конкуруючі служби або налаштувати інтеграцію через DBus-інтерфейси.
