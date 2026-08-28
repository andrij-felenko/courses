# ⚙️ Модуль моніторингу стільникового радіоканалу та стану соти

Цей проект демонструє реалізацію вбудованого модуля для циклічного опитування модему через UART, обробки URC-повідомлень (Unsolicited Result Codes), парсингу параметрів соти (`+CESQ`, `+CEREG`, `+COPS`) та відстеження зміни базової станції (Serving Cell) і стану радіозв'язку.

## Інженерні виклики та принципи побудови AT-драйвера

Взаємодія мікроконтролера зі стільниковим модемом через послідовний інтерфейс UART ускладнена кількома специфічними факторами:

1. **Асинхронна природа зв'язку:** модем може передати ініціативне повідомлення URC (наприклад, сповіщення про зміну соти `+CEREG` або втрату реєстрації) у будь-який момент часу, зокрема під час очікування відповіді на періодичний запит якості сигналу `AT+CESQ`. Якщо драйвер модему реалізовано як простий блокуючий автомат із жорстким очікуванням `OK`, такий URC зламає послідовність парсингу або призведе до помилкового розпізнавання таймауту.
2. **Нестабільність затримок (Jitter):** час відповіді модему варіюється від кількох мілісекунд (для локальних команд конфігурації `ATE0`) до кількох секунд або навіть хвилин (під час сканування радіоефіру `AT+COPS=?` або автентифікації в мережі). Блокування процесора в очікуванні відповіді неприпустиме для систем реального часу.
3. **Кільцевий буфер та переповнення:** швидкість передачі по UART (типово 115200 або 921600 біт/с) вимагає накопичення символів через кільцевий буфер переривань або DMA. Обробка повинна потоково шукати маркери кінця рядка `\r\n` і розбивати вхідний потік на атомарні текстові повідомлення.
4. **Апаратний контроль потоку (Hardware Flow Control):** використання ліній RTS/CTS є обов'язковим при активній передачі IP-даних, оскільки внутрішній буфер модему може швидко заповнюватися при погіршенні радіоканалу, і модем виставлятиме сигнал неготовності (CTS High) для призупинення відправки з боку хоста.

## Архітектура програмного модуля та скінченний автомат

Пропонована реалізація розбиває обробку стільникових даних на три чітко розділені рівні:

1. **Канальний рівень (Line Framing):** виділення цілісних текстових рядків із кільцевого буфера UART, очищення від службових символів `\r` та `\n`.
2. **Парсер протоколу AT:** зіставлення сигнатур команд (`+CESQ:`, `+CEREG:`, `+COPS:`, `OK`, `ERROR`), безпечне вилучення числових та шістнадцяткових полів без використання динамічного виділення пам'яті (`malloc`/`free`) і перерахунок квантованих індексів 3GPP у фізичні одиниці (dBm, dB).
3. **Менеджер стану мобільності (Mobility State Manager):** збереження поточної конфігурації радіозв'язку (Cell ID, TAC, RSRP, RSRQ, реєстрація), виявлення факту естафетної передачі (Handover) при зміні `Cell ID` та генерація подій для вищих рівнів програми.

### Послідовність ініціалізації та конфігурації модему

Перед початком циклічного збору метрик драйвер виконує стандартизовану послідовність ініціалізації:
* `ATE0`: вимикає відлуння (Echo) команд, що зменшує навантаження на UART і спрощує парсинг відповідей;
* `AT+CMEE=2`: вмикає докладні текстові повідомлення про помилки замість лаконічного `ERROR`;
* `AT+CEREG=2`: активує розширені асинхронні повідомлення URC, які автоматично надходять при кожному переході модему між сотами або зонами відстеження TAC;
* `AT+CESQ`: періодичне опитування (наприклад, кожні 1000 мс) для відстеження динаміки рівня RSRP та RSRQ.

### Простеження типової сесії та колізії з URC (Trace Analysis)

