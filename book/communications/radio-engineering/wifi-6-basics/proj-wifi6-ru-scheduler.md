# ⚙️ Практична реалізація планувальника RU для Wi-Fi 6

Ця вставка містить програмний алгоритм розрахунку та оптимального розподілу ресурсних блоків (Resource Units, RU) у каналі 20 МГц для точки доступу Wi-Fi 6 (IEEE 802.11ax). У статті детально розкрито модель групування активних станцій, вибір конфігурації RU залежно від черги буфера даних і відношення сигнал/шум, архітектуру черг драйвера `mac80211`, трасування через `ftrace` та розширений аналіз часових накладних витрат OFDMA у порівнянні з традиційним послідовним доступом CSMA/CA.

## 1. Архітектура черг та логіка планувальника RU

Головне завдання рівня управління доступом до середовища (MAC-рівня) точки доступу (Access Point, AP) у стандарті 802.11ax полягає у формуванні кадру ініціалізації (Trigger Frame) або мультикористувацького кадру Downlink MU-PPDU. Планувальник відповідає за детерміноване розбиття доступних 242 корисних піднесучих каналу шириною 20 МГц між активними клієнтськими станціями.

### Внутрішня структура черг `mac80211` та диспетчеризація трафіку

У стеку бездротового зв'язку Linux системна субсистема `mac80211` зберігає пакети у чотирьох програмних чергах за категоріями якості обслуговування (QoS Access Categories, WMM):
1. **AC_VO (Voice):** Голосовий трафік із найвищим пріоритетом та вимогами до затримки `< 10 мкс`.
2. **AC_VI (Video):** Потокове відео високої чіткості із жорстким допуском джитера.
3. **AC_BE (Best Effort):** Стандартний інтерактивний веб-трафік (HTTP/HTTPS, SSH).
4. **AC_BK (Background):** Фонове завантаження файлів та службові оновлення.

У застарілих версіях Wi-Fi планировщик обробляв ці черги послідовно: пакети вишиковувалися в одну лінію, а алгоритм дискретного вирівнювання ефірного часу (Airtime Fairness, `fq_codel`) виділяв кожному пристрою часовий квант.

У Wi-Fi 6 планувальник OFDMA аналізує вміст усіх черг одночасно. Якщо в черзі AC_VO накопичилися два коротких голосових пакети від двох різних смартфонів, а в черзі AC_BE лежить об'ємний фрагмент файлу від ноутбука, планувальник об'єднує їх в один символ OFDMA: смартфонам виділяються два блоки RU26, а ноутбуку — блок RU106.

### Покроковий алгоритм роботи планувальника

Алгоритм планування радіоресурсу в точці доступу працює у п'ять послідовних етапів:

1. **Збір та аналіз метрик пристроїв:** 
   Для кожного активного клієнта драйвер `mac80211` зчитує поточний стан програмного буфера черги (розмір накопичених даних у байтах), рівень пріоритету трафіку (Access Category) та оцінку якості каналу (індекс модуляції MCS, SNR та рівень згасання).

2. **Сортування та ранжування черги:**
   Пріоритет у розкладі надається пристроям із чутливими до затримок пакетами (Voice/VoIP, інтерактивне відео, ігрові підтвердження), а також клієнтам із малими розмірами накопичених буферів. Це дозволяє очищати черги чергових службових пакетів без затримання масивного потокового трафіку.

3. **Вибір геометричної конфігурації RU:**
   Планувальник вибирає один із чотирьох канонічних варіантів частотного розбиття 20 МГц каналу:
   - `9 × RU26`: Виділяється до 9 ресурсних блоків по 26 піднесучих. Оптимально для обслуговування великої кількості IoT-датчиків чи передачі TCP ACK підтверджень.
   - `4 × RU52`: Виділяється 4 ресурсних блоки по 52 піднесучі (ширина ~4 МГц на клієнта).
   - `2 × RU106`: Виділяється 2 ресурсних блоки по 106 піднесучих (ширина ~8 МГц на клієнта).
   - `1 × RU242`: Монопольний режим Single-User для одного клієнта, що вимагає максимальної фізичної швидкості.

4. **Обчислення тривалості кадру та часу символів:**
   Визначається кількість OFDM-символів, необхідна для передачі найдовшого пакета серед обраної групи клієнтів. Оскільки тривалість одного символу 802.11ax становить `12.8 мкс + 0.8 мкс GI = 13.6 мкс`, загальна тривалість радіокадру обчислюється як множення кількості символів на `13.6 мкс`.

5. **Вирівнювання довжини кадрів (MAC Padding):**
   У зворотному каналі UL-OFDMA всі станції повинні завершити передачу строго одночасно. Станції, чий обсяг даних менший за ємність виділеного часу, заповнюють залишок кадру вирівнюючими нульовими байтами (MAC Padding).

