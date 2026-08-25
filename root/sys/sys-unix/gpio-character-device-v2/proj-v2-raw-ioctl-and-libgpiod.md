# ⚙️ Практична реалізація: Прямі ioctl v2 та бібліотека libgpiod v2

Ця вставка надає готові до використання, автономні та повністю протестовані приклади коду для роботи з сучасним ABI v2 символьного пристрою GPIO у Linux. У практичній системній розробці вибір інструментарію доступу до апаратних виводів є фундаментальним архітектурним рішенням. Нижче детально проаналізовано та реалізовано два протилежні підходи:

1. **Низькорівнева взаємодія через прямі системні виклики `ioctl()`:** Використовує виключно системні заголовкові файли ядра (`<linux/gpio.h>`, `<sys/ioctl.h>`). Цей підхід є єдиним можливим вибором у середовищах із суворими обмеженнями на розмір та залежності (наприклад, утиліти initramfs, автономні завантажувачі, мінімалістичні системи Embedded Linux на базі BusyBox або системи з автономними статичними бінарними файлами).
2. **Високорівневе управління через офіційну бібліотеку `libgpiod` v2:** Офіційний проєкт спільноти ядра Linux, який надає безпечні, зручні та виразні абстракції простору користувача. Бібліотека абстрагує складність конструювання бінарних структур `ioctl()`, обробляє відмінності у вирівнюванні типів даних та надає ідіоматичний C++20 API.

Усі приклади нижче реалізовано у двох рівнозначних варіантах — мовами C та C++, із дотриманням суворих стандартизованих практик безпеки та lifetime management.

---

## 1. Низькорівнева реалізація через прямі системні виклики ioctl v2

Низькорівневий підхід вимагає від системного програміста глибокого розуміння бінарного макету структур ядра. Перед викликом `ioctl()` над відкритим дескриптором `/dev/gpiochipN` необхідно обнулити пам'ять структури за допомогою `memset()` або виразу ініціалізації `{0}`, щоб запобігти передачі неочищеного стек-сміття у простір ядра.

### 1.1. Детальний аналіз механізму масок атрибутів

У структурі `gpio_v2_line_request` масив `offsets` містить перелік фізичних пінів на контролері. Кожен елемент `config.attrs[]` — це `struct gpio_v2_line_config_attribute`, тобто пара з самого атрибута (`attr`) та маски ліній (`mask`); порядок елементів у `offsets` визначає бітову позицію в цій масці:
* Якщо `offsets[0] = 17` та `offsets[1] = 27`, то перший елемент (індекс 0) відповідає біту `1 << 0` (маска `0x01`), а другий елемент (індекс 1) — біту `1 << 1` (маска `0x02`).
* Атрибут із `id = GPIO_V2_LINE_ATTR_ID_FLAGS` та `mask = 0x01` перевизначає прапори конфігурації лише для лінії 17 (робить її виходом з підтяжкою Pull-Up).
* Атрибут із `id = GPIO_V2_LINE_ATTR_ID_DEBOUNCE` та `mask = 0x02` задає період фільтрації брязкоту 5000 мікросекунд (5 мс) лише для лінії 27.

Цей механізм дозволяє конфігурувати до 64 ліній в одному системному виклику, задаючи унікальні апаратні параметри для кожного піна.

### 1.2. Обробка неблокуючого I/O та виявлення втрати подій

При роботі з перериваннями дескриптор `line_fd` може функціонувати як у блокуючому, так і в неблокуючому режимі (`O_NONBLOCK`). У неблокуючому режимі виклик `read(line_fd, ...)` при відсутності нових подій повертає `-1`, а змінна `errno` встановлюється в `EAGAIN` або `EWOULDBLOCK`.

Для контролю цілісності потоку подій структура `gpio_v2_line_event` містить 32-бітне поле `seqno` (глобальний порядковий номер події для даного дескриптора) та `line_seqno` (порядковий номер для конкретної лінії). Якщо при зчитуванні чергової події `event.seqno` виявляється більшим за `last_seqno + 1`, додаток фіксує втрату переривань через переповнення кільцевого буфера ядра. У такому разі програма повинна зчитати поточні логічні рівні через `GPIO_V2_LINE_GET_VALUES_IOCTL` для синхронізації стану.

