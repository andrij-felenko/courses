# ⚙️ Реалізація утиліти зчитування /dev/hwrng, статистичної перевірки та поповнення пулу ядра

Цей практичний проєкт демонструє розробку повноцінної користувацької утиліти для роботи з апаратними генераторами випадкових чисел у Linux. Програма зчитує сирі випадкові дані з символьного пристрою `/dev/hwrng`, виконує реальний статистичний тест Monobit за стандартом FIPS 140-2 для виявлення дефектів заліза та безпечно передає перевірену ентропію у пул ядра Linux за допомогою системного виклику `ioctl(RNDADDENTROPY)`.

---

## Чому необхідне статистичне тестування перед поповненням пулу

Символьний пристрій `/dev/hwrng` надає безпосередній доступ до сирого потоку байтів, витягнутого з аналогових чи квантових процесів мікросхеми (теплового шуму резисторів, кільцевих осциляторів або лавинного пробою діодів). На відміну від криптографічних генераторів ядра, апаратні модулі схильні до фізичних деформацій, температурного дрейфу та старіння кремнію.

Якщо апаратний генератор зазнає локального перегріву або впливу сильного зовнішнього електромагнітного поля, фізичний процес може збоїти: кільцевий осцилятор може заблокуватися у стабільному стані, видаючи суцільну послідовність одиниць (`11111111`) або нулів (`00000000`), чи періодичний патерн (`10101010`).

Якщо такий зіпсований потік даних потрапить безпосередньо у криптографічні застосунки, це призведе до катастрофічного зниження безпеки ключів. Для запобігання "отруєнню ентропії" (entropy poisoning) демон простору користувача зобов'язаний пропустити зчитану порцію даних через математичні перевірки випадковості.

---

## Математичний суть статистичного тесту Monobit (FIPS 140-2)

Стандарт безпеки Федерального уряду США FIPS 140-2 (Annex D) регламентує суворі статистичні тести для перевірки генераторів випадкових чисел у реальному часі.

Тест Monobit перевіряє рівномірність розподілу бітів. У справді випадковій послідовності бітів ймовірність появи одиниці або нуля дорівнює точно 50%.

Процедура тестування:
1. Зчитується фіксована вибірка бітів обсягом `N = 20,000` біт (що відповідає exactamente `2500` байтам).
2. Підраховується загальна кількість одиниць `X` у цій вибірці.
3. Згідно вимог FIPS 140-2, вибірка вважається пройденою тоді і тільки тоді, коли кількість одиниць перебуває у строго визначеному інтервалі:
   ```
   9725 < X < 10275
   ```
4. Якщо кількість одиниць `X <= 9725` (занадто багато нулів) або `X >= 10275` (занадто багато одиниць), утиліта відкидає увесь блок даних як дефектний та не допускає його змішування у ядро.

---

## Покроковий розбір алгоритму роботи утиліти

Утиліта виконує наступні послідовні кроки:
1. **Відкриття файлових дескрипторів:** Відкриває пристрій `/dev/hwrng` у режимі тільки для читання (`O_RDONLY`) та пристрій `/dev/random` у режимі тільки для запису (`O_WRONLY`).
2. **Зчитування блоку даних:** Зчитує рівно 2500 байт із пристрою `/dev/hwrng`. Оскільки читання з псевдофайлів пристроїв ядра може бути перервано сигналами (`EINTR`) або повернути часткові дані, утиліта повинна гарантувати повне заповнення буфера.
3. **Обчислення бітового балансу:** Перебирає всі байти зчитаного буфера та підраховує кількість встановлених бітів (одиниць). У C++20 для цього використовується надшвидка інструкція процесора `std::popcount`.
4. **Оцінка за FIPS 140-2:** Перевіряє умову `9725 <= ones <= 10275`. Якщо умова не виконується, генерується помилка, блок ігнорується, а лічильник апаратних збоїв збільшується.
5. **Формування структури ioctl:** Формує структуру `struct rand_pool_info` у динамічній пам'яті. Поле `entropy_count` заповнюється значенням `20000` (кількість біт), поле `buf_size` — значенням `2500` (байтів), а вибірка копіюється у гнучкий масив `buf`.
6. **Передача в ядро:** Викликає системний виклик `ioctl(fd_random, RNDADDENTROPY, info)`. Ядро Linux приймає ці дані, змішує їх через BLAKE2s у стан `crng` та поповнює лічильник ентропії ядра.

---

## Двомовна реалізація утиліти (C та ідіоматичний C++)

