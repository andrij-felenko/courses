# ⚙️ Динамічне усунення хиб USB-пристрою та програмне скидання шини

Коли нестандартний або бракований пристрій USB під'єднується до робочої станції чи промислового сервера, системний інженер часто стикається з помилками нумерації (enumeration), раптовими таймаутами вводу-виводу або зависанням контролера після виходу з режиму енергозбереження. Перезбирання ядра Linux заради додавання одного рядка в таблицю `usb_quirk_list[]` є надто тривалим, ризикованим і часто неприпустимим процесом на виробничих серверах або вбудованих платформах без компілятора. Цей практичний проект демонструє повний інженерний цикл усунення апаратних відхилень: діагностику помилок за допомогою системних журналів ядра, розрахунок бітової маски відхилень, динамічне застосування прапорців через параметри `usbcore` у файловій системі `sysfs`, а також написання користувацької утиліти мовами C та C++ для програмного скидання порту USB через інтерфейс `usbfs`.

## 1. Сценарій проблеми та збір діагностичних даних

Розглянемо типовий практичний випадок: зовнішній апаратний USB-модуль на базі мікроконтролера FX2 (Vendor ID: `0x04b4`, Product ID: `0x8613`) або нестандартний вимірювальний прилад після під'єднання до порту комп'ютера видає помилки у кільцевому буфері ядра `dmesg`:

```text
[  142.105432] usb 1-1.2: new high-speed USB device number 14 using xhci_hcd
[  142.235118] usb 1-1.2: unable to read config index 0 descriptor/all
[  147.355021] usb 1-1.2: can't set config #1, error -110
[  147.355102] usb 1-1.2: USB disconnect, device number 14
```

Код помилки `-110` (`-ETIMEDOUT`) свідчить про те, що хост-контролер не отримав відповіді на керувальний запит протягом стандартного 5-секундного вікна таймауту. Внутрішній кінцевий автомат мікроконтролера перейшов у стан невизначеності або взаємного блокування. Основні причини такої поведінки:

1. **Повільна ініціалізація прошивки:** Контролер пристрою після отримання апаратного імпульсу скидання порту занадто повільно стабілізує свій внутрішній тактовий генератор PLL та завантажує таблиці векторів переривань із зовнішньої мікросхеми EEPROM. Якщо хост надсилає запит `GET_DESCRIPTOR` раніше ніж через 200 мс, пристрій просто не готовий відповісти (для виправлення потрібен прапорець `USB_QUIRK_DELAY_INIT`).
2. **Зависання на нульовому альтернативному налаштуванні:** Пристрій має лише один фіксований режим роботи без альтернативних інтерфейсів. Коли ядро надсилає стандартний запит `SET_INTERFACE (Interface = 0, AltSetting = 0)`, мікропрограма пристрою повертає помилку `STALL` або намертво зависає (потрібен прапорець `USB_QUIRK_NO_SET_INTF`).
3. **Некоректний вихід із режиму сну:** Підсистема керування живленням хосту переводить неактивний порт у стан низького енергоспоживання `runtime suspend`. Контролер пристрою втрачає синхронізацію фазового автопідстроювання частоти і не здатний відновити передачу без повного апаратного перезавантаження (потрібен прапорець `USB_QUIRK_NO_AUTOSUSPEND`).

Для отримання повної ієрархії дескрипторів та перевірки наявності кінцевих точок виконуємо детальне опитування:

```bash
# Опитування конфігурації пристрою через утиліту lsusb
lsusb -d 04b4:8613 -v
```

Якщо пристрій зависає настільки швидко, що `lsusb` не встигає зчитати дані, слід увімкнути низькорівневе трасування USB-пакетів через модуль `usbmon`:

```bash
# Підключення модуля трасування та читання сирих подій шини USB 1
sudo modprobe usbmon
sudo cat /sys/kernel/debug/usb/usbmon/1u | head -n 30
```

## 2. Розрахунок прапорців та динамічне застосування через sysfs

Для повного усунення збоїв комбінуємо три прапорці ядра з довідника `include/linux/usb/quirks.h`:
- `USB_QUIRK_DELAY_INIT` (маска `0x00000040`, літерний код `g`);
- `USB_QUIRK_NO_SET_INTF` (маска `0x00000004`, літерний код `c`);
- `USB_QUIRK_NO_AUTOSUSPEND` (маска `0x00400000`, літерний код `r`).

Об'єднана шістнадцяткова маска розраховується порозрядним логічним «АБО»:
```text
0x00000040 | 0x00000004 | 0x00400000 = 0x00400044
```

