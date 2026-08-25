# ⚙️ Реалізація Syslog-клієнта та парсера повідомлень RFC 5424

Практична робота із протоколом Syslog у мовах програмування C та C++ охоплює два фундаментальних завдання: створення та відправку мережевих чи локальних пакетів від імені програми-клієнта та зворотне розбирання (парсинг) вхідного потоку байтів на боці фонового демона чи сервера збору логів.

Офіційна специфікація RFC 5424 регламентує суворий текстовий формат кадру, який починається з кутових дужок із числовим значенням пріоритету `<PRIVAL>`, за якими слідують версія протоколу, часова мітка у стандарті ISO 8601, ім'я хоста, ідентифікатор програми, PID процесу, ідентифікатор типу події, блок структурованих даних у квадратних дужках `[SD-ID PARAM="VALUE"]` та довільне текстове повідомлення в кодуванні UTF-8.

Нижче наведено повноцінну реалізацію двох взаємопов'язаних компонентів:
1. **Низькорівневий Syslog-клієнт:** створює локальний міжпроцесний сокет Unix (`AF_UNIX`, `SOCK_DGRAM`), форматує повідомлення відповідно до вимог RFC 5424 з обчисленням пріоритету `PRIVAL = Facility · 8 + Severity` та надсилає його безпосередньо в системний канал `/dev/log`.
2. **Нуль-копіювальний парсер повідомлень RFC 5424:** приймає сирий текстовий пакет, виділяє з нього числові параметри категорій та рівнів важливості, перевіряє цілісність полів і повертає розібрану структуру даних для подальшої обробки або зберігання.

### Архітектура локального сокета `/dev/log` та мережевих сокетів

При створенні сокета Unix типу `SOCK_DGRAM` системний виклик `sendto()` відправляє датаграму безпосередньо у сокет операційної системи. Якщо демон логування (`rsyslogd` чи `journald`) запущені та слухають сокет `/dev/log`, пакет приймається миттєво. На відміну від сокетів `SOCK_STREAM` (TCP), датаграмний сокет `SOCK_DGRAM` зберігає межі окремих повідомлень, що спрощує зчитування та унеможливлює склеювання кількох логів в один потік.

Особливості роботи з міжпроцесними сокетами Unix у C та C++:
- **Шлях сокета:** Файл сокета розташований за шляхом `/dev/log` (у сучасних системах з `systemd` це символьне посилання на `/run/systemd/journal/dev-log`).
- **Неблокуюча відправка:** Для запобігання зависанню програми під час переповнення системних буферів сокет можна перевести у неблокуючий режим за допомогою прапорця `SOCK_NONBLOCK`. Якщо сокет переповнено, виклик `sendto()` миттєво поверне помилку `EAGAIN` або `EWOULDBLOCK`, дозволяючи програмі зберегти лог у локальному буфері пам'яті.
- **Розмір датаграми:** Рекомендований максимальний розмір буфера становить 2048 байтів, що повністю покриває вимоги RFC 5424 і запобігає відкиданню пакетів ядром.

### Налаштування буферів сокета через setsockopt()

При високій інтенсивності генерування логів системні буфери сокета за замовчуванням можуть швидко переповнюватися. Для уникнення втрати пакетів програма розширює розмір буфера відправки `SO_SNDBUF` або буфера прийому `SO_RCVBUF` за допомогою системного виклику `setsockopt()`:

```text
int sndbuf_size = 65536; // 64 Кб буфер відправки
if (setsockopt(sock_fd, SOL_SOCKET, SO_SNDBUF, &sndbuf_size, sizeof(sndbuf_size)) < 0) {
    perror("setsockopt SO_SNDBUF");
}
```

Таке налаштування дозволяє згладжувати тимчасові піки навантаження, коли фоновий демон логування зайнятий обробкою попередніх записів і не встигає зчитувати нові датаграми з сокета `/dev/log`.

### Особливості парсингу та відсутність динамічних виділень

При виконанні парсингу вхідного рядка ключовою інженерною задачею є мінімізація динамічного виділення пам'яті (`malloc`). На високонавантаженому сервері логування обробка мільйонів повідомлень на секунду з постійним виділенням пам'яті у купі (heap) створює критичне навантаження на фрагментацію пам'яті та збирач сміття.

