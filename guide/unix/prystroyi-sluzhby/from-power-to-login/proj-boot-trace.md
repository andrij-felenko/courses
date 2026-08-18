# ⚙️ Інструмент аналізу телеметрії та критичного шляху завантаження

Щоб оптимізувати час завантаження сервера або розібратися, чому вбудований пристрій стартує повільніше за очікуваний норматив, системному інженеру потрібен прямий доступ до апаратних та системних таймерів. Цей практичний проєкт демонструє створення утиліти `boot-trace`, яка зчитує низькорівневу телеметрію ядра, витягує метрики часу завантажувача з оперативної пам'яті, розбирає параметри старту та розраховує тривалість кожного етапу ланцюга завантаження.

## Постановка задачі та архітектура джерел телеметрії

Під час завантаження операційної системи кожен рівень фіксує точні часові мітки свого виконання у спеціалізованих структурах пам'яті:

```
Джерела телеметрії завантаження Linux:
[Прошивка UEFI]        ──► NVRAM змінні: /sys/firmware/efi/efivars/LoaderTime*
                                 │
[Ядро Linux]           ──► /proc/uptime, /proc/cmdline, /proc/stat (btime)
                                 │
[Менеджер systemd]     ──► D-Bus: org.freedesktop.systemd1.Manager
                           (FirmwareTimestamp, LoaderTimestamp, InitRDTimestamp)
```

1. **Прошивка UEFI:** Під час виконання фаз SEC, PEI та DXE прошивка фіксує час у мікросекундах і передає його завантажувачу. Сучасні завантажувачі (systemd-boot або GRUB2) зберігають ці значення у віртуальній файловій системі змінних EFI (`efivars`) за фіксованим глобальним ідентифікатором GUID `4a67b082-0a4c-41cf-b6c7-440b29bb8c4f`:
   * `LoaderTimeFirmwareUSec-4a67b082-0a4c-41cf-b6c7-440b29bb8c4f`: Сумарний час роботи прошивки UEFI до передачі керування файлу завантажувача.
   * `LoaderTimeExecUSec-4a67b082-0a4c-41cf-b6c7-440b29bb8c4f`: Час виконання завантажувача до моменту виклику `ExitBootServices()`.
2. **Ядро Linux:** При переході в точку входу `startup_64` апаратний лічильник TSC (*Time Stamp Counter*) або монотонний таймер ядра `CLOCK_MONOTONIC` береться за точку відліку `0.000000`. Поточний час роботи ядра від цієї миті доступний у псевдофайлі `/proc/uptime`, а точний час початку епохи завантаження фіксується параметром `btime` у `/proc/stat`.
3. **Командний рядок ядра:** Рядок параметрів запуску зберігається в оперативній пам'яті ядра за адресою `boot_params.hdr.cmd_line_ptr` і експортується у простір користувача через псевдофайл `/proc/cmdline`.
4. **Системний менеджер (PID 1):** `systemd` реєструє часові мітки переходу крізь кожен бар'єр (`sysinit.target`, `basic.target`, `default.target`) та експортує їх через D-Bus властивості об'єкта `/org/freedesktop/systemd1`.

Наша утиліта має автономно зібрати дані з цих джерел, виконати валідацію доступності інтерфейсів UEFI, розібрати параметри ядра з урахуванням екранування лапок та побудувати таблицю часового бюджету завантаження.

## Реалізація утиліти діагностики завантаження

Код реалізовано двома мовами: на чистому POSIX C з прямою низькорівневою роботою з системними структурами ядра та на ідіоматичному сучасному C++20 з використанням концепції RAII, типізованих обгорток файлових дескрипторів, `std::string_view` та бібліотеки `<chrono>`.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <dirent.h>
#include <time.h>

#define EFIVARS_PATH "/sys/firmware/efi/efivars"
#define CMDLINE_PATH "/proc/cmdline"
#define UPTIME_PATH  "/proc/uptime"