У параметрах ядра можна використовувати як компактний символьний запис `gcr`, так і пряме шістнадцяткове число `0x400044`.

### Застосування прапорців наживо через sysfs без перезавантаження

Файлова система `sysfs` надає інтерфейс запису для параметра `quirks` модуля `usbcore`:

```bash
# Запис правила для мікроконтролера FX2 у ядро
echo "04b4:8613:gcr" | sudo tee /sys/module/usbcore/parameters/quirks
```

Якщо проблема стосується USB-накопичувача (наприклад, дефектного моста SATA-USB з VID `174c` та PID `55aa`, який зависає при використанні протоколу UAS), прапорець `US_FL_IGNORE_UAS` (`u`) передається у відповідний параметр драйвера `usb-storage`:

```bash
# Примусове відключення UAS та відкат на протокол Bulk-Only Transport
echo "174c:55aa:u" | sudo tee /sys/module/usb-storage/parameters/quirks
```

Після запису в `sysfs` ядро додає вказаний запис до динамічного зв'язного списку. Кожне наступне під'єднання пристрою з цими VID/PID автоматично отримає скориговані прапорці.

## 3. Програмне скидання шини через інтерфейс usbfs (C та C++)

Після запису нових прапорців у `sysfs` уже під'єднаний пристрій залишається у попередньому стані зі старими налаштуваннями. Щоб змусити ядро повторно виконати повний цикл нумерації без фізичного витягування кабелю з роз'єму, необхідно ініціювати апаратне скидання порту.

В операційній системі Linux це реалізується через інтерфейс `usbfs` (`/dev/bus/usb/BBB/DDD`) за допомогою системного виклику `ioctl` із кодом `USBDEVFS_RESET`. Коли цей системний виклик надходить у драйвер `drivers/usb/core/devio.c`, ядро тимчасово блокує введення-виведення, викликає функцію `usb_reset_device()`, генерує сигнал Single-Ended Zero (SE0) на порту концентратора та заново опитує дескриптори пристрою, активуючи нові прапорці quirks.

Нижче наведено повноцінну утиліту `usb_reset_tool`, яка сканує дерево шини `/dev/bus/usb`, ідентифікує пристрій за 18-байтовим дескриптором і надсилає запит скидання.