### 1.3. Архітектурні особливості C та C++ реалізацій

У цьому прикладі реалізовано повний цикл управління двома лініями:
* **Лінія 17 (Offset 17):** Конфігурується як цифровий вихід із підтяжкою до живлення (`GPIO_V2_LINE_FLAG_OUTPUT | GPIO_V2_LINE_FLAG_BIAS_PULL_UP`). Після захоплення програма виставляє на ній логічну 1 через виклик `GPIO_V2_LINE_SET_VALUES_IOCTL`.
* **Лінія 27 (Offset 27):** Конфігурується як цифровий вхід із моніторингом двох фронтів сигналу (`EDGE_RISING | EDGE_FALLING`) та фільтрацією брязкоту 5 мілісекунд (5000 мкс, `GPIO_V2_LINE_ATTR_ID_DEBOUNCE`).

* **Версія мовою C:** Застосовує перевірку повернення викликів `open()`, `ioctl()`, `poll()` та `read()`. Обробка помилок спирається на макроси `perror()` та перевірку змінної `errno`. Вивільнення ресурсів виконується явно через `close(line_fd)` та `close(chip_fd)`.
* **Версія мовою C++20:** Використовує власну шаблонізовану RAII-обгортку `sys::UniqueFd`. Вона позбавляє розробника необхідності вручну закривати файлові дескриптори у гілках обробки помилок: при виході з області видимості деструктор `UniqueFd` автоматично викликає `::close()`. Помилки системних викликів транслюються у текстові повідомлення через `std::generic_category().message(errno)`.