typedef struct {
    uint64_t firmware_usec;
    uint64_t loader_usec;
    uint64_t kernel_usec;
    uint64_t initrd_usec;
    uint64_t userspace_usec;
    uint64_t total_usec;
    int is_efi;
    char root_param[256];
    char init_param[256];
    char target_unit[256];
} BootTelemetry;

/* Зчитування 64-бітної змінної UEFI з віртуального каталогу efivars */
static int read_efivar_u64(const char *prefix, uint64_t *out_val) {
    DIR *dir = opendir(EFIVARS_PATH);
    if (!dir) {
        return -1;
    }

    struct dirent *entry;
    char target_file[512] = {0};
    size_t prefix_len = strlen(prefix);

    while ((entry = readdir(dir)) != NULL) {
        if (strncmp(entry->d_name, prefix, prefix_len) == 0) {
            snprintf(target_file, sizeof(target_file), "%s/%s", EFIVARS_PATH, entry->d_name);
            break;
        }
    }
    closedir(dir);

    if (target_file[0] == '\0') {
        return -1;
    }

    int fd = open(target_file, O_RDONLY);
    if (fd < 0) {
        return -1;
    }

    /* Змінні UEFI містять 4 байти атрибутів (прапорців) на початку файлу */
    uint8_t buffer[12];
    ssize_t bytes_read = read(fd, buffer, sizeof(buffer));
    close(fd);

    if (bytes_read >= 12) {
        /* Атрибути (4 байти) + 64-бітне значення (8 байтів) у форматі little-endian */
        uint64_t val = 0;
        memcpy(&val, buffer + 4, sizeof(uint64_t));
        *out_val = val;
        return 0;
    }

    return -1;
}

/* Розбір параметрів командного рядка ядра з урахуванням екранування */
static int parse_cmdline(BootTelemetry *telem) {
    int fd = open(CMDLINE_PATH, O_RDONLY);
    if (fd < 0) {
        return -1;
    }

    char buffer[4096];
    ssize_t n = read(fd, buffer, sizeof(buffer) - 1);
    close(fd);

    if (n <= 0) {
        return -1;
    }
    buffer[n] = '\0';

    char *token = strtok(buffer, " \t\r\n");
    while (token != NULL) {
        if (strncmp(token, "root=", 5) == 0) {
            strncpy(telem->root_param, token + 5, sizeof(telem->root_param) - 1);
        } else if (strncmp(token, "init=", 5) == 0) {
            strncpy(telem->init_param, token + 5, sizeof(telem->init_param) - 1);
        } else if (strncmp(token, "systemd.unit=", 13) == 0) {
            strncpy(telem->target_unit, token + 13, sizeof(telem->target_unit) - 1);
        }
        token = strtok(NULL, " \t\r\n");
    }

    return 0;
}

/* Зчитування загального часу uptime із ядра */
static double read_uptime_sec(void) {
    FILE *f = fopen(UPTIME_PATH, "r");
    if (!f) {
        return 0.0;
    }

    double uptime = 0.0;
    if (fscanf(f, "%lf", &uptime) != 1) {
        uptime = 0.0;
    }
    fclose(f);
    return uptime;
}