## 2. Реалізація планувальника мовами Python та C++

Нижче наведено робочі програмні модулі симуляції планувальника RU. Приклади реалізовано мовами Python та сучасним ідіоматичним C++20.

:::tabs
```py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import List, Tuple
import math

# Тривалість одного символу 802.11ax (12.8 мкс + 0.8 мкс GI) у секундах
T_SYM_SEC = 13.6e-6

# Таблиця кількості піднесучих даних у ресурсних блоках RU
RU_DATA_SUBCARRIERS = {
    26: 24,
    52: 48,
    106: 102,
    242: 234
}

# Співвідношення MCS до кількості біт на піднесучу (з урахуванням FEC rate)
MCS_BITS_PER_SUBCARRIER = {
    0: 0.5,    # BPSK 1/2
    3: 2.5,    # 16-QAM 1/2
    7: 4.5,    # 64-QAM 5/6
    9: 6.667,  # 256-QAM 5/6
    11: 8.333  # 1024-QAM 5/6
}

@dataclass
class ClientRequest:
    client_id: int
    buffer_bytes: int
    mcs: int
    latency_sensitive: bool

@dataclass
class RUAllocation:
    client_id: int
    ru_type: int
    allocated_bytes: int
    frame_duration_us: float

class Wifi6RuScheduler:
    def __init__(self, bandwidth_mhz: int = 20):
        self.bandwidth_mhz = bandwidth_mhz

    def calculate_bits_per_symbol(self, ru_type: int, mcs: int) -> float:
        data_subcarriers = RU_DATA_SUBCARRIERS[ru_type]
        bits_per_sc = MCS_BITS_PER_SUBCARRIER.get(mcs, 1.0)
        return data_subcarriers * bits_per_sc

    def schedule_20mhz(self, clients: List[ClientRequest]) -> Tuple[str, List[RUAllocation]]:
        if not clients:
            return "NO_CLIENTS", []

        # Сортування: спершу критичні до затримки, потім за зростанням буфера
        sorted_clients = sorted(clients, key=lambda c: (not c.latency_sensitive, c.buffer_bytes))
        num_clients = len(sorted_clients)

        # Визначення геометрії RU залежно від кількості клієнтів у черзі
        if num_clients >= 5:
            pattern_name = "9xRU26"
            ru_type = 26
            max_slots = 9
        elif num_clients >= 3:
            pattern_name = "4xRU52"
            ru_type = 52
            max_slots = 4
        elif num_clients == 2:
            pattern_name = "2xRU106"
            ru_type = 106
            max_slots = 2
        else:
            pattern_name = "1xRU242"
            ru_type = 242
            max_slots = 1

        selected_clients = sorted_clients[:max_slots]
        allocations = []

        # Обчислення максимальної тривалості передачі серед обраних клієнтів
        max_symbols = 0
        for client in selected_clients:
            bits_per_sym = self.calculate_bits_per_symbol(ru_type, client.mcs)
            total_bits = client.buffer_bytes * 8
            needed_symbols = math.ceil(total_bits / bits_per_sym) if bits_per_sym > 0 else 1
            max_symbols = max(max_symbols, needed_symbols)

        frame_duration_us = max_symbols * T_SYM_SEC * 1e6

        # Формування результатів розподілу для кожного пристрою
        for client in selected_clients:
            bits_per_sym = self.calculate_bits_per_symbol(ru_type, client.mcs)
            capacity_bytes = math.floor((max_symbols * bits_per_sym) / 8)
            allocated_bytes = min(client.buffer_bytes, capacity_bytes)

            allocations.append(RUAllocation(
                client_id=client.client_id,
                ru_type=ru_type,
                allocated_bytes=allocated_bytes,
                frame_duration_us=frame_duration_us
            ))

        return pattern_name, allocations

def main():
    clients = [
        ClientRequest(client_id=1, buffer_bytes=120, mcs=7,  latency_sensitive=True),  # VoIP
        ClientRequest(client_id=2, buffer_bytes=80,  mcs=9,  latency_sensitive=True),  # Game ACK
        ClientRequest(client_id=3, buffer_bytes=500, mcs=11, latency_sensitive=False), # HTTP
        ClientRequest(client_id=4, buffer_bytes=300, mcs=7,  latency_sensitive=False)  # Sensor
    ]

    scheduler = Wifi6RuScheduler(bandwidth_mhz=20)
    pattern, allocs = scheduler.schedule_20mhz(clients)

    print(f"--- Результат планування Wi-Fi 6 OFDMA (Конфігурація: {pattern}) ---")
    for a in allocs:
        print(f"Клієнт #{a.client_id}: RU{a.ru_type} | Передано: {a.allocated_bytes} байт | Тривалість кадру: {a.frame_duration_us:.2f} мкс")

if __name__ == "__main__":
    main()
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <string>
#include <string_view>
#include <numeric>
#include <format>

// Тривалість одного символу 802.11ax (12.8 мкс + 0.8 мкс GI) у секундах
constexpr double T_SYM_SEC = 13.6e-6;

struct ClientRequest {
    int client_id;
    size_t buffer_bytes;
    int mcs;
    bool latency_sensitive;
};

struct RUAllocation {
    int client_id;
    int ru_type;
    size_t allocated_bytes;
    double frame_duration_us;
};

class Wifi6RuScheduler {
public:
    explicit Wifi6RuScheduler(int bandwidth_mhz = 20) : bandwidth_mhz_(bandwidth_mhz) {}

    static constexpr int get_data_subcarriers(int ru_type) noexcept {
        switch (ru_type) {
            case 26:  return 24;
            case 52:  return 48;
            case 106: return 102;
            case 242: return 234;
            default:  return 24;
        }
    }

    static constexpr double get_bits_per_subcarrier(int mcs) noexcept {
        switch (mcs) {
            case 0:  return 0.5;   // BPSK 1/2
            case 3:  return 2.5;   // 16-QAM 1/2
            case 7:  return 4.5;   // 64-QAM 5/6
            case 9:  return 6.667; // 256-QAM 5/6
            case 11: return 8.333; // 1024-QAM 5/6
            default: return 1.0;
        }
    }

    double calculate_bits_per_symbol(int ru_type, int mcs) const noexcept {
        return get_data_subcarriers(ru_type) * get_bits_per_subcarrier(mcs);
    }

    std::pair<std::string, std::vector<RUAllocation>> schedule_20mhz(std::vector<ClientRequest> clients) const {
        if (clients.empty()) {
            return {"NO_CLIENTS", {}};
        }

        // Сортування за пріоритетом затримки та розміром буфера
        std::sort(clients.begin(), clients.end(), [](const ClientRequest& a, const ClientRequest& b) {
            if (a.latency_sensitive != b.latency_sensitive) {
                return a.latency_sensitive > b.latency_sensitive;
            }
            return a.buffer_bytes < b.buffer_bytes;
        });

        const size_t num_clients = clients.size();
        std::string pattern_name;
        int ru_type = 26;
        size_t max_slots = 1;

        if (num_clients >= 5) {
            pattern_name = "9xRU26";
            ru_type = 26;
            max_slots = 9;
        } else if (num_clients >= 3) {
            pattern_name = "4xRU52";
            ru_type = 52;
            max_slots = 4;
        } else if (num_clients == 2) {
            pattern_name = "2xRU106";
            ru_type = 106;
            max_slots = 2;
        } else {
            pattern_name = "1xRU242";
            ru_type = 242;
            max_slots = 1;
        }

        const size_t active_count = std::min(num_clients, max_slots);
        size_t max_symbols = 0;

        for (size_t i = 0; i < active_count; ++i) {
            const double bits_per_sym = calculate_bits_per_symbol(ru_type, clients[i].mcs);
            const double total_bits = static_cast<double>(clients[i].buffer_bytes * 8);
            const size_t needed_syms = static_cast<size_t>(std::ceil(total_bits / bits_per_sym));
            max_symbols = std::max(max_symbols, needed_syms);
        }

        const double frame_duration_us = max_symbols * T_SYM_SEC * 1e6;
        std::vector<RUAllocation> allocations;
        allocations.reserve(active_count);

        for (size_t i = 0; i < active_count; ++i) {
            const double bits_per_sym = calculate_bits_per_symbol(ru_type, clients[i].mcs);
            const size_t capacity_bytes = static_cast<size_t>((max_symbols * bits_per_sym) / 8.0);
            const size_t allocated_bytes = std::min(clients[i].buffer_bytes, capacity_bytes);

            allocations.push_back(RUAllocation{
                .client_id = clients[i].client_id,
                .ru_type = ru_type,
                .allocated_bytes = allocated_bytes,
                .frame_duration_us = frame_duration_us
            });
        }

        return {pattern_name, allocations};
    }

private:
    int bandwidth_mhz_;
};

int main() {
    std::vector<ClientRequest> clients = {
        {.client_id = 1, .buffer_bytes = 120, .mcs = 7,  .latency_sensitive = true},
        {.client_id = 2, .buffer_bytes = 80,  .mcs = 9,  .latency_sensitive = true},
        {.client_id = 3, .buffer_bytes = 500, .mcs = 11, .latency_sensitive = false},
        {.client_id = 4, .buffer_bytes = 300, .mcs = 7,  .latency_sensitive = false}
    };

    Wifi6RuScheduler scheduler(20);
    auto [pattern, allocations] = scheduler.schedule_20mhz(clients);

    std::cout << "--- Результат планування Wi-Fi 6 OFDMA (Конфігурація: " << pattern << ") ---
";
    for (const auto& alloc : allocations) {
        std::cout << "Клієнт #" << alloc.client_id
                  << ": RU" << alloc.ru_type
                  << " | Передано: " << alloc.allocated_bytes << " байт"
                  << " | Тривалість кадру: " << alloc.frame_duration_us << " мкс
";
    }

    return 0;
}
```
:::

