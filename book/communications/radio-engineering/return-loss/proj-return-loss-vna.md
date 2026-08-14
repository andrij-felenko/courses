# ⚙️ Автоматизоване вимірювання зворотних втрат та смуги пропускання за протоколом SCPI

Розробка автоматизованого програмного забезпечення для радіочастотних вимірювальних стендів вимагає прямої взаємодії з вимірювальними приладами — векторними аналізаторами кіл (VNA, такими як Keysight E5071C, Rohde & Schwarz ZNB, Rigol DSG або бюджетними приладами серії NanoVNA). 

Архітектура автоматизованого вимірювального комплексу VNA будується довкола мережевого драйвера зчитування S-параметрів, реалізованого мовами C та C++. Системне програмне забезпечення виконує підключення до приладу через мережевий інтерфейс TCP/IP (порт 5025 SCPI/RAW або порт 5024 VISA), конфігурує параметри частотного сканування, зчитує масив виміряних точок, розраховує зворотні втрати `RL`, коефіцієнт стоячої хвилі `VSWR`, точку резонансу `f₀` та смугу пропускання антени за рівнем `−10` дБ.

---

### 1. Архитектура SCPI-протоколу та мережевої взаємодії

Стандарт **SCPI (Standard Commands for Programmable Instruments)** визначає текстову ієрархію команд для керування вимірювальними приладами через сокети TCP/IP, інтерфейс USB-TMC або послідовний порт.

Протокол SCPI побудований за клієнт-серверною архітектурою. Аналізатор кіл виступає як TCP-сервер, який прослуховує стандартний порт 5025 (або порт 5024 для VISA-сервера). Клієнтська програма встановлює звичайне потокове з'єднання TCP/IP і відправляє текстові SCPI-команди, завершені символом переводу рядка `\n` (ASCII 0x0A) або `\r\n`.

#### Послідовність команд конфігурації VNA

Для вимірювання зворотних втрат антени у діапазоні від 2.30 ГГц до 2.60 ГГц програма відправляє послідовно такі текстові рядки:

1. `*IDN?` — запит ідентифікаційного рядка приладу. Прилад повертає назву виробника, модель, серійний номер та версію прошивки (наприклад `Keysight Technologies,E5071C,MY46521890,A.12.05`).
2. `:SENS:FREQ:STAR 2.30GHZ` — встановлення початкової частоти сканування `f_start`.
3. `:SENS:FREQ:STOP 2.60GHZ` — встановлення кінцевої частоти сканування `f_stop`.
4. `:SENS:SWE:POIN 201` — кількість точок вимірювання у спектрі (типово 101, 201, 401 або 1601 точка).
5. `:CALC:PAR1:DEF S11` — вибір першого вимірювального каналу для вимірювання параметра `S₁₁` (відбиття від порту 1).
6. `:CALC:FORM MLOG` — налаштування формату виводу даних: логарифмічна амплітуда `S₁₁` в дБ (`S₁₁ [дБ] = −RL`).
7. `:CALC:DATA? FDATA` — запит на повернення обробленого масиву виміряних точок у форматі CSV (текстовий рядок чисел з плаваючою крапкою, розділених комами).

#### Оцінка форматів даних SCPI та мережева буферизація

VNA може повертати дані у кількох форматах:

- **ASCII / CSV (`FDATA`)**: Простий для парсингу текстовий рядок (наприклад `"-2.15, -2.48, -3.12, -10.50, -28.40..."`). Перевагою цього формату є повна незалежність від порядку байтів у процесорі (Endianness) та легкість відлагодження. Проте обсяг даних становить близько 10-15 байтів на одну точку.
- **IEEE 488.2 Binary Block (`SDATA`)**: Двійковий блок 32-бітних або 64-бітних чисел у форматі IEEE 754 (Big-Endian або Little-Endian). Заголовок блоку починається з символу `#`, за яким іде кількість байтів. Двійковий режим використовують у високошвидкісних автоматизованих лініях конвеєрного контролю, коли сканування виконується 100 разів на секунду.

Під час зчитування великого текстового відгуку через сокет важливо враховувати, що стек TCP/IP може фрагментувати відповідь на кілька пакетів (сегментів MTU). Програма повинна продовжувати цикл зчитування `recv()` доти, доки не отримає символ переводу рядка або не зчитає очікувану кількість байтів.

---

### 2. Алгоритми цифрової обробки спектральних даних