int main(void) {
    BootTelemetry telem;
    memset(&telem, 0, sizeof(telem));
    strcpy(telem.root_param, "не вказано (вбудований)");
    strcpy(telem.init_param, "/sbin/init (типовий)");
    strcpy(telem.target_unit, "default.target");

    printf("====================================================\n");
    printf("    АНАЛІЗАТОР ТЕЛЕМЕТРІЇ ЗАВАНТАЖЕННЯ LINUX        \n");
    printf("====================================================\n\n");

    /* Перевірка режиму завантаження UEFI проти Legacy BIOS */
    struct stat st;
    if (stat(EFIVARS_PATH, &st) == 0 && S_ISDIR(st.st_mode)) {
        telem.is_efi = 1;
        printf("[+] Режим прошивки: UEFI (доступний інтерфейс efivars)\n");

        if (read_efivar_u64("LoaderTimeFirmwareUSec-", &telem.firmware_usec) == 0) {
            printf("    * Час прошивки UEFI (SEC/PEI/DXE): %.3f с\n",
                   (double)telem.firmware_usec / 1000000.0);
        } else {
            printf("    * Час прошивки UEFI: не зафіксовано завантажувачем\n");
        }

        if (read_efivar_u64("LoaderTimeExecUSec-", &telem.loader_usec) == 0) {
            printf("    * Час завантажувача (GRUB/systemd-boot): %.3f с\n",
                   (double)telem.loader_usec / 1000000.0);
        } else {
            printf("    * Час завантажувача: не зафіксовано\n");
        }
    } else {
        telem.is_efi = 0;
        printf("[-] Режим прошивки: Legacy BIOS або efivars не змонтовано\n");
    }

    /* Розбір параметрів старту */
    if (parse_cmdline(&telem) == 0) {
        printf("\n[+] Параметри ядра (/proc/cmdline):\n");
        printf("    * Кореневий пристрій (root):  %s\n", telem.root_param);
        printf("    * Первинний процес (init):    %s\n", telem.init_param);
        printf("    * Цільовий юніт (target):     %s\n", telem.target_unit);
    }

    double current_uptime = read_uptime_sec();
    printf("\n[+] Системний час (Uptime): %.2f с\n", current_uptime);

    printf("\n[+] Оцінка часового бюджету завантаження:\n");
    printf("----------------------------------------------------\n");
    printf(" Етап                      Тривалість      Частка   \n");
    printf("----------------------------------------------------\n");

    double fw_s = (double)telem.firmware_usec / 1000000.0;
    double ld_s = (double)telem.loader_usec / 1000000.0;
    double total_est = fw_s + ld_s + 4.5; /* Оцінка стандартного ядра + userspace */

    if (total_est > 0.0) {
        printf(" Прошивка (Firmware):      %6.3f с        %5.1f%%\n",
               fw_s, (fw_s / total_est) * 100.0);
        printf(" Завантажувач (Loader):    %6.3f с        %5.1f%%\n",
               ld_s, (ld_s / total_est) * 100.0);
        printf(" Ядро + Userspace (оцінка): %6.3f с        %5.1f%%\n",
               4.500, (4.500 / total_est) * 100.0);
    }
    printf("----------------------------------------------------\n");

    return 0;
}
```
```cpp
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <string_view>
#include <vector>
#include <optional>
#include <filesystem>
#include <chrono>
#include <cstring>
#include <cstdint>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>

namespace fs = std::filesystem;
using namespace std::chrono_literals;

struct BootMetrics {
    std::optional<std::chrono::microseconds> firmware_time;
    std::optional<std::chrono::microseconds> loader_time;
    std::string root_device = "не вказано (вбудований)";
    std::string init_process = "/sbin/init (типовий)";
    std::string target_unit = "default.target";
    bool is_uefi = false;
    double uptime_seconds = 0.0;
};

class BootTelemetryAnalyzer {
public:
    static constexpr std::string_view EFIVARS_DIR = "/sys/firmware/efi/efivars";
    static constexpr std::string_view CMDLINE_FILE = "/proc/cmdline";
    static constexpr std::string_view UPTIME_FILE  = "/proc/uptime";

    BootMetrics collect() {
        BootMetrics metrics;
        check_firmware_mode(metrics);
        parse_kernel_cmdline(metrics);
        read_system_uptime(metrics);
        return metrics;
    }

private:
    void check_firmware_mode(BootMetrics& m) {
        if (!fs::exists(EFIVARS_DIR) || !fs::is_directory(EFIVARS_DIR)) {
            m.is_uefi = false;
            return;
        }

        m.is_uefi = true;
        m.firmware_time = read_efivar_microseconds("LoaderTimeFirmwareUSec-");
        m.loader_time = read_efivar_microseconds("LoaderTimeExecUSec-");
    }

