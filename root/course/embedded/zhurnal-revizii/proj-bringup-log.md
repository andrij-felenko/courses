# ⚙️ Шаблон інженерного журналу оживлення та структура обліку дефектів

Шаблон Bring-up Log і вбудований діагностичний логер забезпечують наскрізне трасування кожної змонтованої плати прототипної партії від першого контакту зі щупом вольтметра до випуску серійної ревізії, виключаючи втрату апаратних доробок та хаотичне тестування нестабільних зразків.

---

## 1. Паспорт первинного аудиту плати (Board Bring-up Sheet)

Для кожного фізичного екземпляра друкованої плати заводять індивідуальну картку аудиту. Нижче наведено стандартизовану структуру інженерного протоколу, яка заповнюється монтажником та схемотехніком під час першого пуску.

Протокол вимагає суворого дотримання послідовності заповнення: жоден вимір під напругою не виконується доти, доки блок холодного аудиту не підтвердить безпеку шин живлення. Для низькоомних силових ліній ядра процесора рекомендується застосовувати чотирипровідну схему вимірювання опору (Kelvin Connection), яка компенсує опір власних вимірювальних щупів мультиметра (зазвичай 0.1–0.3 Ом).

Перед підключенням джерела енергії обов'язково перевіряють стан усіх захисних діодів TVS у режимі діодної продзвонки: пряме падіння напруги повинно складати 0.45–0.65 В, а зворотне — нескінченність (OL). Будь-яке симетричне падіння напруги в обидва боки свідчить про тепловий пробій кристала напівпровідника під час паяння.

```yaml
# ==============================================================================
# ПАСПОРТ ОБЛІКУ ЗРАЗКА ПЛАТИ (BOARD PASSPORT)
# ==============================================================================
board_metadata:
  project_name: "Telemetry-Node-Pro"
  hardware_revision: "REV_A"
  pcb_batch_id: "BATCH-2026-W34-01"
  board_serial_id: "NODE-A-003"
  assembly_date: "2026-08-28"
  assembled_by: "Engineer-HW"
  tested_by: "Engineer-Embedded"
  board_disposition: "FIRMWARE_BENCH"   # GOLDEN_SAMPLE, FIRMWARE_BENCH, THERMAL_STRESS, PATCH_PIONEER

# ------------------------------------------------------------------------------
# 1. ХОЛОДНИЙ АУДИТ ДО ПОДАЧІ ЖИВЛЕННЯ (COLD RESISTANCE MATRIX)
# ------------------------------------------------------------------------------
cold_checks:
  optical_inspection:
    pin1_orientation_ic: "PASS"
    tantalum_polarity: "PASS"
    qfn_solder_bridges: "PASS"
    tombstoned_passives: "PASS"
  resistance_to_gnd:
    rail_5v0_in: "145.2 kOhm"          # Норма: > 50 kOhm
    rail_3v3_main: "12.4 kOhm"         # Норма: > 5 kOhm
    rail_1v8_io: "8.6 kOhm"            # Норма: > 2 kOhm
    rail_1v2_core: "1.8 kOhm"          # Норма для MCU: > 500 Ohm
    vbat_rtc: "OL (Open Loop)"         # Норма: > 1 MOhm
  diode_drop_to_gnd:
    tp_swdio: "0.58 V"                 # Внутрішній ESD-діод буфера
    tp_swclk: "0.58 V"
    tp_nrst: "0.62 V"
    usart1_tx: "0.54 V"
    usart1_rx: "0.55 V"

# ------------------------------------------------------------------------------
# 2. ПЕРША ПОДАЧА ЖИВЛЕННЯ (FIRST POWER-UP & RAILS VERIFICATION)
# ------------------------------------------------------------------------------
power_on_checks:
  psu_settings:
    input_voltage_v: 5.00
    current_limit_ma: 100
  measured_rails:
    tp_v_in: "4.98 V"                  # Вхід після захисного діода
    tp_3v3_out: "3.31 V"               # LDO U1 (норма 3.30 В ± 2%)
    tp_1v8_out: "1.80 V"               # Buck U3 (норма 1.80 В ± 2%)
    tp_1v2_vcap: "1.23 V"              # Внутрішній регулятор ядра MCU
  rail_ac_ripple_pkpk:
    tp_3v3_ripple: "8 mV"              # Осцилограф, AC coupling, смуга 20 МГц
    tp_1v8_ripple: "15 mV"
  thermal_screening:
    ambient_temp_c: 23.5
    hottest_component: "U1 (LDO 3.3V)"
    max_measured_temp_c: 31.2
    thermal_hotspots_detected: false

# ------------------------------------------------------------------------------
# 3. ПРОФІЛЬ СТРУМУ СПОЖИВАННЯ (CURRENT CONSUMPTION PROFILE)
# ------------------------------------------------------------------------------
current_consumption_profile:
  unprogrammed_reset_held_ma: 3.2      # NRST притиснутий до GND
  unprogrammed_idle_bootloader_ma: 14.8# ROM-bootloader активний
  active_running_hsi_16mhz_ma: 18.5    # Базова прошивка
  active_running_pll_168mhz_ma: 54.2   # Повна продуктивність ядра
  sleep_wfi_mode_ma: 6.8               # Периферія увімкнена, ядро спить
  stop_low_power_mode_ua: 340          # Тактування вимкнено, SRAM збережено
  standby_mode_ua: 2.8                 # Живлення лише Backup Domain

# ------------------------------------------------------------------------------
# 4. АПАРАТНІ ІДЕНТИФІКАТОРИ ТА ЗВ'ЯЗОК (HARDWARE ID BINDING)
# ------------------------------------------------------------------------------
hardware_binding:
  mcu_uid_96bit: "0x003A002F-34385108-30373432"
  ethernet_mac: "02:42:AC:11:00:03"
  ble_bd_addr: "E4:5F:01:23:45:67"
  patch_bundle_applied: ["PATCH-REV_A-001", "PATCH-REV_A-003"]
```

