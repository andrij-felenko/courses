# ⚙️ Практична робота з AF_ALG із користувацького простору

Взаємодія з ядерним криптографічним фреймворком із простору користувача виконується через мережеві сокети домену `AF_ALG`. Цей підхід забезпечує передачу обчислювальних завдань безпосередньо ядерним драйверам, у тому числі апаратним прискорювачам та процесорним інструкціям (AES-NI), без необхідності лінкувати важкі користувацькі бібліотеки у власний бінарний файл.

Нижче наведено практичні приклади реалізації обчислення хеш-дайджесту SHA-256 та розшифрування даних. У прикладах показано повний життєвий цикл роботи із сокетом: створення керівного сокета, зв'язування `bind()` із структурою `struct sockaddr_alg`, виділення робочого контексту через `accept()`, передача вхідних даних та зчитування результату.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <linux/if_alg.h>
#include <errno.h>

#ifndef SOL_ALG
#define SOL_ALG 279
#endif

int calculate_sha256_kernel(const unsigned char *data, size_t len, unsigned char hash_out[32])
{
    int tfm_fd = -1;
    int op_fd = -1;
    ssize_t ret;
    struct sockaddr_alg sa = {
        .salg_family = AF_ALG,
        .salg_type = "hash",
        .salg_name = "sha256"
    };

    tfm_fd = socket(AF_ALG, SOCK_SEQPACKET, 0);
    if (tfm_fd < 0) {
        perror("socket(AF_ALG)");
        return -1;
    }

    if (bind(tfm_fd, (struct sockaddr *)&sa, sizeof(sa)) < 0) {
        perror("bind(AF_ALG)");
        close(tfm_fd);
        return -1;
    }

    op_fd = accept(tfm_fd, NULL, 0);
    if (op_fd < 0) {
        perror("accept(AF_ALG)");
        close(tfm_fd);
        return -1;
    }

    ret = write(op_fd, data, len);
    if (ret != (ssize_t)len) {
        perror("write(op_fd)");
        close(op_fd);
        close(tfm_fd);
        return -1;
    }

    ret = read(op_fd, hash_out, 32);
    if (ret != 32) {
        perror("read(op_fd)");
        close(op_fd);
        close(tfm_fd);
        return -1;
    }

    close(op_fd);
    close(tfm_fd);
    return 0;
}

int main(void)
{
    const char *msg = "Hello, Kernel Crypto API!";
    unsigned char hash[32];
    
    if (calculate_sha256_kernel((const unsigned char *)msg, strlen(msg), hash) == 0) {
        printf("SHA-256 дайджест: ");
        for (int i = 0; i < 32; i++) {
            printf("%02x", hash[i]);
        }
        printf("\n");
    }
    return 0;
}
```
```cpp
#include <iostream>
#include <iomanip>
#include <algorithm>
#include <array>
#include <span>
#include <string_view>
#include <system_error>
#include <cerrno>
#include <cstdint>
#include <unistd.h>
#include <sys/socket.h>
#include <linux/if_alg.h>

#ifndef SOL_ALG
#define SOL_ALG 279
#endif