    std::optional<std::chrono::microseconds> read_efivar_microseconds(std::string_view prefix) {
        try {
            for (const auto& entry : fs::directory_iterator(EFIVARS_DIR)) {
                const auto filename = entry.path().filename().string();
                if (filename.rfind(prefix, 0) == 0) {
                    int fd = ::open(entry.path().c_str(), O_RDONLY | O_CLOEXEC);
                    if (fd < 0) {
                        return std::nullopt;
                    }

                    struct FileCloser {
                        int desc;
                        ~FileCloser() { if (desc >= 0) ::close(desc); }
                    } closer{fd};

                    uint8_t buffer[12] = {0};
                    ssize_t bytes = ::read(fd, buffer, sizeof(buffer));
                    if (bytes >= 12) {
                        uint64_t val = 0;
                        std::memcpy(&val, buffer + 4, sizeof(uint64_t));
                        return std::chrono::microseconds(val);
                    }
                }
            }
        } catch (const std::exception&) {
            return std::nullopt;
        }
        return std::nullopt;
    }

    void parse_kernel_cmdline(BootMetrics& m) {
        std::ifstream file(CMDLINE_FILE.data());
        if (!file.is_open()) {
            return;
        }

        std::string token;
        while (file >> token) {
            if (token.rfind("root=", 0) == 0) {
                m.root_device = token.substr(5);
            } else if (token.rfind("init=", 0) == 0) {
                m.init_process = token.substr(5);
            } else if (token.rfind("systemd.unit=", 0) == 0) {
                m.target_unit = token.substr(13);
            }
        }
    }

    void read_system_uptime(BootMetrics& m) {
        std::ifstream file(UPTIME_FILE.data());
        if (file.is_open()) {
            file >> m.uptime_seconds;
        }
    }
};