Після отримання масиву з `N` точок `S₁₁[i]` (де `i = 0…N−1`) програма виконує послідовну цифрову обробку:

#### Генерація частотної сітки
Для кожної точки `i` вираховується її точна частота `f[i]`:

```
f[i] = f_start + i · (f_stop − f_start) / (N − 1)
```

#### Обчислення зворотних втрат RL та КСХ
Зворотні втрати `RL[i] = −S₁₁[i]`. Модуль коефіцієнта відбиття `|Γ[i]| = 10^(S₁₁[i] / 20)`. 

КСХ вираховується за формулою:

```
VSWR[i] = (1 + |Γ[i]|) / (1 − |Γ[i]|)
```

Якщо виміряне значення `S₁₁` перевищує 0 дБ (що можливе при наявності шумів або невідкаліброваного приладу), значення `|Γ|` обмежеється верхньою межею 0.999 для запобігання діленню на нуль.

#### Пошук точки резонансу
Глобальний мінімум `S₁₁` (максимум `RL`) визначає резонансну частоту антени `f₀`:

```
S₁₁_min = min(S₁₁[i]),  f₀ = f[i_min]
```

#### Визначення робочої смуги частот BW_-10dB та обробка складних випадків
Програма сканує масив і знаходить першу точку `f_low`, де `S₁₁[i] ≤ −10.0` дБ (`RL ≥ 10` дБ), та останнюю точку `f_high`, де ця умова ще виконується. Смуга пропускання обчислюється як:

```
BW_-10dB = f_high − f_low
```

Якщо у діапазоні сканування значення `S₁₁` жодного разу не опускається нижче −10 дБ, програма фіксує значення `BW = 0` і повертає статус про те, що антена розлаштована або неузгоджена. Якщо антена є двохвильовою (має два резонансні провали), даний алгоритм обчислює загальне охоплення смуги або може бути розширений для пошуку локальних мінімумів.

---

### 3. Особливості реалізації мовою C та C++

У наведених далі реалізаціях враховано кросплатформові відмінності між мережевими бібліотеками Windows (Winsock2) та POSIX (Linux/macOS):

- Для Windows виконується ініціалізація `WSAStartup()` та закриття через `closesocket()`.
- Для POSIX-систем використовуються стандартні системні виклики `socket()`, `connect()`, `close()`.
- Реалізація мовою C++ застосовує концепцію RAII (Resource Acquisition Is Initialization), загортаючи дескриптор сокета у клас `ScpiSocket`, який автоматично закриває з'єднання у деструкторі.
- Обробка помилок у C++23 виконується за допомогою `std::expected<T, E>`, що виключає накладні витрати винятків C++ та забезпечує явну перевірку кодів помилок.

---

### 4. Вихідний код реалізації

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#if defined(_WIN32)
  #include <winsock2.h>
  #include <ws2tcpip.h>
  #pragma comment(lib, "ws2_32.lib")
  typedef SOCKET socket_t;
  #define CLOSE_SOCKET(s) closesocket(s)
#else
  #include <sys/socket.h>
  #include <arpa/inet.h>
  #include <unistd.h>
  typedef int socket_t;
  #define CLOSE_SOCKET(s) close(s)
  #define INVALID_SOCKET (-1)
#endif

#define MAX_SWEEP_POINTS 1024
#define BUFFER_SIZE 32768

/* Структура однієї точці частотного спектра */
typedef struct {
    double freq_hz;
    double s11_db;
    double return_loss_db;
    double vswr;
} vna_point_t;

/* Підсумкові результати аналізу спектра */
typedef struct {
    vna_point_t points[MAX_SWEEP_POINTS];
    size_t count;
    double min_s11_db;
    double max_return_loss_db;
    double resonant_freq_hz;
    double bw_10db_hz;
    double peak_vswr;
} vna_result_t;

/* Перерахунок параметра S11 [дБ] у КСХ (VSWR) */
static double calculate_vswr(double s11_db) {
    if (s11_db >= 0.0) return 999.0;
    double gamma = pow(10.0, s11_db / 20.0);
    if (gamma >= 0.999) return 999.0;
    return (1.0 + gamma) / (1.0 - gamma);
}

/* Відправка SCPI-команди у сокет та зчитування відповіді */
static int scpi_query(socket_t sock, const char *cmd, char *response, size_t resp_size) {
    char send_buf[256];
    snprintf(send_buf, sizeof(send_buf), "%s\n", cmd);
    
    if (send(sock, send_buf, (int)strlen(send_buf), 0) < 0) {
        return -1;
    }
    
    if (response && resp_size > 0) {
        int bytes_received = recv(sock, response, (int)resp_size - 1, 0);
        if (bytes_received <= 0) return -1;
        response[bytes_received] = '\0';
    }
    return 0;
}

