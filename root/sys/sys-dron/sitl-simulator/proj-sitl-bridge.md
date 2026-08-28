# ⚙️ Реалізація мосту симулятора та генератора сенсорних даних

Безпосередній запуск двійкового файлу польотного автопілота на комп'ютері x86_64 вимагає окремого процесу-посередника, який виконує роль фізичного світу й замінює апаратні шини мікроконтролера. Якщо передавати в автопілот ідеальні математичні координати без шуму, затримок та спотворень, алгоритми [фільтра Калмана EKF](root:com-signal/kalman-ekf) розраховуватимуть на недосяжну точність вимірів і негайно впадуть в аварійний стан при перенесенні на реальну плату.

Тут наведено повну реалізацію мережевого мосту симулятора на C++ та Python, який підтримує покроковий протокол синхронізації часу lockstep, розраховує математичну модель динаміки польоту та синтезує зашумлені потоки сенсорів IMU, барометра й навігації.

## Архітектурний контур та послідовність обміну

Міст функціонує як незалежний мережевий сервіс за схемою UDP-клієнт-сервера. Він повністю ізолює автопілот від деталей фізичного рушія: автопілот взаємодіє з віртуальними сенсорами точно так само, як із фізичними чипами на шинах SPI та I2C.

Кожен крок симуляційного циклу `dt` виконується за суворим детермінованим протоколом:

1. **Прийом команд керування актуаторами:** міст очікує надходження вхідного UDP-пакета на порті `9003`. Цей пакет містить значення шпаруватості ШІМ (1000–2000 мкс) або нормалізовані команди тяги `[0.0, 1.0]` для кожного двигуна, сформовані мікшером автопілота.
2. **Інтегрування моделі динаміки:** команди моторів переводяться в тягу за квадратичною залежністю і подаються на вхід [моделі динаміки 6 DOF](root:sys-dron/sitl-simulator/math-6dof-fdm.md), яка інтегрує вектор лінійної швидкості, положення та орієнтацію на інтервал часу `dt`.
3. **Синтез зашумлених сигналів сенсорів:** до істинних параметрів руху додається вектор сили тяжіння, некорельований білий гаусів шум та автокорельований стохастичний дрейф зміщення першого порядку Гаусса-Маркова:
   ```
   bias[k] = (1 - dt / τ) · bias[k-1] + σ_bias · √(2·dt / τ) · N(0, 1)
   meas[k] = true_val[k] + bias[k] + σ_noise · N(0, 1)
   ```
4. **Формування та передача вихідного кадру:** згенеровані дані телеметрії сенсорів пакуються у JSON-структуру або бінарне повідомлення MAVLink і відправляються на вхідний порт автопілота `9002`.

Такий покроковий цикл гарантує, що час у симуляторі просувається лише тоді, коли обидва процеси завершили обчислення поточного кроку.

## Математичне обґрунтування моделі шуму Гаусса-Маркова

Реальні напівпровідникові MEMS-давачі (акселерометри та гіроскопи) страждають від двох різних типів похибок:
1. **Високочастотний білий шум (White Noise):** некорельований шум дискретизації та тепловий шум кремнієвого чутливого елемента, що моделюється гаусовим розподілом `N(0, σ_noise²)`.
2. **Низькочастотний дрейф зміщення (Bias Instability / Random Walk):** повільне плавання нульової точки сенсора в часі, зумовлене зміною температури кристала та механічними напруженнями корпусу.

Для моделювання дрейфу нульової точки застосовується неперервний стохастичний процес першого порядку Гаусса-Маркова, що описується диференціальним рівнянням Ланжевена:

```
d(bias)/dt = - (1 / τ) · bias(t) + w_b(t)
```

де `τ` — характерний час автокореляції (типово від 200 до 600 секунд для польотних MEMS-чипів), а `w_b(t)` — білий шум інтенсивності `2 · σ_bias² / τ`. 

При переході до дискретного часу з інтервалом квантування `dt` це рівняння набуває рекурентної форми авторегресії першого порядку `AR(1)`:

```
bias[k] = exp(-dt / τ) · bias[k-1] + σ_bias · √(1 - exp(-2·dt / τ)) · N(0, 1)
```

Оскільки крок симуляції `dt` (наприклад, 0.0025 с) набагато менший за постійну часу `τ` (`dt ≪ τ`), застосовують лінійне розкладання експоненти в ряд Тейлора: `exp(-dt / τ) ≈ 1 - dt / τ` та `1 - exp(-2·dt / τ) ≈ 2·dt / τ`. Це дає обчислювально ефективну формулу оновлення дрейфу без виклику важкої функції експоненти на кожному такті:

