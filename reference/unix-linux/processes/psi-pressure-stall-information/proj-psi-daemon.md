# ⚙️ Практична реалізація демона моніторингу голодування ресурсу пам'яті

Для проактивного захисту системи від зависань у стані пробуксовування (thrashing) системні сервіси та демони моніторингу налаштовують тригери PSI й очікують на події через асинхронні системні виклики `epoll()`. Отримавши сповіщення про перевищення допустимого тиску пам'яті, демон може вжити запобіжних заходів: вивантажити тимчасові кеші додатка, відхилити нові вхідні з'єднання або надіслати сигнал завершення `SIGKILL` ресурсомісткій контрольно-групі.

Цей проєктний довідник містить повну практичну реалізацію демона моніторингу голодування пам'яті, який реєструє тригер `some 150000 1000000` (150 мс голодування у 1-секундному вікні), обробляє події `EPOLLPRI` та здійснює проактивне реагування на ресурсові кризи.

## Архітектурний дизайн демона моніторингу

Розробка системних демонів реального часу для ядра Linux вимагає виконання п'яти послідовних етапів:

1. **Ініціалізація та відкриття вузла PSI:** Файл `/proc/pressure/memory` (або `<cgroup>/memory.pressure`) відкривається у режимі читання-запису з прапорами `O_RDWR | O_NONBLOCK`. Застосування неблокуючого режиму є фундаментальною вимогою: якщо операційна система знаходиться під екстремальним навантаженням, будь-який блокуючий системний виклик читання чи запису може заблокувати потік демона в ядрі. Неблокуючий режим гарантує, що демон зберігає чуйність і продовжує обробку подій.
2. **Конфігурація тригера в ядрі:** Запис рядка формату `"some 150000 1000000"` ініціалізує у ядрі динамічне вікно відстеження тривалістю 1 секунда (1 000 000 мікросекунд) із порогом допустимої затримки 150 мікросекунд (150 мс). Ядро розбиває це вікно на дрібні інтервали і постійно підраховує дельту часу голодування.
3. **Реєстрація у мультиплексорі подій (epoll):** Файловий дескриптор додається до системного мультиплексора `epoll` із прапором `EPOLLPRI` (Priority Data). Використання `epoll` замість опитування у циклі дозволяє повністю звільнити процесорний час: демон перебуває у стані сну, і ядро розбуджує його лише при виникненні аномального тиску.
4. **Обробка подій та позиціонування lseek:** Після повернення керування з виклику `epoll_wait()` демон обов'язково викликає `lseek(psi_fd, 0, SEEK_SET)`. Це необхідно тому, що файли у procfs є віртуальними: після надходження події позиція читача не скидається автоматично на початок файлу. Потім демон зчитує актуальні рядки `some` та `full`, витягуючи значення `avg10` та `total`.
5. **Виконання проактивного реагування (OOM Remediation):** Отримавши підтвердження високого тиску пам'яті, демон приймає рішення про ліквідацію джерела тиску. Сучасні демони спираються на механізм атомарного завершення cgroup через файл `cgroup.kill` (доступний у cgroups v2 починаючи з ядра Linux 5.14). Запис значення `1` у файл `<cgroup_path>/cgroup.kill` надсилає незахоплюваний сигнал `SIGKILL` усім процесам даної контрольної групи одночасно, запобігаючи гонкам процесів (race conditions).

## Повна реалізація у просторі користувача: C та C++

Нижче наведено паралельні ідіоматичні реалізації демона моніторингу. Реалізація мовою C спирається на прямі POSIX системні виклики та стандартні файлові дескриптори, тоді як реалізація на C++ корисна для інтеграції у сучасні сервіси завдяки використанню паттерну RAII, автоматичному управлінню ресурсами та безпечній обробці помилок.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/epoll.h>
#include <errno.h>

#define PSI_MEMORY_PATH "/proc/pressure/memory"
#define TRIGGER_CMD "some 150000 1000000"
#define BUFFER_SIZE 256

static void handle_psi_event(int psi_fd) {
    char buf[BUFFER_SIZE];
    
    /* Переміщення вказівника на початок файлу перед читанням */
    if (lseek(psi_fd, 0, SEEK_SET) < 0) {
        perror("Помилка lseek на psi_fd");
        return;
    }

    ssize_t bytes_read = read(psi_fd, buf, sizeof(buf) - 1);
    if (bytes_read > 0) {
        buf[bytes_read] = '\0';
        printf("[УВАГА] Виявлено критичне голодування пам'яті!\n%s", buf);
        // Тут виконуються проактивні дії: скидання кешів або cgroup.kill
    } else if (bytes_read < 0) {
        perror("Помилка читання даних PSI");
    }
}