Нижче наведено дві повноцінні реалізації утиліти. Версія на мові C висвітлює класичний POSIX-підхід із мануальним управлінням ресурсами та гілками `goto out`. Версія на мові C++20 демонструє сучасний об'єктно-орієнтований підхід: використання концепції RAII для автоматичного закриття дескрипторів, концепту `std::span` для безпечної передачі масивів, шаблону `std::expected` для відсутності винятків та стандартної функції `std::popcount`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/random.h>

#define BLOCK_BYTES 2500
#define BLOCK_BITS (BLOCK_BYTES * 8)
#define MONOBIT_MIN 9725
#define MONOBIT_MAX 10275

static bool fips_monobit_test(const uint8_t *buffer, size_t size) {
    size_t ones = 0;
    for (size_t i = 0; i < size; ++i) {
        uint8_t byte = buffer[i];
        while (byte > 0) {
            ones += (byte & 1);
            byte >>= 1;
        }
    }
    return (ones >= MONOBIT_MIN && ones <= MONOBIT_MAX);
}

int main(void) {
    int hwrng_fd = -1;
    int random_fd = -1;
    int ret = EXIT_FAILURE;

    hwrng_fd = open("/dev/hwrng", O_RDONLY);
    if (hwrng_fd < 0) {
        perror("Не вдалося відкрити /dev/hwrng");
        goto out;
    }

    random_fd = open("/dev/random", O_WRONLY);
    if (random_fd < 0) {
        perror("Не вдалося відкрити /dev/random");
        goto out;
    }

    uint8_t buffer[BLOCK_BYTES];
    size_t total_read = 0;
    while (total_read < BLOCK_BYTES) {
        ssize_t bytes = read(hwrng_fd, buffer + total_read, BLOCK_BYTES - total_read);
        if (bytes <= 0) {
            perror("Помилка зчитування з /dev/hwrng");
            goto out;
        }
        total_read += (size_t)bytes;
    }

    if (!fips_monobit_test(buffer, BLOCK_BYTES)) {
        fprintf(stderr, "Помилка: блок відкинуто, FIPS Monobit test провалився!\n");
        goto out;
    }

    size_t info_size = sizeof(struct rand_pool_info) + BLOCK_BYTES;
    struct rand_pool_info *info = (struct rand_pool_info *)malloc(info_size);
    if (!info) {
        perror("Помилка виділення пам'яті");
        goto out;
    }

    info->entropy_count = BLOCK_BITS;
    info->buf_size = BLOCK_BYTES;
    for (size_t i = 0; i < BLOCK_BYTES; ++i) {
        ((uint8_t *)info->buf)[i] = buffer[i];
    }

    if (ioctl(random_fd, RNDADDENTROPY, info) < 0) {
        perror("Помилка ioctl(RNDADDENTROPY)");
        free(info);
        goto out;
    }

    printf("Успішно перевірено та додано %d біт ентропії до ядра Linux.\n", BLOCK_BITS);
    free(info);
    ret = EXIT_SUCCESS;

out:
    if (hwrng_fd >= 0) close(hwrng_fd);
    if (random_fd >= 0) close(random_fd);
    return ret;
}
```
```cpp
#include <iostream>
#include <vector>
#include <span>
#include <memory>
#include <expected>
#include <numeric>
#include <bit>
#include <system_error>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/random.h>

class PosixFd {
    int m_fd{-1};
public:
    explicit PosixFd(int fd) noexcept : m_fd(fd) {}
    ~PosixFd() { if (m_fd >= 0) ::close(m_fd); }
    
    PosixFd(const PosixFd&) = delete;
    PosixFd& operator=(const PosixFd&) = delete;
    
