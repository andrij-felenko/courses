# ⚙️ Побудова пісочниці за допомогою Capsicum

Практична ізоляція ненадійного коду (наприклад, парсерів складних медіаформатів, обробників мережевих пакетів, розпакувальників архівів чи інтерпретаторів байт-коду) у традиційних Unix-подібних операційних системах традиційно стикається з дилемою: або надавати сторонньому коду повні привілеї поточного користувача, або вимагати прав адміністратора (`root`) для побудови ізольованих контейнерів, використання виклику `chroot()` чи складних просторів імен (Linux Namespaces).

Фреймворк **Capsicum**, інтегрований у ядро FreeBSD, пропонує принципово інший підхід. Він дозволяє звичайному непривілейованому процесу самостійно замкнути себе в пісочниці під час роботи, перетворивши відкриті файлові дескриптори на невдавані повноваження зі строго зменшеними правами.

---

## Архітектурний шаблон пісочниці: трифазний життєвий цикл

Ізольована програма на основі Capsicum структурується як послідовність трьох чітко розмежованих фаз виконання:

```
[ Фаза 1: Ambient Init ]      [ Фаза 2: Rights Attenuation ]    [ Фаза 3: Capability Mode ]
Відкриття потрібних файлів → Звуження масок дескрипторів     → Виклик cap_enter()
(open, socket, конфіги)      (cap_rights_limit на кожен fd)    (повна ізоляція VFS)
```

### 1. Фаза ініціалізації (Ambient Initialization Phase)
Процес стартує у звичайному режимі POSIX. На цьому етапі він має законний доступ до глобального простору імен VFS. Програма відкриває вхідний файл контенту, створює вихідний файл результатів, завантажує таблиці локалей, файли конфігурацій та динамічні бібліотеки. Наприкінці фази у процесу залишаються лише числові файлові дескриптори відкритих ресурсів. 

Критично важливо, щоб динамичний компонувальник (*dynamic linker / rtld*) на цьому етапі завершив прив'язку всіх символів (жадібне зв'язування `LD_BIND_NOW`), оскільки ліниве завантаження бібліотек після переходу в ізоляцію буде заблоковано ядром.

### 2. Фаза звуження прав (Rights Attenuation Phase)
Для кожного відкритого дескриптора формується мінімально необхідна бітова маска операцій `cap_rights_t`. За принципом найменших привілеїв дескриптор вхідного файлу позбавляється прав на запис, зміну прав доступу чи видалення, отримуючи виключно `CAP_READ | CAP_SEEK | CAP_FSTAT`. 

Дескриптор вихідного файлу обмежується операціями запису `CAP_WRITE | CAP_SEEK | CAP_FSTAT | CAP_FTRUNCATE`. Усі службові дескриптори, які більше не потрібні (наприклад, дескриптори конфігураційних файлів), обов'язково закриваються за допомогою `close()`.

### 3. Фаза ізоляції (Capability Sandbox Phase)
Процес викликає системну функцію `cap_enter()`. З цього моменту ядро встановлює у структурі процесу прапорець `P_CAPMODE`. Будь-який подальший системний виклик, що намагається знайти файл за текстовим шляхом у VFS, створити новий сокет чи звернутися до системного процесу за PID, негайно перехоплюється ядром і повертає помилку `ECAPMODE`. Процес перетворюється на чистий обчислювальний автомат, здатний взаємодіяти із зовнішнім світом виключно через уже надані йому дескриптори.

---

## Практична реалізація: безпечний потоковий перетворювач

Нижче наведено повний вихідний код утиліти, що реалізує захищену обробку потоку даних. Програма відкриває вхідний файл, створює файл результату, звужує права дескрипторів, замикає себе в пісочниці та виконує трансформацію байтів.