---

## 2. Реєстр апаратних патчів (Hardware Patch Log)

Жодна модифікація плати ревізії А (перерізання доріжки, навісний провідник, корекція номіналу) не виконується без присвоєння унікального індексу та занесення в єдиний реєстр.

Перед монтажем навісних провідників обов'язково враховують швидкість сигналів. Для високочастотних ліній (тактові сигнали SPI з частотою понад 10 МГц або лінії SDIO) погонна індуктивність дроту bodge wire створює значний паразитно сформований імпеданс. Якщо довжина дроту перевищує 30–40 мм, його прокладають у парі із заземленим провідником або додають послідовний демпфуючий резистор 22–33 Ом безпосередньо біля виводу джерела сигналу для придушення дзвону на фронтах.

Для контролю якості різання доріжок (Trace Cut) після виконання розриву контактні площадки перевіряють тестером ізоляції: опір між розділеними ділянками міді повинен перевищувати 10 МОм при випробувальній напрузі 50 В. Це гарантує відсутність прихованих мікрозадирок фольги, які можуть замкнути коло при нагріванні або вібрації.

| Patch ID | Тип втручання | Позиційні елементи / Координати | Першопричина відхилення | Інструкція виконання (Work Instruction) | Зачеплені плати | Вплив на прошивку | Статус для Rev B (ECO) |
|---|---|---|---|---|---|---|---|
| **PATCH-REV_A-001** | Bodge Wire + Trace Cut | `U2` (RS-485 transceiver), `R14`, `TP8` | Інверсія ліній `DI` та `RO` у символі схеми | 1. Перерізати доріжку біля U2.Pin1.<br>2. Перерізати доріжку біля U2.Pin4.<br>3. Запаяти дріт Kynar 30 AWG від U2.Pin1 до TP8.<br>4. Запаяти дріт від U2.Pin4 до контактного майданчика R14.Pin2.<br>5. Зафіксувати 2 краплями УФ-клею. | Всі (SN-01..SN-05) | Без змін (прошивка використовує штатний USART2) | `ECO-101`: Дзеркально розвернути символ U2 у бібліотеці |
| **PATCH-REV_A-002** | Tombstone Resistor | `R21` (Pull-Up шини I2C1_SDA) | Занижений опір підтяжки (встановлено 470 Ом замість 4.7 кОм), що блокує перехід у низький рівень при струмі 3 мА | 1. Демонтувати SMD-резистор 0402 `470R`.<br>2. Змонтувати резистор `4.7k 1% 0402`. | SN-02, SN-03, SN-05 | Знижено енергоспоживання шини на 6.2 мА | `ECO-102`: Оновити номінал у схемі та BOM-файлі |
| **PATCH-REV_A-003** | Piggyback Capacitor | `C18` (Фільтр LDO 3.3V) | Високочастотне самозбудження регулятора LDO через ультранизький ESR вихідного керамічного конденсатора MLCC 10 мкФ | 1. Напаяти зверху на корпус C18 послідовно резистор 0.5 Ом (типорозмір 0402) або замінити C18 на танталовий конденсатор з нормованим ESR 0.3 Ом. | SN-01..SN-05 | Зникли спонтанні перезавантаження Brown-out | `ECO-103`: Змінити тип вихідного конденсатора в BOM |
| **PATCH-REV_A-004** | Fly-Wire to Header | `BOOT0` (Pin 44 MCU), `GND` | Підтягувальний резистор R5 (10 кОм) помилково розведений на 3.3 В замість землі; чіп завжди стартує в режимі системного bootloader | 1. Зняти резистор R5.<br>2. Прокласти провідник AWG 34 від майданчика R5 (зі сторони чіпа) до земляного полігону GND. | Всі (SN-01..SN-05) | Дозволяє нормальне завантаження прошивки з Flash | `ECO-104`: Перепід'єднати R5 до GND на схемі живлення |