Розглянемо випадок, коли під час виконання періодичного опитування якості сигналу відбувається естафетне перемикання між секторами базової станції:
1. Керуючий контролер відправляє в UART команду `AT+CESQ\r\n`.
2. У цей самий момент фізичний рівень модему фіксує перехід на новий сектор і виводить у порт асинхронний рядок: `\r\n+CEREG: 1,"1A2F","05B2A02",7\r\n`.
3. Одразу за ним модем повертає результат вимірювання та код завершення: `\r\n+CESQ: 99,99,255,255,22,68\r\n\r\nOK\r\n`.

Завдяки розділенню на рівні рядків метод `processLine()` послідовно обробляє кожен блок:
* Перший рядок `+CEREG:` виявляє зміну `Cell ID` з `0x05B2A01` на `0x05B2A02`, оновлює поле `tac`, встановлює прапорець `handover_occurred` і генерує системне сповіщення про перехід на нову соту.
* Другий рядок `+CESQ:` оновлює метрики потужності: `RSRP = -140 + 68 = -72 dBm`, `RSRQ = -19.5 + 22 · 0.5 = -8.5 dB`.
* Рядок `OK` підтверджує успішне завершення поточної синхронної транзакції. Жодне повідомлення не губиться, а стан зв'язку залишається коректним.

### Обробка позаштатних ситуацій та перезапуск

Якщо модем не відповідає на AT-команди протягом трьох послідовних циклів опитування (таймаут 3 секунди на команду) або повертає статус відхилення реєстрації `+CEREG: 3`, драйвер застосовує ступеневу стратегію відновлення:
1. Скидання радіотракту за допомогою команди `AT+CFUN=0` з наступним увімкненням `AT+CFUN=1` через 2 секунди;
2. Якщо радіоперезапуск не відновив зв'язок — формування апаратного імпульсу скидання (Hardware Reset) тривалістю 150–500 мс на вивід `RESET_N` мікросхеми модему;
3. Очікування системного повідомлення готовності стека (`RDY` або `+CPIN: READY`);
4. Повторне виконання повної конфігураційної послідовності (`ATE0`, `AT+CMEE=2`, `AT+CEREG=2`).

### Порівняльний аналіз реалізацій C та C++

У реалізації мовою C використовується процедурний підхід із компактними структурами даних та статичними буферами без динамічного виділення пам'яті, що забезпечує пряму сумісність із мікроконтролерами на базі ARM Cortex-M0/M3/M4.

Реалізація мовою C++20 використовує парадигму інкапсуляції у клас `CellMonitor`. Замість небезпечних операцій над покажчиками застосовується `std::string_view` для безалокаційного парсингу рядків, строга типізація переліків `enum class` та швидкий парсер `std::from_chars`, що виключає накладні витрати стандартної бібліотеки C на обробку локалей.

:::tabs
@tab C
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdlib.h>

typedef enum {
    REG_NOT_REGISTERED = 0,
    REG_HOME           = 1,
    REG_SEARCHING      = 2,
    REG_DENIED         = 3,
    REG_UNKNOWN        = 4,
    REG_ROAMING        = 5
} cell_reg_status_t;

typedef enum {
    ACT_GSM    = 0,
    ACT_UTRAN  = 2,
    ACT_LTE    = 7,
    ACT_NR_5G  = 12
} cell_act_t;

typedef struct {
    bool valid;
    int16_t rsrp_dbm;     /* -140 .. -44 dBm, 0x7FFF = unknown */
    float   rsrq_db;      /* -19.5 .. -3.0 dB, NAN = unknown */
    uint32_t cell_id;     /* E-UTRAN Cell Identifier (28 bit) */
    uint16_t tac;         /* Tracking Area Code */
    cell_reg_status_t reg;
    cell_act_t act;
    char oper_name[32];
} cell_metrics_t;

typedef struct {
    cell_metrics_t current;
    uint32_t last_cell_id;
    bool handover_occurred;
} cell_monitor_t;

void cell_monitor_init(cell_monitor_t *mon) {
    if (!mon) return;
    memset(mon, 0, sizeof(*mon));
    mon->current.rsrp_dbm = -140;
    mon->current.rsrq_db = -20.0f;
    mon->current.reg = REG_NOT_REGISTERED;
}