:::tabs
```c
#include <sys/types.h>
#include <sys/capsicum.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>

#define CHUNK_SIZE 4096

/* Основна функція обробки даних усередині пісочниці */
static int process_stream(int fd_in, int fd_out) {
    char buffer[CHUNK_SIZE];
    ssize_t bytes_read;

    while ((bytes_read = read(fd_in, buffer, sizeof(buffer))) > 0) {
        /* Трансформація: інверсія регістру символів латиниці */
        for (ssize_t i = 0; i < bytes_read; ++i) {
            if (buffer[i] >= 'a' && buffer[i] <= 'z') {
                buffer[i] = (char)(buffer[i] - 32);
            } else if (buffer[i] >= 'A' && buffer[i] <= 'Z') {
                buffer[i] = (char)(buffer[i] + 32);
            }
        }
        
        ssize_t bytes_written = write(fd_out, buffer, (size_t)bytes_read);
        if (bytes_written != bytes_read) {
            return -1;
        }
    }
    return (bytes_read == 0) ? 0 : -1;
}

int main(int argc, char *argv[]) {
    if (argc != 3) {
        fprintf(stderr, "Використання: %s <input_file> <output_file>\n", argv[0]);
        return 1;
    }

    /* 1. Фаза ініціалізації: відкриття файлів до входу в пісочницю */
    int fd_in = open(argv[1], O_RDONLY);
    if (fd_in < 0) {
        perror("Не вдалося відкрити вхідний файл");
        return 1;
    }

    int fd_out = open(argv[2], O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd_out < 0) {
        perror("Не вдалося створити вихідний файл");
        close(fd_in);
        return 1;
    }

    /* 2. Фаза звуження прав: підготовка та застосування масок */
    cap_rights_t rights_in;
    cap_rights_init(&rights_in, CAP_READ, CAP_SEEK, CAP_FSTAT);
    if (cap_rights_limit(fd_in, &rights_in) < 0) {
        perror("Помилка cap_rights_limit для вхідного дескриптора");
        close(fd_in);
        close(fd_out);
        return 1;
    }

    cap_rights_t rights_out;
    cap_rights_init(&rights_out, CAP_WRITE, CAP_SEEK, CAP_FSTAT, CAP_FTRUNCATE);
    if (cap_rights_limit(fd_out, &rights_out) < 0) {
        perror("Помилка cap_rights_limit для вихідного дескриптора");
        close(fd_in);
        close(fd_out);
        return 1;
    }

    /* 3. Фаза ізоляції: вхід у capability mode */
    if (cap_enter() < 0) {
        perror("Помилка виклику cap_enter");
        close(fd_in);
        close(fd_out);
        return 1;
    }

    /* Демонстрація захисту: спроба несанкціонованого доступу до файлової системи */
    int fd_leak = open("/etc/resolv.conf", O_RDONLY);
    if (fd_leak < 0 && errno == ECAPMODE) {
        /* Ядро заблокувало виклик: глобальні шляхи заборонені */
    }

    /* Виконання обчислень у безпечному середовищі */
    int status = process_stream(fd_in, fd_out);

    close(fd_in);
    close(fd_out);
    return (status == 0) ? 0 : 2;
}
```
```cpp
#include <sys/types.h>
#include <sys/capsicum.h>
#include <fcntl.h>
#include <unistd.h>

#include <iostream>
#include <span>
#include <vector>
#include <string_view>
#include <system_error>
#include <cerrno>

namespace sandbox {

/* RAII-обгортка над файловим дескриптором з підтримкою Capsicum */
class CapabilityDescriptor {
public:
    explicit CapabilityDescriptor(int fd = -1) noexcept : fd_{fd} {}

    ~CapabilityDescriptor() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    CapabilityDescriptor(const CapabilityDescriptor&) = delete;
    CapabilityDescriptor& operator=(const CapabilityDescriptor&) = delete;

    CapabilityDescriptor(CapabilityDescriptor&& other) noexcept : fd_{other.fd_} {
        other.fd_ = -1;
    }

    CapabilityDescriptor& operator=(CapabilityDescriptor&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) {
                ::close(fd_);
            }
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int native_handle() const noexcept { return fd_; }
    [[nodiscard]] bool is_valid() const noexcept { return fd_ >= 0; }

    template <typename... RightsArgs>
    void limit_rights(RightsArgs... args) {
        cap_rights_t rights;
        ::cap_rights_init(&rights, args..., 0);
        if (::cap_rights_limit(fd_, &rights) < 0) {
            throw std::system_error(errno, std::generic_category(), "cap_rights_limit failed");
        }
    }

private:
    int fd_;
};

void enter_sandbox() {
    if (::cap_enter() < 0) {
        throw std::system_error(errno, std::generic_category(), "cap_enter failed");
    }
}

void transform_data(int fd_in, int fd_out) {
    std::vector<char> buffer(4096);
    while (true) {
        ssize_t bytes_read = ::read(fd_in, buffer.data(), buffer.size());
        if (bytes_read < 0) {
            throw std::system_error(errno, std::generic_category(), "read failed");
        }
        if (bytes_read == 0) {
            break;
        }

        std::span<char> chunk{buffer.data(), static_cast<size_t>(bytes_read)};
        for (char& ch : chunk) {
            if (ch >= 'a' && ch <= 'z') {
                ch = static_cast<char>(ch - 32);
            } else if (ch >= 'A' && ch <= 'Z') {
                ch = static_cast<char>(ch + 32);
            }
        }

        ssize_t bytes_written = ::write(fd_out, chunk.data(), chunk.size());
        if (bytes_written != bytes_read) {
            throw std::system_error(errno, std::generic_category(), "write failed");
        }
    }
}

} // namespace sandbox

int main(int argc, char* argv[]) {
    if (argc != 3) {
        std::cerr << "Використання: " << argv[0] << " <input_file> <output_file>\n";
        return 1;
    }

    try {
        int raw_in = ::open(argv[1], O_RDONLY);
        if (raw_in < 0) {
            throw std::system_error(errno, std::generic_category(), "Failed to open input file");
        }
        sandbox::CapabilityDescriptor input_fd(raw_in);

        int raw_out = ::open(argv[2], O_WRONLY | O_CREAT | O_TRUNC, 0644);
        if (raw_out < 0) {
            throw std::system_error(errno, std::generic_category(), "Failed to open output file");
        }
        sandbox::CapabilityDescriptor output_fd(raw_out);

        /* Фаза звуження: обмежуємо дескриптори за принципом найменших привілеїв */
        input_fd.limit_rights(CAP_READ, CAP_SEEK, CAP_FSTAT);
        output_fd.limit_rights(CAP_WRITE, CAP_SEEK, CAP_FSTAT, CAP_FTRUNCATE);

        /* Фаза ізоляції: перехід у capability mode */
        sandbox::enter_sandbox();

        /* Безпечна потокова обробка */
        sandbox::transform_data(input_fd.native_handle(), output_fd.native_handle());

    } catch (const std::exception& ex) {
        std::cerr << "Критична помилка виконання: " << ex.what() << '\n';
        return 1;
    }

    return 0;
}
```
:::

