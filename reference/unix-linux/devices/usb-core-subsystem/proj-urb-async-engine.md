# ⚙️ Асинхронний двигун обміну через URB

Усунення блокування обчислювальних потоків під час очікування апаратних відповідей шини USB є критичною інженерною задачею при побудові високопродуктивних систем введення-виведення. Використання псевдофайлової системи ядра `usbfs` (USB Filesystem) у поєднанні з неблокувальним асинхронним механізмом URB (USB Request Block) дозволяє виключити простій процесорних ядер, реалізувати конвеєризацію запитів та забезпечити граничну пропускну здатність каналу зв'язку в реальному часі.

---

## Проблема продуктивності синхронного I/O та переваги асинхронних URB

При розробці систем комп'ютерного зору (опитування вебкамер високої чіткості), програмно-визначених радіосистем (SDR) або швидких вимірювальних приладів розробники нерідко стикаються з межею продуктивності синхронних викликів.

При використанні блокуючого синхронного підходу (наприклад, викликів `libusb_bulk_transfer` або блокуючих читань з файлового дескриптора) потік виконання програми занурюється в сон на час апаратного обміну пакетами по шині. У цей проміжок часу шина USB залишається порожньою між завершенням одного пакета та підготовкою наступного системного виклику у юзерспейсі. Цей паузовий інтервал називається **простоєм шини (Bus Idle Time)**. На високошвидкісних шинах USB 3.x (5–10 Гбіт/с) простій у кілька мікросекунд між пакетами відчутно знижує реальну пропускну здатність і призводить до систематичної втрати кадрів (Frame Drops).

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