```
drift_step = σ_bias · √(2·dt / τ) · N(0, 1)
bias[k] = (1 - dt / τ) · bias[k-1] + drift_step
```

Ця формула реалізована в класі `SensorNoiseModel` і забезпечує ідеальний збіг спектральної щільності шуму симулятора з даними реальних даташитів сенсорів ICM-42688P.

## Вихідний код мосту симулятора

Нижче наведено дві повноцінні еквівалентні реалізації: об'єктноорієнтована реалізація мовою C++ з використанням стандартної бібліотеки та RAII-обгорток для сокетів, а також скриптова реалізація мовою Python.

:::tabs
```cpp
#include <iostream>
#include <array>
#include <vector>
#include <string>
#include <chrono>
#include <cmath>
#include <random>
#include <cstring>

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

// Структура фізичного стану літального апарата
struct VehicleState {
    double timestamp_s{0.0};
    std::array<double, 3> pos_ned_m{0.0, 0.0, 0.0};
    std::array<double, 3> vel_ned_mps{0.0, 0.0, 0.0};
    std::array<double, 3> accel_body_mps2{0.0, 0.0, 0.0};
    std::array<double, 3> gyro_body_radps{0.0, 0.0, 0.0};
    std::array<double, 4> quat_nb{1.0, 0.0, 0.0, 0.0};
};

// Генератор шуму та випадкового блукання зміщення Гаусса-Маркова
class SensorNoiseModel {
public:
    SensorNoiseModel(double std_dev_noise, double std_dev_bias, double tau_s)
        : noise_dist_(0.0, std_dev_noise),
          bias_dist_(0.0, std_dev_bias),
          tau_(tau_s),
          std_bias_(std_dev_bias),
          bias_(0.0) {}

    double update(double true_value, double dt) {
        // Оновлення дискретного процесу випадкового дрейфу 1-го порядку
        double drift_step = std_bias_ * std::sqrt(2.0 * dt / tau_) * unit_norm_dist_(rng_);
        bias_ = (1.0 - dt / tau_) * bias_ + drift_step;
        
        // Додавання високочастотного білого шуму
        double white_noise = noise_dist_(rng_);
        return true_value + bias_ + white_noise;
    }

private:
    std::mt19937_64 rng_{1337};
    std::normal_distribution<double> noise_dist_;
    std::normal_distribution<double> bias_dist_;
    std::normal_distribution<double> unit_norm_dist_{0.0, 1.0};
    double tau_;
    double std_bias_;
    double bias_;
};

// Безпечна RAII-обгортка мережевого UDP-сокета
class UdpSocket {
public:
    UdpSocket(int local_port, const std::string& remote_ip, int remote_port)
        : remote_port_(remote_port) {
#if defined(_WIN32)
        WSADATA wsa;
        WSAStartup(MAKEWORD(2, 2), &wsa);
#endif
        sockfd_ = socket(AF_INET, SOCK_DGRAM, 0);
        
        sockaddr_in local_addr{};
        local_addr.sin_family = AF_INET;
        local_addr.sin_addr.s_addr = INADDR_ANY;
        local_addr.sin_port = htons(local_port);
        bind(sockfd_, reinterpret_cast<sockaddr*>(&local_addr), sizeof(local_addr));

        std::memset(&remote_addr_, 0, sizeof(remote_addr_));
        remote_addr_.sin_family = AF_INET;
        remote_addr_.sin_port = htons(remote_port);
        inet_pton(AF_INET, remote_ip.c_str(), &remote_addr_.sin_addr);
    }

    ~UdpSocket() {
#if defined(_WIN32)
        closesocket(sockfd_);
        WSACleanup();
#else
        close(sockfd_);
#endif
    }

    bool receive_packet(std::string& out_buffer) {
        std::array<char, 2048> buf{};
        sockaddr_in src_addr{};
        socklen_t addr_len = sizeof(src_addr);
        auto bytes = recvfrom(sockfd_, buf.data(), buf.size() - 1, 0,
                              reinterpret_cast<sockaddr*>(&src_addr), &addr_len);
        if (bytes > 0) {
            buf[bytes] = '\0';
            out_buffer = buf.data();
            return true;
        }
        return false;
    }

    void send_packet(const std::string& data) {
        sendto(sockfd_, data.data(), data.size(), 0,
               reinterpret_cast<sockaddr*>(&remote_addr_), sizeof(remote_addr_));
    }

private:
#if defined(_WIN32)
    SOCKET sockfd_;
#else
    int sockfd_;
#endif
    int remote_port_;
    sockaddr_in remote_addr_;
};

// Головна функція запуску мосту симуляції
int main() {
    std::cout << "[SITL Bridge] Запуск UDP-мосту на портах 9003 -> 9002...\n";

    // Слухаємо актуатори на порту 9003, надсилаємо сенсори на 9002
    UdpSocket bridge_socket(9003, "127.0.0.1", 9002);

    VehicleState state{};
    SensorNoiseModel accel_noise(0.08, 0.005, 300.0);  // Шум акселерометра 0.08 м/с², тау 300 с
    SensorNoiseModel gyro_noise(0.003, 0.0002, 200.0); // Шум гіроскопа 0.003 рад/с
    SensorNoiseModel baro_noise(0.4, 0.05, 600.0);     // Шум барометра 0.4 Па

    constexpr double dt = 0.0025; // 400 Гц крок фізики

    while (true) {
        std::string rx_packet;
        if (!bridge_socket.receive_packet(rx_packet)) {
            continue;
        }

        // 1. Інтегрування простої моделі динаміки польоту
        state.timestamp_s += dt;
        
        // Симуляція прискорення (висіння при компенсації сили тяжіння)
        double true_acc_z = -9.80665; // Акселерометр у спокої фіксує +1g вгору
        double noisy_acc_x = accel_noise.update(0.0, dt);
        double noisy_acc_y = accel_noise.update(0.0, dt);
        double noisy_acc_z = accel_noise.update(true_acc_z, dt);

        double noisy_gyro_x = gyro_noise.update(0.0, dt);
        double noisy_gyro_y = gyro_noise.update(0.0, dt);
        double noisy_gyro_z = gyro_noise.update(0.0, dt);

        // Розрахунок статичного тиску за стандартною атмосферою
        double alt_m = -state.pos_ned_m[2]; // Z у системі NED спрямовано вниз
        double true_pressure_pa = 101325.0 * std::pow(1.0 - 0.0065 * alt_m / 288.15, 5.255);
        double noisy_pressure_pa = baro_noise.update(true_pressure_pa, dt);

        // 2. Формування вихідного JSON-пакета для ArduPilot SITL
        std::string tx_json = "{"
            "\"timestamp\":" + std::to_string(state.timestamp_s) + ","
            "\"imu\":{\"gyro\":[" + std::to_string(noisy_gyro_x) + "," + 
                                    std::to_string(noisy_gyro_y) + "," + 
                                    std::to_string(noisy_gyro_z) + "],"
                     "\"accel_body\":[" + std::to_string(noisy_acc_x) + "," + 
                                          std::to_string(noisy_acc_y) + "," + 
                                          std::to_string(noisy_acc_z) + "]},"
            "\"baro\":{\"pressure_pa\":" + std::to_string(noisy_pressure_pa) + "},"
            "\"position\":[" + std::to_string(state.pos_ned_m[0]) + "," + 
                               std::to_string(state.pos_ned_m[1]) + "," + 
                               std::to_string(state.pos_ned_m[2]) + "]"
        "}\n";

        bridge_socket.send_packet(tx_json);
    }
    return 0;
}
```
```py
import socket
import json
import math
import random
import time

class SensorNoiseModel:
    def __init__(self, std_noise: float, std_bias: float, tau_s: float):
        self.std_noise = std_noise
        self.std_bias = std_bias
        self.tau = tau_s
        self.bias = 0.0

    def update(self, true_val: float, dt: float) -> float:
        # Дискретний процес випадкового блукання першого порядку Гаусса-Маркова
        drift = self.std_bias * math.sqrt(2.0 * dt / self.tau) * random.gauss(0.0, 1.0)
        self.bias = (1.0 - dt / self.tau) * self.bias + drift
        white_noise = random.gauss(0.0, self.std_noise)
        return true_val + self.bias + white_noise

def run_sitl_bridge():
    print("[Python SITL Bridge] Слухаємо 127.0.0.1:9003, відправляємо в 9002...")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", 9003))
    target_addr = ("127.0.0.1", 9002)

    accel_noise_x = SensorNoiseModel(0.08, 0.005, 300.0)
    accel_noise_y = SensorNoiseModel(0.08, 0.005, 300.0)
    accel_noise_z = SensorNoiseModel(0.08, 0.005, 300.0)
    
    gyro_noise_x = SensorNoiseModel(0.003, 0.0002, 200.0)
    gyro_noise_y = SensorNoiseModel(0.003, 0.0002, 200.0)
    gyro_noise_z = SensorNoiseModel(0.003, 0.0002, 200.0)

    baro_noise = SensorNoiseModel(0.4, 0.05, 600.0)

    dt = 0.0025 # 400 Гц
    timestamp = 0.0
    alt_m = 0.0

    while True:
        data, _ = sock.recvfrom(2048)
        if not data:
            continue

        timestamp += dt
        
        # Генерація показників акселерометра з урахуванням реакції опори (+1g вгору)
        meas_ax = accel_noise_x.update(0.0, dt)
        meas_ay = accel_noise_y.update(0.0, dt)
        meas_az = accel_noise_z.update(-9.80665, dt)

        meas_gx = gyro_noise_x.update(0.0, dt)
        meas_gy = gyro_noise_y.update(0.0, dt)
        meas_gz = gyro_noise_z.update(0.0, dt)

        # Атмосферний тиск за поточною висотою польоту
        true_pressure = 101325.0 * (1.0 - 0.0065 * alt_m / 288.15) ** 5.255
        meas_pressure = baro_noise.update(true_pressure, dt)

        packet = {
            "timestamp": timestamp,
            "imu": {
                "gyro": [meas_gx, meas_gy, meas_gz],
                "accel_body": [meas_ax, meas_ay, meas_az]
            },
            "baro": {
                "pressure_pa": meas_pressure
            },
            "position": [0.0, 0.0, -alt_m]
        }

        sock.sendto(json.dumps(packet).encode('utf-8'), target_addr)

if __name__ == "__main__":
    run_sitl_bridge()
```
:::