---

## Делегування системних служб через libcasper

Якщо ізольованій програмі в процесі тривалої роботи все ж потрібен доступ до окремих системних служб (наприклад, резолюції доменних імен DNS через `getaddrinfo` або читання системних параметрів `sysctl`), класичний підхід заблокує такі виклики.

У FreeBSD для вирішення цієї задачі використовують бібліотеку **libcasper** (*Casper daemon framework*):
1. До переходу в пісочницю процес створює IPC-з'єднання з демоном Casper і відкриває спеціалізовані служби (сервіси `system.dns`, `system.sysctl` або `system.grp`).
2. Процес отримує дескриптор каналу служби Casper (`cap_channel_t`).
3. Після виклику `cap_enter()` програма надсилає запити на резолюцію імен не через прямі системні виклики сокетів, а через RPC-повідомлення до Casper-демона, який виконує дію від свого імені та повертає лише готовий результат.
4. Процес залишається повністю ізольованим у пісочниці, не маючи прямого доступу до сокетів чи файлів конфігурації.

---

## Діагностика поведінки пісочниці через ktrace та kdump

Для перевірки коректності ізоляції та аналізу відхилених системних викликів у FreeBSD використовують штатний системний трейсер `ktrace` разом із дешифратором журналу `kdump`.

Команди для запуску профілювання:
```bash
ktrace -di ./capsicum_sandbox input.txt output.txt
kdump -f ktrace.out
```

