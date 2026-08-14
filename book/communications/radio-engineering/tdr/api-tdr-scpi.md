# 📋 Протокол SCPI та API керування часовим рефлектометром

Автоматизація вимірювань у часовій рефлектометрії (TDR), інтеграція рефлектометрів у автоматизовані тестові комплекси (ATE) та розробка програмного забезпечення для аналізу цілісності сигналів здійснюються через стандартизований текстовий протокол SCPI (Standard Commands for Programmable Instruments).

Нижче наведено вичерпний довідник команд SCPI для керування TDR-модулями стробоскопічних осцилографів (наприклад, Tektronix DSA8300, Keysight 86100D DCA) та векторних аналізаторів кіл у режимі TDR (Keysight E5071C TDR / Anritsu ShockLine), а також практичну реалізацію клієнтської бібліотеки мовами C та C++.

---

### 1. Транспортні протоколи зв'язку та фізичні інтерфейси

Сучасні TDR-рефлектографи та стробоскопічні осцилографи підтримують три основні транспортні інтерфейси для передачі команд SCPI:

1. **LXI / Ethernet (TCP/IP):** Протокол HiSLIP (High Speed LAN Instrument Protocol) або прямі сирі сокети (RAW Sockets) на порту 5025. Забезпечує найвищу швидкість передачі бінарних масивів відліків (до 100 Мбіт/с) на великі відстані.
2. **USBTMC (USB Test and Measurement Class):** Фізичне з'єднання по шині USB 2.0/3.0. Забезпечує низькі часові затримки при передачі окремих SCPI-команд та не вимагає мережевого налаштування IP-адрес.
3. **GPIB (IEEE 488.2):** Класична вимірювальна паралельна шина. Застосовується в лабораторних приладах попередніх поколінь (наприклад, HP 54750A чи Tektronix 11801).

---

### 2. Ієрархія та підсистеми команд SCPI для TDR

Протокол SCPI ділить керування приладом на кілька підсистем (`:SENSe`, `:TIMebase`, `:CALCulate`, `:TRACe`, `:SYSTem`), кожна з яких відповідає за свій фізичний каскад вимірювального тракту.

```
                  [Головне SCPI Дерево]
                            │
   ┌────────────────────────┼────────────────────────┐
   ▼                        ▼                        ▼
:SENSe:TDR              :TIMebase               :CALCulate:TDR
(Генератор & Самплер)   (Часова розгортка)      (DSP & Одиниці)
   │                        │                        │
   ├─ :STATe ON|OFF         ├─ :SPAN <sec>           ├─ :UNIT RHO|IMP|VOLT
   ├─ :PULSe:AMPL <V>       ├─ :POSition <sec>       ├─ :VFACTor <val>
   └─ :PULSe:RISE <sec>     └─ :DESKew <sec>         └─ :GATE:STATe ON|OFF
```

#### А. Підсистема джерела збудження та самплера (`:SENSe:TDR`)

Підсистема `:SENSe:TDR` відповідає за ввімкнення генератора надшвидких перепадів напруги, налаштування амплітуди, форми та імпульсної полярності.

* `:SENSe:TDR:STATe <1|0|ON|OFF>` — ввімкнення або вимкнення вихідного генератора перепаду на вказаному каналі. При включенні генератор починає випромінювати послідовність ступенястих перепадів напруги з заданою частотою повторення.
* `:SENSe:TDR:PULSe:AMPLitude <value_volts>` — встановлення пікової амплітуди перепаду напруги у Вольтах (типові значення від `0.100` В до `0.500` В для захисту чутливих входів мікросхем).
* `:SENSe:TDR:PULSe:RISEtime <value_seconds>` — встановлення тривалості фронту наростання перепаду. Дозволяє інженеру програмно «уповільнити» фронт (наприклад, з `28 пс` до `100 пс`), щоб імітувати реальний сигнал цифрової шини та оцінити відбиття у робочому діапазоні.
* `:SENSe:TDR:MODE <SINGle|DIFFerential|COMMon>` — вибір режиму виходу: однофазний (Single-Ended), диференційний протифазний (Differential) або синфазний (Common Mode).
* `:SENSe:TDR:POLarity <POSitive|NEGative>` — вибір полярності зондувального перепаду (позитивний ступенястий перепад від 0 до +V або негативний від 0 до -V).