## 3. Простеження та відлагодження планувальника через Linux `ftrace`

При тестуванні та відлагодженні роботи планувальника Wi-Fi 6 у ядрі Linux інженери розробники використовують субсистему трасування ядра `ftrace` та трасувальні точки (Tracepoints) субсистеми `mac80211`.

### Ключові Tracepoints для відстеження OFDMA

Субсистема `mac80211` експортує наступні точки трасування:
- `mac80211:mac80211_tx_status`: Реєструє вихідний статус переданого кадру (успіх, retries, MCS).
- `mac80211:mac80211_he_ru_alloc`: Протоколює вибраний розклад RU, тип ресурсного блоку та ідентифікатор станції.
- `mac80211:mac80211_trigger_tx`: Відстежує факт відправки Trigger Frame у зворотній канал.

Для запису логу трасування з командного рядка використовується утиліта `trace-cmd`:

```bash
# 1. Ввімкнути запис трасувальних точок mac80211
sudo trace-cmd record -e mac80211:mac80211_he_ru_alloc -e mac80211:mac80211_trigger_tx

# 2. Перегляд сформованого звіту
sudo trace-cmd report | grep -E "(ru_alloc|trigger)"
```

Приклад рядка трасування з логу ядра:

```text
hostapd-1290 [002] 1245.892014: mac80211_he_ru_alloc: wlan0 sta 00:25:90:a1:b2:c3 RU_type 26 RU_index 3 MCS 7 NSS 1
```