bool cell_parse_cesq(const char *line, cell_metrics_t *out) {
    if (!line || !out) return false;
    const char *prefix = "+CESQ: ";
    const char *p = strstr(line, prefix);
    if (!p) return false;
    p += strlen(prefix);

    int rxlev, ber, rscp, ecno, rsrq_raw, rsrp_raw;
    if (sscanf(p, "%d,%d,%d,%d,%d,%d", 
               &rxlev, &ber, &rscp, &ecno, &rsrq_raw, &rsrp_raw) != 6) {
        return false;
    }

    if (rsrp_raw >= 0 && rsrp_raw <= 97) {
        out->rsrp_dbm = (int16_t)(-140 + rsrp_raw);
        out->valid = true;
    } else {
        out->rsrp_dbm = -140;
    }

    if (rsrq_raw >= 0 && rsrq_raw <= 34) {
        out->rsrq_db = -19.5f + (float)rsrq_raw * 0.5f;
    } else {
        out->rsrq_db = -20.0f;
    }

    return true;
}

bool cell_parse_cereg(const char *line, cell_metrics_t *out, cell_monitor_t *mon) {
    if (!line || !out) return false;
    const char *prefix = "+CEREG: ";
    const char *p = strstr(line, prefix);
    if (!p) return false;
    p += strlen(prefix);

    int n = 0, stat = 0, act = 7;
    char tac_str[16] = {0};
    char ci_str[16] = {0};

    int matched = sscanf(p, "%d,%d,\"%15[^\"]\",\"%15[^\"]\",%d", 
                         &n, &stat, tac_str, ci_str, &act);
    if (matched < 2) {
        matched = sscanf(p, "%d,\"%15[^\"]\",\"%15[^\"]\",%d", 
                         &stat, tac_str, ci_str, &act);
    }

    if (matched >= 1) {
        out->reg = (cell_reg_status_t)stat;
    }

    if (matched >= 3 && strlen(ci_str) > 0) {
        uint32_t new_ci = (uint32_t)strtoul(ci_str, NULL, 16);
        out->tac = (uint16_t)strtoul(tac_str, NULL, 16);
        out->act = (cell_act_t)act;

        if (mon && mon->last_cell_id != 0 && mon->last_cell_id != new_ci) {
            mon->handover_occurred = true;
        }
        out->cell_id = new_ci;
        if (mon) {
            mon->last_cell_id = new_ci;
        }
    }

    return true;
}

void cell_monitor_process_line(cell_monitor_t *mon, const char *line) {
    if (!mon || !line) return;

    if (cell_parse_cesq(line, &mon->current)) {
        printf("[METRICS] RSRP: %d dBm, RSRQ: %.1f dB\n", 
               mon->current.rsrp_dbm, mon->current.rsrq_db);
    } else if (cell_parse_cereg(line, &mon->current, mon)) {
        printf("[REG] Status: %d, TAC: 0x%04X, Cell ID: 0x%07X\n", 
               mon->current.reg, mon->current.tac, mon->current.cell_id);
        if (mon->handover_occurred) {
            printf("[EVENT] Handover detected! New Cell ID: 0x%07X\n", 
                   mon->current.cell_id);
            mon->handover_occurred = false;
        }
    }
}
```
@tab C++
```cpp
#include <iostream>
#include <string_view>
#include <optional>
#include <charconv>
#include <cstdint>
#include <vector>
#include <iomanip>

enum class RegStatus : uint8_t {
    NotRegistered = 0,
    Home          = 1,
    Searching     = 2,
    Denied        = 3,
    Unknown       = 4,
    Roaming       = 5
};

enum class AccessTech : uint8_t {
    Gsm    = 0,
    Utran  = 2,
    Eutran = 7,
    Nr5G   = 12
};

struct CellMetrics {
    bool valid{false};
    int16_t rsrp_dbm{-140};
    float rsrq_db{-20.0f};
    uint32_t cell_id{0};
    uint16_t tac{0};
    RegStatus reg{RegStatus::NotRegistered};
    AccessTech act{AccessTech::Eutran};
    std::string operator_name{};
};

class CellMonitor {
public:
    CellMonitor() = default;