#### Б. Підсистема часової розгортки та синхронізації (`:TIMebase`)

Підсистема `:TIMebase` задає тривалість часового вікна, частоту дискретизації та точний часовий зсув точки початку зчитування.

* `:TIMebase:SPAN <value_seconds>` — ширина вікна спостереження у секундах (наприклад, `10E-9` відповідає вікну 10 наносекунд).
* `:TIMebase:POSition <value_seconds>` — часова затримка початку відліку відносно синхроімпульсу. Дозволяє «зсунути» вікно спостереження на далеку ділянку кабелю.
* `:TIMebase:DESKew <value_seconds>` — компенсація часового розсинхронізму між вимірювальними кабелями зондів (Deskew calibration).
* `:TIMebase:REFerence <LEFT|CENTer|RIGHt>` — вибір опорної точки часового зсуву на екрані приладу.

#### В. Підсистема цифрової обробки та перетворення одиниць (`:CALCulate:TDR`)

Підсистема `:CALCulate` перераховує напругу відбігу `V(t)` у вимірювальні одиниці за вибором користувача:

* `:CALCulate:TDR:UNIT <VOLT|RHO|IMPedance>` — одиниці відображення траси:
  * `VOLT` — сира напруга у Вольтах.
  * `RHO` — коефіцієнт відбиття `Γ` (від `-1.0` до `+1.0`, або у відсотках `mRho`).
  * `IMPedance` — розрахований локальний хвильовий опір у Омах ($Z_L$).
* `:CALCulate:TDR:VFACTor <value>` — коефіцієнт укорочення лінії `VF = 1 / √(ε_r)`. Використовується приладом для автоматичного перерахунку часової осі `t` у просторову відстань `x` у метрах.
* `:CALCulate:TDR:CORRect:STATe <1|0>` — увімкнення векторного калібрування плоскості відліку (Short-Open-Load calibration) для усунення паразитного впливу підключених вимірювальних кабелів та переходів.
* `:CALCulate:TDR:GATE:STATe <1|0>` — ввімкнення часового селектування (Time Gating) для математичного відсікання відбиттів вимірювального роз'єму.
* `:CALCulate:TDR:GATE:STARt <value_seconds>` — початок часового вікна селектування.
* `:CALCulate:TDR:GATE:STOP <value_seconds>` — кінець часового вікна селектування.

---

### 3. Специфікація команд SCPI та форматів даних

| Команда SCPI | Тип | Діапазон параметрів | Опис та приклад |
| :--- | :--- | :--- | :--- |
| `:SENS1:TDR:STAT ON` | Команда | `ON`, `OFF`, `1`, `0` | Ввімкнути генератор TDR на каналі 1 |
| `:SENS1:TDR:PULS:AMPL 0.2` | Команда | `0.05` ... `0.50` В | Встановити амплітуду перепаду 200 мВ |
| `:SENS1:TDR:PULS:RISE 35E-12` | Команда | `20E-12` ... `1E-9` с | Встановити фронт наростання 35 пікосекунд |
| `:TIM:SPAN 5E-9` | Команда | `100E-12` ... `1E-6` с | Часове вікно 5 наносекунд |
| `:TIM:POS 12E-9` | Команда | `0` ... `10E-6` с | Зсув вікна спостереження на 12 нс |
| `:CALC1:TDR:UNIT IMP` | Команда | `VOLT`, `RHO`, `IMP` | Перевести шкалу у значення опору (Оми) |
| `:CALC1:TDR:VFACT 0.667` | Команда | `0.1` ... `1.0` | Встановити коефіцієнт укорочення поліетилену |
| `:CALC1:TDR:GATE:STAT ON` | Команда | `ON`, `OFF` | Увімкнути часове вікно селектування (Gating) |
| `:FORMat:DATA REAL,32` | Команда | `ASCII`, `REAL,32` | Встановити бінарний 32-бітний формат IEEE 754 |
| `:TRACe:DATA? TRACE1` | Запит | — | Зчитати масив відліків рефлектограми |
| `:SYSTem:ERRor?` | Запит | — | Перевірити чергу системних помилок |