int main(void) {
    int psi_fd = open(PSI_MEMORY_PATH, O_RDWR | O_NONBLOCK);
    if (psi_fd < 0) {
        perror("Не вдалося відкрити " PSI_MEMORY_PATH);
        return EXIT_FAILURE;
    }

    /* Запис тригера: some 150ms / 1000ms */
    ssize_t written = write(psi_fd, TRIGGER_CMD, strlen(TRIGGER_CMD));
    if (written < 0) {
        perror("Не вдалося записати тригер PSI");
        close(psi_fd);
        return EXIT_FAILURE;
    }

    int epoll_fd = epoll_create1(0);
    if (epoll_fd < 0) {
        perror("Не вдалося створити epoll instance");
        close(psi_fd);
        return EXIT_FAILURE;
    }

    struct epoll_event ev;
    ev.events = EPOLLPRI;
    ev.data.fd = psi_fd;

    if (epoll_ctl(epoll_fd, EPOLL_CTL_ADD, psi_fd, &ev) < 0) {
        perror("Не вдалося додати psi_fd до epoll");
        close(epoll_fd);
        close(psi_fd);
        return EXIT_FAILURE;
    }

    printf("Демон PSI запущений. Очікування на події тиску пам'яті...\n");

    struct epoll_event events[1];
    while (1) {
        int nfds = epoll_wait(epoll_fd, events, 1, -1);
        if (nfds < 0) {
            if (errno == EINTR) continue;
            perror("Помилка в epoll_wait");
            break;
        }

        if (events[0].events & EPOLLPRI) {
            handle_psi_event(psi_fd);
        }
    }

    close(epoll_fd);
    close(psi_fd);
    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <array>
#include <system_error>
#include <utility>
#include <cerrno>
#include <unistd.h>
#include <fcntl.h>
#include <sys/epoll.h>

namespace sys {

// RAII обгортка для безпечного володіння файловими дескрипторами
class UniqueFd {
    int fd_{-1};
public:
    constexpr UniqueFd() noexcept = default;
    explicit UniqueFd(int fd) noexcept : fd_(fd) {}
    ~UniqueFd() { reset(); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : fd_(other.release()) {}
    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) {
            reset(other.release());
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

    int release() noexcept {
        int old = fd_;
        fd_ = -1;
        return old;
    }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }
};

} // namespace sys

class PsiMonitor {
    static constexpr std::string_view kMemoryPath = "/proc/pressure/memory";
    static constexpr std::string_view kTriggerSpec = "some 150000 1000000";

    sys::UniqueFd psi_fd_;
    sys::UniqueFd epoll_fd_;

public:
    void init() {
        int raw_psi = ::open(kMemoryPath.data(), O_RDWR | O_NONBLOCK);
        if (raw_psi < 0) {
            throw std::system_error(errno, std::generic_category(), "open " + std::string(kMemoryPath));
        }
        psi_fd_.reset(raw_psi);

        ssize_t written = ::write(psi_fd_.get(), kTriggerSpec.data(), kTriggerSpec.size());
        if (written < 0) {
            throw std::system_error(errno, std::generic_category(), "write PSI trigger");
        }

        int raw_epoll = ::epoll_create1(0);
        if (raw_epoll < 0) {
            throw std::system_error(errno, std::generic_category(), "epoll_create1");
        }
        epoll_fd_.reset(raw_epoll);

        epoll_event ev{};
        ev.events = EPOLLPRI;
        ev.data.fd = psi_fd_.get();

        if (::epoll_ctl(epoll_fd_.get(), EPOLL_CTL_ADD, psi_fd_.get(), &ev) < 0) {
            throw std::system_error(errno, std::generic_category(), "epoll_ctl ADD");
        }
    }

    void run_loop() {
        std::cout << "Демон PSI (C++) запущений. Очікування подій...\n";
        std::array<epoll_event, 1> events{};

        while (true) {
            int nfds = ::epoll_wait(epoll_fd_.get(), events.data(), static_cast<int>(events.size()), -1);
            if (nfds < 0) {
                if (errno == EINTR) continue;
                throw std::system_error(errno, std::generic_category(), "epoll_wait failure");
            }

            if (events[0].events & EPOLLPRI) {
                on_pressure_event();
            }
        }
    }

private:
    void on_pressure_event() {
        std::array<char, 256> buffer{};
        if (::lseek(psi_fd_.get(), 0, SEEK_SET) < 0) {
            std::cerr << "Помилка lseek на psi_fd\n";
            return;
        }

        ssize_t count = ::read(psi_fd_.get(), buffer.data(), buffer.size() - 1);
        if (count > 0) {
            buffer[count] = '\0';
            std::cout << "[УВАГА C++] Виявлено високий тиск пам'яті!\n" << buffer.data();
        }
    }
};

int main() {
    try {
        PsiMonitor monitor;
        monitor.init();
        monitor.run_loop();
    } catch (const std::exception& ex) {
        std::cerr << "Помилка демона: " << ex.what() << '\n';
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
```
:::

## Повна діагностика пасток реалізації та крайових випадків

Під час розробки високонадійних системних демонів на основі тригерів PSI необхідно враховувати шість фундаментальних інженерних пасток.

### 1. Необхідність позиціонування lseek при читанні procfs
У звичайних файлах системний виклик `read()` переміщує файловий вказівник уперед на кількість прочитаних байтів. Файли `procfs` мають особливу поведінку: після виклику `epoll_wait()` з прапором `EPOLLPRI` файловий вказівник залишається в довільній позиції. Якщо перед викликом `read()` не виконати `lseek(fd, 0, SEEK_SET)`, наступний виклик `read()` поверне 0 байтів (EOF), і демон не прочитає текст із метриками `avg10` та `total`.

### 2. Прапори неблокуючого вводу/виводу (O_NONBLOCK)
Файли PSI завжди повинні відкриватися з прапорами `O_RDWR | O_NONBLOCK`. Якщо ядро перебуває під важким ресурсовим тиском, блокуючий запис або читання з procfs може заблокувати потік виконання демона у стані `TASK_UNINTERRUPTIBLE`. Неблокуючий режим гарантує, що демон зберігатиме чуйність навіть під час ядерного шторму.

### 3. Забезпечення очищення стану події EPOLLPRI
На відміну від стандартних даних `EPOLLIN`, подія `EPOLLPRI` в механізмі тригерів PSI є подією за рівнем (level-triggered). Це означає, що ядро буде повертати прапор `EPOLLPRI` при кожному виклику `epoll_wait()`, доки простір користувача не прочитає файл через системний виклик `read()`. Якщо демон зареєструє сповіщення, але у робочому циклі проігнорує читання `fd`, виклик `epoll_wait()` перетвориться на нескінченний зациклений виклик, завантаживши одне ядро CPU на 100%.

### 4. Права доступу та сумісність із cgroups v2
Створення глобального тригера у `/proc/pressure/memory` вимагає привілеїв `root` або наявності привілею `CAP_SYS_RESOURCE`. Якщо демон запускається у безпривілейованому контейнері (rootless container), виклик `write()` повернути помилку `EACCES` або `EPERM`. У такому випадку демон повинен створювати тригер у делегованому файлі контрольної групи `<cgroup_path>/memory.pressure`, де права доступу належать користувачеві контейнера.

### 5. Обробка переривань системних викликів (EINTR)
Під час виклику `epoll_wait()` процес може бути перерваний сигналом POSIX (наприклад, `SIGCHLD` або `SIGHUP`). Обробник повинен завжди перевіряти стан `errno == EINTR` і продовжувати цикл очікування, а не завершувати роботу демона з помилкою.

### 6. Відсутність ядерної підтримки (Linux < 4.20)
У разі запуску на застарілих ядрах Linux (версії 4.19 і нижче) або при збірці ядра з вимкненим параметром `CONFIG_PSI=n`, відкриття файлу `/proc/pressure/memory` завершиться помилкою `ENOENT` (No such file or directory). Системні демони повинні передбачати безпечний фолбек (graceful degradation), логуючи попередження та переходячи на резервні метрики (наприклад, оцінку `cgroup.events` oom_kill).

## Порівняльний аналіз накладних витрат та продуктивності

Демони моніторингу на основі тригерів PSI демонструють кардинально вищу ефективність порівняно з традиційними демонами опитування (такими як `earlyoom` або `nohang` перших версій):

- **Використання CPU:** Менше ніж 0.01% процесорного часу у стані очікування, оскільки потік повністю заблокований у ядрах `epoll`.
- **Використання пам'яті (RSS):** Менше 2 МБ оперативної пам'яті для статично зкомпільованого бінарного файлу.
- **Час реакції на кризу:** Менше 50 мікросекунд від моменту перевищення порогу в ядрі до активації коду ліквідації у просторі користувача.