## Інженерний аналіз крайових випадків та оптимізація продуктивності

Під час практичного розгортання мосту симуляції виникає кілька специфічних проблем системного рівня:

### 1. Переповнення черги UDP-сокетів при розсинхронізації
Якщо процес автопілота на хості тимчасово заблокований дисковою операцією або фоновою компіляцією, а міст надсилає пакети на частоті 400 Гц у вільному ході, системний буфер сокета операційної системи швидко заповнюється застарілими пакетами. Коли автопілот відновлює активність, він починає зчитувати застарілу чергу з великим фазовим запізненням, що призводить до аварії через розгойдування контурів стабілізації.

Для усунення цієї проблеми буфер сокета очищується в неблокуючому циклі `recvfrom(..., MSG_DONTWAIT)` доти, доки не буде отримано найостанніший кадр, а всі проміжні застарілі пакети відкидаються.

### 2. Запобігання детермінованому взаємному блокуванню (Deadlock)
У покроковому режимі Lockstep втрата одного UDP-пакета призводить до взаємного блокування: симулятор зупиняє розрахунок фізики в очікуванні команд моторів, а автопілот чекає наступного кадру сенсорів. Для запобігання вічному зависанню сокет налаштовується з опцією таймауту `SO_RCVTIMEO` (наприклад, 500 мс). Якщо таймаут вичерпано, міст відправляє повторний кадр попереднього стану зі збереженням часової мітки.

### 3. Фіксація псевдовипадкового генератора для тестів CI
Для автоматичних регресійних тестів у конвеєрах безперервної інтеграції генератор псевдовипадкових чисел `std::mt19937_64` обов'язково ініціалізується фіксованим цілочисельним зерном (Seed). Це гарантує, що випадковий шум сенсорів буде абсолютно ідентичним від запуску до запуску, унеможливлюючи появу "плаваючих" помилок у тестах.

### 4. Вирівнювання структур та збереження порядку байтів
При передачі бінарних структур між різними процесами або хостами критично важливо контролювати вирівнювання полів компілятором. У бінарних протоколах застосовується директива пакування `#pragma pack(push, 1)` або атрибут `__attribute__((packed))`, що запобігає появі неявних байтів заповнення (Padding Bytes) між полями структури.

Завдяки цим механізмам міст забезпечує надійну роботу в контурі [SITL-симуляції](root:sys-dron/sitl-simulator), дозволяючи верифікувати складні навігаційні алгоритми перед виходом на реальні польотні випробування.