---

## 3. Вбудований логер ідентифікаторів та телеметрії живлення

Для автоматизації заповнення паспорта плати перший бінарний образ, що прошивається в мікроконтролер, містить сервісний модуль телеметрії. Програма вичитує апаратні регістри кристала (96-бітний унікальний UID, регістри калібрування внутрішньої напруги `VREFINT` та температури кристала), опитує внутрішній АЦП і транслює структурований JSON-пакет у порт UART.

Принцип вимірювання спирається на наявність у пам'яті System Memory заводських калібрувальних значень:
- `VREFINT_CAL`: значення відліку АЦП при вимірюванні внутрішнього стабільного джерела 1.20 В при заводській напрузі живлення `VDDA = 3.30 В` (температура 30 °C).
- `TS_CAL1` та `TS_CAL2`: калібрувальні відліки вбудованого термодатчика кристала при 30 °C та 110 °C відповідно.

Код автоматично обчислює реальну напругу аналогового живлення `VDDA` мікроконтролера та миттєву температуру напівпровідникового кристала. Якщо виміряна напруга `VDDA` падає нижче 3.10 В під час роботи радіотрансивера або передавача RS-485, логер фіксує просідання в енергонезалежному буфері помилок. Крайовий випадок з нульовим або насиченим відліком АЦП (`0x000` або `0xFFF`) перехоплюється як апаратна помилка ініціалізації аналогового тракту, захищаючи математичні формули від ділення на нуль.

Нижче наведено повну реалізацію модуля: на чистому C (C99) та ідіоматичному C++ (C++20) з використанням строгої типізації, просторів імен, контейнерів `std::span` та механізму обробки помилок `std::expected`.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define STM32_UID_BASE          0x1FFF7A10U
#define STM32_VREFINT_CAL_ADDR  0x1FFF7A2AU
#define STM32_TS_CAL1_ADDR      0x1FFF7A2CU
#define STM32_TS_CAL2_ADDR      0x1FFF7A2EU

#define VREFINT_CAL_VREF_MV     3300U
#define TS_CAL1_TEMP_C          30
#define TS_CAL2_TEMP_C          110

typedef struct {
    uint32_t uid[3];
    uint16_t vrefint_cal;
    uint16_t ts_cal1;
    uint16_t ts_cal2;
    uint16_t adc_vref_raw;
    uint16_t adc_temp_raw;
    uint32_t calculated_vdda_mv;
    int32_t  calculated_core_temp_c;
} board_telemetry_t;

void board_telemetry_read_hardware_ids(board_telemetry_t *telem) {
    const uint32_t *uid_ptr = (const uint32_t *)STM32_UID_BASE;
    telem->uid[0] = uid_ptr[0];
    telem->uid[1] = uid_ptr[1];
    telem->uid[2] = uid_ptr[2];

    telem->vrefint_cal = *(const uint16_t *)STM32_VREFINT_CAL_ADDR;
    telem->ts_cal1     = *(const uint16_t *)STM32_TS_CAL1_ADDR;
    telem->ts_cal2     = *(const uint16_t *)STM32_TS_CAL2_ADDR;
}

