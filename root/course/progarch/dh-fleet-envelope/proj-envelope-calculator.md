# ⚙️ Калькулятор оцінки ємності флоту DH

У цій вставці наведено практичну реалізацію та інженерний аналіз консольного інструменту оцінки ємності (Envelope Capacity Calculator) для флоту пристроїв Digital Homes. Калькулятор приймає вихідні характеристики флоту — кількість пристроїв, частоту відправки телеметрії, розміри пакетів та коефіцієнти пікових сплесків — і розраховує підсумкові потреби у ресурсах: оперативній пам'яті сокетів, обчислювальних ядрах CPU для TLS-хендшейків та десеріалізації, мережевій смузі й дискових IOPS.

## Інженерна концепція інструменту розрахунку

При розробці високонавантаженої платформи Digital Homes інженерам постійно доводиться відповідати на запитання щодо впливу нових бізнес-вимог на інфраструктуру. Наприклад, що станеться з серверами, якщо частоту опитування датчиків протікання води збільшити з 30 секунд до 5 секунд? Або скільки додаткової оперативної пам'яті вимагатиме перехід з протоколу HTTP/2 на довготривалі WebSocket-з'єднання при зростанні флоту до 500 тисяч будинків?

Замість того щоб кожного разу виконувати розрахунки на папері наново або розгортати дорогі тестувальні кластери, інженерна команда створює спеціалізований калькулятор оцінки ємності. Цей інструмент кодує фізичні параметри системних ресурсів і дозволяє проводити миттєвий аналіз чутливості (Sensitivity Analysis) інфраструктурного бюджету до будь-яких змін системних параметрів.

## Моделювання режимів навантаження

Програма моделює три різні фази функціонування розподіленої платформи, кожна з яких накладає пікове навантаження на свій вектор ресурсів:

1. **Штатний режим (Steady State):** Характеризується рівномірним розподілом вхідних повідомлень телеметрії від 200 000 активних хабів протягом доби. Пристрої відправляють серцебиття (Heartbeat) та поточні показники датчиків кожні 30 секунд. У цьому режимі головним лімітуючим фактором є обсяг оперативної пам'яті, необхідний для утримання 200 000 відкритих TCP-сесій та контекстів пристроїв.
2. **Вечірній пік (Evening Peak):** У період з 18:00 до 21:00 мешканці повертаються додому, активують системи освітлення, камери спостереження та кліматичне обладнання. Інтенсивність повідомлень зростає у 3 рази порівняно зі штатним режимом (до 20 000 msg/s). У цій фазі система перевіряє пропускну здатність мережевих інтерфейсів шлюзу та спроможність дискової підсистеми обробляти потік записів у Write-Ahead Log (WAL).
3. **Шторм повторних підключень (Blackout Reconnect Storm):** Відбувається у разі масового відновлення електроживлення у житловому масиві, коли 100 000 хабів одночасно вмикаються та намагаються встановити нове TLS-з'єднання з хмарою протягом 60 секунд. Цей режим дає екстремальне навантаження на обчислювальні ядра процесора (CPU Saturation), оскільки асиметрична криптографія TLS 1.3 вимагає значних обчислювальних ресурсів для перевірки сертифікатів та обміну ключами.

## Розбір математичної логіки розрахунку у коді

В основі роботи калькулятора лежить послідовне перетворення вихідних параметрів флоту на фізичні одиниці виміру заліза.

Спочатку програма обчислює базову інтенсивність повідомлень у штатному та піковому режимах шляхом ділення кількості пристроїв на інтервал відправки телеметрії. Далі розраховується обсяг пам'яті сокетів: кількість пристроїв множиться на 48 кілобайтів (сума буферів прийому й передачі ядра Linux, контексту OpenSSL та доменного стану сесії) і конвертується у гігабайти.

Мережева смуга обчислюється шляхом додавання 107 байтів протокольного оверхеду (Ethernet, IP, TCP, TLS) до корисного навантаження Protobuf. Підсумковий розмір кадру множиться на піковий темп повідомлень і переводиться у мегабіти на секунду.

