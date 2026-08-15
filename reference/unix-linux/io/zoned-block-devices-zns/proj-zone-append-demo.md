# ⚙️ Багатонитковий запис через Zone Append та zonefs

Файлова система `zonefs` та апаратна команда `Zone Append` у специфікації NVMe ZNS дозволяють розробникам реалізувати високоефективні системи паралельного дописування даних (Log-Structured Write) без використання дорогих хостових блокувань (Mutexes) на рівні зон.

---

## 1. Постановка задачі та архітектурні виклики

При побудові високонавантажених журналів баз даних (WAL) або незмінних SSTable-файлів у базах даних типу RocksDB декілька робочих ниток процесу намагаються одночасно записувати фрагменти даних в одну й ту саму зонову ділянку носія.

На традиційному блоковому пристрої кожна нитка виконує `pwrite(fd, buf, len, offset)`. Оскільки довільний запис дозволено, операційна система та контролер накопичувача паралельно обробляють запити до різних зміщень. 

На зонованому блоковому пристрої Host-Managed спроба двох ниток одночасно відправити звичайний `write()` за поточною адресою Write Pointer викликає гонитву (Race Condition). Перший запит, що дійде до пристрою, змістить вказівник WP, а другий запит дійде до пристрою з застарілим зміщенням LBA та буде апаратно відхилений з помилкою `Unaligned Write`.

Використання хостового м'ютексу серіалізує запити, але примушує кожну нитку чекати завершення попередньої операції вводу-виводу (I/O Round-Trip Latency), знижуючи пропускну здатність з гігабайтів до кількох мегабайтів на секунду.

### Розв'язання через `zonefs` та `O_APPEND`

Файлова система `zonefs` відображає кожну SWR-зону як окремий файл у каталозі `seq/`. 

Коли додаток відкриває файл-зону з прапорцями `O_APPEND | O_DIRECT`, ядро Linux перетворює звичайний системний виклик `write()` на операцію `REQ_OP_ZONE_APPEND`; буферизований запис такої трансляції не дає й іде звичайними `WRITE` зі сторінкового кешу. Операційна система не вказує точний LBA запису в самій команді — вона передає контролеру пристрою лише початковий сектор зони (`Zone Start LBA`).

Контролер NVMe SSD приймає запити у свій апаратний мульти-черговий конвеєр, самостійно атомарно призначає поточний доступний LBA для кожного блоку, зміщує WP та повертає фактично призначений LBA у відповіді на Completion Queue. Це гарантує нульові очікування блокувань на хості.

---

## 2. Реалізація мовами C та C++

Наведені нижче приклади демонструють повний цикл маніпуляцій із файлом-зоною у `zonefs`: відкриття, скидання зони у стан `Empty` через `ftruncate(fd, 0)` (що транслюється у команду `Reset Zone`) та паралельне дописування вирівняних за розміром сектора блоків пам'яті.

Для забезпечення максимальної швидкості та оминання сторінкового кешу Linux (Page Cache) ми використовуємо прапорець `O_DIRECT`. Це вимагає від прикладного коду обов'язкового вирівнювання адреси буфера пам'яті у просторі користувача за допомогою системного виклику `posix_memalign()` на межу фізичного сектора (4096 байтів).

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <errno.h>

#define SECTOR_SIZE 4096

// Функція виконує безпечне відкриття, скидання та запис у файл-зону zonefs
int write_to_zone_c(const char *zone_file_path, const void *buffer, size_t len) {
    if (len % 512 != 0) {
        fprintf(stderr, "Розмір запису %zu не вирівняний на сектор 512B\n", len);
        return -EINVAL;
    }

    // Відкриваємо файл зони у режимі лише запис + O_APPEND (обов'язково для zonefs seq)
    int fd = open(zone_file_path, O_WRONLY | O_APPEND | O_DIRECT);
    if (fd < 0) {
        int err = errno;
        perror("Не вдалося відкрити файл зони zonefs");
        return -err;
    }

    // Скидання зони у стан Empty (WP -> Start LBA).
    // У zonefs truncate файлу до довжини 0 змушує ядро видати команду Reset Zone.
    if (ftruncate(fd, 0) < 0) {
        int err = errno;
        perror("Помилка виконання ftruncate(fd, 0) для скидання зони");
        close(fd);
        return -err;
    }

    // Дописування даних у зону. Ядро конвертує O_APPEND у команду Zone Append.
    ssize_t bytes_written = write(fd, buffer, len);
    if (bytes_written < 0) {
        int err = errno;
        perror("Помилка виконання write() через Zone Append");
        close(fd);
        return -err;
    }

    printf("[C] Успішно записано %zd байтів у зону %s\n", bytes_written, zone_file_path);

    close(fd);
    return 0;
}