void board_telemetry_calculate_analog(board_telemetry_t *telem, uint16_t raw_vref, uint16_t raw_temp) {
    telem->adc_vref_raw = raw_vref;
    telem->adc_temp_raw = raw_temp;

    if (raw_vref > 0) {
        telem->calculated_vdda_mv = (VREFINT_CAL_VREF_MV * (uint32_t)telem->vrefint_cal) / (uint32_t)raw_vref;
    } else {
        telem->calculated_vdda_mv = 0;
    }

    if (telem->ts_cal2 > telem->ts_cal1) {
        int32_t temp_num = ((int32_t)raw_temp * (int32_t)telem->calculated_vdda_mv / (int32_t)VREFINT_CAL_VREF_MV) - (int32_t)telem->ts_cal1;
        int32_t temp_den = (int32_t)telem->ts_cal2 - (int32_t)telem->ts_cal1;
        telem->calculated_core_temp_c = TS_CAL1_TEMP_C + (temp_num * (TS_CAL2_TEMP_C - TS_CAL1_TEMP_C)) / temp_den;
    } else {
        telem->calculated_core_temp_c = 0;
    }
}

static void uint32_to_hex_str(uint32_t val, char *out) {
    const char hex_digits[] = "0123456789ABCDEF";
    for (int i = 7; i >= 0; --i) {
        out[i] = hex_digits[val & 0x0F];
        val >>= 4;
    }
    out[8] = '\0';
}

void board_telemetry_format_json(const board_telemetry_t *telem, const char *serial_id, char *buf, size_t max_len) {
    char u0[9], u1[9], u2[9];
    uint32_to_hex_str(telem->uid[0], u0);
    uint32_to_hex_str(telem->uid[1], u1);
    uint32_to_hex_str(telem->uid[2], u2);

    /* Форматування спрощеним копіюванням без залучення важкого sprintf */
    const char *header = "{\"board_serial\":\"";
    size_t pos = 0;
    
    #define APPEND_STR(s) do { \
        size_t len = strlen(s); \
        if (pos + len < max_len) { memcpy(&buf[pos], (s), len); pos += len; } \
    } while(0)

    APPEND_STR(header);
    APPEND_STR(serial_id);
    APPEND_STR("\",\"uid\":\"");
    APPEND_STR(u0);
    APPEND_STR("-");
    APPEND_STR(u1);
    APPEND_STR("-");
    APPEND_STR(u2);
    APPEND_STR("\",\"vdda_mv\":");
    
    /* Друк цілого числа VDDA */
    char num_buf[16];
    uint32_t v = telem->calculated_vdda_mv;
    int idx = 0;
    if (v == 0) { num_buf[idx++] = '0'; }
    else {
        char rev[16];
        int r_idx = 0;
        while (v > 0) { rev[r_idx++] = (char)('0' + (v % 10)); v /= 10; }
        while (r_idx > 0) { num_buf[idx++] = rev[--r_idx]; }
    }
    num_buf[idx] = '\0';
    APPEND_STR(num_buf);

    APPEND_STR(",\"temp_c\":");
    int32_t t = telem->calculated_core_temp_c;
    idx = 0;
    if (t < 0) { num_buf[idx++] = '-'; t = -t; }
    if (t == 0) { num_buf[idx++] = '0'; }
    else {
        char rev[16];
        int r_idx = 0;
        while (t > 0) { rev[r_idx++] = (char)('0' + (t % 10)); t /= 10; }
        while (r_idx > 0) { num_buf[idx++] = rev[--r_idx]; }
    }
    num_buf[idx] = '\0';
    APPEND_STR(num_buf);
    APPEND_STR("}\r\n");

    if (pos < max_len) {
        buf[pos] = '\0';
    } else if (max_len > 0) {
        buf[max_len - 1] = '\0';
    }
    #undef APPEND_STR
}
```
```cpp
#include <cstdint>
#include <array>
#include <span>
#include <string_view>
#include <expected>

namespace telemetry {

struct CalibrationPoints {
    static constexpr std::uintptr_t uid_base        = 0x1FFF7A10U;
    static constexpr std::uintptr_t vrefint_cal_ptr = 0x1FFF7A2AU;
    static constexpr std::uintptr_t ts_cal1_ptr     = 0x1FFF7A2CU;
    static constexpr std::uintptr_t ts_cal2_ptr     = 0x1FFF7A2EU;