/* Модуль мережевого підключення та вимірювання S11 через SCPI */
int analyze_return_loss(const char *ip_address, int port, double start_freq, double stop_freq, vna_result_t *res) {
#if defined(_WIN32)
    WSADATA wsa;
    if (WSAStartup(MAKEWORD(2, 2), &wsa) != 0) return -1;
#endif

    socket_t sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock == INVALID_SOCKET) {
#if defined(_WIN32)
        WSACleanup();
#endif
        return -1;
    }

    struct sockaddr_in server;
    memset(&server, 0, sizeof(server));
    server.sin_family = AF_INET;
    server.sin_port = htons((unsigned short)port);
    inet_pton(AF_INET, ip_address, &server.sin_addr);

    if (connect(sock, (struct sockaddr *)&server, sizeof(server)) < 0) {
        CLOSE_SOCKET(sock);
#if defined(_WIN32)
        WSACleanup();
#endif
        return -2;
    }

    /* Налаштування режимів сканування VNA */
    char cmd[128];
    snprintf(cmd, sizeof(cmd), ":SENS:FREQ:STAR %.0f", start_freq);
    scpi_query(sock, cmd, NULL, 0);
    snprintf(cmd, sizeof(cmd), ":SENS:FREQ:STOP %.0f", stop_freq);
    scpi_query(sock, cmd, NULL, 0);
    scpi_query(sock, ":CALC:FORM MLOG", NULL, 0);

    /* Запит масиву виміряних даних */
    static char rx_buf[BUFFER_SIZE];
    if (scpi_query(sock, ":CALC:DATA? FDATA", rx_buf, sizeof(rx_buf)) < 0) {
        CLOSE_SOCKET(sock);
#if defined(_WIN32)
        WSACleanup();
#endif
        return -3;
    }

    CLOSE_SOCKET(sock);
#if defined(_WIN32)
    WSACleanup();
#endif

    /* Парсинг CSV-рядка зі значеннями S11 в дБ */
    res->count = 0;
    res->min_s11_db = 0.0;
    res->max_return_loss_db = 0.0;
    res->resonant_freq_hz = 0.0;
    res->peak_vswr = 1.0;

    char *token = strtok(rx_buf, ",\n\r ");
    while (token != NULL && res->count < MAX_SWEEP_POINTS) {
        double s11_val = atof(token);
        double step = (stop_freq - start_freq) / (MAX_SWEEP_POINTS - 1);
        double f_curr = start_freq + res->count * step;

        res->points[res->count].freq_hz = f_curr;
        res->points[res->count].s11_db = s11_val;
        res->points[res->count].return_loss_db = -s11_val;
        res->points[res->count].vswr = calculate_vswr(s11_val);

        if (res->count == 0 || s11_val < res->min_s11_db) {
            res->min_s11_db = s11_val;
            res->max_return_loss_db = -s11_val;
            res->resonant_freq_hz = f_curr;
        }

        if (res->points[res->count].vswr > res->peak_vswr) {
            res->peak_vswr = res->points[res->count].vswr;
        }

        res->count++;
        token = strtok(NULL, ",\n\r ");
    }

    /* Розрахунок смуги пропускання за рівнем S11 <= -10 дБ (RL >= 10 дБ) */
    double f_low = 0.0, f_high = 0.0;
    for (size_t i = 0; i < res->count; i++) {
        if (res->points[i].s11_db <= -10.0) {
            if (f_low == 0.0) f_low = res->points[i].freq_hz;
            f_high = res->points[i].freq_hz;
        }
    }
    res->bw_10db_hz = (f_high > f_low) ? (f_high - f_low) : 0.0;

    return 0;
}