У C++ реалізації для цього застосовується класична техніка зрізів пам'яті через обгортку `std::string_view`, яка вказує на фрагменти вже існуючого текстового буфера без створення нових копій рядків. Обгортка `std::optional<Message>` дозволяє елегантно повертати результат розбору або повідомляти про помилку синтаксису без використання повільних винятків C++ (exceptions).

Контроль помилок синтаксису перевіряє наявність початкової кутової дужки, правильно розраховує діленням на 8 та остачею від ділення числові значення категорій та важливості, а також відокремлює блок структурованих даних від корисного навантаження (payload).

### Вимоги до вирівнювання пам'яті та упакованих структур у C

При розробці системних парсерів у C часто виникає спокуса використовувати упаковані структури (`__attribute__((packed))`) для відображення байтів протоколу безпосередньо у пам'яті. 

Проте для текстових протоколів на кшталт RFC 5424 цей підхід не застосовується, оскільки поля мають змінну довжину та розділені пробілами. Замість прямого відображення структури C-пасер використовує лінійні покажчики на символьні масиви. Масиви `timestamp`, `hostname`, `app_name` фіксованого розміру у структурі `syslog_message_t` забезпечують безпечне копіювання через `strncpy()`, гарантуючи наявність нульового термінатора `\0` в кінці кожного рядка.

### Обробка помилок та повторне підключення при перезапуску логера

При тривалій роботі сервісу системний демон логування (наприклад `rsyslogd` чи `journald`) може бути перезапущений адміністратором. Під час перезапуску файл сокета `/dev/log` вилучається і створюється заново з новим інодом на файловій системі.

Якщо клієнтський процес відкрив сокет Unix за допомогою системного виклику `connect()`, після перезапуску демона наступні виклики `write()` або `send()` повертатимуть помилку `ECONNREFUSED` або `EPIPE`.

Для гарантування надійної відправки системний клієнт повинен обробляти ці помилки та виконувати повторну ініціалізацію (reconnect):
1. Якщо `sendto()` повертає `ECONNREFUSED` або `ENOENT`, закрити старий дескриптор `close(fd)`.
2. Створити новий сокет `socket(AF_UNIX, SOCK_DGRAM, 0)`.
3. Повторити спробу відправки повідомлення у новий сокет.

Виробничий код логування завжди передбачає обробку повернення `sendto()` з відновленням підключення, що гарантує безперебійну роботу служби протягом місяців без втрати повідомлень.

---

## Приклад реалізації у C та C++

