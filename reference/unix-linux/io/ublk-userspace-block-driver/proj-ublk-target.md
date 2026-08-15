# ⚙️ Реалізація ublk-таргета мовами C та C++

Створення власного блокового пристрою у просторі користувача за допомогою фреймворку ublk вимагає взаємодії з офіційною бібліотекою `libublksrv`. Ця бібліотека надає високорівневу абстракцію над низькорівневими механізмами `io_uring` та керуючим символьним пристроєм `/dev/ublkc*`, вивільняючи розробника від необхідності вручну керувати кільцевими буферами SQ/CQ та формувати командні структури `IORING_OP_URING_CMD`.

Основою будь-якого ublk-таргета є callback-функція обробки запитів вводу-виводу (зазвичай звана `queue_rq` або `handle_io`). Ця функція викликається бібліотекою `libublksrv` кожного разу, коли ядро Linux передає новий блоковий запит через Completion Queue (CQ) інтерфейсу `io_uring`. 

## Механіка обробки запитів та параметри I/O

Кожен запит, переданий у callback-функцію, описується двома головними аргументами: вказівником на чергу `struct ublksrv_queue` та вказівником на дані запиту `struct ublk_io_data`. З об'єкта метаданих `data->desc` розробник вилучає ключові параметри I/O-операції:

1. **Тип операції (`ublksrv_get_op`)**: визначає, яку саме дію вимагає ядро. Найчастішими є `UBLK_IO_OP_READ` (читання даних з пристрою) та `UBLK_IO_OP_WRITE` (запис даних на пристрій). Додатково підтримуються спеціальні операції `UBLK_IO_OP_FLUSH` (скидання внутрішніх кешів накопичувача), `UBLK_IO_OP_DISCARD` (аналог команд TRIM/UNMAP для вивільнення блоків) та `UBLK_IO_OP_WRITE_ZEROES` (швидке обнулення діапазонів секторів).
2. **Початковий сектор (`ublksrv_get_sector`)**: номер 512-байтного сектора, з якого починається операція. Щоб отримати зсув у байтах у внутрішньому сховищі або файлі, номер сектора зсувається на 9 біт вліво (`sector << 9`).
3. **Обсяг даних (`ublksrv_get_nr_bytes`)**: розмір трансферу в байтах. Розмір завжди кратний логічному розміру блока пристрою — 512 байтів за замовчуванням або 4096, якщо таргет оголосив саме такий логічний блок.
4. **Буфер даних (`ublksrv_get_io_buf`)**: повертає вказівник на пам'ять у просторі користувача, в яку необхідно прочитати дані або з якої слід взяти дані для запису. У режимі Zero-Copy цей буфер безпосередньо відображає фізичні сторінки пам'яті користувацького застосунку.

Після завершення обробки даних (наприклад, виконання `memcpy` для RAM-диска або відправки пакету по мережі) таргет зобов'язаний повідомити ядро про результати. Це виконується за допомогою функції `ublksrv_complete_io(q, data, res)`. Аргумент `res` передає кількість успішно переданих байтів або від'ємний код помилки POSIX (наприклад, `-EIO` при збої або `-EINVAL` при неправильному зсуві).

## Ініціалізація та багатопоточна обробка

Для запуску таргета демон створює об'єкт керування `ublksrv_dev`. Процес ініціалізації охоплює визначення кількості апаратних черг (hardware queues), глибини кожної черги (queue depth) та налаштування прапорів пристрою:

- **Кількість черг (`nr_hw_queues`)**: для досягнення максимальної продуктивності створюється по одній черзі на кожне ядро CPU.
- **Глибина черги (`queue_depth`)**: кількість одночасних запитів, які ядро може тримати в черзі (зазвичай від 64 до 512).
- **Прив'язка до ядер (CPU affinity)**: потік обробки кожної черги прив'язується до конкретного ядра CPU, що дозволяє уникнути міжядерної синхронізації й тримати кеш L1/L2 гарячим.

## Практична реалізація: C проти C++

Нижче наведено паралельні приклади реалізації ublk RAM-диска на 64 МБ. Версія на мові C демонструє безпосереднє використання низькорівневого C API `libublksrv`, тоді як версія на мові C++ загортає сховище у безпечний клас з використанням `std::vector`, RAII-управління ресурсами, безпечних зрізів `std::span` та викликів без винятків (`noexcept`).

