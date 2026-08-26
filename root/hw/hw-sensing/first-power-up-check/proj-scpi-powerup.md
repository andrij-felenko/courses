# ⚙️ Автоматизований перший запуск через SCPI: плавний підйом напруги та моніторинг струму

Ручне ввімкнення нової плати регулятором блока живлення вимагає безперервної уваги інженера: потрібно одночасно тримати руку на вимикачі, дивитися на дисплей струму й слідкувати за реакцією схеми. Якщо на платі є частковий напівпровідниковий пробій або паразитна ємність, струм може наростати нелінійно при досягненні порогової напруги відкриття внутрішніх p-n переходів. Автоматизація цього процесу за протоколом SCPI (*Standard Commands for Programmable Instruments*) дозволяє реалізувати кероване ступінчасте підняття напруги (Ramp-up), миттєве програмне та апаратне вимкнення виходу при перевищенні ліміту струму спокою та реєстрацію вольт-амперної характеристики холодного старту для протоколу верифікації.

### Фізичні передумови та протокол SCPI

Протокол SCPI є текстовим стандартом синтаксису команд, побудованим поверх базового стандарту IEEE 488.2. Він стандартизує взаємодію з вимірювальними приладами через інтерфейси USB (клас USBTMC — *USB Test & Measurement Class*), RS-232/UART, GPIB (IEEE 488) та локальну мережу Ethernet за специфікацією LXI (*LAN eXtensions for Instrumentation*, стандартний TCP-порт 5025).

У контексті безпечного запуску плати (DUT, *Device Under Test*) взаємодія з блоком живлення будується навколо двох контурів регулювання:
1. **Апаратний контур стабілізації струму (CC Loop):** аналогова схема зворотного зв'язку самого блока живлення, яка вимірює струм через внутрішній шунт і при досягненні заданого порогу `CURR` переводить силовий регулятор у режим джерела сталого струму за частки мікросекунди (1–10 мкс).
2. **Програмний контур телеметрії та захисту (SCPI Loop):** програма керування на ПК або випробувальному стенді, яка періодично надсилає команди запиту вимірювань `MEAS:VOLT?` та `MEAS:CURR?`, аналізує відповіді та приймає рішення про продовження підйому напруги або аварійне знеструмлення `OUTP OFF`.

Важливо враховувати фундаментальне обмеження вихідного каскаду блока живлення: на його вихідних клемах завжди встановлено паразитний вихідний блокувальний конденсатор `C_out` (зазвичай від 10 до 470 мкФ залежно від схемотехніки БЖ). Якщо на клемах виставлено 5 В, цей конденсатор накопичує енергію:

```
E_cap = 0.5 · C_out · V²
= 0.5 · 100·10⁻⁶ F · (5.0 V)²
= 1.25 mJ                      [енергія, запасена у вихідній ємності БЖ]
```

При раптовому замиканні на платі ця енергія миттєво розряджається в точку дефекту ДО того, як внутрішній аналоговий контур CC встигне знизити напругу. Ступінчастий підйом напруги малими кроками (по 0.1–0.2 В) мінімізує енергію, накопичену у вихідному фільтрі БЖ на кожному етапі, запобігаючи випалюванню мікродоріжок.

### Завдання та покрокова логіка утиліти

Програма реалізує випробувальний цикл початкового оживлення друкованої плати:

1. **Ініціалізація та ідентифікація:** відкриває TCP-сокет до IP-адреси блока живлення, зчитує рядок ідентифікації `*IDN?` (перевірка зв'язку), скидає прилад у вихідний стан `*RST` і гарантовано вимикає вихід `OUTP OFF`.
2. **Конфігурація апаратного захисту:** встановлює апаратний струмовий ліміт захисту `CURR 0.050` (50 мА) та початкову напругу `VOLT 0.0`.
3. **Активація виходу:** подає команду `OUTP ON`, після чого навантаження отримує нульовий потенціал.
4. **Ступінчасте наростання напруги:** у циклі збільшує напругу від 0.2 В до номінальних 3.3 В із кроком 0.2 В та затримкою 100 мс після кожного кроку для завершення перехідних процесів заряду ємностей.
5. **Телеметрія струму в реальному часі:** після кожної зміни напруги запитує виміряний струм командою `MEAS:CURR?`.
6. **Контроль порогу спокою холостого ходу:** якщо струм перевищує очікуваний поріг спокою (наприклад, 35 мА для мікроконтролера в стані скидання), утиліта негайно посилає команду `OUTP OFF`, розраховує еквівалентний опір дефектного кола `R = V / I` та перериває тест із виведенням звіту про аварію.
7. **Фіксація усталеного стану:** при досягненні цільових 3.3 В утиліта витримує паузу 1 секунду та фіксує фінальний струм холостого ходу, записуючи статус успішного запуску.

### Реалізація: мови C та ідіоматичний C++

Нижче наведено кросплатформенний вихідний код утиліти керування. Варіант на C демонструє роботу із сокетами POSIX/Winsock та пряме формування текстових SCPI-буферів. Варіант на C++ використовує парадигму RAII для гарантованого автоматичного знеструмлення плати у деструкторі при будь-яких винятках, сучасний тип `std::expected` для обробки помилок парсингу та засоби форматування `std::format`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#if defined(_WIN32)
  #include <winsock2.h>
  #include <ws2tcpip.h>
  #pragma comment(lib, "ws2_32.lib")
  typedef SOCKET socket_t;
  #define CLOSE_SOCKET closesocket
  #define SLEEP_MS(ms) Sleep(ms)
#else
  #include <unistd.h>
  #include <sys/types.h>
  #include <sys/socket.h>
  #include <netinet/in.h>
  #include <arpa/inet.h>
  typedef int socket_t;
  #define INVALID_SOCKET (-1)
  #define SOCKET_ERROR (-1)
  #define CLOSE_SOCKET close
  #define SLEEP_MS(ms) usleep((ms) * 1000)
#endif

typedef struct {
    socket_t sock;
    char ip[64];
    int port;
} ScpiClient;

bool scpi_connect(ScpiClient *client, const char *ip, int port) {
    strncpy(client->ip, ip, sizeof(client->ip) - 1);
    client->port = port;

#if defined(_WIN32)
    WSADATA wsa_data;
    if (WSAStartup(MAKEWORD(2, 2), &wsa_data) != 0) {
        fprintf(stderr, "Помилка ініціалізації Winsock WSAStartup\n");
        return false;
    }
#endif

    client->sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (client->sock == INVALID_SOCKET) {
        fprintf(stderr, "Не вдалося створити мережевий TCP сокет\n");
        return false;
    }

    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons((unsigned short)port);
    inet_pton(AF_INET, ip, &server_addr.sin_addr);

    if (connect(client->sock, (struct sockaddr *)&server_addr, sizeof(server_addr)) == SOCKET_ERROR) {
        fprintf(stderr, "Помилка з'єднання з блоком живлення за адресою %s:%d\n", ip, port);
        CLOSE_SOCKET(client->sock);
        client->sock = INVALID_SOCKET;
        return false;
    }

    return true;
}

void scpi_disconnect(ScpiClient *client) {
    if (client->sock != INVALID_SOCKET) {
        // Обов'язкове захисне вимкнення силового виходу перед розривом сесії
        send(client->sock, "OUTP OFF\n", 9, 0);
        CLOSE_SOCKET(client->sock);
        client->sock = INVALID_SOCKET;
    }
#if defined(_WIN32)
    WSACleanup();
#endif
}

bool scpi_send(ScpiClient *client, const char *cmd) {
    if (client->sock == INVALID_SOCKET) return false;
    int len = (int)strlen(cmd);
    int sent = send(client->sock, cmd, len, 0);
    return sent == len;
}

bool scpi_query(ScpiClient *client, const char *cmd, char *buf, size_t buf_size) {
    if (!scpi_send(client, cmd)) return false;
    int received = recv(client->sock, buf, (int)(buf_size - 1), 0);
    if (received <= 0) return false;
    buf[received] = '\0';
    // Видаляємо кінцеві символи нового рядка
    char *nl = strchr(buf, '\n');
    if (nl) *nl = '\0';
    char *cr = strchr(buf, '\r');
    if (cr) *cr = '\0';
    return true;
}

double scpi_measure_current(ScpiClient *client) {
    char response[64];
    if (scpi_query(client, "MEAS:CURR?\n", response, sizeof(response))) {
        return atof(response);
    }
    return -1.0;
}

bool run_safe_bringup(ScpiClient *client, double target_voltage, double current_limit, double max_safe_quiescent) {
    char cmd[128];
    char idn[128];

    // Ідентифікація приладу
    if (scpi_query(client, "*IDN?\n", idn, sizeof(idn))) {
        printf("Підключено до вимірювального приладу: %s\n", idn);
    }

    // Скидання приладу та попереднє налаштування обмеження струму
    scpi_send(client, "*RST\n");
    SLEEP_MS(200);

    snprintf(cmd, sizeof(cmd), "CURR %.4f\n", current_limit);
    scpi_send(client, cmd);
    scpi_send(client, "VOLT 0.0\n");
    scpi_send(client, "OUTP ON\n");
    SLEEP_MS(100);

    printf("Початок плавного наростання напруги (Апаратний ліміт: %.1f мА, Ціль: %.2f В)...\n",
           current_limit * 1000.0, target_voltage);

    double v_step = 0.20;
    for (double v = 0.20; v <= target_voltage + 0.001; v += v_step) {
        snprintf(cmd, sizeof(cmd), "VOLT %.3f\n", v);
        scpi_send(client, cmd);
        SLEEP_MS(100);

        double i_meas = scpi_measure_current(client);
        if (i_meas < 0.0) {
            fprintf(stderr, "Помилка зчитування струму з шини SCPI!\n");
            scpi_send(client, "OUTP OFF\n");
            return false;
        }

        printf("  Напруга: %5.2f В | Виміряний струм: %6.2f мА\n", v, i_meas * 1000.0);

        // Перевірка перевищення струму спокою холостого ходу
        if (i_meas > max_safe_quiescent) {
            fprintf(stderr, "\n[УВАГА] Перевищення безпечного струму спокою! Зафіксовано %.2f мА при %.2f В\n",
                    i_meas * 1000.0, v);
            fprintf(stderr, "[АВАРІЯ] Негайне знеструмлення виходу (OUTP OFF).\n");
            scpi_send(client, "OUTP OFF\n");
            double r_equiv = v / i_meas;
            fprintf(stderr, "Розрахунковий еквівалентний опір дефекту: %.2f Ом\n", r_equiv);
            return false;
        }
    }

    printf("\nУспішний вихід на номінальний рівень напруги %.2f В.\n", target_voltage);
    SLEEP_MS(1000);
    double final_i = scpi_measure_current(client);
    printf("Усталений струм холостого ходу плати: %.2f мА (У межах норми)\n", final_i * 1000.0);
    return true;
}

int main(int argc, char *argv[]) {
    const char *psu_ip = (argc > 1) ? argv[1] : "192.168.1.105";
    int psu_port = 5025;

    ScpiClient client;
    if (!scpi_connect(&client, psu_ip, psu_port)) {
        return 1;
    }

    // Запуск: цільова напруга 3.3 В, апаратний захист 50 мА, програмний поріг спокою 35 мА
    bool ok = run_safe_bringup(&client, 3.30, 0.050, 0.035);

    if (!ok) {
        printf("Випробування зупинено через аварійний стан. Плата знеструмлена.\n");
    } else {
        printf("Плата успішно заживлена і готова до перевірки сигналів та підключення налагоджувача.\n");
    }

    scpi_disconnect(&client);
    return ok ? 0 : 1;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <chrono>
#include <thread>
#include <format>
#include <expected>
#include <stdexcept>
#include <span>
#include <charconv>

#if defined(_WIN32)
  #include <winsock2.h>
  #include <ws2tcpip.h>
  #pragma comment(lib, "ws2_32.lib")
  using socket_handle_t = SOCKET;
  constexpr socket_handle_t invalid_socket = INVALID_SOCKET;
  inline int close_socket(socket_handle_t s) { return closesocket(s); }
#else
  #include <unistd.h>
  #include <sys/socket.h>
  #include <netinet/in.h>
  #include <arpa/inet.h>
  using socket_handle_t = int;
  constexpr socket_handle_t invalid_socket = -1;
  inline int close_socket(socket_handle_t s) { return close(s); }
#endif

// RAII обгортка мережевої сесії керування SCPI
class ScpiSession {
public:
    ScpiSession(std::string_view ip, uint16_t port) {
#if defined(_WIN32)
        WSADATA wsa_data;
        if (WSAStartup(MAKEWORD(2, 2), &wsa_data) != 0) {
            throw std::runtime_error("Не вдалося ініціалізувати підсистему WSAStartup");
        }
        wsa_initialized_ = true;
#endif
        sock_ = ::socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
        if (sock_ == invalid_socket) {
            cleanup();
            throw std::runtime_error("Помилка створення сокета TCP");
        }

        sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_port = htons(port);
        std::string ip_str(ip);
        inet_pton(AF_INET, ip_str.c_str(), &addr.sin_addr);

        if (::connect(sock_, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) < 0) {
            cleanup();
            throw std::runtime_error(std::format("Не вдалося підключитися до приладу {}:{}", ip, port));
        }
    }

    ~ScpiSession() noexcept {
        try {
            // Безпечне вимкнення силового каналу в деструкторі за будь-яких умов
            send("OUTP OFF\n");
        } catch (...) {}
        cleanup();
    }

    ScpiSession(const ScpiSession&) = delete;
    ScpiSession& operator=(const ScpiSession&) = delete;
    ScpiSession(ScpiSession&& other) noexcept : sock_(other.sock_) {
        other.sock_ = invalid_socket;
    }

    void send(std::string_view cmd) {
        if (sock_ == invalid_socket) {
            throw std::runtime_error("Спроба запису в закритий сокет");
        }
        size_t total = 0;
        while (total < cmd.size()) {
            auto sent = ::send(sock_, cmd.data() + total, static_cast<int>(cmd.size() - total), 0);
            if (sent <= 0) {
                throw std::runtime_error("Помилка передачі команди SCPI через сокет");
            }
            total += static_cast<size_t>(sent);
        }
    }

    std::string query(std::string_view cmd) {
        send(cmd);
        std::vector<char> buffer(256);
        auto received = ::recv(sock_, buffer.data(), static_cast<int>(buffer.size() - 1), 0);
        if (received <= 0) {
            throw std::runtime_error("Помилка отримання відповіді або таймаут зв'язку SCPI");
        }
        buffer[received] = '\0';
        std::string res(buffer.data());
        while (!res.empty() && (res.back() == '\r' || res.back() == '\n')) {
            res.pop_back();
        }
        return res;
    }

    std::expected<double, std::string> measure_current() {
        try {
            auto res = query("MEAS:CURR?\n");
            double val = 0.0;
            auto [ptr, ec] = std::from_chars(res.data(), res.data() + res.size(), val);
            if (ec == std::errc()) {
                return val;
            }
            return std::unexpected("Не вдалося розпарсити числове значення струму: " + res);
        } catch (const std::exception& e) {
            return std::unexpected(e.what());
        }
    }

private:
    void cleanup() noexcept {
        if (sock_ != invalid_socket) {
            close_socket(sock_);
            sock_ = invalid_socket;
        }
#if defined(_WIN32)
        if (wsa_initialized_) {
            WSACleanup();
            wsa_initialized_ = false;
        }
#endif
    }

    socket_handle_t sock_{invalid_socket};
#if defined(_WIN32)
    bool wsa_initialized_{false};
#endif
};

struct BringupConfig {
    double target_voltage_v = 3.30;
    double current_limit_a = 0.050;       // Апаратний ліміт 50 мА
    double max_safe_quiescent_a = 0.035;  // Поріг тривоги струму спокою 35 мА
    double step_voltage_v = 0.20;
    std::chrono::milliseconds step_delay{100};
};

bool execute_bringup(ScpiSession& psu, const BringupConfig& cfg) {
    std::cout << std::format("Ідентифікатор обладнання: {}\n", psu.query("*IDN?\n"));

    psu.send("*RST\n");
    std::this_thread::sleep_for(std::chrono::milliseconds(200));

    // Фіксуємо апаратний ліміт струму в блоці живлення
    psu.send(std::format("CURR {:.4f}\n", cfg.current_limit_a));
    psu.send("VOLT 0.0\n");
    psu.send("OUTP ON\n");
    std::this_thread::sleep_for(std::chrono::milliseconds(100));

    std::cout << std::format("Початок керованого підйому напруги до {:.2f} В (Ліміт: {:.1f} мА)...\n",
                             cfg.target_voltage_v, cfg.current_limit_a * 1000.0);

    for (double v = cfg.step_voltage_v; v <= cfg.target_voltage_v + 0.001; v += cfg.step_voltage_v) {
        psu.send(std::format("VOLT {:.3f}\n", v));
        std::this_thread::sleep_for(cfg.step_delay);

        auto i_meas = psu.measure_current();
        if (!i_meas) {
            std::cerr << "Помилка зчитування струму: " << i_meas.error() << "\n";
            psu.send("OUTP OFF\n");
            return false;
        }

        double current = *i_meas;
        std::cout << std::format("  Напруга: {:5.2f} В | Струм споживання: {:6.2f} мА\n",
                                 v, current * 1000.0);

        if (current > cfg.max_safe_quiescent_a) {
            std::cerr << std::format("\n[АВАРІЯ] Струм холостого ходу ({:.2f} мА) перевищив норму ({:.2f} мА) при {:.2f} В!\n",
                                     current * 1000.0, cfg.max_safe_quiescent_a * 1000.0, v);
            psu.send("OUTP OFF\n");
            double r_equiv = v / current;
            std::cerr << std::format("Розрахунковий опір витоку кола: {:.2f} Ом\n", r_equiv);
            return false;
        }
    }

    std::this_thread::sleep_for(std::chrono::seconds(1));
    auto final_i = psu.measure_current().value_or(0.0);
    std::cout << std::format("\nСтабільний режим підтверджено. Фінальний струм спокою: {:.2f} мА\n",
                             final_i * 1000.0);
    return true;
}

int main(int argc, char* argv[]) {
    const std::string ip = (argc > 1) ? argv[1] : "192.168.1.105";
    constexpr uint16_t port = 5025;

    try {
        ScpiSession psu(ip, port);
        BringupConfig cfg{
            .target_voltage_v = 3.30,
            .current_limit_a = 0.050,
            .max_safe_quiescent_a = 0.035,
            .step_voltage_v = 0.20,
            .step_delay = std::chrono::milliseconds(100)
        };

        if (!execute_bringup(psu, cfg)) {
            std::cout << "Запуск зупинено через критичне відхилення струму. Перевірте монтаж.\n";
            return 1;
        }
        std::cout << "Перший запуск плати успішно завершено. Живлення залишається увімкненим.\n";
    } catch (const std::exception& ex) {
        std::cerr << "Критична системна помилка: " << ex.what() << "\n";
        return 1;
    }
    return 0;
}
```
:::

### Інженерні пастки та крайові випадки

1. **Затримка програмного опитування проти швидкодії апаратного захисту:** передача текстової команди запиту по TCP/IP, її інтерпретація мікропроцесором блока живлення, аналого-цифрове перетворення та зворотна відправка пакету займають від 10 до 80 мс. Програмний моніторинг призначений для виявлення повільних аномалій (підвищений струм спокою ненавантаженої плати, нелінійне відкриття напівпровідникових переходів), але не може замінити апаратне обмеження струму `CURR`. Якщо на платі виникне пряме металеве коротке замикання, єдиним захисником від випалювання доріжок є саме перехід вихідного каскаду блока живлення в аналоговий режим стабілізації струму (CC), що відбувається за мікросекунди.
2. **Пусковий заряд вихідних ємностей (Inrush Current):** якщо на платі встановлено великі електролітичні або танталові конденсатори ємністю 100–470 мкФ, миттєве перемикання напруги з нуля до 3.3 В викличе піковий пусковий струм `I = C · (dV/dt) > 1 А`. Це змусить блок живлення на кілька мілісекунд перейти в режим CC і просадити напругу. Ступінчастий підйом із кроком 0.2 В зменшує величину `dV/dt` у кожній точці, усуваючи помилкові спрацьовування захисту.
3. **Падіння напруги на вимірювальних проводах (Remote Sense):** при струмах понад кількасот міліампер на тонких з'єднувальних проводах виникає відчутне падіння напруги (0.1–0.3 В). Для точних випробувань активують режим чотирипровідного підключення (*4-Wire Remote Sense*) командою `VOLT:SENS EXT`, підключаючи виносні сенсорні щупи безпосередньо до контрольних точок плати.
4. **Паразитні контури заземлення через інтерфейс керування:** якщо блок живлення з'єднаний із ПК неекранованим USB-кабелем або звичайним кабелем Ethernet, сигнальна земля приладу може утворити паразитний контур із захисним заземленням мережі (*Protective Earth, PE*). Струми вирівнювання потенціалів спотворюють показання вбудованого амперметра блока на одиниці міліампер. Для прецизійних вимірювань застосовують опторозв'язані USB-ізолятори або живлять випробувальний ноутбук від власного акумулятора.