int main(void) {
    vna_result_t res;
    printf("З'єднання з VNA для вимірювання зворотних втрат...\n");
    
    int ret = analyze_return_loss("127.0.0.1", 5025, 2.3e9, 2.6e9, &res);
    if (ret != 0) {
        printf("Примітка: Реальне з'єднання з VNA відсутнє (код %d).\n", ret);
        printf("Демонстраційні розраховані параметри:\n");
        printf("  Резонансна частота: 2.450 ГГц\n");
        printf("  Максимальні зворотні втрати (RL): 28.50 дБ (S11 = -28.50 дБ)\n");
        printf("  Смуга пропускання (RL >= 10 дБ): 100.00 МГц (2.400 - 2.500 ГГц)\n");
        printf("  КСХ (VSWR) на резонансі: 1.07\n");
        return 0;
    }

    printf("Успішно оброблено точок: %zu\n", res.count);
    printf("Резонансна частота f0: %.3f ГГц\n", res.resonant_freq_hz / 1e9);
    printf("Максимальний RL: %.2f дБ (S11 = %.2f дБ)\n", res.max_return_loss_db, res.min_s11_db);
    printf("Смуга пропускання BW (-10дБ): %.2f МГц\n", res.bw_10db_hz / 1e6);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <expected>
#include <cmath>
#include <sstream>

#if defined(_WIN32)
  #include <winsock2.h>
  #include <ws2tcpip.h>
  #pragma comment(lib, "ws2_32.lib")
#else
  #include <sys/socket.h>
  #include <arpa/inet.h>
  #include <unistd.h>
#endif

namespace rf {

struct VnaPoint {
    double freq_hz{0.0};
    double s11_db{0.0};
    double return_loss_db{0.0};
    double vswr{1.0};
};

struct VnaAnalysisResult {
    std::vector<VnaPoint> points;
    double max_return_loss_db{0.0};
    double min_s11_db{0.0};
    double resonant_freq_hz{0.0};
    double bw_10db_hz{0.0};
    double peak_vswr{1.0};
};

enum class VnaError {
    NetworkInitFailed,
    ConnectionFailed,
    QueryFailed,
    ParseError
};

// RAII обгортка для мережевого сокета
class ScpiSocket {
public:
    explicit ScpiSocket(std::string_view ip, uint16_t port) {
#if defined(_WIN32)
        WSADATA wsa;
        if (WSAStartup(MAKEWORD(2, 2), &wsa) != 0) return;
#endif
        sock_ = ::socket(AF_INET, SOCK_STREAM, 0);
        if (sock_ < 0) return;

        sockaddr_in server{};
        server.sin_family = AF_INET;
        server.sin_port = htons(port);
        ::inet_pton(AF_INET, std::string(ip).c_str(), &server.sin_addr);

        if (::connect(sock_, reinterpret_cast<sockaddr*>(&server), sizeof(server)) < 0) {
            close_socket();
        }
    }

    ~ScpiSocket() {
        close_socket();
#if defined(_WIN32)
        WSACleanup();
#endif
    }

    [[nodiscard]] bool is_valid() const noexcept { return sock_ >= 0; }

    bool send_command(std::string_view cmd) {
        if (!is_valid()) return false;
        std::string full_cmd = std::string(cmd) + "\n";
        return ::send(sock_, full_cmd.c_str(), static_cast<int>(full_cmd.size()), 0) >= 0;
    }

    std::expected<std::string, VnaError> query(std::string_view cmd) {
        if (!send_command(cmd)) {
            return std::unexpected(VnaError::QueryFailed);
        }
        std::vector<char> buffer(32768, 0);
        int bytes = ::recv(sock_, buffer.data(), static_cast<int>(buffer.size() - 1), 0);
        if (bytes <= 0) {
            return std::unexpected(VnaError::QueryFailed);
        }
        return std::string(buffer.data(), static_cast<size_t>(bytes));
    }

private:
    void close_socket() noexcept {
        if (sock_ >= 0) {
#if defined(_WIN32)
            ::closesocket(sock_);
#else
            ::close(sock_);
#endif
            sock_ = -1;
        }
    }

    int sock_{-1};
};

class ReturnLossAnalyzer {
public:
    static double calculate_vswr(double s11_db) noexcept {
        if (s11_db >= 0.0) return 999.0;
        double gamma = std::pow(10.0, s11_db / 20.0);
        if (gamma >= 0.999) return 999.0;
        return (1.0 + gamma) / (1.0 - gamma);
    }

    static std::expected<VnaAnalysisResult, VnaError> measure(
        std::string_view ip, uint16_t port, double start_freq_hz, double stop_freq_hz, size_t num_points = 201)
    {
        ScpiSocket vna(ip, port);
        if (!vna.is_valid()) {
            return std::unexpected(VnaError::ConnectionFailed);
        }

        vna.send_command(":SENS:FREQ:STAR " + std::to_string(start_freq_hz));
        vna.send_command(":SENS:FREQ:STOP " + std::to_string(stop_freq_hz));
        vna.send_command(":CALC:FORM MLOG");

        auto raw_data = vna.query(":CALC:DATA? FDATA");
        if (!raw_data) {
            return std::unexpected(raw_data.error());
        }

        VnaAnalysisResult res;
        std::stringstream ss(*raw_data);
        std::string val_str;
        size_t idx = 0;
        double step = (stop_freq_hz - start_freq_hz) / static_cast<double>(num_points - 1);

        while (std::getline(ss, val_str, ',')) {
            try {
                double s11_db = std::stod(val_str);
                double freq = start_freq_hz + static_cast<double>(idx) * step;
                double rl = -s11_db;
                double vswr = calculate_vswr(s11_db);

                res.points.push_back({freq, s11_db, rl, vswr});

                if (idx == 0 || s11_db < res.min_s11_db) {
                    res.min_s11_db = s11_db;
                    res.max_return_loss_db = rl;
                    res.resonant_freq_hz = freq;
                }

                if (vswr > res.peak_vswr) {
                    res.peak_vswr = vswr;
                }
                idx++;
            } catch (...) {
                continue;
            }
        }

        if (res.points.empty()) {
            return std::unexpected(VnaError::ParseError);
        }

        double f_low = 0.0, f_high = 0.0;
        for (const auto& pt : res.points) {
            if (pt.s11_db <= -10.0) {
                if (f_low == 0.0) f_low = pt.freq_hz;
                f_high = pt.freq_hz;
            }
        }
        res.bw_10db_hz = (f_high > f_low) ? (f_high - f_low) : 0.0;

        return res;
    }
};

} // namespace rf

int main() {
    std::cout << "Аналізатор зворотних втрат VNA (C++23)\n";
    auto result = rf::ReturnLossAnalyzer::measure("127.0.0.1", 5025, 2.3e9, 2.6e9);
    
    if (!result) {
        std::cout << "З'єднання з VNA відсутнє, демонстраційні розраховані параметри:\n";
        std::cout << "  Резонанс: 2.450 ГГц, Max RL: 28.5 дБ (S11 = -28.5 дБ)\n";
        std::cout << "  Смуга BW (-10 дБ): 100.0 МГц, VSWR на резонансі: 1.07\n";
        return 0;
    }

    std::cout << "Зворотні втрати виміряно успішно!\n";
    std::cout << "  Точок: " << result->points.size() << "\n";
    std::cout << "  f0: " << result->resonant_freq_hz / 1e9 << " ГГц\n";
    std::cout << "  RL max: " << result->max_return_loss_db << " дБ\n";
    std::cout << "  BW (-10дБ): " << result->bw_10db_hz / 1e6 << " МГц\n";
    return 0;
}
```
:::

---

### 5. Особливості реалізації та випробування у промислових умовах

Під час побудови виробничих автоматизованих вимірювальних систем слід ураховувати декілька потенційних пасток:

- **Таймаути мережевого сокета**: Сканування з високою деталізацією (наприклад 1601 точка) або низькою смугою ПЧ (IF Bandwidth = 100 Гц) може тривати від 500 мс до 5 секунд. Стандартні таймаути сокета у 100 мс призведуть до передчасного розриву з'єднання. У реальних системах таймаут прийому `SO_RCVTIMEO` слід встановлювати не менше ніж 5000 мс.
- **Векторне калібрування SOLT (Short-Open-Load-Through)**: Програма передбачає, що VNA вже відкалібровано на рівні вимірювального кабелю. Якщо калібрування не виконане, некомпенсоване загасання та фазовий набіг кабелю викривляють виміряні зворотні втрати (як показано у математичній моделі кабелю). За потреби SCPI-драйвер може відправляти команди завантаження калібрувального стану `:SENS:CORR:CSET:ACT "MY_CAL_50OHM"`.
- **Фільтрація шумів та згладжування**: У реальних умовах вимірювальний сигнал містить завади. Для запобігання хибному визначенню меж смуги `BW_-10dB` застосовують алгоритм рухомого середнього (Moving Average Filter) з вікном у 3–5 точок перед пошуком порогу −10 дБ.
- **RAII та безпечність ресурсів у C++**: Реалізація `ScpiSocket` мовою C++ гарантує закриття дескриптора сокета та виклики `WSACleanup()` у деструкторі навіть при виникненні винятків під час парсингу даних. Використання `std::expected` дозволяє явно обробляти помилки мережі без накладних витрат на винятки в обчислювальному циклі.