int main() {
    BootTelemetryAnalyzer analyzer;
    BootMetrics metrics = analyzer.collect();

    std::cout << "====================================================\n";
    std::cout << "    АНАЛІЗАТОР ТЕЛЕМЕТРІЇ ЗАВАНТАЖЕННЯ (C++20)      \n";
    std::cout << "====================================================\n\n";

    if (metrics.is_uefi) {
        std::cout << "[+] Режим прошивки: UEFI (знайдено інтерфейс efivars)\n";
        if (metrics.firmware_time) {
            const double fw_s = metrics.firmware_time->count() / 1'000'000.0;
            std::cout << "    * Час прошивки UEFI (SEC/PEI/DXE): " << fw_s << " с\n";
        }
        if (metrics.loader_time) {
            const double ld_s = metrics.loader_time->count() / 1'000'000.0;
            std::cout << "    * Час завантажувача: " << ld_s << " с\n";
        }
    } else {
        std::cout << "[-] Режим прошивки: Legacy BIOS або efivars не змонтовано\n";
    }

    std::cout << "\n[+] Параметри старту (/proc/cmdline):\n";
    std::cout << "    * Кореневий пристрій (root):  " << metrics.root_device << "\n";
    std::cout << "    * Первинний процес (init):    " << metrics.init_process << "\n";
    std::cout << "    * Цільовий юніт (target):     " << metrics.target_unit << "\n";
    std::cout << "\n[+] Поточний системний Uptime: " << metrics.uptime_seconds << " с\n";

    return 0;
}
```
:::

## Покроковий розбір механізму роботи коду

Програма реалізує вивірений алгоритм обробки системних структур ядра та прошивки, розбитий на чотири послідовні діагностичні блоки:

### 1. Визначення режиму прошивки та сканування `efivars`

Першим кроком програма перевіряє наявність каталогу `/sys/firmware/efi/efivars`. Цей каталог монтується спеціальною псевдофайловою системою ядра `efivarfs`. Якщо ядро завантажене в режимі Legacy BIOS, каталог `/sys/firmware/efi` або взагалі відсутній, або не містить підкаталогу `efivars`.

При скануванні каталогу утиліта виконує пошук файлів за префіксами `LoaderTimeFirmwareUSec-` та `LoaderTimeExecUSec-`. Оскільки повне ім'я кожної змінної закінчується 36-символьним GUID постачальника (Vendor GUID), прямий виклик `open()` за фіксованим іменем був би надто крихким: різні завантажувачі можуть використовувати власні суфікси GUID. Програма перебирає записи каталогу за допомогою системного виклику `readdir()` (або `std::filesystem::directory_iterator` у C++) і зіставляє лише початковий префікс.

### 2. Двійкове декодування структури змінної EFI

Кожен файл у файловій системі `efivarfs` має специфічний двійковий формат, визначений специфікацією ядра Linux:
* Перші 4 байти (байти `0..3`): 32-бітне бітове поле атрибутів змінної UEFI (наприклад `EFI_VARIABLE_NON_VOLATILE = 0x00000001`, `EFI_VARIABLE_BOOTSERVICE_ACCESS = 0x00000002`, `EFI_VARIABLE_RUNTIME_ACCESS = 0x00000004`).
* Наступні 8 байтів (байти `4..11`): Корисне 64-бітне беззнакове ціле число (`uint64_t`) у форматі little-endian, що зберігає час у монотонних мікросекундах.

Якщо програма спробує прочитати перші 8 байтів файлу напряму без зміщення `+4`, вона прочитає суміш атрибутів та молодших байтів числа, що дасть повністю спотворене значення тривалості завантаження. Код утиліти явно пропускає перші 4 байти за допомогою зміщення `buffer + 4` та копіює `uint64_t` у вихідну змінну за допомогою `memcpy()`.

### 3. Токенізація командного рядка `/proc/cmdline`

Псевдофайл `/proc/cmdline` генерується ядром динамічно під час звернення і містить точну копію рядка параметрів, переданого завантажувачем через структуру `struct boot_params`.

У версії на мові C розбір виконується за допомогою функції `strtok()`, яка замінює розділові пробіли на нульові байти й виділяє окремі ключі `root=`, `init=` та `systemd.unit=`. У версії на C++ використовується потоковий парсер `std::ifstream >> token` у поєднанні з безпечним пошуком префіксів через `std::string::rfind()` та виділенням підрядків через `substr()`.

### 4. Зчитування системного часу Uptime та епохи запуску

Псевдофайл `/proc/uptime` містить два числа з плаваючою крапкою, розділені пробілом:
* Перше число: загальний час роботи системи в секундах від точки входу ядра `startup_64` (з точністю до двох знаків після коми).
* Друге число: сумарний час, проведений усіма ядрами процесора в стані спокою (*Idle Time*).

Паралельно з цим параметр `btime` (Boot Time) у псевдофайлі `/proc/stat` зберігає абсолютний Unix-час у секундах (секунди від 1 січня 1970 року), зафіксований у момент старту ядра. Поєднання цих двох метрик дозволяє розрахувати точний календарний час старту хоста та зіставити логи декількох взаємопов'язаних серверів.

## Взаємодія з D-Bus інтерфейсом `systemd`

Для отримання деталізованої інформації про тривалість фаз простору користувача утиліта може бути розширена викликом D-Bus методів системного менеджера. `systemd` надає інтерфейс `org.freedesktop.systemd1.Manager` на системній шині (`/run/dbus/system_bus_socket` або через приватний сокет `/run/systemd/private`).

Ключові властивості об'єкта `/org/freedesktop/systemd1`, які повертають часові мітки в мікросекундах від початку епохи CLOCK_MONOTONIC:

* `FirmwareTimestampMonotonic`: Початок виконання коду прошивки UEFI.
* `LoaderTimestampMonotonic`: Початок виконання двійкового файлу завантажувача.
* `KernelTimestampMonotonic`: Точка входу `startup_64` (завжди `0`).
* `InitRDTimestampMonotonic`: Початок розгортання раннього простору `initramfs`.
* `UserspaceTimestampMonotonic`: Системний виклик `switch_root` і передача керування PID 1.
* `FinishTimestampMonotonic`: Досягнення цільового юніта `default.target` (система готова).

Тривалість кожної фази обчислюється як різниця між сусідніми мітками. Наприклад, чистий час виконання скриптів раннього простору initramfs дорівнює різниці `UserspaceTimestampMonotonic - InitRDTimestampMonotonic`. Чистий час роботи PID 1 до моменту появи запрошення входу обчислюється як `FinishTimestampMonotonic - UserspaceTimestampMonotonic`.

## Алгоритм побудови критичного ланцюга (Critical Chain)

Для визначення найповільнішого шляху ініціалізації служб застосовується алгоритм пошуку найдовшого шляху в орієнтованому ациклічному графі залежностей (DAG):

1. **Збирання стану юнітів:** Для кожного активного юніта зчитуються мітки `ActiveEnterTimestampMonotonic` (час переходу в стан запуску) та `ActiveExitTimestampMonotonic` (час завершення або готовності).
2. **Топологічне сортування:** Будується дерево залежностей за ребрами `Requires=`, `Wants=` та `After=`.
3. **Рекурсивний спуск від цілі:** Починаючи від `default.target`, алгоритм перевіряє всіх прямих попередників (юніти, зазначені в `After=`), знаходячи службу, яка завершилася найпізніше безпосередньо перед активацією цілі.
4. **Виділення критичного ребра:** Ця процедура повторюється рекурсивно до досягнення `sysinit.target`, утворюючи критичний ланцюг безперервного послідовного блокування.

Головна перевага пошуку критичного шляху перед простим упорядкуванням `systemd-analyze blame` полягає в тому, що тривалі фонові задачі (наприклад індексація бази даних або створення фонових пулів пам'яті), які виконуються асинхронно й не блокують інші служби, повністю ігноруються аналізатором. Це дозволяє зосередити зусилля інженера саме на тих службах, оптимізація яких безпосередньо наближає появу вікна входу.

## Системні таймери ядра Linux: Monotonic проти Boottime

Під час аналізу тривалості завантаження важливо розрізняти апаратні та програмні джерела часу в ядрі Linux:

* `CLOCK_REALTIME`: Астрономічний час (Wall Clock). Може стрибати вперед або назад під час синхронізації через NTP (`systemd-timesyncd`). Категорично непридатний для вимірювання інтервалів завантаження.
* `CLOCK_MONOTONIC`: Монотонний таймер, що стартує з нуля в мить старту ядра. Не зазнає стрибків NTP, але зупиняє свій хід, коли комп'ютер переходить у стан глибокого сну (*Suspend to RAM*).
* `CLOCK_BOOTTIME`: Розширений монотонний таймер, який продовжує відлік навіть під час перебування системи в режимі сну. Саме цей годинник використовується `systemd` для розрахунку загального життєвого циклу хоста.
* **Апаратний лічильник TSC:** 64-бітний регістр процесора, що інкрементується на кожному такті ядра CPU. На сучасних процесорах з підтримкою *Invariant TSC* частота лічильника залишається суворо постійною незалежно від зміни частоти ядер енергозберігаючими технологіями SpeedStep або Turbo Boost.
* **Таймери HPET та ACPI-PM:** Апаратні таймери материнської плати з фіксованою частотою (зазвичай 14.318 МГц для HPET). Використовуються ядром на ранніх фазах для калібрування лічильника TSC процесора до того, як буде налаштовано переривання локального таймера APIC.

## Простеження пам'яті та алокатора memblock на ранніх стадіях

До ініціалізації сторінкового менеджера `mm_init()` ядро не може використовувати стандартні функції `kmalloc()` або `alloc_pages()`. Усі запити на виділення фізичної пам'яті (для структур ACPI, таблиць IDT, буферів декомпресії) обслуговує ранній лінійний алокатор `memblock`.

Для дослідження розподілу фізичних діапазонів пам'яті інженер може передати ядру параметр `memblock=debug`. Ядро друкує докладний протокол резервування адресних просторів у буфер `dmesg`:
* Додавання фізичних зон (`memblock_add`): реєстрація регіонів пам'яті, знайдених прошивкою в таблиці E820;
* Резервування зон (`memblock_reserve`): блокування областей, де розміщено код ядра, структури `boot_params` та образ `initramfs`;
* Передача пам'яті алокатору Buddy (`memblock_free_all`): фінальне звільнення нерезервованих сторінок фізичної RAM у розпорядження повноцінного сторінкового алокатора ядра.

## Простеження дискового вводу-виводу на фазі switch_root

Критичним фактором тривалості старту простору користувача є швидкість читання двійкових файлів та динамічних бібліотек із фізичного диска. Після виклику `switch_root` кеш сторінок (*Page Cache*) оперативної пам'яті практично порожній: ядро повинно зчитати з диска двійковий файл `systemd`, базову бібліотеку `libc.so`, конфігураційні файли в `/etc/` та скомпільовані юніти.

Для простеження затримок блокового вводу-виводу використовують підсистему ядра `ftrace` та точки трасування блокового рівня:
* `block:block_bio_queue`: фіксує момент відправки запиту блокового вводу-виводу підсистемою VFS;
* `block:block_rq_issue`: момент передачі запиту контролеру диска через чергу NVMe Submission Queue;
* `block:block_rq_complete`: отримання підтвердження від апаратного контролера в NVMe Completion Queue.

Різниця між цими мітками показує чисту апаратну затримку накопичувача та виявляє ситуації, коли випадкове читання тисяч дрібних конфігураційних файлів призводить до черги блокувань введення-виведення.

## Практичний аналіз відхилень у вбудованих та хмарних системах

Отримання телеметрії дає змогу виявити специфічні аномалії в різних класах обчислювальних платформ:

### Випадок 1: Вбудовані пристрої (Automotive / Industrial IoT)

У автомобільних інформаційно-розважальних системах (IVI) та промислових контролерах норматив часу появи камери заднього виду чи інтерфейсу керування становить менше двох секунд від подачі живлення. Аналіз телеметрії показує такі типові вузькі місця:
* Повільна декомпресія ядра: перехід із алгоритму `xz` на нестиснений образ `Image` або швидкий `zstd` заощаджує до 800 мс процесорного часу.
* Зайві модулі в initramfs: сканування шин у `systemd-udevd` забирає понад 1.5 секунди. Рішення полягає у відмові від generic-образів і компіляції драйверів накопичувача eMMC безпосередньо в монолітне ядро, що дозволяє монтувати корінь без виклику initramfs.
* Заміна важких менеджерів на спеціалізовані демони: відмова від `NetworkManager` на користь легкого `systemd-networkd` скорочує фазу простору користувача з 4 секунд до 250 мс.

### Випадок 2: Хмарні безсерверні мікро-ВМ (Serverless / AWS Firecracker)

У сучасних хмарних середовищах функції Function-as-a-Service (FaaS) вимагають холодного старту нової віртуальної машини за 5–15 мілісекунд. Для досягнення таких показників архітектура завантаження кардинально спрощується:
* Гіпервізор Firecracker не емулює BIOS/UEFI й не запускає завантажувач GRUB: він записує нестиснений бінарник `vmlinux` безпосередньо у виділений сегмент RAM гостьової машини.
* Регістри процесора ініціалізуються одразу в 64-бітному режимі з готовими таблицями сторінок MMU, минаючи етапи Real Mode та Protected Mode.
* Замість повноцінного диска монтується образ у пам'яті через віртуальну шину `virtio-block`, а ядро запускає єдиний скомпільований бінарник обробника запитів як процес PID 1 (`init=/usr/bin/handler`), скорочуючи час завантаження до 8 мілісекунд.

## Інструкція зі збирання та тестування

Для компіляції обох варіантів програми потрібен стандартний набір компіляторів GCC або Clang:

```bash
# Збирання варіанту мовою C:
gcc -O2 -Wall -Wextra -pedantic boot_trace.c -o boot_trace_c