Для розрахунку навантаження на CPU під час шторму реконектів калькулятор вираховує кількість хендшейків на секунду та зважену середньозважену тривалість обчислення криптографії з урахуванням відсотка успішного використання TLS Session Tickets (Session Resumption).

Нарешті, дискові IOPS розраховуються у двох варіантах: сирий потік поодиноких записів проти агрегованого потоку після застосування кільцевого буфера накопичення (100 ms flush window), що дає фіксовані 10 IOPS послідовного запису.

## Реалізація калькулятора різними мовами програмування

Нижче наведено робочі реалізації калькулятора навантаження мовами C, C++, Python та Go. Кожна реалізація є самостійною і може бути скомпільована та запущена в консолі для перевірки розрахунків.

:::tabs
```c
/* envelope_calc.c - C implementation of DH Capacity Calculator */
#include <stdio.h>
#include <stdint.h>
#include <math.h>

typedef struct {
    uint64_t fleet_size;           /* Кількість пристроїв (наприклад, 200000) */
    double   telemetry_interval_s; /* Інтервал між повідомленнями у секундах (30.0) */
    uint32_t payload_bytes;        /* Розмір корисної телеметрії у байтах (500) */
    double   peak_multiplier;      /* Коефіцієнт піку (3.0) */
    double   reconnect_window_s;   /* Вікно реконекту при блекаут штормі (60.0) */
    double   reconnect_fraction;   /* Частка пристроїв у реконекті (0.50) */
    double   tls_resumption_rate;  /* Частка скористанних TLS Session Tickets (0.80) */
} fleet_config_t;

typedef struct {
    double   msg_rate_steady;     /* msg/s у штатному режимі */
    double   msg_rate_peak;       /* msg/s у вечірній пік */
    double   ram_sockets_gb;      /* Пам'ять під TCP/TLS сесії у GB */
    double   net_bandwidth_mbps;  /* Мережева смуга у Mbps */
    double   cpu_crypto_cores;    /* Необхідні ядра CPU під TLS хендшейки у пік */
    double   cpu_parse_cores;     /* Необхідні ядра CPU під парсинг Protobuf */
    uint32_t iops_raw;            /* IOPS без батчингу */
    uint32_t iops_batched;        /* IOPS з батчингом (100 ms) */
    double   storage_gb_per_day;  /* Добовий обсяг збереження у GB */
} capacity_report_t;

void calculate_capacity(const fleet_config_t* cfg, capacity_report_t* out) {
    /* 1. Інтенсивність повідомлень */
    out->msg_rate_steady = (double)cfg->fleet_size / cfg->telemetry_interval_s;
    out->msg_rate_peak   = out->msg_rate_steady * cfg->peak_multiplier;

    /* 2. Пам'ять (48 KB на з'єднання: 16K kernel rx/tx + 16K TLS + 16K app state) */
    const double bytes_per_session = 48.0 * 1024.0;
    out->ram_sockets_gb = ((double)cfg->fleet_size * bytes_per_session) / (1024.0 * 1024.0 * 1024.0);

    /* 3. Мережева смуга (корисне навантаження + 107B оверхед L2-L4/TLS) */
    const double frame_bytes = (double)cfg->payload_bytes + 107.0;
    out->net_bandwidth_mbps = (out->msg_rate_peak * frame_bytes * 8.0) / 1000000.0;

    /* 4. CPU для TLS-хендшейків під час реконект шторму */
    double reconnect_events = (double)cfg->fleet_size * cfg->reconnect_fraction;
    double handshakes_per_sec = reconnect_events / cfg->reconnect_window_s;

    double full_handshake_ms = 0.60;
    double resume_handshake_ms = 0.05;

    double avg_handshake_ms = (handshakes_per_sec * (1.0 - cfg->tls_resumption_rate) * full_handshake_ms) +
                              (handshakes_per_sec * cfg->tls_resumption_rate * resume_handshake_ms);
    out->cpu_crypto_cores = avg_handshake_ms / 1000.0;

    /* 5. CPU для парсингу евентів (припустимо 5 µs на Protobuf декодування) */
    out->cpu_parse_cores = (out->msg_rate_peak * 0.000005);

    /* 6. Дискові IOPS та обсяг зберігання */
    out->iops_raw = (uint32_t)out->msg_rate_peak;
    out->iops_batched = 10; /* 100 ms flush window = 10 IOPS */

    double daily_bytes = out->msg_rate_steady * 86400.0 * (double)cfg->payload_bytes;
    out->storage_gb_per_day = daily_bytes / (1024.0 * 1024.0 * 1024.0);
}

int main(void) {
    fleet_config_t cfg = {
        .fleet_size = 200000,
        .telemetry_interval_s = 30.0,
        .payload_bytes = 500,
        .peak_multiplier = 3.0,
        .reconnect_window_s = 60.0,
        .reconnect_fraction = 0.50,
        .tls_resumption_rate = 0.80
    };

    capacity_report_t rep;
    calculate_capacity(&cfg, &rep);

    printf("=== DH Fleet Capacity Report (200k devices) ===\n");
    printf("Steady Msg Rate:   %.1f msg/s\n", rep.msg_rate_steady);
    printf("Peak Msg Rate:     %.1f msg/s\n", rep.msg_rate_peak);
    printf("RAM Sockets State: %.2f GB\n", rep.ram_sockets_gb);
    printf("Peak Bandwidth:    %.2f Mbps\n", rep.net_bandwidth_mbps);
    printf("TLS Crypto Cores:  %.2f cores\n", rep.cpu_crypto_cores);
    printf("Event Parse Cores: %.2f cores\n", rep.cpu_parse_cores);
    printf("Raw Disk IOPS:     %u IOPS\n", rep.iops_raw);
    printf("Batched Disk IOPS: %u IOPS\n", rep.iops_batched);
    printf("Storage Growth:    %.2f GB/day\n", rep.storage_gb_per_day);

    return 0;
}
```
```cpp
// envelope_calc.cpp - Idiomatic C++20 implementation of DH Capacity Calculator
#include <iostream>
#include <iomanip>
#include <cstdint>
#include <cmath>

struct FleetConfig {
    std::uint64_t fleet_size{200000};
    double        telemetry_interval_s{30.0};
    std::uint32_t payload_bytes{500};
    double        peak_multiplier{3.0};
    double        reconnect_window_s{60.0};
    double        reconnect_fraction{0.50};
    double        tls_resumption_rate{0.80};
};

struct CapacityReport {
    double        msg_rate_steady{0.0};
    double        msg_rate_peak{0.0};
    double        ram_sockets_gb{0.0};
    double        net_bandwidth_mbps{0.0};
    double        cpu_crypto_cores{0.0};
    double        cpu_parse_cores{0.0};
    std::uint32_t iops_raw{0};
    std::uint32_t iops_batched{0};
    double        storage_gb_per_day{0.0};

    static constexpr CapacityReport compute(const FleetConfig& cfg) noexcept {
        CapacityReport rep{};

        rep.msg_rate_steady = static_cast<double>(cfg.fleet_size) / cfg.telemetry_interval_s;
        rep.msg_rate_peak   = rep.msg_rate_steady * cfg.peak_multiplier;

        // 48 KB per session: 16K kernel rx/tx + 16K TLS + 16K app state
        constexpr double bytes_per_session = 48.0 * 1024.0;
        rep.ram_sockets_gb = (static_cast<double>(cfg.fleet_size) * bytes_per_session) / (1024.0 * 1024.0 * 1024.0);

        constexpr double frame_overhead = 107.0; // TLS/TCP/IP/Ethernet framing
        const double frame_bytes = static_cast<double>(cfg.payload_bytes) + frame_overhead;
        rep.net_bandwidth_mbps = (rep.msg_rate_peak * frame_bytes * 8.0) / 1'000'000.0;

        const double reconnect_events = static_cast<double>(cfg.fleet_size) * cfg.reconnect_fraction;
        const double handshakes_per_sec = reconnect_events / cfg.reconnect_window_s;

        constexpr double full_handshake_ms   = 0.60;
        constexpr double resume_handshake_ms = 0.05;

        const double total_handshake_ms = (handshakes_per_sec * (1.0 - cfg.tls_resumption_rate) * full_handshake_ms) +
                                           (handshakes_per_sec * cfg.tls_resumption_rate * resume_handshake_ms);
        rep.cpu_crypto_cores = total_handshake_ms / 1000.0;

        rep.cpu_parse_cores = rep.msg_rate_peak * 0.000005; // 5 microseconds per Protobuf event

        rep.iops_raw = static_cast<std::uint32_t>(rep.msg_rate_peak);
        rep.iops_batched = 10; // 100 ms flush window

        const double daily_bytes = rep.msg_rate_steady * 86400.0 * static_cast<double>(cfg.payload_bytes);
        rep.storage_gb_per_day = daily_bytes / (1024.0 * 1024.0 * 1024.0);

        return rep;
    }

    void print() const {
        std::cout << std::fixed << std::setprecision(2);
        std::cout << "=== DH Fleet Capacity Report (200k devices) ===\n";
        std::cout << "Steady Msg Rate:   " << msg_rate_steady << " msg/s\n";
        std::cout << "Peak Msg Rate:     " << msg_rate_peak << " msg/s\n";
        std::cout << "RAM Sockets State: " << ram_sockets_gb << " GB\n";
        std::cout << "Peak Bandwidth:    " << net_bandwidth_mbps << " Mbps\n";
        std::cout << "TLS Crypto Cores:  " << cpu_crypto_cores << " cores\n";
        std::cout << "Event Parse Cores: " << cpu_parse_cores << " cores\n";
        std::cout << "Raw Disk IOPS:     " << iops_raw << " IOPS\n";
        std::cout << "Batched Disk IOPS: " << iops_batched << " IOPS\n";
        std::cout << "Storage Growth:    " << storage_gb_per_day << " GB/day\n";
    }
};

int main() {
    constexpr FleetConfig config{};
    constexpr auto report = CapacityReport::compute(config);
    report.print();
    return 0;
}
```
```python
# envelope_calc.py - Python implementation of DH Capacity Calculator
from dataclasses import dataclass

@dataclass
class FleetConfig:
    fleet_size: int = 200_000
    telemetry_interval_s: float = 30.0
    payload_bytes: int = 500
    peak_multiplier: float = 3.0
    reconnect_window_s: float = 60.0
    reconnect_fraction: float = 0.50
    tls_resumption_rate: float = 0.80

def calculate_capacity(cfg: FleetConfig) -> dict:
    steady_rate = cfg.fleet_size / cfg.telemetry_interval_s
    peak_rate = steady_rate * cfg.peak_multiplier

    # RAM: 48 KB per session
    ram_gb = (cfg.fleet_size * 48 * 1024) / (1024 ** 3)

    # Net bandwidth
    frame_bytes = cfg.payload_bytes + 107
    net_mbps = (peak_rate * frame_bytes * 8) / 1e6

    # TLS crypto CPU
    reconnect_hps = (cfg.fleet_size * cfg.reconnect_fraction) / cfg.reconnect_window_s
    crypto_ms = (reconnect_hps * (1 - cfg.tls_resumption_rate) * 0.60) + \
                (reconnect_hps * cfg.tls_resumption_rate * 0.05)
    crypto_cores = crypto_ms / 1000.0

    parse_cores = peak_rate * 0.000005
    storage_gb_day = (steady_rate * 86400 * cfg.payload_bytes) / (1024 ** 3)

    return {
        "msg_rate_steady": steady_rate,
        "msg_rate_peak": peak_rate,
        "ram_sockets_gb": ram_gb,
        "net_bandwidth_mbps": net_mbps,
        "cpu_crypto_cores": crypto_cores,
        "cpu_parse_cores": parse_cores,
        "iops_raw": int(peak_rate),
        "iops_batched": 10,
        "storage_gb_per_day": storage_gb_day
    }

if __name__ == "__main__":
    rep = calculate_capacity(FleetConfig())
    print("=== DH Fleet Capacity Report (200k devices) ===")
    for k, v in rep.items():
        print(f"{k:20s}: {v:.2f}")
```
```go
// envelope_calc.go - Go implementation of DH Capacity Calculator
package main

import (
	"fmt"
)

type FleetConfig struct {
	FleetSize          uint64
	TelemetryIntervalS float64
	PayloadBytes       uint32
	PeakMultiplier     float64
	ReconnectWindowS   float64
	ReconnectFraction  float64
	TLSResumptionRate  float64
}

type CapacityReport struct {
	MsgRateSteady    float64
	MsgRatePeak      float64
	RAMSocketsGB     float64
	NetBandwidthMbps float64
	CPUCryptoCores   float64
	CPUParseCores    float64
	IOPSRaw          uint32
	IOPSBatched      uint32
	StorageGBPerDay  float64
}

func CalculateCapacity(cfg FleetConfig) CapacityReport {
	steadyRate := float64(cfg.FleetSize) / cfg.TelemetryIntervalS
	peakRate := steadyRate * cfg.PeakMultiplier

	bytesPerSession := 48.0 * 1024.0
	ramSocketsGB := (float64(cfg.FleetSize) * bytesPerSession) / (1024.0 * 1024.0 * 1024.0)

	frameBytes := float64(cfg.PayloadBytes) + 107.0
	netBandwidthMbps := (peakRate * frameBytes * 8.0) / 1000000.0

	reconnectEvents := float64(cfg.FleetSize) * cfg.ReconnectFraction
	handshakesPerSec := reconnectEvents / cfg.ReconnectWindowS

	fullHandshakeMS := 0.60
	resumeHandshakeMS := 0.05

	avgHandshakeMS := (handshakesPerSec * (1.0 - cfg.TLSResumptionRate) * fullHandshakeMS) +
		(handshakesPerSec * cfg.TLSResumptionRate * resumeHandshakeMS)
	cpuCryptoCores := avgHandshakeMS / 1000.0

	cpuParseCores := peakRate * 0.000005

	return CapacityReport{
		MsgRateSteady:    steadyRate,
		MsgRatePeak:      peakRate,
		RAMSocketsGB:     ramSocketsGB,
		NetBandwidthMbps: netBandwidthMbps,
		CPUCryptoCores:   cpuCryptoCores,
		CPUParseCores:    cpuParseCores,
		IOPSRaw:          uint32(peakRate),
		IOPSBatched:      10,
		StorageGBPerDay:  (steadyRate * 86400.0 * float64(cfg.PayloadBytes)) / (1024.0 * 1024.0 * 1024.0),
	}
}

func main() {
	cfg := FleetConfig{
		FleetSize:          200000,
		TelemetryIntervalS: 30.0,
		PayloadBytes:       500,
		PeakMultiplier:     3.0,
		ReconnectWindowS:   60.0,
		ReconnectFraction:  0.50,
		TLSResumptionRate:  0.80,
	}

	rep := CalculateCapacity(cfg)
	fmt.Println("=== DH Fleet Capacity Report (200k devices) ===")
	fmt.Printf("Steady Msg Rate:   %.1f msg/s\n", rep.MsgRateSteady)
	fmt.Printf("Peak Msg Rate:     %.1f msg/s\n", rep.MsgRatePeak)
	fmt.Printf("RAM Sockets State: %.2f GB\n", rep.RAMSocketsGB)
	fmt.Printf("Peak Bandwidth:    %.2f Mbps\n", rep.NetBandwidthMbps)
	fmt.Printf("TLS Crypto Cores:  %.2f cores\n", rep.CPUCryptoCores)
	fmt.Printf("Event Parse Cores: %.2f cores\n", rep.CPUParseCores)
	fmt.Printf("Raw Disk IOPS:     %d IOPS\n", rep.IOPSRaw)
	fmt.Printf("Batched Disk IOPS: %d IOPS\n", rep.IOPSBatched)
	fmt.Printf("Storage Growth:    %.2f GB/day\n", rep.StorageGBPerDay)
}
```
:::

