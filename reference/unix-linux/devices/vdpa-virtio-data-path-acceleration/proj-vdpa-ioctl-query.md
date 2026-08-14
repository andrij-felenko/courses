# ⚙️ Практична програма для інспектування vDPA-пристрою через ioctl

Цей практичний приклад демонструє створення повноцінної утиліти для низькорівневої діагностики та опитування апаратного vDPA-пристрою через символьний файл `/dev/vhost-vdpa-0`. Розроблена програма відкриває файловий дескриптор, запитує у ядра тип пристрою virtio, вичитає узгоджені апаратні можливості (features), поточний статус автомата станів virtio та зчитує MAC-адресу з конфігураційного простору мережевого контролера.

## Завдання та послідовність дій утиліти

Для прямої взаємодії з vDPA-пристроєм у користувацькому просторі без залучення гіпервізора QEMU програма реалізує чітку послідовність системних викликів:

1. **Відкриття пристрою:** Виклик `open()` відкриває вузол `/dev/vhost-vdpa-0` у режимі читання та запису (`O_RDWR`). Файловий дескриптор уособлює відкритий сеанс зв'язку з драйвером `vhost-vdpa`.
2. **Запит типу пристрою:** Виклик `ioctl(fd, VHOST_VDPA_GET_DEVICE_ID, &device_id)` запитує числовий ідентифікатор типу пристрою. Стандарт virtio визначає ID `1` для мережевих адаптерів (`virtio-net`) та `2` для блочних дискових накопичувачів (`virtio-blk`).
3. **Опитування апаратних можливостей:** Виклик `ioctl(fd, VHOST_GET_FEATURES, &features)` отримує 64-бітову маску прапорців, які описують підтримувані SmartNIC функції (наприклад, підтримка упакованих кілець `VIRTIO_F_RING_PACKED` або чексумми `VIRTIO_NET_F_CSUM`).
4. **Перевірка стану пристрою:** Виклик `ioctl(fd, VHOST_VDPA_GET_STATUS, &status)` запитує поточний байт статусу (наприклад, прапорці `ACKNOWLEDGE`, `DRIVER`, `DRIVER_OK`).
5. **Зчитання конфігураційного простору:** Для пристроїв `virtio-net` програма формує структуру `vhost_vdpa_config` зі зсувом `off = 0` та довжиною `len = 6`, після чого викликає `ioctl(fd, VHOST_VDPA_GET_CONFIG, &cfg)` для отримання запрограмованої апаратної MAC-адреси.
6. **Звільнення ресурсів:** Закриття дескриптора при завершенні програми.

Утиліту реалізовано двома мовами у вкладках нижче: у класичному стилі C із прямим керуванням ресурсами та в ідіоматичному C++23 із використанням обгортки RAII для файлового дескриптора, типізованих буферів `std::span` та сучасної бібліотеки форматування `std::format`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <stdint.h>
#include <linux/vhost.h>
#include <linux/virtio_ids.h>

#define VDPA_DEV_PATH "/dev/vhost-vdpa-0"