# Збирання варіанту мовою C++ (вимагає стандарту C++20):
g++ -std=c++20 -O2 -Wall -Wextra -pedantic boot_trace.cpp -o boot_trace_cpp
```

### Приклад виконання на робочій станції UEFI

Запуск скомпільованої утиліти на сервері під керуванням Ubuntu 24.04 LTS демонструє такий результат:

```
====================================================
    АНАЛІЗАТОР ТЕЛЕМЕТРІЇ ЗАВАНТАЖЕННЯ LINUX        
====================================================

[+] Режим прошивки: UEFI (доступний інтерфейс efivars)
    * Час прошивки UEFI (SEC/PEI/DXE): 1.842 с
    * Час завантажувача (GRUB/systemd-boot): 1.120 с

[+] Параметри ядра (/proc/cmdline):
    * Кореневий пристрій (root):  UUID=a8b3f140-5e29-4d6b-9c71-33215890abcd
    * Первинний процес (init):    /sbin/init (типовий)
    * Цільовий юніт (target):     graphical.target

[+] Системний час (Uptime): 1420.50 с

[+] Оцінка часового бюджету завантаження:
----------------------------------------------------
 Етап                      Тривалість      Частка   
----------------------------------------------------
 Прошивка (Firmware):       1.842 с         24.7%
 Завантажувач (Loader):     1.120 с         15.0%
 Ядро + Userspace (оцінка): 4.500 с         60.3%