:::tabs
```c
/* Приклад низькорівневого коду мовою C (ioctl ABI v2) */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <poll.h>
#include <linux/gpio.h>

int main(void) {
    int chip_fd = open("/dev/gpiochip0", O_RDWR | O_CLOEXEC);
    if (chip_fd < 0) {
        perror("Не вдалося відкрити /dev/gpiochip0");
        return EXIT_FAILURE;
    }

    struct gpio_v2_line_request req;
    memset(&req, 0, sizeof(req));

    /* Налаштування ліній: offset 17 (OUT), offset 27 (IN з IRQ) */
    req.offsets[0] = 17;
    req.offsets[1] = 27;
    req.num_lines = 2;
    snprintf(req.consumer, sizeof(req.consumer), "raw-ioctl-demo");

    /* Глобальні прапори за замовчуванням: вхід з перехопленням фронтів */
    req.config.flags = GPIO_V2_LINE_FLAG_INPUT |
                       GPIO_V2_LINE_FLAG_EDGE_RISING |
                       GPIO_V2_LINE_FLAG_EDGE_FALLING;

    /* Перевизначення для лінії 17: вихід із підтяжкою PULL_UP */
    req.config.num_attrs = 2;
    
    /* Атрибут 0: Прапори для лінії 17 (маска 0x01 = перший елемент offsets[]) */
    req.config.attrs[0].attr.id = GPIO_V2_LINE_ATTR_ID_FLAGS;
    req.config.attrs[0].attr.flags = GPIO_V2_LINE_FLAG_OUTPUT | GPIO_V2_LINE_FLAG_BIAS_PULL_UP;
    req.config.attrs[0].mask = 0x01;

    /* Атрибут 1: Фільтрація брязкоту 5 мс (5000 мкс) для лінії 27 (маска 0x02 = другий елемент) */
    req.config.attrs[1].attr.id = GPIO_V2_LINE_ATTR_ID_DEBOUNCE;
    req.config.attrs[1].attr.debounce_period_us = 5000;
    req.config.attrs[1].mask = 0x02;

    if (ioctl(chip_fd, GPIO_V2_GET_LINE_IOCTL, &req) < 0) {
        perror("Помилка виконання GPIO_V2_GET_LINE_IOCTL");
        close(chip_fd);
        return EXIT_FAILURE;
    }

    int line_fd = req.fd;
    printf("Отримано Line FD: %d. Встановлюємо HIGH на лінії 17...\n", line_fd);

    /* Встановлення логічної 1 на лінії 17 (маска 0x01) */
    struct gpio_v2_line_values vals;
    memset(&vals, 0, sizeof(vals));
    vals.mask = 0x01;
    vals.bits = 0x01;

    if (ioctl(line_fd, GPIO_V2_LINE_SET_VALUES_IOCTL, &vals) < 0) {
        perror("Помилка виконання GPIO_V2_LINE_SET_VALUES_IOCTL");
    }

    /* Очікування подій переривання на лінії 27 за допомогою poll() */
    struct pollfd pfd;
    pfd.fd = line_fd;
    pfd.events = POLLIN;

    printf("Очікування подій на лінії 27 (натисніть кнопку або змініть рівень)...\n");
    int ret = poll(&pfd, 1, 10000); /* таймаут 10 секунд */

    if (ret > 0 && (pfd.revents & POLLIN)) {
        struct gpio_v2_line_event event;
        ssize_t bytes = read(line_fd, &event, sizeof(event));
        if (bytes == sizeof(event)) {
            printf("ПОДІЯ! Час: %llu нс, Фронт: %s, Лінія: %u, SeqNo: %u\n",
                   (unsigned long long)event.timestamp_ns,
                   (event.id == GPIO_V2_LINE_EVENT_RISING_EDGE) ? "RISING" : "FALLING",
                   event.offset, event.seqno);
        }
    } else if (ret == 0) {
        printf("Таймаут очікування події.\n");
    }

    /* Автоматичне вивільнення ліній ядром при закритті дескрипторів */
    close(line_fd);
    close(chip_fd);
    return EXIT_SUCCESS;
}
```
```cpp
// Ідіоматичний приклад C++20 (ioctl ABI v2 з RAII та шаблонами)
#include <iostream>
#include <string_view>
#include <array>
#include <system_error>
#include <cstdint>
#include <cstring>
#include <cstdlib>
#include <cerrno>
#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <poll.h>
#include <linux/gpio.h>

namespace sys {
    // Обгортка RAII для файлового дескриптора
    class UniqueFd {
        int fd_{-1};
    public:
        constexpr UniqueFd() noexcept = default;
        explicit UniqueFd(int fd) noexcept : fd_(fd) {}
        ~UniqueFd() { reset(); }

        UniqueFd(const UniqueFd&) = delete;
        UniqueFd& operator=(const UniqueFd&) = delete;

        UniqueFd(UniqueFd&& o) noexcept : fd_(o.release()) {}
        UniqueFd& operator=(UniqueFd&& o) noexcept {
            if (this != &o) { reset(o.release()); }
            return *this;
        }

        [[nodiscard]] int get() const noexcept { return fd_; }
        [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
        [[nodiscard]] int release() noexcept {
            int tmp = fd_;
            fd_ = -1;
            return tmp;
        }
        void reset(int new_fd = -1) noexcept {
            if (fd_ >= 0) { ::close(fd_); }
            fd_ = new_fd;
        }
    };
}

int main() {
    sys::UniqueFd chip_fd{::open("/dev/gpiochip0", O_RDWR | O_CLOEXEC)};
    if (!chip_fd.valid()) {
        std::cerr << "Не вдалося відкрити /dev/gpiochip0: " 
                  << std::generic_category().message(errno) << '\n';
        return EXIT_FAILURE;
    }

    ::gpio_v2_line_request req{};
    req.offsets[0] = 17;
    req.offsets[1] = 27;
    req.num_lines = 2;
    std::strncpy(req.consumer, "cpp-raw-ioctl-demo", sizeof(req.consumer) - 1);

    req.config.flags = GPIO_V2_LINE_FLAG_INPUT |
                       GPIO_V2_LINE_FLAG_EDGE_RISING |
                       GPIO_V2_LINE_FLAG_EDGE_FALLING;

    req.config.num_attrs = 2;
    
    // Атрибут 0: Output + Pull-Up для лінії 17 (mask = 0x01)
    req.config.attrs[0].attr.id = GPIO_V2_LINE_ATTR_ID_FLAGS;
    req.config.attrs[0].attr.flags = GPIO_V2_LINE_FLAG_OUTPUT | GPIO_V2_LINE_FLAG_BIAS_PULL_UP;
    req.config.attrs[0].mask = 0x01;

    // Атрибут 1: Debounce 5000 мкс для лінії 27 (mask = 0x02)
    req.config.attrs[1].attr.id = GPIO_V2_LINE_ATTR_ID_DEBOUNCE;
    req.config.attrs[1].attr.debounce_period_us = 5000;
    req.config.attrs[1].mask = 0x02;

    if (::ioctl(chip_fd.get(), GPIO_V2_GET_LINE_IOCTL, &req) < 0) {
        std::cerr << "Помилка ioctl GET_LINE: " << std::generic_category().message(errno) << '\n';
        return EXIT_FAILURE;
    }

    sys::UniqueFd line_fd{req.fd};
    std::cout << "Отримано Line FD (" << line_fd.get() << "). Встановлюємо HIGH на 17...\n";

    ::gpio_v2_line_values vals{};
    vals.mask = 0x01;
    vals.bits = 0x01;

    if (::ioctl(line_fd.get(), GPIO_V2_LINE_SET_VALUES_IOCTL, &vals) < 0) {
        std::cerr << "Помилка SET_VALUES: " << std::generic_category().message(errno) << '\n';
    }

    ::pollfd pfd{.fd = line_fd.get(), .events = POLLIN, .revents = 0};
    std::cout << "Очікування події переривання (10 с таймаут)...\n";

    if (int ret = ::poll(&pfd, 1, 10000); ret > 0 && (pfd.revents & POLLIN)) {
        ::gpio_v2_line_event event{};
        if (::read(line_fd.get(), &event, sizeof(event)) == sizeof(event)) {
            std::cout << "ПОДІЯ C++! Timestamp: " << event.timestamp_ns << " нс, "
                      << "Фронт: " << (event.id == GPIO_V2_LINE_EVENT_RISING_EDGE ? "RISING" : "FALLING")
                      << ", Пін: " << event.offset << ", SeqNo: " << event.seqno << '\n';
        }
    }

    // Звільнення ресурсів відбудеться автоматично завдяки RAII-деструкторам UniqueFd
    return EXIT_SUCCESS;
}
```
:::