int main(void) {
    int fd = open(VDPA_DEV_PATH, O_RDWR);
    if (fd < 0) {
        perror("Не вдалося відкрити " VDPA_DEV_PATH);
        return EXIT_FAILURE;
    }

    uint32_t device_id = 0;
    if (ioctl(fd, VHOST_VDPA_GET_DEVICE_ID, &device_id) < 0) {
        perror("Помилка VHOST_VDPA_GET_DEVICE_ID");
        close(fd);
        return EXIT_FAILURE;
    }

    printf("[+] vDPA Device ID: %u (%s)\n", device_id,
           device_id == VIRTIO_ID_NET ? "virtio-net" :
           device_id == VIRTIO_ID_BLOCK ? "virtio-blk" : "інший");

    uint64_t features = 0;
    if (ioctl(fd, VHOST_GET_FEATURES, &features) < 0) {
        perror("Помилка VHOST_GET_FEATURES");
        close(fd);
        return EXIT_FAILURE;
    }
    printf("[+] HW Feature Bits: 0x%llx\n", (unsigned long long)features);

    uint8_t status = 0;
    if (ioctl(fd, VHOST_VDPA_GET_STATUS, &status) < 0) {
        perror("Помилка VHOST_VDPA_GET_STATUS");
        close(fd);
        return EXIT_FAILURE;
    }
    printf("[+] Device Status Byte: 0x%02x\n", status);

    if (device_id == VIRTIO_ID_NET) {
        struct {
            uint32_t off;
            uint32_t len;
            uint8_t buf[6];
        } cfg = { .off = 0, .len = 6 };

        if (ioctl(fd, VHOST_VDPA_GET_CONFIG, &cfg) < 0) {
            perror("Помилка VHOST_VDPA_GET_CONFIG");
            close(fd);
            return EXIT_FAILURE;
        }

        printf("[+] Hardware MAC Address: %02x:%02x:%02x:%02x:%02x:%02x\n",
               cfg.buf[0], cfg.buf[1], cfg.buf[2],
               cfg.buf[3], cfg.buf[4], cfg.buf[5]);
    }

    close(fd);
    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <format>
#include <span>
#include <array>
#include <cstdint>
#include <system_error>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/vhost.h>
#include <linux/virtio_ids.h>

class ScopedFd {
public:
    explicit ScopedFd(int fd) noexcept : fd_(fd) {}
    ~ScopedFd() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }
    ScopedFd(const ScopedFd&) = delete;
    ScopedFd& operator=(const ScopedFd&) = delete;
    ScopedFd(ScopedFd&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }
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
    int fd_ = -1;
};

