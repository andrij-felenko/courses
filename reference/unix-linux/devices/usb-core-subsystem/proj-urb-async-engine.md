# ⚙️ Асинхронний двигун обміну через URB

Усунення блокування обчислювальних потоків під час очікування апаратних відповідей шини USB є критичною інженерною задачею при побудові високопродуктивних систем введення-виведення. Використання псевдофайлової системи ядра `usbfs` (USB Filesystem) у поєднанні з неблокувальним асинхронним механізмом URB (USB Request Block) дозволяє виключити простій процесорних ядер, реалізувати конвеєризацію запитів із нульовим копіюванням буферів (Zero-Copy DMA) та забезпечити граничну пропускну здатність каналу зв'язку в реальному часі.

---

## Проблема продуктивності синхронного I/O та переваги асинхронних URB

При розробці систем комп'ютерного зору (опитування вебкамер високої чіткості), програмно-визначених радіосистем (SDR) або швидких вимірювальних приладів розробники нерідко стикаються з межею продуктивності синхронних викликів.

При використанні блокуючого синхронного підходу (наприклад, викликів `libusb_bulk_transfer` або блокуючих читань з файлового дескриптора) потік виконання програми занурюється в сон на час апаратного обміну пакетами по шині. У цей проміжок часу шина USB залишається порожньою між завершенням одного пакета та підготовкою наступного системного виклику у юзерспейсі. Цей паузовий інтервал називається **простоєм шини (Bus Idle Time)**. На високошвидкісних шинах USB 3.x (5–10 Гбіт/с) простій у кілька мікросекунд призводить до падіння реальної пропускної здатності на 30–50% та систематичної втрати кадрів (Frame Drops).

```
Синхронний підхід (Паузи та простій шини):
[Submit URB 1] ──> [Bus Transfer 1] ──> [IRQ] ──> [User Awake] ──> (PAUSE) ──> [Submit URB 2]

Асинхронний підхід (Конвеєризація без простою):
[Submit URB 1, 2, 3, 4] ──> [Bus Transfer 1][Bus Transfer 2][Bus Transfer 3]...
                              ▲ IRQ Reaping у тлі без зупинки шини
```

Асинхронний двигун усуває простій шини за рахунок **попереднього заповнення кільця транзакцій (Queue Depth)**. Програма створює пул з 4–16 пакетів URB і передає їх у ядро одночасно. Коли контролер HCD завершує обробку першого пакета, він негайно переходить до виконання другого пакета з апаратної черги без участі процесора, а програма у просторі користувача паралельно збирає вже готові буфери.

---

## Внутрішній механізм інтерфейсу `usbfs`

Підсистема ядра `usbcore` розкриває прямий доступ до пристроїв шини через символьні файли нод `/dev/bus/usb/BBB/DDD` (де `BBB` — номер шини, `DDD` — адреса пристрою).

Взаємодія з цим файлом здійснюється за допомогою системних викликів `ioctl()` зі спеціальними командами:

1. `USBFS_CLAIMINTERFACE`: Запитує у ядра `usbcore` право на володіння конкретним інтерфейсом пристрою (`struct usb_interface`). Якщо до цього інтерфейсу був прив'язаний ядерний драйвер, ядро поверне помилку `-EBUSY` (із юзерспейсу можна попередньо викликати `USBFS_DISCONNECT` для від'єднання ядерного драйвера).
2. `USBFS_SUBMITURB`: Приймає покажчик на структуру `struct usbdevfs_urb`. Ядро перевіряє права доступу, виділяє внутрішній об'єкт `struct urb`, виконує пряме DMA-відображення буфера пам'яті юзерспейсу (`transfer_buffer`) у фізичні сторінки та відправляє транзакцію в чергу HCD. Виклик повертає керування **негайно**.
3. `USBFS_REAPURBNDELAY`: Перевіряє апаратне кільце завершених транзакцій. Якщо є готові URB, функція записує покажчик на завершений `struct usbdevfs_urb` у передану змінну і повертає `0`. Якщо готових пакетів немає, функція негайно повертає `-EAGAIN`.
4. `USBFS_RELEASEINTERFACE`: Звільняє володіння інтерфейсом та повертає його під контроль ядра.

---

## Практична реалізація: C та C++

У цьому розділі наведено повноцінний реалізаційний код асинхронного двигуна обміну через `usbfs`. Код реалізовано у двох незалежних вкладках: класичний ідіоматичний C та сучасний об'єктно-орієнтований C++20 з використанням RAII-управління ресурсами.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <sys/poll.h>
#include <linux/usbdevice_fs.h>

#define NUM_URBS 4
#define BUFFER_SIZE 64
#define ENDPOINT_IN 0x81