Фрагмент журналу `kdump` демонструє типовий перебіг виконання системних викликів:
```
 1042 capsicum_sandbox CALL  open(0x7fffffffe810,0<O_RDONLY>)
 1042 capsicum_sandbox NAMI  "input.txt"
 1042 capsicum_sandbox RET   open 3
 1042 capsicum_sandbox CALL  cap_rights_limit(0x3,0x7fffffffe780)
 1042 capsicum_sandbox RET   cap_rights_limit 0
 1042 capsicum_sandbox CALL  cap_enter
 1042 capsicum_sandbox RET   cap_enter 0
 1042 capsicum_sandbox CALL  open(0x401820,0<O_RDONLY>)
 1042 capsicum_sandbox NAMI  "/etc/resolv.conf"
 1042 capsicum_sandbox RET   open -1 errno 94 Not permitted in capability mode
 1042 capsicum_sandbox CALL  read(0x3,0x7fffffffe890,0x1000)
 1042 capsicum_sandbox GIO   fd 3 read 1024 bytes
 1042 capsicum_sandbox RET   read 1024/0x400
```

Журнал наочно підтверджує системний інваріант: після виклику `cap_enter` спроба звернутися до файлу конфігурації мережі `/etc/resolv.conf` була миттєво відхилена ядром із кодом `errno 94` (`ECAPMODE`), тоді як операція читання з попередньо обмеженого дескриптора `fd 3` завершилася успішно.

---

## Інженерні пастки та крайові випадки під час ізоляції

1. **Неявна поведінка стандартної бібліотеки мови C:**
   Реалізації розподільника пам'яті `malloc` або функції форматованого виведення (`printf`, `std::cout`) при першому зверненні можуть намагатися зчитати системні конфігураційні файли (наприклад, `/etc/malloc.conf` або дані часових поясів `/etc/localtime`). Якщо перший виклик `malloc()` відбудеться після `cap_enter()`, ядро заблокує його з помилкою `ECAPMODE`, що призведе до аварійного завершення процесу. Щоб уникнути цього, рекомендується прогрівати розподільник пам'яті (виклик `malloc(1); free(...)`) та ініціалізувати локалі до виклику `cap_enter()`.
2. **Обов'язкова наявність права `CAP_FSTAT`:**
   Високорівневі потокові бібліотеки (`FILE*`, `fread`, `fwrite`, `std::ifstream`) перед початком буферизованого читання автоматично виконують системний виклик `fstat()` для визначення розміру блоку файлової системи (`st_blksize`). Якщо надати дескриптору лише право `CAP_READ` без `CAP_FSTAT`, перший же виклик `fread()` або `std::cin.read()` поверне помилку `ENOTCAPABLE`.
3. **Генерація псевдовипадкових чисел:**
   Спроба відкрити файл `/dev/urandom` усередині пісочниці зазнає краху. Замість файлового читання необхідно застосовувати прямий системний виклик `getrandom(2)` або функцію `arc4random_buf(3)`, які обслуговуються ядром безпосередньо через системний пул ентропії без звернення до простору імен VFS.
4. **Управління дочірніми процесами через `pdfork`:**
   Усередині пісочниці традиційний виклик `fork()` створює дочірній процес у тому ж capability-режимі, проте батьківський процес не може надіслати сигнал нащадку через `kill(pid, sig)`, оскільки глобальний простір PID заблоковано. Для коректного керування нащадками Capsicum надає дескриптори процесів `pdfork(int *pdp, 0)`: батько отримує дескриптор процесу `pdp` і керує життєвим циклом нащадка через виклики `pdkill(pdp, sig)` та `pdwait(pdp)`.