1. `USBDEVFS_CLAIMINTERFACE`: Запитує у ядра `usbcore` право на володіння конкретним інтерфейсом пристрою (`struct usb_interface`). Якщо до цього інтерфейсу вже прив'язаний ядерний драйвер, виклик падає з `errno = EBUSY`; від'єднати драйвер можна окремою командою `USBDEVFS_DISCONNECT`.
2. `USBDEVFS_SUBMITURB`: Приймає покажчик на структуру `struct usbdevfs_urb`. Ядро перевіряє права доступу, виділяє внутрішній об'єкт `struct urb`, готує придатний для DMA буфер (власний — або, якщо пам'ять отримано через `mmap()` цього самого файлу, безпосередньо юзерспейсну) та відправляє транзакцію в чергу HCD. Виклик повертає керування **негайно**.
3. `USBDEVFS_REAPURBNDELAY`: Перевіряє чергу завершених транзакцій. Якщо є готові URB, функція записує покажчик на завершений `struct usbdevfs_urb` у передану змінну і повертає `0`. Якщо готових пакетів немає, повертає `-1` зі значенням `errno = EAGAIN`.
4. `USBDEVFS_RELEASEINTERFACE`: Звільняє володіння інтерфейсом та повертає його під контроль ядра.

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
    if (ioctl(fd, USBDEVFS_CLAIMINTERFACE, &interface_num) < 0) {
        perror("Помилка захоплення інтерфейсу USBDEVFS_CLAIMINTERFACE");
        close(fd);
        return EXIT_FAILURE;
    }

    struct async_transfer transfers[NUM_URBS];
    memset(transfers, 0, sizeof(transfers));

    /* Ініціалізація та асинхронна відправка пакетів URB */
    for (int i = 0; i < NUM_URBS; ++i) {
        transfers[i].id = i;
        transfers[i].urb.type = USBDEVFS_URB_TYPE_BULK;
        transfers[i].urb.endpoint = ENDPOINT_IN;
        transfers[i].urb.buffer = transfers[i].buffer;
        transfers[i].urb.buffer_length = BUFFER_SIZE;
        transfers[i].urb.usercontext = &transfers[i];

        if (ioctl(fd, USBDEVFS_SUBMITURB, &transfers[i].urb) < 0) {
            perror("Помилка відправки USBDEVFS_SUBMITURB");
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
        while (ioctl(fd, USBDEVFS_REAPURBNDELAY, &reaped_urb) == 0) {
            struct async_transfer *st = (struct async_transfer *)reaped_urb->usercontext;
            printf("[✓] URB #%d завершено: статус=%d, отримано=%d байтів\n",
                   st->id, reaped_urb->status, reaped_urb->actual_length);
            completed_urbs++;
        }
    }

release_and_close:
    ioctl(fd, USBDEVFS_RELEASEINTERFACE, &interface_num);
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

        if (::ioctl(fd_, USBDEVFS_CLAIMINTERFACE, &interface_num_) < 0) {
            ::close(fd_);
            throw std::system_error(errno, std::generic_category(), "Помилка захоплення інтерфейсу через usbfs");
        }
    }

    ~UsbDeviceHandle() noexcept {
        if (fd_ >= 0) {
            ::ioctl(fd_, USBDEVFS_RELEASEINTERFACE, &interface_num_);
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
        urb.type = USBDEVFS_URB_TYPE_BULK;
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
            if (::ioctl(device.native_handle(), USBDEVFS_SUBMITURB, &transfer->urb) < 0) {
                throw std::system_error(errno, std::generic_category(), "Помилка відправки USBDEVFS_SUBMITURB");
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
            while (::ioctl(device.native_handle(), USBDEVFS_REAPURBNDELAY, &reaped) == 0) {
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

У версії мовою C вивільнення ресурсів при виникненні помилки здійснюється через класичний ядерний паттерн `goto release_and_close`. Якщо під час виконання `ioctl(USBDEVFS_SUBMITURB)` виникає помилка, потік виконання стрибає на мітку очищення, де послідовно звільняє інтерфейс та закриває дескриптор.

У версії на C++20 управління файловим дескриптором та інтерфейсом повністю загорнуто у RAII-клас `UsbDeviceHandle`. Деструктор класу гарантує виклики `USBDEVFS_RELEASEINTERFACE` та `close()` при виході з області видимості за будь-яких умов, включно з виникненням винятків `std::system_error`.

### 2. Керування пам'яттю буферів і копіювання

Обидві реалізації виділяють буфери у просторі користувача (масив `unsigned char buffer[]` у C або `std::vector<uint8_t>` у C++).

Покажчик на цей буфер передається в ядро у полі `urb.buffer`. За замовчуванням `usbfs` не віддає контролеру юзерспейсну пам'ять напряму: на кожен URB ядро бере власний придатний для DMA буфер і копіює дані між ним і буфером програми. Справжнє нульове копіювання доступне лише тоді, коли буфер отримано через `mmap()` того самого файлу `/dev/bus/usb/BBB/DDD` — тоді контролер працює з тією ж фізичною пам'яттю, і зайвого `memcpy` не відбувається.

### 3. Очікування подій та неблокуючий збір (Reaping)

Файловий дескриптор `/dev/bus/usb/BBB/DDD` сигналізує подією `POLLOUT`, щойно в черзі з'явиться хоча б один завершений URB, готовий до збирання, — саме тому в `pollfd` вказано `POLLOUT`.

Програма занурюється в сон у системному виклику `poll()`, не споживаючи ресурсів процесора. Як тільки `poll()` повертає керування, програма викликає `USBFS_REAPURBNDELAY` у внутрішньому циклі `while`. Оскільки один сигнал переривання може відповідати завершенню одразу кількох пакетів URB, внутрішній цикл `while` зчитує всі готові пакети доти, доки `ioctl` не поверне `-1` зі значенням `errno = EAGAIN`.

---

## Крайові випадки та обробка помилок

При експлуатації асинхронних двигунів у реальних умовах слід враховувати такі крайові ситуації:

1. **Раптове відключення пристрою (Unplug Event)**: Якщо користувач висмикнув кабель під час активного обміну, виклик `poll()` негайно поверне прапорець `POLLHUP` або `POLLERR`. Спроба викликати `USBDEVFS_REAPURBNDELAY` поверне всі відправлені URB зі статусом `reaped_urb->status = -ENODEV` або `-ESHUTDOWN`.
2. **Короткі пакети (Short Packets)**: Якщо пристрій надіслав менше байтів, ніж розмір буфера `buffer_length`, обмін вважається успішно завершеним. Фактичну кількість отриманих байтів слід зчитувати з поля `reaped_urb->actual_length`.
3. **Вирівнювання пам'яті (DMA Alignment)**: Для досягнення максимальної швидкості на архітектурах x86_64 та ARM64 буфери пам'яті `transfer_buffer` рекомендовано вирівнювати по межі 64 байтів (розмір лінії кешу L1/L2) за допомогою `posix_memalign()` або `std::aligned_alloc()`.