:::tabs
```c
#include <ublksrv.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>

#define RAMDISK_SIZE (64 * 1024 * 1024) // 64 MB

struct ramdisk_ctx {
    char *data;
};

static int ramdisk_handle_io(const struct ublksrv_queue *q,
                             const struct ublk_io_data *data)
{
    struct ramdisk_ctx *ctx = (struct ramdisk_ctx *)ublksrv_get_queue_app_data(q);
    const struct ublksrv_io_desc *desc = data->desc;

    uint32_t op = ublksrv_get_op(desc);
    uint64_t sector = ublksrv_get_sector(desc);
    uint32_t nr_bytes = ublksrv_get_nr_bytes(desc);
    uint64_t offset = sector << 9;

    void *buf = ublksrv_get_io_buf(q, data);

    if (offset + nr_bytes > RAMDISK_SIZE) {
        ublksrv_complete_io(q, data, -EIO);
        return 0;
    }

    if (op == UBLK_IO_OP_READ) {
        memcpy(buf, ctx->data + offset, nr_bytes);
    } else if (op == UBLK_IO_OP_WRITE) {
        memcpy(ctx->data + offset, buf, nr_bytes);
    }

    ublksrv_complete_io(q, data, nr_bytes);
    return 0;
}

int main(int argc, char *argv[])
{
    struct ramdisk_ctx ctx;
    ctx.data = (char *)calloc(1, RAMDISK_SIZE);
    if (!ctx.data) {
        perror("calloc");
        return 1;
    }

    struct ublksrv_dev *dev = ublksrv_dev_init(0, ramdisk_handle_io, &ctx);
    if (!dev) {
        fprintf(stderr, "Помилка ініціалізації ublk пристрою\n");
        free(ctx.data);
        return 1;
    }

    printf("ublk RAM-диск успішно створено, розмір: %d MB\n", RAMDISK_SIZE / (1024 * 1024));
    ublksrv_start_dev(dev);

    ublksrv_dev_deinit(dev);
    free(ctx.data);
    return 0;
}
```
```cpp
#include <ublksrv.h>
#include <algorithm>
#include <cerrno>
#include <iostream>
#include <vector>
#include <memory>
#include <span>
#include <cstdint>

class UblkRamdiskTarget {
public:
    explicit UblkRamdiskTarget(std::size_t size_bytes)
        : storage_(size_bytes, 0) {}

    int handle_io(const struct ublksrv_queue* q, const struct ublk_io_data* data) noexcept {
        const auto* desc = data->desc;
        const uint32_t op = ublksrv_get_op(desc);
        const uint64_t offset = ublksrv_get_sector(desc) << 9;
        const uint32_t nr_bytes = ublksrv_get_nr_bytes(desc);

        if (offset + nr_bytes > storage_.size()) {
            ublksrv_complete_io(q, data, -EIO);
            return 0;
        }

        auto* io_buf = static_cast<std::byte*>(ublksrv_get_io_buf(q, data));
        std::span<std::byte> buffer(io_buf, nr_bytes);
        std::span<std::byte> storage_span(reinterpret_cast<std::byte*>(storage_.data()) + offset, nr_bytes);

        if (op == UBLK_IO_OP_READ) {
            std::copy(storage_span.begin(), storage_span.end(), buffer.begin());
        } else if (op == UBLK_IO_OP_WRITE) {
            std::copy(buffer.begin(), buffer.end(), storage_span.begin());
        }

        ublksrv_complete_io(q, data, nr_bytes);
        return 0;
    }

    [[nodiscard]] std::size_t size() const noexcept { return storage_.size(); }

private:
    std::vector<uint8_t> storage_;
};

int main() {
    constexpr std::size_t disk_size = 64 * 1024 * 1024; // 64 MB
    auto target = std::make_unique<UblkRamdiskTarget>(disk_size);

    auto io_callback = [](const struct ublksrv_queue* q, const struct ublk_io_data* data) -> int {
        auto* instance = static_cast<UblkRamdiskTarget*>(ublksrv_get_queue_app_data(q));
        return instance->handle_io(q, data);
    };

    struct ublksrv_dev* dev = ublksrv_dev_init(0, io_callback, target.get());
    if (!dev) {
        std::cerr << "Помилка ініціалізації ublk пристрою у C++" << std::endl;
        return 1;
    }

    std::cout << "ublk C++ RAM-диск запущено: " << target->size() / (1024 * 1024) << " MB" << std::endl;
    ublksrv_start_dev(dev);

    ublksrv_dev_deinit(dev);
    return 0;
}
```
:::

## Аналіз відмінностей та ідіом C++

При порівнянні C та C++ реалізацій звертають на себе увагу кілька ключових відмінностей у підходах до проектування системного коду:

1. **Керування пам'яттю**: У версії C виділення пам'яті під сховище відбувається через `calloc`, що вимагає ручного відстеження помилок виділення та обов'язкового виклику `free()` на всіх шляхах завершення програми. У версії на C++ за виділення відповідає `std::vector<uint8_t>`, а сам таргет загортається у `std::unique_ptr`, забезпечуючи концепцію RAII (Resource Acquisition Is Initialization). При виході з функції пам'ять буде звільнена автоматично без ризику витоків.
2. **Безпека типів та зрізи пам'яті**: Сирий вказівник `void*` у C замінюється в C++ на `std::span<std::byte>`. Обгортка `std::span` не копіює дані, але зберігає довжину буфера та дозволяє використовувати безпечні алгоритми `std::copy` замість `memcpy`, запобігаючи помилкам виходу за межі масиву (buffer overflow).
3. **Обробка винятків**: Оскільки callback-функції викликаються з C-коду бібліотеки `libublksrv`, виклик винятку C++ (`throw`) через C-рамку призвів би до невизначеної поведінки (`undefined behavior`). Тому функція-обробник C++ позначена як `noexcept`, гарантуючи, що всі помилки повертаються як коди статусу POSIX.
4. **Крайові випадки та обробка помилок**: Якщо зсув виходить за межі виділеної пам'яті RAM-диска (`offset + nr_bytes > size`), обидва приклади викликають `ublksrv_complete_io(q, data, -EIO)`, передаючи в блокову підсистему Linux код помилки вводу-виводу (просто `-1` тут був би `-EPERM`). Операційна система отримує системний результат помилки вводу-виводу без краху демона.

## Права доступу та непривілейовані пристрої

Створення пристроїв ublk за замовчуванням вимагає прав суперкористувача (`CAP_SYS_ADMIN`). Проте сучасні версії ublk підтримують прапор `UBLK_F_UNPRIVILEGED_DEV`.

Завдяки цьому прапору демон може бути запущений у непривілейованому контейнері або під звичайним користувачем, якщо пристрій `/dev/ublk-control` має відповідні права `udev`. Це суттєво підвищує безпеку хмарних середовищ Kubernetes, оскільки таргет-демон не потребує системних привілеїв root для обслуговування своїх віртуальних дисків.