---

## 2. Високорівневе управління через бібліотеку libgpiod v2

Офіційна системна бібліотека `libgpiod` v2 спрощує роботу з GPIO, надаючи високорівневі об'єкти конфігурації. Вона ізолює системного розробника від ручного заповнення структур `ioctl()`, обробляє різницю у вирівнюванні та забезпечує атомарний життєвий цикл об'єктів.

### 2.1. Архітектурні компоненти libgpiod v2

Модель об'єктів `libgpiod` v2 розділена на чотири ключові сутності:
1. `gpiod_chip` (`gpiod::chip`): Представляє відкритий контролер GPIO. Слугує фабрикою для запиту ліній.
2. `gpiod_line_settings` (`gpiod::line_settings`): Інкапсулює конфігурацію однієї лінії (напрямок, підтяжка, режим виходу, придушення брязкоту, джерело міток часу).
3. `gpiod_line_config` (`gpiod::line_config`): Контейнер, який асоціює об'єкти `line_settings` із фізичними індексами пінів (`offsets`).
4. `gpiod_line_request` (`gpiod::line_request`): Об'єкт активного захоплення ліній. Надає методи `set_value()`, `get_value()`, `read_edge_events()` та автоматично вивільняє ресурси ядра у деструкторі.

### 2.2. Багатопотоковість та крайові випадки при гарячому відключенні

Об'єкти `gpiod::chip` та `gpiod::line_request` не є потокобезпечними за замовчуванням для паралельних модифікацій з кількох потоків. Якщо кілька потоків застосунку мають змінювати рівні різних ліній одного запиту, доступ до об'єкта `line_request` необхідно захищати за допомогою `std::mutex`.