int main() {
    constexpr const char* dev_path = "/dev/vhost-vdpa-0";
    ScopedFd dev{::open(dev_path, O_RDWR)};

    if (!dev.valid()) {
        std::cerr << std::format("Не вдалося відкрити {}: {}\n",
                                 dev_path, std::generic_category().message(errno));
        return EXIT_FAILURE;
    }

    std::uint32_t device_id = 0;
    if (::ioctl(dev.get(), VHOST_VDPA_GET_DEVICE_ID, &device_id) < 0) {
        std::cerr << "Помилка VHOST_VDPA_GET_DEVICE_ID\n";
        return EXIT_FAILURE;
    }

    std::string_view type_str = (device_id == VIRTIO_ID_NET)   ? "virtio-net" :
                                (device_id == VIRTIO_ID_BLOCK) ? "virtio-blk" : "інший";

    std::cout << std::format("[+] vDPA Device ID: {} ({})\n", device_id, type_str);

    std::uint64_t features = 0;
    if (::ioctl(dev.get(), VHOST_GET_FEATURES, &features) < 0) {
        std::cerr << "Помилка VHOST_GET_FEATURES\n";
        return EXIT_FAILURE;
    }
    std::cout << std::format("[+] HW Feature Bits: {:#x}\n", features);

    std::uint8_t status = 0;
    if (::ioctl(dev.get(), VHOST_VDPA_GET_STATUS, &status) < 0) {
        std::cerr << "Помилка VHOST_VDPA_GET_STATUS\n";
        return EXIT_FAILURE;
    }
    std::cout << std::format("[+] Device Status Byte: {:#04x}\n", status);

    if (device_id == VIRTIO_ID_NET) {
        struct ConfigHeader {
            std::uint32_t off;
            std::uint32_t len;
            std::array<std::uint8_t, 6> mac;
        } cfg{.off = 0, .len = 6, .mac = {}};

        if (::ioctl(dev.get(), VHOST_VDPA_GET_CONFIG, &cfg) < 0) {
            std::cerr << "Помилка VHOST_VDPA_GET_CONFIG\n";
            return EXIT_FAILURE;
        }

        std::span<const std::uint8_t, 6> mac_span{cfg.mac};
        std::cout << std::format("[+] Hardware MAC Address: {:02x}:{:02x}:{:02x}:{:02x}:{:02x}:{:02x}\n",
                                 mac_span[0], mac_span[1], mac_span[2],
                                 mac_span[3], mac_span[4], mac_span[5]);
    }

    return EXIT_SUCCESS;
}
```
:::

## Опис архітектури коду та софтверних обгорток

Наведена програма показує фундаментальну відмінність між підходами системного програмування на мовах C та C++ при взаємодії з ядерними інтерфейсами:

1. **Управління ресурсами (RAII vs Manual Cleanup):** Приклад мовою C вимагає явного відстеження всіх точок виходу з функції та гарантованого викликання `close(fd)` у кожній гілці обробки помилок. У версії C++ створено обгортку `ScopedFd`, яка реалізує семантику переміщення (move semantics) та гарантує закриття файлового дескриптора у деструкторі при виході зі області видимості (зокрема при виникненні винятків).
2. **Типізація та безпека буферів:** Режим C спирається на анонімні структури з гнучкими масивами байтів. Версія C++ використовує безпечний типізований масив `std::array<std::uint8_t, 6>` та представлення `std::span`, що унеможливлює вихід за межі виділеної пам'яті при форматуванні MAC-адреси.
3. **Обробка та форматування системних помилок:** Для відображення системних помилок системних викликів C++ використовує метод `std::generic_category().message(errno)`, що інтегрує коди помилок POSIX із сучасною бібліотекою форматування `std::format`.

## Механізм конструювання системних команд ioctl

Усі команди сімейства `VHOST_VDPA_*` конструюються за допомогою ядерних макросів `_IOR`, `_IOW` та `_IOWR`, які кодують у 32-бітовому цілому числі напрямок передачі даних, розмір аргументу та магічний номер типу (`VHOST_VIRTIO = 0xAF`):

- **`_IOR(VHOST, 0x70, __u32)`:** Команда зчитування (`_IOR`), яка кодує передачу 4-байтового ідентифікатора пристрою з ядра в простір користувача.
- **`_IOW(VHOST, 0x72, __u8)`:** Команда запису (`_IOW`), яка передає 1-байтовий статус автомата станів із простору користувача у ядро.
- **`_IOWR(VHOST, 0x73, struct vhost_vdpa_config)`:** Двонаправлена команда (`_IOWR`), де користувацька програма передає зсув та довжину бувера, а ядро заповнює масив результатами з апаратних регістрів SmartNIC.

## Аналіз бітів можливостей (Features Negotiation)

Причинний зв'язок між зчитаною бітовою маскою `features` та внутрішнім автоматом станів SmartNIC є вирішальним для продуктивності:

- **Прапор `VIRTIO_F_RING_PACKED` (Bit 34):** Вказує на підтримку упакованих кілець дескрипторів. Якщо прапорець встановлено у `1`, апаратне забезпечення переходить у високопродуктивний режим обробки єдиного масиву дескрипторів.
- **Прапор `VIRTIO_NET_F_MRG_RXBUF` (Bit 15):** Дозволяє пристрою об'єднувати кілька буферів гостя для прийому великих мережевих пакетів (Jumbo Frames).
- **Прапор `VIRTIO_F_VERSION_1` (Bit 32):** Гарантує відповідність стандарту Virtio 1.0+ з Little-Endian кодуванням усіх структур у пам'яті.

## Синхронізація з автоматикою системного адміністрування

При автоматизованому розгортанні віртуальних машин у середовищі Kubernetes (KubeVirt) або OpenStack описана діагностична утиліта може бути зкомпільована як легковажний перевірочник готовності (readiness probe). Вона перевіряє факт появи та коректної конфігурації апаратного вузла `/dev/vhost-vdpa-0` перед тим, як контейнер віртуалізації отримає доступ до пристрою, запобігаючи помилкам ініціалізації KVM під час старту пода.

## Часті помилки та пастки системного програмування

Під час розробки програм для роботи з підсистемою `vhost-vdpa` слід враховувати декілька потенційних пасток:

- **Права доступу до системного символьного файлу:** Символьний файл `/dev/vhost-vdpa-N` створюється підсистемою `udev` із власником `root:root` та маскою `0600`. Для надання прав непривілейованим користувачам необхідно додати відповідні правила `udev` (наприклад, `KERNEL=="vhost-vdpa-*", GROUP="kvm", MODE="0660"`).
- **Помилки `EINVAL` при виклику `VHOST_VDPA_GET_CONFIG`:** Помилка `EINVAL` виникає у випадку, коли сума `off + len` у переданій структурі перевищує фактичний розмір конфігураційного простору, який драйвер апаратного забезпечення оголосив через колбек `get_config_size()`.
- **Конфлікт захоплення пристрою кількома процесами:** Файловий дескриптор `/dev/vhost-vdpa-N` призначений для одночасної роботи лише одного екземпляра гіпервізора. Якщо файл вже відкрито й налаштовано QEMU, виклик `VHOST_SET_OWNER` поверне помилку `EBUSY`.