struct async_transfer {
    struct usbdevfs_urb urb;
    unsigned char buffer[BUFFER_SIZE];
    int id;
};

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s /dev/bus/usb/001/002\n", argv[0]);
        return EXIT_FAILURE;
    }

    int fd = open(argv[1], O_RDWR);
    if (fd < 0) {
        perror("Не вдалося відкрити пристрій USB");
        return EXIT_FAILURE;
    }

    /* Запитуємо володіння інтерфейсом 0 у usbcore */
    int interface_num = 0;
    if (ioctl(fd, USBFS_CLAIMINTERFACE, &interface_num) < 0) {
        perror("Помилка захоплення інтерфейсу USBFS_CLAIMINTERFACE");
        close(fd);
        return EXIT_FAILURE;
    }

    struct async_transfer transfers[NUM_URBS];
    memset(transfers, 0, sizeof(transfers));

    /* Ініціалізація та асинхронна відправка пакетів URB */
    for (int i = 0; i < NUM_URBS; ++i) {
        transfers[i].id = i;
        transfers[i].urb.type = USBFS_URB_TYPE_BULK;
        transfers[i].urb.endpoint = ENDPOINT_IN;
        transfers[i].urb.buffer = transfers[i].buffer;
        transfers[i].urb.buffer_length = BUFFER_SIZE;
        transfers[i].urb.usercontext = &transfers[i];

        if (ioctl(fd, USBFS_SUBMITURB, &transfers[i].urb) < 0) {
            perror("Помилка відправки USBFS_SUBMITURB");
            goto release_and_close;
        }
        printf("[+] Асинхронний URB #%d успішно відправлено до usbcore\n", i);
    }

    /* Головний цикл обробки результатів */
    int completed_urbs = 0;
    struct pollfd pfd = { .fd = fd, .events = POLLOUT };

    while (completed_urbs < NUM_URBS) {
        int poll_ret = poll(&pfd, 1, 2000);
        if (poll_ret < 0) {
            perror("Помилка виклику poll()");
            break;
        } else if (poll_ret == 0) {
            fprintf(stderr, "Таймаут очікування завершення URB\n");
            break;
        }

        struct usbdevfs_urb *reaped_urb = NULL;
        while (ioctl(fd, USBFS_REAPURBNDELAY, &reaped_urb) == 0) {
            struct async_transfer *st = (struct async_transfer *)reaped_urb->usercontext;
            printf("[✓] URB #%d завершено: статус=%d, отримано=%d байтів\n",
                   st->id, reaped_urb->status, reaped_urb->actual_length);
            completed_urbs++;
        }
    }

release_and_close:
    ioctl(fd, USBFS_RELEASEINTERFACE, &interface_num);
    close(fd);
    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <vector>
#include <memory>
#include <span>
#include <system_error>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/poll.h>
#include <linux/usbdevice_fs.h>

class UsbDeviceHandle {
    int fd_{-1};
    int interface_num_{0};

public:
    explicit UsbDeviceHandle(const std::string& path, int interface_num = 0)
        : interface_num_(interface_num) {
        fd_ = ::open(path.c_str(), O_RDWR);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити USB-пристрій");
        }

        if (::ioctl(fd_, USBFS_CLAIMINTERFACE, &interface_num_) < 0) {
            ::close(fd_);
            throw std::system_error(errno, std::generic_category(), "Помилка захоплення інтерфейсу USBFS");
        }
    }

    ~UsbDeviceHandle() noexcept {
        if (fd_ >= 0) {
            ::ioctl(fd_, USBFS_RELEASEINTERFACE, &interface_num_);
            ::close(fd_);
        }
    }

    UsbDeviceHandle(const UsbDeviceHandle&) = delete;
    UsbDeviceHandle& operator=(const UsbDeviceHandle&) = delete;

    [[nodiscard]] int native_handle() const noexcept { return fd_; }
};

struct UrbTransfer {
    usbdevfs_urb urb{};
    std::vector<uint8_t> buffer;
    std::size_t id{0};