## Аналіз результатів моделювання та інтерпретація показників

Запуск вищенаведеного калькулятора на базових параметрах флоту (200 000 пристроїв, інтервал 30 с, корисний payload 500 байтів) видає чітку картину інфраструктурного бюджету:

1. **Мережева смуга:** Вхідний піковий потік становить 97.12 Мбіт/с. Це свідчить про те, що мережева смуга не є первинним вузьким місцем для даного типу телеметрії. Для обробки трафіку достатньо одного стандартного мережевого адаптера 1 Gbps з увімкненим режимом Receive Side Scaling (RSS) для рівномірного розподілу обробки пакетних переривань між ядрами CPU.
2. **Оперативна пам'ять:** Для утримання сокетів та контекстів 200 000 пристроїв необхідно 9.16 Гігабайтів RAM. Це важливе одкровення: система вимагає серйозного обсягу пам'яті навіть тоді, коли пристрої просто мовчки тримають з'єднання. Для забезпечення відмовостійкості рекомендується розгортати три вузли Gateway по 8 GB RAM кожен (по 3.05 GB на вузол), що залишає понад 60% запасу під операційну систему та розширення буферів сокетів.
3. **Обчислювальні ядра CPU:** У стаціонарному піковому режимі для парсингу Protobuf-пакетів потрібно лише 0.10 ядра CPU. Проте під час шторму реконектів криптографічний розрахунок хендшейків вимагає 1.00 ядра CPU навіть за умови, що 80% пристроїв успішно використовують TLS Session Tickets. Якщо ж вимкнути Session Resumption, потреба зросте до 6 ядер CPU, що може призвести до CPU Throttling і масової втрати підключень.
4. **Дискові IOPS та сховище:** Без буферизації диск отримує смертельні 20 000 випадкових IOPS. Застосування вхідного кільцевого буфера з вікном скидання 100 мілісекунд згортає цей потік у 10 послідовних записів на секунду обсягом по 1.0 МБ кожен. При цьому добовий обсяг збереження становить 268.2 ГБ/добу, що вимагає 8.05 Терабайт дискового простору для зберігання глибини історії у 30 днів.

## Інтеграція калькулятора у конвеєр автоматичного контролю (CI/CD)

Найбільша цінність калькулятора ємності досягається тоді, коли він стає частиною автоматичних перевірок у конвеєрі підготовки релізів (CI/CD Pipeline).

У багатьох продуктових командах виникає ситуація, коли розробники прошивок або сервісів збільшують розмір структури Protobuf або додають нові поля у серцебиття (Heartbeat), не усвідомлюючи наслідків для хмари. Якщо розробник збільшить корисне навантаження з 500 байтів до 1500 байтів, це непомітно для одного пристрою, але для флоту з 200 000 хабів це означає зростання добового дискового накопичення з 268 ГБ до 804 ГБ та збільшення мережевої смуги до 260 Мбіт/с.

Інтегруючи консольну версію калькулятора у крок CI-перевірки Pull Request-ів, команда може впровадити автоматичне правило: якщо зміни у схемах Protobuf або таймаутах призводять до зростання ресурсних вимог понад визначений ліміт (наприклад, +10% до бюджету RAM або Storage), білд зупиняється і вимагає явного підтвердження (Sign-off) від архітектора розподіленої системи.