// RAII обгортка для файлового дескриптора сокета
class UniqueFd {
    int fd_ = -1;
public:
    explicit UniqueFd(int fd = -1) : fd_(fd) {}
    ~UniqueFd() { if (fd_ >= 0) ::close(fd_); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : fd_(other.fd_) { other.fd_ = -1; }
    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
};

class KernelCrypto {
public:
    static std::array<uint8_t, 32> sha256(std::span<const uint8_t> input) {
        UniqueFd tfm_fd(::socket(AF_ALG, SOCK_SEQPACKET, 0));
        if (!tfm_fd.valid()) {
            throw std::system_error(errno, std::generic_category(), "Помилка створення сокета AF_ALG");
        }

        struct sockaddr_alg sa{};
        sa.salg_family = AF_ALG;
        std::string_view type = "hash";
        std::string_view name = "sha256";
        std::copy(type.begin(), type.end(), sa.salg_type);
        std::copy(name.begin(), name.end(), sa.salg_name);

        if (::bind(tfm_fd.get(), reinterpret_cast<struct sockaddr*>(&sa), sizeof(sa)) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка bind(AF_ALG)");
        }

        UniqueFd op_fd(::accept(tfm_fd.get(), nullptr, nullptr));
        if (!op_fd.valid()) {
            throw std::system_error(errno, std::generic_category(), "Помилка accept(AF_ALG)");
        }

        if (::write(op_fd.get(), input.data(), input.size()) != static_cast<ssize_t>(input.size())) {
            throw std::system_error(errno, std::generic_category(), "Помилка запису даних у сокет");
        }

        std::array<uint8_t, 32> digest{};
        if (::read(op_fd.get(), digest.data(), digest.size()) != static_cast<ssize_t>(digest.size())) {
            throw std::system_error(errno, std::generic_category(), "Помилка читання дайджесту з сокета");
        }

        return digest;
    }
};

int main() {
    try {
        std::string_view msg = "Hello, Kernel Crypto API!";
        auto input = std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(msg.data()), msg.size());
        auto hash = KernelCrypto::sha256(input);

        std::cout << "SHA-256 дайджест (C++20 RAII): ";
        for (uint8_t byte : hash) {
            std::cout << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(byte);
        }
        std::cout << std::dec << "\n";
    } catch (const std::exception& e) {
        std::cerr << "Помилка: " << e.what() << "\n";
        return 1;
    }
    return 0;
}
```
:::

## Особливості обробки файлових дескрипторів та керування пам’яттю

Під час використання сокетів `AF_ALG` у реальних застосунках важливо дотримуватися кількох критичних правил системного програмування:

1. **Фабрика об’єктів та повторне використання `tfm_fd`:** Керуючий сокет (`tfm_fd`), виділений викликом `socket(AF_ALG, ...)`, виконує роль фабрики контекстів. Виконавши виклик `bind()` один раз при старті застосунку, програма може викликати `accept()` для кожного нового файлу чи потоку. Згенеровані робочі дескриптори (`op_fd`) є повністю незалежними і можуть паралельно використовуватися в різних потоках виконання без додаткового блокування мутексами.
2. **Передача даних без копіювання (Zero-Copy):** Замість копіювання вмісту великих файлів у буфер користувача через `read()` і подальшої відправки у сокет через `write()`, програма може використовувати системний виклик `splice()`. Дані з файлового дескриптора джерела передаються безпосередньо у конвеєр (pipe), а з нього — у сокет `AF_ALG`. Це виключає накладні витрати на копіювання пам’яті між простором ядра та простором користувача, оскільки ядро передає сторінки пам’яті безпосередньо в криптографічний драйвер.
3. **Обнулення секретних буферів:** Після завершення роботи із секретними ключами чи парольними фразами у користувацькому просторі обов'язково викликати `explicit_bzero()` (є в glibc та BSD, у самому стандарті C її немає) або `memzero_explicit()` при розробці ядерних модулів. Звичайний `memset()` може бути повністю вилучений компілятором у процесі оптимізації неактивного коду (dead-code elimination).
4. **Обмеження привілеїв та фільтрація системних викликів:** У ізольованих контейнерах або пісочницях створення сокетів домену `AF_ALG` регулюється модулями LSM (SELinux, AppArmor) та фільтрами `seccomp`. Якщо програма діє всередині обмеженого профілю, спроба виклику `socket(AF_ALG, ...)` буде заблокована: LSM відмовить із `-EACCES`, а `seccomp` — залежно від дії профілю — поверне `-EPERM` або вб'є процес сигналом `SIGSYS`.
5. **Обробка асинхронних збоїв та сигналів:** При роботі із робочим сокетом у багатопотоковому середовищі системні виклики `read()` або `recvmsg()` можуть бути перервані сигналами (помилка `-EINTR`). Обгортка має повторювати перерваний виклик у циклі або чекати готовності через `ppoll()` із власною маскою сигналів — щоб перевірка маски й очікування не розходилися в часі.
6. **Порівняння C та C++ реалізацій:** У той час як приклад мовою C використовує явне управління дескрипторами з ручною перевіркою помилок на кожному етапі, версія на C++20 інкапсулює дескриптор у RAII-клас `UniqueFd`. Це гарантує автоматичне закриття файлового дескриптора при виході з області видимості через винятки або передчасний повернення з функції, унеможливлюючи витік файлових дескрипторів у довгопрацюючих сервісах. Застосування `std::span` та `std::string_view` запобігає помилкам з виходом за межі буфера та передачею некоректної довжини масиву.

## Режим блокового шифрування та передача ключів у C++

При викликах `skcipher` (наприклад, `cbc(aes)`) додається етап передачі ключа через `setsockopt()` та передача вектора ініціалізації (IV) у контрольному повідомленні `sendmsg()`. У мові C++20 для пакування контрольних повідомлень створюється допоміжний клас-інкапсулятор, який формує шар `cmsghdr` у стековій пам'яті без використання нетипізованих вказівників `void*`, що забезпечує типобезпечність обчислень та високу продуктивність.

Крім того, при розробці системних сервісів у просторі користувача слід зважати на те, що кожна операція `accept()` генерує новий об'єкт трансформації в ядрі. Тому для циклічних операцій обчислення контрольних сум або розшифрування багатьох масивів доцільно перевикористовувати один і той самий робочий дескриптор `op_fd`, відправляючи нові порції даних послідовними викликами `sendmsg()`, а не створювати нові сокети на кожен фрагмент даних.

При використанні zero-copy передачі через `splice()` вимогу до розміру диктує не сторінка пам'яті, а сам алгоритм: для блокових режимів без доповнення (`cbc(aes)`, `ecb(aes)`) загальний обсяг даних мусить бути кратним розміру блоку — 16 байтів для AES, — інакше ядро поверне `-EINVAL`. Окремий виклик `splice()` при цьому має право передати менше, ніж просили: повернене значення треба перевіряти й дописувати залишок.

Для запобігання втраті продуктивності при виклику `setsockopt(..., ALG_SET_KEY, ...)` ключі слід встановлювати один раз на керівному сокеті `tfm_fd` до створення робочих дескрипторів `op_fd`. Якщо додаток намагається змінити ключ безпосередньо на робочому дескрипторі `op_fd` після початку читання даних, ядро поверне помилку: на робочому дескрипторі опція взагалі не підтримується (`-ENOPROTOOPT`), а спроба перевстановити ключ на керівному сокеті, коли з нього вже створено робочі, дає `-EBUSY`.

У випадку, коли ключ передається із підсистеми `Kernel Keyring` через опцію `ALG_SET_KEY_BY_KEY_SERIAL` (доступна у ядрах 6.x), додаток передає 32-бітний серійний номер ключа типу `key_serial_t`. Ядро самостійно шукає ключ у сховищах поточного процесу та вимагає права пошуку (`KEY_NEED_SEARCH`) — інакше повертає `-EPERM`. Це усуває потребу тримати ключовий матеріал в адресній пам’яті користувацького процесу, суттєво підвищуючи рівень безпеки.