    PosixFd(PosixFd&& other) noexcept : m_fd(other.m_fd) { other.m_fd = -1; }
    PosixFd& operator=(PosixFd&& other) noexcept {
        if (this != &other) {
            if (m_fd >= 0) ::close(m_fd);
            m_fd = other.m_fd;
            other.m_fd = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return m_fd; }
    [[nodiscard]] bool valid() const noexcept { return m_fd >= 0; }
};

enum class FeederError {
    OpenFailed,
    ReadFailed,
    FipsTestFailed,
    IoctlFailed
};

constexpr size_t BlockBytes = 2500;
constexpr size_t BlockBits = BlockBytes * 8;
constexpr size_t MonobitMin = 9725;
constexpr size_t MonobitMax = 10275;

[[nodiscard]] bool verify_monobit(std::span<const uint8_t> data) noexcept {
    size_t ones = 0;
    for (uint8_t byte : data) {
        ones += std::popcount(byte);
    }
    return ones >= MonobitMin && ones <= MonobitMax;
}

std::expected<void, FeederError> feed_entropy() {
    PosixFd hwrng{::open("/dev/hwrng", O_RDONLY)};
    if (!hwrng.valid()) return std::unexpected(FeederError::OpenFailed);

    PosixFd random_dev{::open("/dev/random", O_WRONLY)};
    if (!random_dev.valid()) return std::unexpected(FeederError::OpenFailed);

    std::vector<uint8_t> buffer(BlockBytes);
    size_t total_read = 0;
    while (total_read < BlockBytes) {
        ssize_t bytes = ::read(hwrng.get(), buffer.data() + total_read, BlockBytes - total_read);
        if (bytes <= 0) {
            return std::unexpected(FeederError::ReadFailed);
        }
        total_read += static_cast<size_t>(bytes);
    }

    if (!verify_monobit(buffer)) {
        return std::unexpected(FeederError::FipsTestFailed);
    }

    size_t info_size = sizeof(struct rand_pool_info) + buffer.size();
    auto storage = std::make_unique<uint8_t[]>(info_size);
    auto* info = reinterpret_cast<struct rand_pool_info*>(storage.get());

    info->entropy_count = static_cast<int>(BlockBits);
    info->buf_size = static_cast<int>(buffer.size());
    std::copy(buffer.begin(), buffer.end(), reinterpret_cast<uint8_t*>(info->buf));

    if (::ioctl(random_dev.get(), RNDADDENTROPY, info) < 0) {
        return std::unexpected(FeederError::IoctlFailed);
    }

    return {};
}

int main() {
    auto result = feed_entropy();
    if (!result) {
        std::cerr << "Помилка передачі ентропії у ядро Linux!\n";
        return EXIT_FAILURE;
    }

    std::cout << "Успішно перевірено та додано " << BlockBits << " біт ентропії.\n";
    return EXIT_SUCCESS;
}
```
:::

---

## Інструкція зі компіляції та тестування утиліти

Для компіляції вихідного коду та перевірки його роботи в системі Linux скористайтеся наступними командами:

### 1. Компіляція програмою `gcc` (C) або `g++` (C++20):

```bash
# Компіляція версії на C
$ gcc -O2 -Wall -Wextra entropy_feeder.c -o entropy_feeder_c

# Компіляція версії на C++20
$ g++ -std=c++20 -O2 -Wall -Wextra entropy_feeder.cpp -o entropy_feeder_cpp
```

### 2. Запуск із правами суперкористувача (`sudo`):

Оскільки системний виклик `ioctl(RNDADDENTROPY)` вимагає адміністративних привілеїв `CAP_SYS_ADMIN`, запуск утиліти від звичайного користувача завершиться помилкою `Permission denied`:

```bash
$ sudo ./entropy_feeder_cpp
Успішно перевірено та додано 20000 біт ентропії.
```

### 3. Перевірка змін стану пулу ядра:

Перевірити поточну оцінку ентропії у ядрі Linux можна до та після запуску утиліти:

```bash
$ cat /proc/sys/kernel/random/entropy_avail
256
```
*(Примітка: У сучасному ядрі Linux 5.17+ максимальне значення лічильника ентропії обмежено значенням 256 біт, що відповідає повній довжині криптографічного ключа ChaCha20).*

---

## Обробка крайових випадків та інтеграція із systemd

У реальних системних середовищах розробник утиліти поповнення ентропії повинен враховувати кілька важливих крайових випадків:

### 1. Переривання виклику `read()` сигналами (`EINTR`)
При зчитуванні з `/dev/hwrng` потік користувача може бути перерваний системним сигналом до того, як апаратний пристрій поверне повний блок у 2500 байт. Утиліта обробляє це у циклі `while (total_read < BlockBytes)`, повертаючи читання доти, доки не буде накопичено повний обсяг вибірки для тесту Monobit.

### 2. Неблокуючий режим `O_NONBLOCK`
Якщо апаратний генератор випадкових чисел відключено або деактивовано через `sysfs`, спроба зчитати з `/dev/hwrng` у блокуючому режимі може зависнути наневизначений час. Відкриття файла з прапорцем `O_NONBLOCK` дозволяє отримати помилку `-EAGAIN` та завершити процес із коректним статусом для подальшої перезапуску демоном.

### 3. Створення юніта systemd (`/etc/systemd/system/entropy-feeder.service`)
Для автоматичного запуску утиліти при завантаженні системи можна створити наступний конфігураційний файл:

```ini
[Unit]
Description=FIPS 140-2 Entropy Feeder Service
After=syslog.target

[Service]
Type=exec
ExecStart=/usr/local/bin/entropy_feeder_cpp
Restart=on-failure
RestartSec=10s
CapabilityBoundingSet=CAP_SYS_ADMIN
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
```

Використання директиви `CapabilityBoundingSet=CAP_SYS_ADMIN` обмежує права демона лише тими системними викликами, які необхідні для `ioctl(RNDADDENTROPY)`, позбавляючи його повних прав `root`.