Цей журнал підтверджує, що планувальник ядра успішно призначив станції `00:25:90:a1:b2:c3` ресурсний блок `RU26` під номером 3 із модуляцією `MCS 7`.

## 4. Практичні підводні камені та крайові випадки реального обладнання

При розробці мікропрограм (Firmware) та драйверів для радіочастотних мікросхем Wi-Fi 6 розробники зіштовхуються з низкою апаратних обмежень, які відсутні у теоретичних моделях:

### 1. Накладні витрати кадрів ініціалізації (Trigger Frame Overhead)
У зворотному каналі UL-OFDMA точка доступу повинна перед кожною передачею відправити управляючий кадр Trigger Frame (TF), вичекати пазу `SIFS = 16 мкс`, прийняти мультикористувацький кадр HE-TB PPDU, ще раз вичекати `SIFS` і відправити підтвердження Multi-STA BlockAck (M-BA).

Якщо корисне навантаження клієнтів дуже мале (наприклад, 20-30 байт), сумарна тривалість передачі службових кадрів TF + M-BA перевищує час передачі самих даних у 3-4 рази. У таких випадках розробники драйверів застосовують динамічний поріг (Aggregation Threshold), перемикаючись назад на звичайний монопольний доступ CSMA/CA для одиночних кадрів.

### 2. Взаємні завади між суміжними блоками (Inter-RU Interference, IRI)
Оскільки розбіжність генераторів частоти у мобільних пристроях може досягати кількох кілогерц, а динамічний діапазон сигналів від близького і віддаленого клієнта відрізняється на `30..40 дБ`, витікання потужності з одного RU в сусідній RU26 здатне повністю перекрити корисний сигнал.

Для захисту від цього ефекту апаратні аналогово-цифрові перетворювачі (АЦП) точки доступу вимагають застосування жорсткого алгоритму **Closed-Loop Power Control**. Точка доступу у кожному Trigger Frame передає значення `Target RSSI`, вимагаючи від близьких станцій знижувати потужність передавача.

### 3. Ресурсні блоки випадкового доступу (UORA)
Якщо всі доступні блоки RU у каналі віддано під строго призначені черги (Scheduled Access), станції, що тільки намагаються приєднатися до мережі або надіслати запит ресурсу (Buffer Status Report, BSR), потрапляють у глухий кут. Для запобігання цього драйвер повинен залишати принаймні один або два блоки RU26 для випадкового доступу на основі алгоритму UORA (OFDMA-based Random Access).