:::tabs
```c
// usb_reset_tool.c — Скидання USB-пристрою через USBDEVFS_RESET (чистий C)
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <dirent.h>
#include <sys/ioctl.h>
#include <linux/usbdevice_fs.h>
#include <errno.h>

static int find_and_reset_usb(int target_vid, int target_pid) {
    const char *usb_base = "/dev/bus/usb";
    DIR *bus_dir = opendir(usb_base);
    if (!bus_dir) {
        perror("Помилка відкриття /dev/bus/usb");
        return -1;
    }

    struct dirent *bus_entry;
    int found = 0;

    while ((bus_entry = readdir(bus_dir)) != NULL) {
        if (bus_entry->d_name[0] == '.') continue;

        char bus_path[256];
        snprintf(bus_path, sizeof(bus_path), "%s/%s", usb_base, bus_entry->d_name);

        DIR *dev_dir = opendir(bus_path);
        if (!dev_dir) continue;

        struct dirent *dev_entry;
        while ((dev_entry = readdir(dev_dir)) != NULL) {
            if (dev_entry->d_name[0] == '.') continue;

            char dev_path[512];
            snprintf(dev_path, sizeof(dev_path), "%s/%s", bus_path, dev_entry->d_name);

            int fd = open(dev_path, O_RDWR);
            if (fd < 0) continue;

            // Зчитування стандартного 18-байтового дескриптора пристрою
            unsigned char desc[18];
            if (read(fd, desc, sizeof(desc)) == sizeof(desc)) {
                int vid = desc[8] | (desc[9] << 8);
                int pid = desc[10] | (desc[11] << 8);

                if (vid == target_vid && pid == target_pid) {
                    printf("Знайдено пристрій %04x:%04x на %s\n", vid, pid, dev_path);
                    printf("Виконання USBDEVFS_RESET ioctl...\n");

                    if (ioctl(fd, USBDEVFS_RESET, 0) < 0) {
                        fprintf(stderr, "Помилка ioctl USBDEVFS_RESET: %s\n", strerror(errno));
                        close(fd);
                        closedir(dev_dir);
                        closedir(bus_dir);
                        return -1;
                    }

                    printf("Скидання USB-пристрою успішно завершено.\n");
                    found = 1;
                    close(fd);
                    break;
                }
            }
            close(fd);
        }
        closedir(dev_dir);
        if (found) break;
    }

    closedir(bus_dir);
    if (!found) {
        fprintf(stderr, "Пристрій %04x:%04x не знайдено на шині USB.\n", target_vid, target_pid);
        return -1;
    }
    return 0;
}

int main(int argc, char *argv[]) {
    if (argc < 3) {
        fprintf(stderr, "Використання: %s <VID_hex> <PID_hex>\n", argv[0]);
        fprintf(stderr, "Приклад: %s 04b4 8613\n", argv[0]);
        return 1;
    }

    int vid = (int)strtol(argv[1], NULL, 16);
    int pid = (int)strtol(argv[2], NULL, 16);

    return find_and_reset_usb(vid, pid) == 0 ? 0 : 1;
}
```
```cpp
// usb_reset_tool.cpp — Скидання USB-пристрою (ідіоматичний C++20 з RAII)
#include <iostream>
#include <filesystem>
#include <fstream>
#include <vector>
#include <string>
#include <string_view>
#include <expected>
#include <system_error>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/usbdevice_fs.h>

namespace fs = std::filesystem;

class ScopedFd {
public:
    explicit ScopedFd(int fd = -1) noexcept : fd_(fd) {}
    ~ScopedFd() { if (fd_ >= 0) ::close(fd_); }

    ScopedFd(const ScopedFd&) = delete;
    ScopedFd& operator=(const ScopedFd&) = delete;

    ScopedFd(ScopedFd&& other) noexcept : fd_(other.fd_) { other.fd_ = -1; }
    ScopedFd& operator=(ScopedFd&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

private:
    int fd_;
};

struct UsbDeviceId {
    uint16_t vid;
    uint16_t pid;
};

class UsbResetter {
public:
    static std::expected<void, std::string> reset_device(UsbDeviceId target) {
        const fs::path usb_base{"/dev/bus/usb"};
        if (!fs::exists(usb_base)) {
            return std::unexpected("Каталог /dev/bus/usb не знайдено в системі");
        }

        for (const auto& bus_entry : fs::directory_iterator(usb_base)) {
            if (!bus_entry.is_directory()) continue;

            for (const auto& dev_entry : fs::directory_iterator(bus_entry.path())) {
                if (!dev_entry.is_character_file()) continue;

                ScopedFd dev_fd{::open(dev_entry.path().c_str(), O_RDWR)};
                if (!dev_fd.valid()) continue;

                std::vector<uint8_t> desc(18);
                ssize_t bytes_read = ::read(dev_fd.get(), desc.data(), desc.size());
                if (bytes_read == static_cast<ssize_t>(desc.size())) {
                    uint16_t vid = static_cast<uint16_t>(desc[8] | (desc[9] << 8));
                    uint16_t pid = static_cast<uint16_t>(desc[10] | (desc[11] << 8));

                    if (vid == target.vid && pid == target.pid) {
                        std::cout << "Знайдено пристрій [" << std::hex << vid << ":" << pid
                                  << "] на шляху: " << dev_entry.path() << std::dec << "\n";
                        std::cout << "Виконання запиту USBDEVFS_RESET...\n";

                        if (::ioctl(dev_fd.get(), USBDEVFS_RESET, 0) < 0) {
                            return std::unexpected(std::string("Помилка ioctl USBDEVFS_RESET: ") + 
                                                   std::generic_category().message(errno));
                        }

                        std::cout << "Скидання порту успішно виконано.\n";
                        return {};
                    }
                }
            }
        }
        return std::unexpected("Пристрій із вказаними VID:PID не знайдено");
    }
};

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "Використання: " << argv[0] << " <VID_hex> <PID_hex>\n"
                  << "Приклад: " << argv[0] << " 04b4 8613\n";
        return 1;
    }

    try {
        uint16_t vid = static_cast<uint16_t>(std::stoul(argv[1], nullptr, 16));
        uint16_t pid = static_cast<uint16_t>(std::stoul(argv[2], nullptr, 16));

        auto result = UsbResetter::reset_device({vid, pid});
        if (!result.has_value()) {
            std::cerr << "Збій: " << result.error() << "\n";
            return 1;
        }
    } catch (const std::exception& ex) {
        std::cerr << "Помилка аргументів: " << ex.what() << "\n";
        return 1;
    }

    return 0;
}
```
:::

### Порівняльний аналіз реалізацій C та C++

Реалізація мовою C спирається на класичні POSIX-виклики `opendir()`, `readdir()` та `open()`, вимагаючи ручного закриття дескрипторів файлів і каталогів у кожній гілці виходу з функції через явні оператори або мітки очищення ресурсів.