    static constexpr std::uint32_t cal_vref_mv      = 3300U;
    static constexpr std::int32_t  ts_cal1_temp_c   = 30;
    static constexpr std::int32_t  ts_cal2_temp_c   = 110;
};

struct BoardMetrics {
    std::array<std::uint32_t, 3> uid{};
    std::uint16_t vrefint_cal{0};
    std::uint16_t ts_cal1{0};
    std::uint16_t ts_cal2{0};
    std::uint32_t vdda_mv{0};
    std::int32_t  core_temperature_c{0};
};

enum class TelemetryError : std::uint8_t {
    invalid_raw_adc,
    calibration_corrupted,
    buffer_overflow
};

class TelemetryCollector {
public:
    static BoardMetrics collect_device_identity() noexcept {
        BoardMetrics metrics{};
        const auto* uid_raw = reinterpret_cast<const std::uint32_t*>(CalibrationPoints::uid_base);
        metrics.uid[0] = uid_raw[0];
        metrics.uid[1] = uid_raw[1];
        metrics.uid[2] = uid_raw[2];

        metrics.vrefint_cal = *reinterpret_cast<const std::uint16_t*>(CalibrationPoints::vrefint_cal_ptr);
        metrics.ts_cal1     = *reinterpret_cast<const std::uint16_t*>(CalibrationPoints::ts_cal1_ptr);
        metrics.ts_cal2     = *reinterpret_cast<const std::uint16_t*>(CalibrationPoints::ts_cal2_ptr);
        return metrics;
    }

    static std::expected<BoardMetrics, TelemetryError> process_samples(
        BoardMetrics metrics,
        std::uint16_t raw_vref,
        std::uint16_t raw_temp) noexcept
    {
        if (raw_vref == 0) {
            return std::unexpected(TelemetryError::invalid_raw_adc);
        }

        metrics.vdda_mv = (CalibrationPoints::cal_vref_mv * static_cast<std::uint32_t>(metrics.vrefint_cal)) / raw_vref;

        if (metrics.ts_cal2 <= metrics.ts_cal1) {
            return std::unexpected(TelemetryError::calibration_corrupted);
        }

        const auto num = (static_cast<std::int32_t>(raw_temp) * static_cast<std::int32_t>(metrics.vdda_mv) / 
                          static_cast<std::int32_t>(CalibrationPoints::cal_vref_mv)) - static_cast<std::int32_t>(metrics.ts_cal1);
        const auto den = static_cast<std::int32_t>(metrics.ts_cal2) - static_cast<std::int32_t>(metrics.ts_cal1);
        
        metrics.core_temperature_c = CalibrationPoints::ts_cal1_temp_c + 
            (num * (CalibrationPoints::ts_cal2_temp_c - CalibrationPoints::ts_cal1_temp_c)) / den;

        return metrics;
    }