---

### 4. Формат двоєтичного блоку IEEE 488.2 Arbitrary Block Data

При запиті великих масивів відліків (наприклад, 4000 або 100000 точок) передача у текстовому форматі ASCII є вкрай повільною. Для прискорення використовують двоєтичний формат IEEE 488.2 `:FORMat:DATA REAL,32`.

Відповідь приладу на запит `:TRACe:DATA?` має таку структуру:

```
# 4 4000 <4000 байт двоєтичних даних float32> \n
│ │  │    │
│ │  │    └─ Масив відліків (1000 чисел float32 у форматі IEEE 754)
│ │  └────── Довжина двоєтичного блоку у байтах (4000 байт)
│ └───────── Кількість символів у полі довжини ("4000" має 4 символи)
└─────────── Маркер початку бінарного SCPI блоку
```

При зчитуванні бінарного блоку важливо враховувати **порядок байтів (Endianness)**: більшість вимірювальних приладів відправляють дані у форматі Big-Endian (Network Byte Order), тоді як архітектури x86/x64 використовують Little-Endian. Для коректного перетворення байтів у C/C++ застосовують функції `ntohl()` або перестановку байтів.

---

### 5. Розширене калібрування OSLT та перевірка стану через SCPI

Для досягнення прецизійної точності вимірювань перед початком сесії TDR-діагностики прилад вимагає процедури калібрування на торці вимірювальних зондів:

1. **Запит стану калібрування:** Команда `:CALibration:TDR:STATe?` повертає `1` (калібровано) або `0` (потрібне калібрування).
2. **Процедура OSLT (Open-Short-Load-Thru):** 
   * Послідовно підключаються поверхові еталони: Обрив (Open), Коротке замикання (Short) та Узгоджене навантаження 50 Ом (Load).
   * SCPI-команди процедури: `:CALibration:TDR:SOLT:OPEN`, `:CALibration:TDR:SOLT:SHORt`, `:CALibration:TDR:SOLT:LOAD`.
   * Прилад обчислює масив векторних помилок прямого тракту та математично віднімає опір зондів від підсумкової траси.

---

### 6. Обробка помилок, регістри статусу STB/ESR та синхронізація

Для забезпечення надійності при роботі в автоматизованих вимірювальних комплексах розробник повинен реалізувати обробку системних регістрів SCPI:

* **Регістр стану статусу (Status Byte Register, STB):** Читається командою `*STB?`. Біт 4 (`MAV` — Message Available) сигналізує про наявність даних у вихідному буфері сокета. Біт 5 (`ESB` — Event Status Bit) інформує про помилки виконання команди.
* **Регістр подій (Event Status Register, ESR):** Читається командою `*ESR?`. Очищає прапорці помилок синтаксису (`Command Error`), виходу за межі діапазону (`Execution Error`) та переповнення вимірювального тракту.
* **Перевірка черги помилок `:SYSTem:ERRor?`:** При виникненні невірного аргументу SCPI прилад повертає код та текстовий опис (наприклад, `-222,"Data out of range"`).
* **Синхронізація `*OPC?` (Operation Complete):** Гарантує, що прилад завершив усереднення траси перед видачею бінарного блоку даних.

---

### 7. Практичні реалізації C та C++ для керування TDR

Нижче наведено повні приклади коду для встановлення з'єднання з TDR-приладом через мережевий сокет LXI/TCP (порт 5025), налаштування параметрів вимірювання та зчитування масиву опору $Z(x)$.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#if defined(_WIN32)
  #include <winsock2.h>
  #include <ws2tcpip.h>
  #pragma comment(lib, "ws2_32.lib")