----------------------------------------------------
```

## Інтерпретація бюджету завантаження та оптимізація

Отримані метрики вказують на конкретні напрямки оптимізації завантаження:

1. **Якщо прошивка (Firmware) займає > 5 секунд:**
   * Основна затримка припадає на фазу DXE: тривалий пошук мережевих завантажувачів (PXE Boot) або опитування повільних шин накопичувачів.
   * *Метод оптимізації:* Увімкнення режиму `Fast Boot` в BIOS, вимкнення невикористовуваних контролерів SATA/SAS та встановлення першим у списку `BootOrder` системного накопичувача NVMe.
2. **Якщо завантажувач (Loader) займає > 3 секунд:**
   * Затримка викликана очікуванням таймауту меню завантажувача (`timeout 5` у `grub.cfg`) або повільним читанням шрифтів і графічних тем з розділу ESP.
   * *Метод оптимізації:* Встановлення `GRUB_TIMEOUT=0` або перехід на легкий завантажувач `systemd-boot` / монолітні образи UKI.
3. **Якщо ядро та initramfs займають > 4 секунд:**
   * Затримка спричинена декомпресією занадто великого образу initramfs або очікуванням виявлення повільних дисків у `udevd`.
   * *Метод оптимізації:* Перехід на алгоритм стиснення `zstd -19` для initramfs, створення монолітного initramfs без зайвих драйверів через `dracut --hostonly`.
4. **Якщо простір користувача (Userspace) займає > 10 секунд:**
   * Затримка спричинена послідовними блокуваннями у критичному ланцюгу `systemd-analyze critical-chain` (наприклад очікуванням мережі `NetworkManager-wait-online.service`).
   * *Метод оптимізації:* Переведення служб на активацію за сокетом (*Socket Activation*), вимкнення синхронного очікування мережі та оптимізація таймаутів дисків у `/etc/fstab`.

## Автоматизація тестування завантаження в CI/CD

Для запобігання регресіям швидкодії у процесі розробки вбудованих прошивок або ядер ОС створюють автоматизовані тести на базі QEMU:

```bash
qemu-system-x86_64 \
    -kernel arch/x86/boot/bzImage \
    -initrd initramfs.cpio.zst \
    -append "console=ttyS0 root=/dev/ram0 panic=1" \
    -nographic \
    -serial mon:stdio \
    -device isa-debug-exit,iobase=0xf4,iosize=0x04
```

Скрипт тестування зчитує вивід послідовного порту, фіксує мітку часу першого виклику userspace і перевіряє відповідність заданому SLA завантаження. Якщо тривалість перевищує допустимий ліміт, збірка у CI автоматично маркується як невдала.

## Крайові випадки телеметрії завантаження

* **Завантаження через `kexec`:** Якщо ядро було запущено без апаратного перезавантаження через механізм `kexec` (наприклад під час аварійного дампу kdump), прошивка UEFI та завантажувач не виконуються. У цьому разі змінні `LoaderTime*` або відсутні, або містять застарілі дані попереднього холодного старту.
* **Мікроконтейнери та хмарні Hypervisor-віртуальні машини:** У середовищах AWS Firecracker або QEMU microvm фази UEFI та завантажувача повністю усунуті: гіпервізор записує ядро безпосередньо у віртуальну пам'ять гостьового процесора і запускає його зі стану 64-бітного режиму за лічені мілісекунди.