int main(void) {
    void *buffer = NULL;
    // Для O_DIRECT потрібна вирівняна адреса пам'яті на межу сектора
    if (posix_memalign(&buffer, SECTOR_SIZE, SECTOR_SIZE) != 0) {
        perror("Помилка виділення вирівняної пам'яті");
        return EXIT_FAILURE;
    }

    memset(buffer, 0x5A, SECTOR_SIZE);

    const char *target_zone = "/mnt/zonefs/seq/0";
    int ret = write_to_zone_c(target_zone, buffer, SECTOR_SIZE);

    free(buffer);

    if (ret != 0) {
        fprintf(stderr, "[C] Операцію запису завершено з помилкою %d\n", ret);
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
```
```cpp
#include <algorithm>
#include <iostream>
#include <string>
#include <span>
#include <memory>
#include <stdexcept>
#include <system_error>
#include <cstddef>
#include <cstdlib>
#include <fcntl.h>
#include <unistd.h>

// RAII Обгортка для безпечної роботи із зонованими файлами у zonefs
class ZonedFile {
private:
    int m_fd{-1};

public:
    explicit ZonedFile(const std::string& path) {
        // Режим O_APPEND гарантує використання команди Zone Append у ядрі
        m_fd = ::open(path.c_str(), O_WRONLY | O_APPEND | O_DIRECT);
        if (m_fd < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити файл зони");
        }
    }

    ~ZonedFile() {
        if (m_fd >= 0) {
            ::close(m_fd);
        }
    }

    // Забороняємо копіювання файлового дескриптора
    ZonedFile(const ZonedFile&) = delete;
    ZonedFile& operator=(const ZonedFile&) = delete;

    // Дозволяємо переміщення (Move semantics)
    ZonedFile(ZonedFile&& other) noexcept : m_fd(other.m_fd) {
        other.m_fd = -1;
    }

    ZonedFile& operator=(ZonedFile&& other) noexcept {
        if (this != &other) {
            if (m_fd >= 0) ::close(m_fd);
            m_fd = other.m_fd;
            other.m_fd = -1;
        }
        return *this;
    }

    // Атомарне скидання зони у стан Empty (Reset Write Pointer)
    void reset() {
        if (::ftruncate(m_fd, 0) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка скидання зони через ftruncate");
        }
    }

    // Безаварійний запис буфера даних через Zone Append
    std::size_t append(std::span<const std::byte> data) {
        if (data.size() % 512 != 0) {
            throw std::invalid_argument("Буфер даних повинен бути вирівняний на 512 байтів");
        }

        ssize_t written = ::write(m_fd, data.data(), data.size());
        if (written < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка виконання Zone Append");
        }
        return static_cast<std::size_t>(written);
    }
};

// Спеціалізований виділювач вирівняної пам'яті для O_DIRECT I/O
template <typename T>
struct AlignedDeleter {
    void operator()(T* ptr) const {
        ::free(ptr);
    }
};

template <typename T>
using UniqueAlignedPtr = std::unique_ptr<T[], AlignedDeleter<T>>;

template <typename T>
UniqueAlignedPtr<T> make_aligned_buffer(std::size_t alignment, std::size_t count) {
    void* ptr = nullptr;
    if (::posix_memalign(&ptr, alignment, count * sizeof(T)) != 0) {
        throw std::bad_alloc();
    }
    return UniqueAlignedPtr<T>(static_cast<T*>(ptr));
}

int main() {
    try {
        constexpr std::size_t alignment = 4096;
        constexpr std::size_t buffer_size = 4096;

        auto buffer = make_aligned_buffer<std::byte>(alignment, buffer_size);
        std::fill_n(buffer.get(), buffer_size, std::byte{0x7E});

        ZonedFile zone("/mnt/zonefs/seq/0");
        zone.reset();

        std::span<const std::byte> payload(buffer.get(), buffer_size);
        std::size_t bytes_written = zone.append(payload);

        std::cout << "[C++] Успішно записано " << bytes_written << " байтів у zonefs (RAII)\n";

    } catch (const std::exception& ex) {
        std::cerr << "[C++] Помилка виконання ZBD операції: " << ex.what() << '\n';
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
```
:::

---

## 3. Оцінка продуктивності та особливості O_DIRECT

При роботі із ZNS SSD використання прямого вводу-виводу `O_DIRECT` є фундаментальним для збереження нульового посилення запису (WAF = 1.0).

Якщо додаток пише через буферизований I/O, сторінковий кеш Linux (Page Cache) накопичує брудні сторінки (Dirty Pages) у пам'яті, а на диск їх пізніше зносить нитка `flusher`. Такий запис уже не є `Zone Append`: ядро видає звичайні послідовні `WRITE` за поточним WP і мусить серіалізувати їх блокуванням зони. Тобто буферизація не просто додає копіювання — вона знищує саме ту паралельність, заради якої брали `Zone Append`. 

Використання `O_DIRECT` гарантує передачу буфера з простору користувача прямо у системну структуру `bio` без проміжних копіювань та затримок у сторінковому кеші.

---

## 4. Інтеграція з асинхронною підсистемою `io_uring`

Для досягнення мільйонів операцій запису на секунду (IOPS) розробники поєднують `zonefs` із асинхронним кільцевим інтерфейсом `io_uring`.

У запиті `io_uring` (Submission Queue Entry, SQE) беруть код операції `IORING_OP_WRITEV` або `IORING_OP_WRITE_FIXED` і додають прапорець `RWF_APPEND`:

:::tabs
```c
// Заповнення SQE для асинхронного Zone Append у zonefs через io_uring (C)
io_uring_prep_writev(sqe, fd, iovecs, nr_iovecs, 0);
sqe->rw_flags |= RWF_APPEND;
```
```cpp
// Заповнення SQE для асинхронного Zone Append у zonefs через io_uring (C++)
::io_uring_prep_writev(sqe, fd, iovecs, nr_iovecs, 0);
sqe->rw_flags |= RWF_APPEND;
```
:::

Прапорець `RWF_APPEND` каже ядру писати в кінець файла, а для прямого вводу-виводу в `zonefs` це й перетворюється на атомарний `REQ_OP_ZONE_APPEND`. У `cqe->res` повертається лише кількість записаних байтів: фактичне зміщення, яке призначив контролер, у користувацький простір не віддається, тому позицію дізнаються з розміру файла (`fstat`) або зі звіту `blkzone report`.

---

## 5. Обробка помилок заповнення та вичерпання лімітів зон

При активній експлуатації `zonefs` у багатониткових системах розробник повинен обробляти два ключові крайові випадки:

1. **Досягнення Zone Capacity (`ENOSPC` / `EFBIG`):** Коли сума записаних даних досягає ємності зони (`Zone Capacity`), подальші спроби запису повертають помилку `ENOSPC` (No space left on device) або `EFBIG` (File too large). Додаток повинен закрити цей файл-зону і перейти до наступного файла `seq/N+1`.
2. **Переповнення активних зон (`EBUSY`):** Пристрої мають обмеження на кількість одночасно відкритих зон (`max_open_zones`). Якщо додаток відкриває забагато файлів на запис, ядро поверне `EBUSY`. Для розблокування ресурсу додаток повинен достроково фіналізувати неповні зони або закрити файли.

---

## 6. Практичний стенд: емуляція ZBD у Linux через `null_blk`

Для тестування розробленого ПЗ без наявності фізичного NVMe ZNS SSD або SMR HDD ядро Linux надає модуль емулятора `null_blk`.

### Крок 1. Завантаження модуля null_blk з підтримкою зон

Модуль створює віртуальний блоковий пристрій у пам'яті з параметрами Host-Managed ZBD:

```bash
# Видаляємо модуль, якщо він був завантажений раніше
$ sudo modprobe -r null_blk

# Завантажуємо null_blk із зоновим режимом Host-Managed
# zoned=1 -> Host-Managed ZBD
# zone_size=256 -> Розмір зони 256 МіБ
# gb=4 -> Загальна ємність 4 ГіБ
$ sudo modprobe null_blk nr_devices=1 zoned=1 zone_size=256 gb=4
```

Перевірка створення зонованого пристрою `/dev/nullb0`:

```bash
$ blkzone report /dev/nullb0 | head -n 5
  start: 0x000000000, len 0x080000, cap 0x080000, wptr 0x000000 reset:0 non-seq:0, zcond: 1(empty) [type: 2(SEQ_WRITE_REQ)]
  start: 0x000080000, len 0x080000, cap 0x080000, wptr 0x000000 reset:0 non-seq:0, zcond: 1(empty) [type: 2(SEQ_WRITE_REQ)]
  start: 0x000100000, len 0x080000, cap 0x080000, wptr 0x000000 reset:0 non-seq:0, zcond: 1(empty) [type: 2(SEQ_WRITE_REQ)]
```

### Крок 2. Форматування та монтування `zonefs`

Використовуємо утиліти з пакету `zonefs-tools`:

```bash
# Форматуємо пристрій під zonefs
$ sudo mkfs.zonefs /dev/nullb0

# Створюємо точку монтування та монтуємо ФС
$ sudo mkdir -p /mnt/zonefs
$ sudo mount -t zonefs /dev/nullb0 /mnt/zonefs

# Перевіряємо структуру файлів
$ ls -la /mnt/zonefs/seq/ | head -n 5
-rw-r--r-- 1 root root 0 Aug 12 12:00 0
-rw-r--r-- 1 root root 0 Aug 12 12:00 1
-rw-r--r-- 1 root root 0 Aug 12 12:00 2
```

### Крок 3. Запуск тесту та контроль стану Write Pointer

Після виконання скомпільованої бінарної програми перевіряємо зміну розміру файлу та стан зони:

```bash
# Розмір файлу відповідає кількості записаних байтів (WP)
$ ls -l /mnt/zonefs/seq/0
-rw-r--r-- 1 root root 4096 Aug 12 12:05 /mnt/zonefs/seq/0

# Інспекція стану через blkzone підтверджує зміщення WP
$ blkzone report -o 0 -c 1 /dev/nullb0
  start: 0x000000000, len 0x080000, cap 0x080000, wptr 0x000008 reset:0 non-seq:0, zcond: 2(imp open) [type: 2(SEQ_WRITE_REQ)]
```

Значення `wptr 0x000008` підтверджує, що вказівник запису апаратно змістився на 8 секторів (8 * 512 = 4096 байтів).