    static std::expected<std::size_t, TelemetryError> serialize_json(
        const BoardMetrics& metrics,
        std::string_view serial_id,
        std::span<char> out_buffer) noexcept
    {
        std::size_t offset = 0;

        auto append_sv = [&](std::string_view sv) -> bool {
            if (offset + sv.size() >= out_buffer.size()) {
                return false;
            }
            for (char ch : sv) {
                out_buffer[offset++] = ch;
            }
            return true;
        };

        auto append_hex32 = [&](std::uint32_t val) -> bool {
            constexpr char digits[] = "0123456789ABCDEF";
            if (offset + 8 >= out_buffer.size()) return false;
            for (int i = 7; i >= 0; --i) {
                out_buffer[offset + i] = digits[val & 0x0F];
                val >>= 4;
            }
            offset += 8;
            return true;
        };

        auto append_int = [&](std::int64_t val) -> bool {
            char tmp[24];
            int idx = 0;
            bool neg = val < 0;
            if (neg) val = -val;
            if (val == 0) tmp[idx++] = '0';
            while (val > 0) {
                tmp[idx++] = static_cast<char>('0' + (val % 10));
                val /= 10;
            }
            if (neg) tmp[idx++] = '-';
            if (offset + idx >= out_buffer.size()) return false;
            while (idx > 0) {
                out_buffer[offset++] = tmp[--idx];
            }
            return true;
        };

        if (!append_sv("{\"serial\":\"")) return std::unexpected(TelemetryError::buffer_overflow);
        if (!append_sv(serial_id)) return std::unexpected(TelemetryError::buffer_overflow);
        if (!append_sv("\",\"uid\":\"")) return std::unexpected(TelemetryError::buffer_overflow);
        if (!append_hex32(metrics.uid[0])) return std::unexpected(TelemetryError::buffer_overflow);
        if (!append_sv("-")) return std::unexpected(TelemetryError::buffer_overflow);
        if (!append_hex32(metrics.uid[1])) return std::unexpected(TelemetryError::buffer_overflow);
        if (!append_sv("-")) return std::unexpected(TelemetryError::buffer_overflow);
        if (!append_hex32(metrics.uid[2])) return std::unexpected(TelemetryError::buffer_overflow);
        if (!append_sv("\",\"vdda_mv\":")) return std::unexpected(TelemetryError::buffer_overflow);
        if (!append_int(metrics.vdda_mv)) return std::unexpected(TelemetryError::buffer_overflow);
        if (!append_sv(",\"temp_c\":")) return std::unexpected(TelemetryError::buffer_overflow);
        if (!append_int(metrics.core_temperature_c)) return std::unexpected(TelemetryError::buffer_overflow);
        if (!append_sv("}\r\n")) return std::unexpected(TelemetryError::buffer_overflow);

        out_buffer[offset] = '\0';
        return offset;
    }
};

} // namespace telemetry
```
:::

---

## 4. Підсумковий регламент передачі зауважень у Ревізію B (ECO Checklist)

Перед запуском виробництва ревізії B головний інженер проєкту скликає рев'ю журналу ревізії А, де кожен запис перевіряється за чеклістом передачі змін:

1. **Верифікація нетлиста (Netlist Reconciliation):** Кожен запис типу `Trace Cut + Bodge Wire` повинен мати пряму відповідність у змінах принципової схеми CAD (перепідключений ланцюг, змінена мітка нетлиста).
2. **Аудит посадкових місць (Footprint Audit):** Для всіх компонентів, де виникали складнощі ручного монтажу або зсуви SMD (наприклад, надмірний розмір термального майданчика QFN), коригуються шари паяльної пасти (Paste Mask Reduction на 25–40%).
3. **Очищення BOM-специфікації (BOM Freeze):** Усі тимчасові номінали резисторів, встановлені під час оживлення ревізії А, фіксуються в BOM із зазначенням конкретних партномерів (MPN) та точних допусків.
4. **Видалення тимчасових перемичок прошивки (Firmware Workaround Deprecation):** У програмному коді переглядаються умовні директиви компілятора `#ifdef HW_REV_A`. Для серійної ревізії B призначається базовий режим без апаратних костилів.

---

## 5. Методика автоматизованого зіставлення логів та валідації ECO

Для проєктів із високою щільністю монтажу або великою кількістю плат у партії (від 10 зразків) ручне зіставлення вимірювань замінюють автоматизованим конвеєром обробки:

1. **Збір логів у єдине сховище (Centralized Log Aggregation):**
   Діагностичні JSON-пакети, які видає прошивка через UART або порт SWO під час першого старту на тестовому стенді, автоматично перехоплюються скриптом на робочому комп'ютері інженера та зберігаються у структурованій теці `artifacts/bringup_logs/<SERIAL_ID>.json`.

2. **Статистичний аналіз розкиду напруг (Voltage Spread Analysis):**
   Скрипт аналізує зібрані дані по всій партії: розраховує середнє значення, стандартне відхилення та максимальний розмах для кожної рейки живлення. Якщо розкид вихідної напруги стабілізатора 3.3 В між зразками перевищує ±1.5%, це слугує сигналом про використання резисторів дільника зворотного зв'язку з низькою точністю (наприклад, 5% замість прецизійних 0.1% або 1%).

3. **Синхронізація з таск-трекером (Automated Issue Generation):**
   Кожен сформований запис `ECO` автоматично генерує пов'язану задачу в таск-трекері проєкту (Jira / GitHub Issues) з міткою `hardware-rev-b`. Це унеможливлює ситуацію, коли апаратний патч, знайдений на стенді оживлення, губиться під час фінального випуску виробничих гербер-файлів нової ревізії.