Реалізація мовою C++ демонструє сучасний системний підхід:
1. **Автоматичне керування ресурсами (RAII):** Клас-обгортка `ScopedFd` гарантує детерміноване закриття дескриптора `/dev/bus/usb/...` через деструктор навіть при виникненні винятків чи передчасних поверненнях із функцій.
2. **Безпечна робота з файловою системою:** Модуль `std::filesystem` інкапсулює ітерацію каталогами ядра без ризику витоку пам'яті структур `DIR*`.
3. **Обробка помилок без винятків:** Шаблон `std::expected` чітко розмежовує успішний результат операції скидання та текстовий опис системної помилки на основі `std::generic_category()`.

## 4. Альтернативні методи перезавантаження пристрою у просторі користувача

Окрім прямого скидання через `ioctl`, адміністратор може керувати життєвим циклом пристрою за допомогою псевдофайлів `sysfs`:

- **Примусове відв'язування та повторна прив'язка драйвера (Driver Re-bind):**
  Якщо необхідно перезапустити лише функціональний драйвер (наприклад, `cdc_acm`), не перериваючи фізичне живлення порту:
  ```bash
  # Від'єднання інтерфейсу від драйвера
  echo "1-1.2:1.0" | sudo tee /sys/bus/usb/drivers/cdc_acm/unbind
  # Повторна прив'язка з новими прапорцями
  echo "1-1.2:1.0" | sudo tee /sys/bus/usb/drivers/cdc_acm/bind
  ```

- **Логічне вимкнення та повторна авторизація порту (USB Authorization):**
  Атрибут `authorized` дозволяє ядрам Linux 2.6.34+ логічно знеструмлювати пристрій:
  ```bash
  # Логічне від'єднання пристрою від шини
  echo 0 | sudo tee /sys/bus/usb/devices/1-1.2/authorized
  # Повторна авторизація та запуск нумерації з нуля
  echo 1 | sudo tee /sys/bus/usb/devices/1-1.2/authorized
  ```

## 5. Повна автоматизація за допомогою правил udev та верифікація

Щоб налаштування відхилень застосовувалися автоматично при кожному під'єднанні нестандартного пристрою в будь-який порт системи, створюємо правило для демона `udev` у файлі `/etc/udev/rules.d/99-usb-quirks.rules`:

```udev
# Автоматичне встановлення прапорців quirks для контролера FX2
ACTION=="add", SUBSYSTEM=="usb", ATTR{idVendor}=="04b4", ATTR{idProduct}=="8613", \
    RUN+="/bin/sh -c 'echo 04b4:8613:gcr > /sys/module/usbcore/parameters/quirks'"

# Автоматичне вимкнення UAS для моста ASMedia
ACTION=="add", SUBSYSTEM=="usb", ATTR{idVendor}=="174c", ATTR{idProduct}=="55aa", \
    RUN+="/bin/sh -c 'echo 174c:55aa:u > /sys/module/usb-storage/parameters/quirks'"
```

Після створення файлу перезавантажуємо конфігурацію підсистеми udev:

```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

Тепер після фізичного під'єднання пристрою або запуску утиліти `usb_reset_tool` перевіряємо системний журнал ядра через `dmesg`:

```text
[  210.450123] usb 1-1.2: new high-speed USB device number 15 using xhci_hcd
[  210.965412] usb 1-1.2: Delaying initial device setup by 500ms (quirk delay_init active)
[  211.512304] usb 1-1.2: Skipping set_interface for default setting (quirk no_set_intf active)
[  211.520110] usb 1-1.2: Disabling autosuspend (quirk no_autosuspend active)
[  211.530452] usb 1-1.2: New USB device found, idVendor=04b4, idProduct=8613, bcdDevice= 0.01
[  211.530460] usb 1-1.2: New USB device strings: Mfr=1, Product=2, SerialNumber=0
[  211.530464] usb 1-1.2: Product: Cypress FX2 USB Device
[  211.535901] cdc_acm 1-1.2:1.0: ttyACM0: USB ACM device
```

Системний журнал наочно підтверджує успішну активацію всіх призначених прапорців: ядро витримало необхідну затримку стабілізації живлення, пропустило аварійний запит `SET_INTERFACE` та заблокувало механізм динамічного засинання. У результаті пристрій стабільно розпізнано і прив'язано до драйвера віртуального послідовного порту `ttyACM0` без необхідності внесення змін до вихідного коду ядра чи перезбирання операційної системи.