У разі гарячого відключення розширювача портів на шині USB або I2C (наприклад, від'єднання адаптера FT232H під час роботи програми) виклики `read_edge_events()` або `set_value()` негайно повертають помилку з кодом `ENODEV` (No such device). В C++ байндингах ця ситуація генерує виняток `gpiod::exception`, у обробнику якого програма має закрити `chip` та перейти в режим періодичного перепідключення.

### 2.3. Компіляція, лінкування та інтеграція з CMake

Для компіляції програми мовою C необхідно встановити системний заголовок `<gpiod.h>` та лінкувати проєкт із бібліотекою `libgpiod`:
```bash
gcc -Wall -O2 demo.c -o demo -lgpiod
```

Для компіляції програми мовою C++20 використовується новий офіційний заголовок `<gpiod.hpp>` та лінкування з бібліотекою `-lgpiodcxx`:
```bash
g++ -std=c++20 -Wall -O2 demo.cpp -o demo -lgpiodcxx
```

При складанні проєкту у збіркових системах CMake рекомендується використовувати PkgConfig для автоматичного пошуку бібліотек:
```cmake
find_package(PkgConfig REQUIRED)
pkg_check_modules(GPIODCXX REQUIRED IMPORTED_TARGET libgpiodcxx>=2.0)
target_link_libraries(my_app PRIVATE PkgConfig::GPIODCXX)
```

### 2.4. Порівняння підходів у C та C++

* **Версія мовою C:** Використовує явне створення об'єктів через `gpiod_line_settings_new()`, `gpiod_line_config_new()` та обов'язковий виклик парних функцій `gpiod_*_free()` у блоці очищення пам'яті (`cleanup:`).
* **Версія мовою C++20:** Працює зі стандартними типами C++ (`std::chrono::microseconds`, `std::exception`). Об'єкти налаштувань та дескриптори запиту створюються на стеку, а їхній життєвий цикл контролюється деструкторами C++. Події переривань зчитуються через об'єкт `edge_event_buffer`, який автоматично виділяє пам'ять під масив структур та надає ітератори C++ для зручного обходу отриманих переривань. Завдяки цій обгортці розробник уникає необхідності працювати з сирими покажчиками C-бібліотеки.

:::tabs
```c
/* Приклад використання libgpiod v2 мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <gpiod.h>

int main(void) {
    int rc = EXIT_SUCCESS;
    struct gpiod_chip *chip = gpiod_chip_open("/dev/gpiochip0");
    if (!chip) {
        perror("Не вдалося відкрити чип через libgpiod");
        return EXIT_FAILURE;
    }

    /* Створення налаштувань для вихідної лінії */
    struct gpiod_line_settings *out_settings = gpiod_line_settings_new();
    gpiod_line_settings_set_direction(out_settings, GPIOD_LINE_DIRECTION_OUTPUT);
    gpiod_line_settings_set_bias(out_settings, GPIOD_LINE_BIAS_PULL_UP);

    /* Створення налаштувань для вхідної лінії з моніторингом подій */
    struct gpiod_line_settings *in_settings = gpiod_line_settings_new();
    gpiod_line_settings_set_direction(in_settings, GPIOD_LINE_DIRECTION_INPUT);
    gpiod_line_settings_set_edge_detection(in_settings, GPIOD_LINE_EDGE_BOTH);
    gpiod_line_settings_set_debounce_period_us(in_settings, 5000);

    /* Збирання загальної конфігурації ліній */
    struct gpiod_line_config *line_cfg = gpiod_line_config_new();
    unsigned int out_offsets[] = {17};
    unsigned int in_offsets[] = {27};

    gpiod_line_config_add_line_settings(line_cfg, out_offsets, 1, out_settings);
    gpiod_line_config_add_line_settings(line_cfg, in_offsets, 1, in_settings);

    /* Конфігурація запиту */
    struct gpiod_request_config *req_cfg = gpiod_request_config_new();
    gpiod_request_config_set_consumer(req_cfg, "libgpiod-c-demo");

    /* Виконання запиту на захоплення ліній */
    struct gpiod_line_request *request = gpiod_chip_request_lines(chip, req_cfg, line_cfg);
    if (!request) {
        perror("Помилка захоплення ліній через gpiod");
        rc = EXIT_FAILURE;
        goto cleanup;
    }

    printf("Лінії успішно захоплено через libgpiod v2! Встановлюємо HIGH на лінії 17...\n");
    gpiod_line_request_set_value(request, 17, GPIOD_LINE_VALUE_ACTIVE);

    /* Буфер для зчитування подій */
    struct gpiod_edge_event_buffer *event_buf = gpiod_edge_event_buffer_new(16);
    printf("Очікування події переривання на лінії 27...\n");

    int ret = gpiod_line_request_read_edge_events(request, event_buf, 16);
    if (ret > 0) {
        struct gpiod_edge_event *event = gpiod_edge_event_buffer_get_event(event_buf, 0);
        enum gpiod_edge_event_type type = gpiod_edge_event_get_event_type(event);
        uint64_t ts = gpiod_edge_event_get_timestamp_ns(event);

        printf("Отримано подію від libgpiod! Timestamp: %llu нс, Тип: %s\n",
               (unsigned long long)ts,
               (type == GPIOD_EDGE_EVENT_RISING_EDGE) ? "RISING" : "FALLING");
    }

    gpiod_edge_event_buffer_free(event_buf);
    gpiod_line_request_release(request);

cleanup:
    gpiod_request_config_free(req_cfg);
    gpiod_line_config_free(line_cfg);
    gpiod_line_settings_free(out_settings);
    gpiod_line_settings_free(in_settings);
    gpiod_chip_close(chip);
    return rc;
}
```
```cpp
// Ідіоматичний приклад C++20 з використанням сучасного libgpiod v2 C++ API (<gpiod.hpp>)
#include <iostream>
#include <chrono>
#include <cstdlib>
#include <gpiod.hpp>

int main() {
    try {
        // Відкриття контролера
        ::gpiod::chip chip("/dev/gpiochip0");

        // Налаштування для виходу (лінія 17)
        ::gpiod::line_settings out_settings;
        out_settings.set_direction(::gpiod::line::direction::OUTPUT);
        out_settings.set_bias(::gpiod::line::bias::PULL_UP);

        // Налаштування для вхідної лінії з подійним моніторингом (лінія 27)
        ::gpiod::line_settings in_settings;
        in_settings.set_direction(::gpiod::line::direction::INPUT);
        in_settings.set_edge_detection(::gpiod::line::edge::BOTH);
        in_settings.set_debounce_period(std::chrono::microseconds(5000));

        // Формування мапи конфігурації
        ::gpiod::line_config line_cfg;
        line_cfg.add_line_settings(17, out_settings);
        line_cfg.add_line_settings(27, in_settings);

        // Конфігурація запиту
        ::gpiod::request_config req_cfg;
        req_cfg.set_consumer("libgpiod-cxx-demo");

        // Захоплення ліній (повертає об'єкт line_request із керуванням RAII)
        auto request = chip.request_lines(req_cfg, line_cfg);

        std::cout << "C++ libgpiod v2: Встановлюємо HIGH на лінію 17...\n";
        request.set_value(17, ::gpiod::line::value::ACTIVE);

        // Буфер подій
        ::gpiod::edge_event_buffer event_buf(16);

        std::cout << "C++ libgpiod v2: Очікування подій на лінії 27...\n";
        if (request.wait_edge_events(std::chrono::seconds(10))) {
            request.read_edge_events(event_buf);
            for (const auto& event : event_buf) {
                std::cout << "Отримано подію! Timestamp: " << event.timestamp_ns() << " нс, "
                          << "Тип: " << (event.type() == ::gpiod::edge_event::type::RISING_EDGE ? "RISING" : "FALLING")
                          << ", Offset: " << event.line_offset() << '\n';
            }
        } else {
            std::cout << "Таймаут очікування події.\n";
        }

    } catch (const std::exception& ex) {
        std::cerr << "Критична помилка gpiod::exception: " << ex.what() << '\n';
        return EXIT_FAILURE;
    }

    // Автоматичне звільнення всіх ресурсів при виході з області видимості
    return EXIT_SUCCESS;
}
```
:::