    void processLine(std::string_view line) {
        if (line.starts_with("+CESQ: ")) {
            parseCesq(line.substr(7));
        } else if (line.starts_with("+CEREG: ")) {
            parseCereg(line.substr(8));
        } else if (line.starts_with("+COPS: ")) {
            parseCops(line.substr(7));
        }
    }

    [[nodiscard]] const CellMetrics& metrics() const noexcept { return metrics_; }
    [[nodiscard]] bool checkAndClearHandover() noexcept {
        const bool flag = handover_flag_;
        handover_flag_ = false;
        return flag;
    }

private:
    CellMetrics metrics_{};
    uint32_t previous_cell_id_{0};
    bool handover_flag_{false};

    static std::vector<std::string_view> split(std::string_view s, char delim) {
        std::vector<std::string_view> tokens;
        size_t start = 0;
        while (start < s.size()) {
            const size_t end = s.find(delim, start);
            if (end == std::string_view::npos) {
                tokens.push_back(s.substr(start));
                break;
            }
            tokens.push_back(s.substr(start, end - start));
            start = end + 1;
        }
        return tokens;
    }

    void parseCesq(std::string_view payload) {
        const auto parts = split(payload, ',');
        if (parts.size() < 6) return;

        int rsrq_raw = 255;
        int rsrp_raw = 255;
        std::from_chars(parts[4].data(), parts[4].data() + parts[4].size(), rsrq_raw);
        std::from_chars(parts[5].data(), parts[5].data() + parts[5].size(), rsrp_raw);

        if (rsrp_raw >= 0 && rsrp_raw <= 97) {
            metrics_.rsrp_dbm = static_cast<int16_t>(-140 + rsrp_raw);
            metrics_.valid = true;
        }
        if (rsrq_raw >= 0 && rsrq_raw <= 34) {
            metrics_.rsrq_db = -19.5f + static_cast<float>(rsrq_raw) * 0.5f;
        }

        std::cout << "[METRICS] RSRP: " << metrics_.rsrp_dbm << " dBm, RSRQ: " 
                  << std::fixed << std::setprecision(1) << metrics_.rsrq_db << " dB\n";
    }

    void parseCereg(std::string_view payload) {
        const auto parts = split(payload, ',');
        if (parts.empty()) return;

        size_t idx = (parts.size() >= 4 && parts[0].size() == 1) ? 1 : 0;
        int stat_int = 0;
        std::from_chars(parts[idx].data(), parts[idx].data() + parts[idx].size(), stat_int);
        metrics_.reg = static_cast<RegStatus>(stat_int);

        if (parts.size() >= idx + 3) {
            auto clean_hex = [](std::string_view sv) -> std::string_view {
                if (sv.size() >= 2 && sv.front() == '"' && sv.back() == '"') {
                    return sv.substr(1, sv.size() - 2);
                }
                return sv;
            };

            const auto tac_sv = clean_hex(parts[idx + 1]);
            const auto ci_sv = clean_hex(parts[idx + 2]);

            uint32_t parsed_tac = 0;
            uint32_t parsed_ci = 0;
            std::from_chars(tac_sv.data(), tac_sv.data() + tac_sv.size(), parsed_tac, 16);
            std::from_chars(ci_sv.data(), ci_sv.data() + ci_sv.size(), parsed_ci, 16);

            metrics_.tac = static_cast<uint16_t>(parsed_tac);
            if (previous_cell_id_ != 0 && parsed_ci != 0 && parsed_ci != previous_cell_id_) {
                handover_flag_ = true;
                std::cout << "[EVENT] Handover detected: 0x" << std::hex << previous_cell_id_ 
                          << " -> 0x" << parsed_ci << std::dec << "\n";
            }
            metrics_.cell_id = parsed_ci;
            previous_cell_id_ = parsed_ci;
        }
    }

    void parseCops(std::string_view payload) {
        const auto parts = split(payload, ',');
        if (parts.size() >= 3) {
            std::string_view oper = parts[2];
            if (oper.size() >= 2 && oper.front() == '"' && oper.back() == '"') {
                oper = oper.substr(1, oper.size() - 2);
            }
            metrics_.operator_name = std::string(oper);
            std::cout << "[OPERATOR] Registered network: " << metrics_.operator_name << "\n";
        }
    }
};
```
:::