    explicit UrbTransfer(std::size_t id_val, std::size_t size, uint8_t endpoint)
        : buffer(size, 0), id(id_val) {
        urb.type = USBFS_URB_TYPE_BULK;
        urb.endpoint = endpoint;
        urb.buffer = buffer.data();
        urb.buffer_length = static_cast<int>(buffer.size());
        urb.usercontext = this;
    }
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " /dev/bus/usb/001/002\n";
        return EXIT_FAILURE;
    }

    try {
        UsbDeviceHandle device(argv[1], 0);
        constexpr std::size_t kNumUrbs = 4;
        constexpr std::size_t kBufferSize = 64;
        constexpr uint8_t kEndpointIn = 0x81;

        std::vector<std::unique_ptr<UrbTransfer>> transfers;
        transfers.reserve(kNumUrbs);

        /* Відправлення асинхронних пакетів через RAII контексти */
        for (std::size_t i = 0; i < kNumUrbs; ++i) {
            auto transfer = std::make_unique<UrbTransfer>(i, kBufferSize, kEndpointIn);
            if (::ioctl(device.native_handle(), USBFS_SUBMITURB, &transfer->urb) < 0) {
                throw std::system_error(errno, std::generic_category(), "Помилка відправки USBFS_SUBMITURB");
            }
            std::cout << "[+] Асинхронний URB #" << i << " надіслано в usbcore\n";
            transfers.push_back(std::move(transfer));
        }

        /* Цикл очікування подій через poll() */
        std::size_t completed = 0;
        ::pollfd pfd{ .fd = device.native_handle(), .events = POLLOUT, .revents = 0 };

        while (completed < kNumUrbs) {
            int ret = ::poll(&pfd, 1, 2000);
            if (ret < 0) {
                throw std::system_error(errno, std::generic_category(), "Помилка poll()");
            } else if (ret == 0) {
                std::cerr << "Таймаут очікування USBFS подій\n";
                break;
            }

            ::usbdevfs_urb* reaped{nullptr};
            while (::ioctl(device.native_handle(), USBFS_REAPURBNDELAY, &reaped) == 0) {
                auto* st = static_cast<UrbTransfer*>(reaped->usercontext);
                std::cout << "[✓] URB #" << st->id << " завершено: status="
                          << reaped->status << ", actual_length=" << reaped->actual_length << "\n";
                completed++;
            }
        }

    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << "\n";
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
```
:::

---

## Детальний розбір реалізації та порівняння мовних моделей

### 1. Управління ресурсами (RAII vs goto cleanup)

У версії мовою C вивільнення ресурсів при виникненні помилки здійснюється через класичний ядерний паттерн `goto release_and_close`. Якщо під час виконання `ioctl(USBFS_SUBMITURB)` виникає помилка, потік виконання стрибає на мітку очищення, де послідовно звільняє інтерфейс та закриває дескриптор.

У версії на C++20 управління файловим дескриптором та інтерфейсом повністю загорнуто у RAII-клас `UsbDeviceHandle`. Деструктор класу гарантує виклики `USBFS_RELEASEINTERFACE` та `close()` при виході з області видимості за будь-яких умов, включно з виникненням винятків `std::system_error`.

### 2. Керування пам'яттю буферів (Zero-Copy DMA)

Обидві реалізації використовують принцип **Zero-Copy**. Буфери пам'яті виділяються у просторі користувача (структура `unsigned char buffer[]` у C або `std::vector<uint8_t>` у C++).

Покажчик на цей буфер передається в ядро у полі `urb.buffer`. Під час виклику `USBFS_SUBMITURB` ядро Linux pinned-страничками закріплює цей буфер у фізичній пам'яті і передає його фізичну адресу безпосередньо у кільце дескрипторів TRB контролера xHCI. Таким чином, передача даних з фізичного порту USB у буфер вашої програми відбувається взагалі без проміжного копіювання процесором (`memcpy`).

### 3. Очікування подій та неблокуючий збір (Reaping)

Файловий дескриптор `/dev/bus/usb/BBB/DDD` сигналізує про готовність до читання (подія `POLLOUT` або `POLLIN`), коли хост-контролер генерує переривання про завершення хоча б одного URB.

Програма занурюється в сон у системному виклику `poll()`, не споживаючи ресурсів процесора. Як тільки `poll()` повертає керування, програма викликає `USBFS_REAPURBNDELAY` у внутрішньому циклі `while`. Оскільки один сигнал переривання може відповідати завершенню одразу кількох пакетів URB, внутрішній цикл `while` зчитує всі готові пакети до тих пір, поки `ioctl` не поверне помилку `-EAGAIN`.

---

## Крайові випадки та обробка помилок

При експлуатації асинхронних двигунів у реальних умовах слід враховувати такі крайові ситуації:

1. **Раптове відключення пристрою (Unplug Event)**: Якщо користувач висмикнув кабель під час активного обміну, виклик `poll()` негайно поверне поверне прапорець `POLLHUP` або `POLLERR`. Спроба викликати `USBFS_REAPURBNDELAY` поверне всі підпорядковані URB зі статусом `reaped_urb->status = -ENODEV` або `-ESHUTDOWN`.
2. **Короткі пакети (Short Packets)**: Якщо пристрій надіслав менше байтів, ніж розмір буфера `buffer_length`, обмін вважається успішно завершеним. Фактичну кількість отриманих байтів слід зчитувати з поля `reaped_urb->actual_length`.
3. **Вирівнювання пам'яті (DMA Alignment)**: Для досягнення максимальної швидкості на архітектурах x86_64 та ARM64 буфери пам'яті `transfer_buffer` рекомендовано вирівнювати по межі 64 байтів (розмір лінії кешу L1/L2) за допомогою `posix_memalign()` або `std::aligned_alloc()`.