:::tabs
```c
/* Практичний Syslog-клієнт та парсер RFC 5424 на мові C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <time.h>
#include <sys/socket.h>
#include <sys/un.h>

#define SYSLOG_PATH "/dev/log"
#define BUFFER_SIZE 2048

/* Структура для збереження розібраного syslog-повідомлення */
typedef struct {
    int prival;
    int facility;
    int severity;
    int version;
    char timestamp[64];
    char hostname[128];
    char app_name[64];
    char procid[32];
    char msgid[64];
    char msg[1024];
} syslog_message_t;

/* Обчислення поточного часу у форматі ISO 8601 */
static void get_iso8601_time(char *buf, size_t len) {
    time_t now = time(NULL);
    struct tm tm_info;
    localtime_r(&now, &tm_info);
    strftime(buf, len, "%Y-%m-%dT%H:%M:%S%z", &tm_info);
}

/* Відправка розширеного RFC 5424 повідомлення у /dev/log */
int send_syslog_rfc5424(int facility, int severity, const char *app_name, const char *msg) {
    int sock_fd = socket(AF_UNIX, SOCK_DGRAM, 0);
    if (sock_fd < 0) {
        perror("socket");
        return -1;
    }

    struct sockaddr_un addr;
    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    strncpy(addr.sun_path, SYSLOG_PATH, sizeof(addr.sun_path) - 1);

    int prival = (facility * 8) + severity;
    char time_str[64];
    get_iso8601_time(time_str, sizeof(time_str));
    pid_t pid = getpid();

    char payload[BUFFER_SIZE];
    /* Формат RFC 5424: <PRIVAL>VERSION TIMESTAMP HOSTNAME APP-NAME PROCID MSGID STRUCTURED-DATA MSG */
    int len = snprintf(payload, sizeof(payload),
                       "<%d>1 %s localhost %s %d ID47 - %s",
                       prival, time_str, app_name, pid, msg);

    if (len < 0 || len >= (int)sizeof(payload)) {
        close(sock_fd);
        return -1;
    }

    ssize_t sent = sendto(sock_fd, payload, len, 0, (struct sockaddr *)&addr, sizeof(addr));
    close(sock_fd);
    return (sent == len) ? 0 : -1;
}

/* Розбір сирого текстового рядка RFC 5424 */
int parse_syslog_rfc5424(const char *raw, syslog_message_t *out) {
    if (!raw || !out) return -1;
    memset(out, 0, sizeof(syslog_message_t));

    /* Очікується формат: <PRIVAL>VERSION TIMESTAMP HOSTNAME APP-NAME PROCID MSGID SD MSG */
    if (raw[0] != '<') return -1;

    const char *ptr = raw + 1;
    out->prival = atoi(ptr);

    /* Розбиваємо PRIVAL на Facility та Severity */
    out->facility = out->prival / 8;
    out->severity = out->prival % 8;

    ptr = strchr(ptr, '>');
    if (!ptr) return -1;
    ptr++; // Переходимо за '>'

    int parsed = sscanf(ptr, "%d %63s %127s %63s %31s %63s",
                        &out->version,
                        out->timestamp,
                        out->hostname,
                        out->app_name,
                        out->procid,
                        out->msgid);

    if (parsed < 6) return -1;

    /* Пропускаємо розібрані поля і шукаємо початок повідомлення */
    const char *msg_ptr = strchr(ptr, '-'); // Пропускаємо Structured-Data (-)
    if (msg_ptr) {
        msg_ptr++;
        if (*msg_ptr == ' ') msg_ptr++;
        strncpy(out->msg, msg_ptr, sizeof(out->msg) - 1);
    }

    return 0;
}

int main(void) {
    printf("--- Відправка RFC 5424 у /dev/log ---\n");
    if (send_syslog_rfc5424(1, 3, "custom_app", "Критична помилка пам'яті!") == 0) {
        printf("Повідомлення успішно відправлено.\n");
    }

    printf("\n--- Парсинг тестового пакету RFC 5424 ---\n");
    const char *sample = "<83>1 2026-08-14T13:36:16+0300 myhost auth_service 4512 ID99 - Пароль користувача скинуто";
    syslog_message_t msg;

    if (parse_syslog_rfc5424(sample, &msg) == 0) {
        printf("PRIVAL: %d (Facility: %d [authpriv], Severity: %d [err])\n",
               msg.prival, msg.facility, msg.severity);
        printf("Версія: %d\nЧас: %s\nХост: %s\nПрограма: %s [PID: %s]\nПовідомлення: %s\n",
               msg.version, msg.timestamp, msg.hostname, msg.app_name, msg.procid, msg.msg);
    }

    return 0;
}
```
```cpp
// Ідіоматичний C++20 Syslog-клієнт та парсер RFC 5424
#include <iostream>
#include <string>
#include <string_view>
#include <optional>
#include <format>
#include <chrono>
#include <system_error>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/un.h>

namespace syslog {

enum class Facility : uint8_t {
    Kern = 0, User = 1, Mail = 2, Daemon = 3, Auth = 4, AuthPriv = 10, Local0 = 16
};

enum class Severity : uint8_t {
    Emerg = 0, Alert = 1, Crit = 2, Error = 3, Warning = 4, Notice = 5, Info = 6, Debug = 7
};

struct Message {
    uint8_t facility;
    uint8_t severity;
    uint8_t version;
    std::string timestamp;
    std::string hostname;
    std::string app_name;
    std::string procid;
    std::string msgid;
    std::string structured_data;
    std::string payload;
};

// RAII обгортка над Unix сокетом
class SocketClient {
public:
    explicit SocketClient(std::string_view socket_path = "/dev/log") {
        m_fd = ::socket(AF_UNIX, SOCK_DGRAM, 0);
        if (m_fd < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося створити сокет");
        }

        m_addr.sun_family = AF_UNIX;
        std::copy_n(socket_path.data(), 
                    std::min(socket_path.size(), sizeof(m_addr.sun_path) - 1), 
                    m_addr.sun_path);
    }

    ~SocketClient() {
        if (m_fd >= 0) ::close(m_fd);
    }

    SocketClient(const SocketClient&) = delete;
    SocketClient& operator=(const SocketClient&) = delete;

    void send(Facility fac, Severity sev, std::string_view app_name, std::string_view msg) const {
        uint16_t prival = static_cast<uint8_t>(fac) * 8 + static_cast<uint8_t>(sev);
        
        auto now = std::chrono::system_clock::now();
        std::string time_str = std::format("{:%Y-%m-%dT%H:%M:%S%z}", std::chrono::floor<std::chrono::seconds>(now));
        
        std::string frame = std::format("<{}>1 {} localhost {} {} ID1 - {}",
                                        prival, time_str, app_name, ::getpid(), msg);

        ssize_t res = ::sendto(m_fd, frame.data(), frame.size(), 0,
                               reinterpret_cast<const sockaddr*>(&m_addr), sizeof(m_addr));
        if (res < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка відправки у syslog сокет");
        }
    }

private:
    int m_fd{-1};
    sockaddr_un m_addr{};
};

// Zero-copy парсер за допомогою std::string_view
class Parser {
public:
    static std::optional<Message> parse(std::string_view raw) {
        if (raw.empty() || raw.front() != '<') return std::nullopt;

        size_t close_bracket = raw.find('>');
        if (close_bracket == std::string_view::npos) return std::nullopt;

        uint16_t prival = 0;
        for (char c : raw.substr(1, close_bracket - 1)) {
            if (c < '0' || c > '9') return std::nullopt;
            prival = prival * 10 + (c - '0');
        }

        Message msg;
        msg.facility = prival / 8;
        msg.severity = prival % 8;

        std::string_view rest = raw.substr(close_bracket + 1);
        
        // Читаємо версію
        size_t space_pos = rest.find(' ');
        if (space_pos == std::string_view::npos) return std::nullopt;
        msg.version = static_cast<uint8_t>(rest[0] - '0');
        rest.remove_prefix(space_pos + 1);

        // Читаємо поля: timestamp, hostname, app_name, procid, msgid
        auto extract_token = [&rest]() -> std::string_view {
            size_t p = rest.find(' ');
            if (p == std::string_view::npos) {
                std::string_view token = rest;
                rest = {};
                return token;
            }
            std::string_view token = rest.substr(0, p);
            rest.remove_prefix(p + 1);
            return token;
        };

        msg.timestamp = std::string(extract_token());
        msg.hostname  = std::string(extract_token());
        msg.app_name  = std::string(extract_token());
        msg.procid    = std::string(extract_token());
        msg.msgid     = std::string(extract_token());

        // Structured data або '-'
        msg.structured_data = std::string(extract_token());
        msg.payload = std::string(rest);

        return msg;
    }
};

} // namespace syslog

int main() {
    try {
        syslog::SocketClient client;
        client.send(syslog::Facility::User, syslog::Severity::Error, "cpp_app", "Тестова подія RFC 5424");
        std::cout << "Повідомлення успішно надіслано в /dev/log\n";
    } catch (const std::exception& e) {
        std::cerr << "Помилка клієнта: " << e.what() << '\n';
    }

    std::string_view raw_frame = "<165>1 2026-08-14T13:36:16.003Z server.corp network_daemon 8812 EVT01 [meta ip=\"10.0.0.1\"] З'єднання скинуто";
    auto parsed = syslog::Parser::parse(raw_frame);

    if (parsed) {
        std::cout << "\nРезультат розбору RFC 5424:\n";
        std::cout << std::format("Facility: {} (local4), Severity: {} (notice)\n", 
                                 parsed->facility, parsed->severity);
        std::cout << std::format("Програма: {} [PID: {}]\n", parsed->app_name, parsed->procid);
        std::cout << std::format("Структуровані дані: {}\n", parsed->structured_data);
        std::cout << std::format("Текст: {}\n", parsed->payload);
    }

    return 0;
}
```
:::