#else
  #include <sys/socket.h>
  #include <netinet/in.h>
  #include <arpa/inet.h>
  #include <unistd.h>
#endif

/* Допоміжна функція відправки SCPI-команди */
int scpi_send(int sock, const char* cmd) {
    int len = (int)strlen(cmd);
    int sent = send(sock, cmd, len, 0);
    return (sent == len) ? 0 : -1;
}

/* 
 * Зчитування текстової відповіді на SCPI-запит
 */
int scpi_query_str(int sock, const char* query, char* out_buf, int max_len) {
    if (scpi_send(sock, query) < 0) return -1;

    int bytes = recv(sock, out_buf, max_len - 1, 0);
    if (bytes <= 0) return -2;

    out_buf[bytes] = '\0';
    return bytes;
}

/*
 * Комплексна функція налаштування TDR та зчитування траси
 */
int tdr_scpi_read_impedance(const char* ip_address, int port,
                             double span_ns, double vf_factor,
                             float* out_trace_ohm, int max_points) {
#if defined(_WIN32)
    WSADATA wsa_data;
    if (WSAStartup(MAKEWORD(2, 2), &wsa_data) != 0) return -1;
#endif

    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) {
#if defined(_WIN32)
        WSACleanup();
#endif
        return -2;
    }

    struct sockaddr_in serv_addr;
    memset(&serv_addr, 0, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(port);
    inet_pton(AF_INET, ip_address, &serv_addr.sin_addr);

    if (connect(sock, (struct sockaddr*)&serv_addr, sizeof(serv_addr)) < 0) {
#if defined(_WIN32)
        closesocket(sock);
        WSACleanup();
#else
        close(sock);
#endif
        return -3;
    }

    /* 1. Ідентифікація приладу */
    char idn[256];
    scpi_query_str(sock, "*IDN?\n", idn, sizeof(idn));
    printf("З'єднано з приладом: %s", idn);

    /* 2. Конфігурація підсистеми TDR */
    scpi_send(sock, ":SENS1:TDR:STAT ON\n");
    scpi_send(sock, ":SENS1:TDR:PULS:AMPL 0.200\n");
    
    char cmd_buf[128];
    snprintf(cmd_buf, sizeof(cmd_buf), ":TIM:SPAN %.9e\n", span_ns * 1e-9);
    scpi_send(sock, cmd_buf);

    snprintf(cmd_buf, sizeof(cmd_buf), ":CALC1:TDR:VFACT %.4f\n", vf_factor);
    scpi_send(sock, cmd_buf);

    scpi_send(sock, ":CALC1:TDR:UNIT IMP\n");
    scpi_send(sock, ":FORM:DATA ASCII\n");

    /* 3. Запит траси даних */
    scpi_send(sock, ":TRAC:DATA? TRACE1\n");

    char rx_chunk[2048];
    int count = 0;
    int bytes_read = 0;

    while ((bytes_read = recv(sock, rx_chunk, sizeof(rx_chunk) - 1, 0)) > 0 && count < max_points) {
        rx_chunk[bytes_read] = '\0';
        char* token = strtok(rx_chunk, ",\n\r");
        while (token && count < max_points) {
            out_trace_ohm[count++] = (float)atof(token);
            token = strtok(NULL, ",\n\r");
        }
        if (bytes_read < (int)sizeof(rx_chunk) - 1) break;
    }

    /* 4. Завершення сесії */
    scpi_send(sock, ":SENS1:TDR:STAT OFF\n");

#if defined(_WIN32)
    closesocket(sock);
    WSACleanup();
#else
    close(sock);
#endif

    return count;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <sstream>
#include <stdexcept>
#include <array>
#include <memory>

#if defined(_WIN32)
  #include <winsock2.h>
  #include <ws2tcpip.h>
  #pragma comment(lib, "ws2_32.lib")
#else
  #include <sys/socket.h>
  #include <netinet/in.h>
  #include <arpa/inet.h>
  #include <unistd.h>
#endif

class ScpiTdrInstrument {
public:
    explicit ScpiTdrInstrument(std::string_view ip, uint16_t port = 5025)
        : m_ip(ip), m_port(port) {
#if defined(_WIN32)
        WSADATA wsaData;
        if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
            throw std::runtime_error("Не вдалося ініціалізувати мережеву бібліотеку Winsock");
        }
#endif
    }

    ~ScpiTdrInstrument() {
        disconnect();
#if defined(_WIN32)
        WSACleanup();
#endif
    }

    void connectToInstrument() {
        m_sockfd = socket(AF_INET, SOCK_STREAM, 0);
        if (m_sockfd < 0) {
            throw std::runtime_error("Помилка створення TCP-сокета");
        }

        sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_port = htons(m_port);
        inet_pton(AF_INET, m_ip.c_str(), &addr.sin_addr);

        if (connect(m_sockfd, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) < 0) {
            disconnect();
            throw std::runtime_error("Не вдалося підключитися до TDR-приладу за адресою: " + m_ip);
        }

        // Перевірка зв'язку
        std::string idn = query("*IDN?\n");
        std::cout << "[SCPI] Підключено прилад: " << idn;
    }

    void configureTdr(double span_ns, double velocity_factor, bool differential = false) {
        sendCommand(":SENS1:TDR:STAT ON\n");
        sendCommand(":SENS1:TDR:PULS:AMPL 0.200\n");

        if (differential) {
            sendCommand(":SENS1:TDR:MODE DIFF\n");
        } else {
            sendCommand(":SENS1:TDR:MODE SING\n");
        }

        std::ostringstream ss;
        ss << ":TIM:SPAN " << (span_ns * 1e-9) << "\n";
        sendCommand(ss.str());

        ss.str("");
        ss.clear();
        ss << ":CALC1:TDR:VFACT " << velocity_factor << "\n";
        sendCommand(ss.str());

        sendCommand(":CALC1:TDR:UNIT IMP\n");
        sendCommand(":FORM:DATA ASCII\n");
    }

    std::vector<float> readImpedanceProfile() {
        sendCommand(":TRAC:DATA? TRACE1\n");
        std::string rawData = receiveResponse();

        std::vector<float> profile;
        std::stringstream ss(rawData);
        std::string item;

        while (std::getline(ss, item, ',')) {
            try {
                profile.push_back(std::stof(item));
            } catch (...) {
                // Пропуск можливих службових символів
            }
        }

        return profile;
    }

    void disableGenerator() {
        if (m_sockfd >= 0) {
            sendCommand(":SENS1:TDR:STAT OFF\n");
        }
    }

private:
    void sendCommand(std::string_view cmd) {
        if (m_sockfd < 0) throw std::runtime_error("Сокет не підключено");
        ssize_t sent = send(m_sockfd, cmd.data(), cmd.size(), 0);
        if (sent != static_cast<ssize_t>(cmd.size())) {
            throw std::runtime_error("Помилка відправки SCPI команди");
        }
    }

    std::string query(std::string_view queryCmd) {
        sendCommand(queryCmd);
        return receiveResponse();
    }

    std::string receiveResponse() {
        std::string response;
        std::array<char, 4096> buffer;
        ssize_t bytesRead = 0;

        while ((bytesRead = recv(m_sockfd, buffer.data(), buffer.size() - 1, 0)) > 0) {
            buffer[bytesRead] = '\0';
            response.append(buffer.data(), bytesRead);
            if (response.find('\n') != std::string::npos) break;
        }

        return response;
    }

    void disconnect() {
        if (m_sockfd >= 0) {
#if defined(_WIN32)
            closesocket(m_sockfd);
#else
            close(m_sockfd);
#endif
            m_sockfd = -1;
        }
    }

    std::string m_ip;
    uint16_t m_port;
    int m_sockfd{-1};
};
```
:::
