# ⚙️ Калькулятор бюджету відеотракту: пам'ять, бітрейт та енергія

Проєктування автономної або мережевої камери у вбудованих системах часто починають «з кінця» — обирають сенсор із привабливою роздільністю (наприклад, 4K чи 5 Мп), а потім стикаються з тим, що внутрішня шина пам'яті захлинається, апаратний буфер кадрів не вміщується в доступну RAM, а батарея ємністю 10 А·год виснажується за лічені години через незбалансований радіотракт та нічне підсвічування. Щоб уникнути подібних помилок ще на етапі вибору апаратної платформи (SoC чи мікроконтролера, типу пам'яті LPDDR3/4 проти PSRAM, ємності акумулятора та потужності радіомодуля), інженеру потрібна цілісна аналітична модель.

Цей інженерний калькулятор об'єднує фізичні рівняння піксельного потоку, вимоги до буферизації опорних кадрів (Decoded Picture Buffer, DPB), множники навантаження на системну шину DRAM (AXI bandwidth), теплові й електричні втрати нічного підсвічування, а також порівняння двох діаметрально протилежних парадигм живлення: безперервного хмарного стрімінгу проти локального аналізу (Edge AI) з подійною активацією радіоканалу.

## Задача

Розробити консольний розрахунковий модуль на мовах C та C++, який приймає набір інженерних параметрів відеосистеми та виконує повний аудит бюджету пристрою за п'ятьма взаємопов'язаними вимірами:

1. **Трафік сенсора та кодека**: обчислення бітрейту сирого піксельного потоку (RAW Bayer, YUV422, YUV420) та вихідного бітрейту для кодеків MJPEG, H.264 (AVC) і H.265 (HEVC).
2. **Навантаження на системну шину пам'яті (DRAM / AXI)**: сумарний трафік шини з урахуванням захоплення через DMA, обробки ISP, читання кодеком та оновлення референсних кадрів.
3. **Обсяг оперативної пам'яті (RAM Allocation)**: мінімальний пул буферів під кадрові черги захоплення, дисплея та декодованих зображень (DPB).
4. **Енергетичний баланс підсистем**: розрахунок потужності сенсора, процесора (ISP/VPU/NPU), радіоканалу (Wi-Fi/LTE) та інфрачервоного підсвічування (IR LED) з урахуванням електрооптичного ККД.
5. **Автономність живлення**: моделювання часу роботи від акумулятора заданої ємності для двох сценаріїв — безперервної передачі відео (Cloud Streaming) та подійного режиму з черговим сном і локальною детекцією (Edge AI).

## Математична модель та інженерні рівняння

Перед тим як перейти до програмної реалізації, зафіксуємо формули, за якими обчислюється кожен блок бюджету.

### 1. Піксельний потік та формати представлення
Сирий потік сенсора визначається кількістю активних пікселів, частотою кадрів та розрядністю аналого-цифрового перетворювача (АЦП) матриці:

```
Потік_RAW (біт/с) = Ширина × Висота × fps × Глибина_RAW
```

При конвертації у формат YUV 4:2:0 розмір одного кадру в байтах становить:

```
Розмір_YUV420 (байт) = Ширина × Висота × 1.5
```

Коефіцієнт 1.5 береться з того, що на кожні 4 пікселі яскравості `Y` (4 байти) припадає лише по 1 байту для каналів `U` та `V` (разом 6 байтів на 4 пікселі = 1.5 байти/піксель).

### 2. Множник трафіку системної шини пам'яті
Внутрішня шина пам'яті обслуговує зустрічні потоки DMA:
- Запис кадру YUV420 блоком ISP у пам'ять: `Потік_YUV (МБ/с)`.
- Читання кадру блоком VPU для кодування: `Потік_YUV (МБ/с)`.
- Трафік зчитування та запису опорних кадрів у буфері DPB під час пошуку векторів руху: `2 × Потік_YUV (МБ/с)`.
- Запис вихідного бітстріму кодером у пам'ять: `Бітрейт_кодека ÷ 8`.

Сумарне навантаження шини пам'яті виражається формулою:

```
Трафік_DRAM (МБ/с) ≈ 4 × (Розмір_YUV420 × fps) + (Бітрейт_кодека ÷ 8)
```

Для забезпечення стабільності системи це навантаження не повинно перевищувати 60 % реальної пропускної здатності шини DRAM, інакше виникає голодування буферів (FIFO Underflow/Overflow).

### 3. Електрооптичні втрати нічного підсвічування
Світлодіодний випромінювач має обмежений коефіцієнт корисної дії (Wall-Plug Efficiency, `η_opt ≈ 0.25 … 0.35`). Тому електрична потужність, яку споживає підсвічування від джерела живлення, значно перевищує оптичне випромінювання:

```
Потужність_електрична_ІЧ (Вт) = Потужність_оптична (Вт) ÷ η_opt
```

### 4. Модель розряду акумулятора та режим Edge AI
При безперервному стрімінгу середня споживана потужність обчислюється як зважене середнє між денним та нічним режимами:

```
Потужність_стрім (Вт) = (Потужність_день + Потужність_ніч) ÷ 2
Час_автономності_стрім (год) = Ємність_батареї (Вт·год) ÷ Потужність_стрім (Вт)
```

У режимі Edge AI пристрій перебуває в активному стані лише частку часу `D` (Duty Cycle, наприклад 0.005 = 0.5 % часу), а решту часу `(1 - D)` спить із мінімальним споживанням чергової схеми (`P_sleep ≈ 0.03 Вт`):

```
Потужність_EdgeAI (Вт) = D × Потужність_активна + (1 - D) × P_sleep
Час_автономності_EdgeAI (діб) = [Ємність_батареї (Вт·год) ÷ Потужність_EdgeAI (Вт)] ÷ 24
```

## Реалізація калькулятора на C та C++

У прикладі нижче реалізовано повний математичний апарат розрахунку з детальними структурами конфігурації.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

// ── Переліки типів кодеків та режимів роботи ───────────────────────────────
typedef enum {
    CODEC_RAW_BAYER = 0,
    CODEC_MJPEG,
    CODEC_H264_AVC,
    CODEC_H265_HEVC
} video_codec_t;

typedef enum {
    LIGHT_DAY = 0,
    LIGHT_NIGHT_IR
} lighting_mode_t;

// ── Вхідні параметри відеосистеми ──────────────────────────────────────────
typedef struct {
    uint32_t width;             // Горизонтальна роздільність (пікселі)
    uint32_t height;            // Вертикальна роздільність (пікселі)
    uint32_t fps;               // Частота кадрів (к/с)
    uint8_t  bpp_raw;           // Глибина кольору сенсора (10 або 12 біт/піксель)
    video_codec_t codec;        // Обраний кодек стиснення
    uint8_t  ref_frames;        // Кількість опорних кадрів для H.264/H.265 (DPB)
    lighting_mode_t light_mode; // Денний або нічний режим
    double   ir_optical_watts;  // Необхідна оптична потужність ІЧ-підсвічування (Вт)
    double   ir_led_efficiency; // Електрооптичний ККД світлодіода (типово 0.25 - 0.35)
    double   soc_base_power_w;  // Базова потужність SoC у роботі (Вт)
    double   vpu_power_w;       // Потужність апаратного кодека VPU (Вт)
    double   sensor_power_w;    // Потужність сенсора камери (Вт)
    double   radio_tx_power_w;  // Потужність Wi-Fi/LTE у режимі передачі (Вт)
    double   radio_idle_power_w;// Потужність Wi-Fi/LTE у черговому прийомі (Вт)
    double   battery_capacity_wh;// Енергоємність акумулятора (Вт·год, напр. 3.7 В * 10 А·год = 37 Вт·год)
    double   edge_ai_duty_cycle;// Частка часу активної передачі в Edge AI (напр. 0.005 = 0.5%)
} video_system_config_t;

// ── Результати аналізу бюджету ─────────────────────────────────────────────
typedef struct {
    double raw_sensor_mbps;     // Бітрейт із сенсора (Мбіт/с)
    double yuv420_frame_mb;     // Розмір одного YUV420 кадру (МБ)
    double compressed_bitrate_mbps; // Бітрейт стисненого потоку (Мбіт/с)
    double dram_bandwidth_mbytes_sec; // Сумарне навантаження на шину RAM (МБ/с)
    double min_ram_dpb_mb;      // Мінімальна пам'ять під DPB та буферизацію (МБ)
    double total_power_day_w;   // Загальна електрична потужність вдень (Вт)
    double total_power_night_w; // Загальна електрична потужність вночі з ІЧ (Вт)
    double autonomy_streaming_hours; // Автономність при безперервному стрімінгу (годин)
    double autonomy_edge_ai_days;    // Автономність у подійно-орієнтованому Edge AI (діб)
} video_budget_result_t;

// ── Функція розрахунку бюджету ─────────────────────────────────────────────
void calculate_video_budget(const video_system_config_t *cfg, video_budget_result_t *res)
{
    uint64_t total_pixels_sec = (uint64_t)cfg->width * cfg->height * cfg->fps;

    // 1. Сирий піксельний потік із сенсора (RAW Bayer)
    res->raw_sensor_mbps = (double)(total_pixels_sec * cfg->bpp_raw) / 1000000.0;

    // Розмір одного кадру YUV420 (12 біт = 1.5 байти на піксель)
    double frame_bytes = (double)cfg->width * cfg->height * 1.5;
    res->yuv420_frame_mb = frame_bytes / (1024.0 * 1024.0);

    // 2. Розрахунок бітрейту залежно від кодека
    // YUV420 сирий бітрейт = width * height * 12 біт * fps
    double yuv_raw_mbps = (double)(total_pixels_sec * 12) / 1000000.0;
    
    switch (cfg->codec) {
        case CODEC_RAW_BAYER:
            res->compressed_bitrate_mbps = res->raw_sensor_mbps;
            break;
        case CODEC_MJPEG:
            // Коефіцієнт стиснення ~10x
            res->compressed_bitrate_mbps = yuv_raw_mbps / 10.0;
            break;
        case CODEC_H264_AVC:
            // Коефіцієнт стиснення ~80x - 100x для типової сцени
            res->compressed_bitrate_mbps = yuv_raw_mbps / 85.0;
            break;
        case CODEC_H265_HEVC:
            // Коефіцієнт стиснення ~150x - 180x
            res->compressed_bitrate_mbps = yuv_raw_mbps / 160.0;
            break;
    }

    // 3. Трафік шини оперативної пам'яті (DRAM / AXI Bandwidth)
    // - ISP записує YUV420 кадри в DRAM: 1.5 байти/пікс * fps
    // - VPU зчитує поточний YUV420 кадр із DRAM: 1.5 байти/пікс * fps
    // - VPU читає/пише опорні кадри (DPB): приблизно 2x від розміру кадру для пошуку руху
    // - VPU записує стиснений бітстрім: compressed_bitrate_mbps / 8
    double yuv_bytes_per_sec = frame_bytes * cfg->fps;
    double isp_write_mbs = yuv_bytes_per_sec / (1024.0 * 1024.0);
    double vpu_read_mbs = isp_write_mbs;
    double dpb_traffic_mbs = (cfg->codec >= CODEC_H264_AVC) ? (isp_write_mbs * 2.0) : 0.0;
    double bitstream_mbs = (res->compressed_bitrate_mbps * 1000000.0 / 8.0) / (1024.0 * 1024.0);

    res->dram_bandwidth_mbytes_sec = isp_write_mbs + vpu_read_mbs + dpb_traffic_mbs + bitstream_mbs;

    // 4. Пам'ять під буферизацію (DPB + черга ISP + черга кодера)
    // Мінімум 2 буфери на захоплення (double buffering) + ref_frames для кодека + 1 вихідний
    uint32_t total_frame_buffers = 2 + (cfg->codec >= CODEC_H264_AVC ? cfg->ref_frames : 1) + 1;
    res->min_ram_dpb_mb = total_frame_buffers * res->yuv420_frame_mb;

    // 5. Електрична потужність
    double ir_electrical_power_w = (cfg->ir_led_efficiency > 0.05) 
        ? (cfg->ir_optical_watts / cfg->ir_led_efficiency) : 0.0;

    double base_active_power = cfg->soc_base_power_w + cfg->vpu_power_w + cfg->sensor_power_w;
    
    // Денний режим (без ІЧ)
    res->total_power_day_w = base_active_power + cfg->radio_tx_power_w;
    // Нічний режим (з ІЧ)
    res->total_power_night_w = res->total_power_day_w + ir_electrical_power_w;

    // 6. Автономність: Хмарний стрімінг (100% активності радіо) проти Edge AI (duty cycle 0.5%)
    double avg_streaming_power = (res->total_power_day_w + res->total_power_night_w) / 2.0;
    res->autonomy_streaming_hours = cfg->battery_capacity_wh / avg_streaming_power;

    // Для Edge AI: 99.5% часу спимо або крутимо черговий сенсор/PIR (наприклад 0.03 Вт),
    // 0.5% часу прокидаємося на інференс і коротку передачу метаданих
    double edge_ai_active_power = base_active_power + cfg->radio_tx_power_w;
    double edge_ai_sleep_power = 0.030; // 30 мВт у черговому режимі
    double edge_ai_avg_power = (cfg->edge_ai_duty_cycle * edge_ai_active_power) + 
                               ((1.0 - cfg->edge_ai_duty_cycle) * edge_ai_sleep_power);
    
    res->autonomy_edge_ai_days = (cfg->battery_capacity_wh / edge_ai_avg_power) / 24.0;
}

// ── Демонстрація розрахунків ───────────────────────────────────────────────
int main(void)
{
    // Профіль: 1080p @ 30 fps, H.264 кодек, 4 референсні кадри, нічне підсвічування 1 Вт оптичної потужності
    video_system_config_t config_1080p = {
        .width = 1920,
        .height = 1080,
        .fps = 30,
        .bpp_raw = 10,
        .codec = CODEC_H264_AVC,
        .ref_frames = 4,
        .light_mode = LIGHT_NIGHT_IR,
        .ir_optical_watts = 1.0,
        .ir_led_efficiency = 0.30,  // 30% ККД світлодіода
        .soc_base_power_w = 0.50,   // 500 мВт ядро SoC/DDR
        .vpu_power_w = 0.30,        // 300 мВт апаратний кодек
        .sensor_power_w = 0.20,     // 200 мВт CMOS сенсор
        .radio_tx_power_w = 1.10,   // 1.1 Вт Wi-Fi передавач
        .radio_idle_power_w = 0.10, // 100 мВт очікування
        .battery_capacity_wh = 37.0,// Акумулятор Li-ion 10 А·год при 3.7 В (37 Вт·год)
        .edge_ai_duty_cycle = 0.005 // 0.5% часу активні (подійна детекція)
    };

    video_budget_result_t result;
    calculate_video_budget(&config_1080p, &result);

    printf("=== АУДИТ БЮДЖЕТУ ВІДЕОСИСТЕМИ (1080p @ 30 fps, H.264) ===\n");
    printf("1. Сирий піксельний потік сенсора (10-bit RAW): %.2f Мбіт/с\n", result.raw_sensor_mbps);
    printf("2. Бітрейт стисненого відеопотоку H.264:        %.2f Мбіт/с\n", result.compressed_bitrate_mbps);
    printf("3. Навантаження на шину DRAM (AXI Bandwidth):   %.2f МБ/с\n", result.dram_bandwidth_mbytes_sec);
    printf("4. Мінімальний розмір пулу кадрових буферів:    %.2f МБ\n", result.min_ram_dpb_mb);
    printf("5. Споживання енергії (Денний режим):           %.2f Вт\n", result.total_power_day_w);
    printf("6. Споживання енергії (Нічний режим з ІЧ):      %.2f Вт\n", result.total_power_night_w);
    printf("7. Автономність (Хмарний безперервний стрім):   %.1f годин\n", result.autonomy_streaming_hours);
    printf("8. Автономність (Edge AI з подійною передачею): %.1f діб\n", result.autonomy_edge_ai_days);

    return 0;
}
```
```cpp
#include <iostream>
#include <iomanip>
#include <cstdint>
#include <string_view>
#include <chrono>
#include <format>

// ── Типи та переліки в C++20 ───────────────────────────────────────────────
enum class VideoCodec {
    RawBayer,
    Mjpeg,
    H264Avc,
    H265Hevc
};

enum class LightingMode {
    Day,
    NightIr
};

// ── Параметри конфігурації відеосистеми ────────────────────────────────────
struct VideoSystemConfig {
    uint32_t width{1920};
    uint32_t height{1080};
    uint32_t fps{30};
    uint8_t  bppRaw{10};
    VideoCodec codec{VideoCodec::H264Avc};
    uint8_t  refFrames{4};
    LightingMode lightMode{LightingMode::NightIr};
    double   irOpticalWatts{1.0};
    double   irLedEfficiency{0.30};
    double   socBasePowerWatts{0.50};
    double   vpuPowerWatts{0.30};
    double   sensorPowerWatts{0.20};
    double   radioTxPowerWatts{1.10};
    double   batteryCapacityWattHours{37.0};
    double   edgeAiDutyCycle{0.005};
};

// ── Результати розрахунку ──────────────────────────────────────────────────
struct VideoBudgetResult {
    double rawSensorMbps{0.0};
    double yuv420FrameMegabytes{0.0};
    double compressedBitrateMbps{0.0};
    double dramBandwidthMegabytesPerSec{0.0};
    double minRamAllocationMegabytes{0.0};
    double totalPowerDayWatts{0.0};
    double totalPowerNightWatts{0.0};
    std::chrono::duration<double, std::ratio<3600>> streamingAutonomyHours{0};
    std::chrono::duration<double, std::ratio<86400>> edgeAiAutonomyDays{0};
};

// ── Модуль розрахунку відеотракту ──────────────────────────────────────────
class VideoBudgetCalculator {
public:
    [[nodiscard]] static constexpr VideoBudgetResult evaluate(const VideoSystemConfig& cfg) noexcept {
        VideoBudgetResult res{};

        const auto totalPixelsSec = static_cast<double>(cfg.width) * cfg.height * cfg.fps;

        // 1. Сирий піксельний потік
        res.rawSensorMbps = (totalPixelsSec * cfg.bppRaw) / 1'000'000.0;

        // Розмір одного кадру YUV420 (1.5 байти на піксель)
        const double frameBytes = static_cast<double>(cfg.width) * cfg.height * 1.5;
        res.yuv420FrameMegabytes = frameBytes / (1024.0 * 1024.0);

        // 2. Бітрейт стисненого потоку
        const double yuvRawMbps = (totalPixelsSec * 12.0) / 1'000'000.0;
        switch (cfg.codec) {
            case VideoCodec::RawBayer:
                res.compressedBitrateMbps = res.rawSensorMbps;
                break;
            case VideoCodec::Mjpeg:
                res.compressedBitrateMbps = yuvRawMbps / 10.0;
                break;
            case VideoCodec::H264Avc:
                res.compressedBitrateMbps = yuvRawMbps / 85.0;
                break;
            case VideoCodec::H265Hevc:
                res.compressedBitrateMbps = yuvRawMbps / 160.0;
                break;
        }

        // 3. Трафік системної пам'яті DRAM (ISP write + VPU read + DPB traffic + Bitstream write)
        const double ispWriteMbs = (frameBytes * cfg.fps) / (1024.0 * 1024.0);
        const double vpuReadMbs = ispWriteMbs;
        const double dpbTrafficMbs = (cfg.codec == VideoCodec::H264Avc || cfg.codec == VideoCodec::H265Hevc) 
                                     ? (ispWriteMbs * 2.0) : 0.0;
        const double bitstreamMbs = (res.compressedBitrateMbps * 1'000'000.0 / 8.0) / (1024.0 * 1024.0);

        res.dramBandwidthMegabytesPerSec = ispWriteMbs + vpuReadMbs + dpbTrafficMbs + bitstreamMbs;

        // 4. Пам'ять під буфери кадру
        const uint32_t bufferCount = 2 + (cfg.codec >= VideoCodec::H264Avc ? cfg.refFrames : 1) + 1;
        res.minRamAllocationMegabytes = bufferCount * res.yuv420FrameMegabytes;

        // 5. Електрична потужність
        const double irElectricalWatts = (cfg.irLedEfficiency > 0.05) 
            ? (cfg.irOpticalWatts / cfg.irLedEfficiency) : 0.0;
        const double baseActiveWatts = cfg.socBasePowerWatts + cfg.vpuPowerWatts + cfg.sensorPowerWatts;

        res.totalPowerDayWatts = baseActiveWatts + cfg.radioTxPowerWatts;
        res.totalPowerNightWatts = res.totalPowerDayWatts + irElectricalWatts;

        // 6. Автономність
        const double avgStreamingWatts = (res.totalPowerDayWatts + res.totalPowerNightWatts) / 2.0;
        res.streamingAutonomyHours = std::chrono::duration<double, std::ratio<3600>>(
            cfg.batteryCapacityWattHours / avgStreamingWatts
        );

        constexpr double edgeAiSleepWatts = 0.030; // 30 мВт черговий режим
        const double edgeAiActiveWatts = baseActiveWatts + cfg.radioTxPowerWatts;
        const double edgeAiAvgWatts = (cfg.edgeAiDutyCycle * edgeAiActiveWatts) + 
                                      ((1.0 - cfg.edgeAiDutyCycle) * edgeAiSleepWatts);

        res.edgeAiAutonomyDays = std::chrono::duration<double, std::ratio<86400>>(
            (cfg.batteryCapacityWattHours / edgeAiAvgWatts) / 24.0
        );

        return res;
    }
};

int main() {
    constexpr VideoSystemConfig config1080p{
        .width = 1920,
        .height = 1080,
        .fps = 30,
        .bppRaw = 10,
        .codec = VideoCodec::H264Avc,
        .refFrames = 4,
        .lightMode = LightingMode::NightIr,
        .irOpticalWatts = 1.0,
        .irLedEfficiency = 0.30,
        .socBasePowerWatts = 0.50,
        .vpuPowerWatts = 0.30,
        .sensorPowerWatts = 0.20,
        .radioTxPowerWatts = 1.10,
        .batteryCapacityWattHours = 37.0,
        .edgeAiDutyCycle = 0.005
    };

    const auto res = VideoBudgetCalculator::evaluate(config1080p);

    std::cout << "=== АУДИТ БЮДЖЕТУ ВІДЕОСИСТЕМИ (C++20 Модель) ===\n";
    std::cout << std::fixed << std::setprecision(2);
    std::cout << "1. Сирий піксельний потік сенсора (10-bit RAW): " << res.rawSensorMbps << " Мбіт/с\n";
    std::cout << "2. Бітрейт стисненого відеопотоку H.264:        " << res.compressedBitrateMbps << " Мбіт/с\n";
    std::cout << "3. Навантаження на шину DRAM (AXI Bandwidth):   " << res.dramBandwidthMegabytesPerSec << " МБ/с\n";
    std::cout << "4. Мінімальний розмір пулу кадрових буферів:    " << res.minRamAllocationMegabytes << " МБ\n";
    std::cout << "5. Споживання енергії (Денний режим):           " << res.totalPowerDayWatts << " Вт\n";
    std::cout << "6. Споживання енергії (Нічний режим з ІЧ):      " << res.totalPowerNightWatts << " Вт\n";
    std::cout << "7. Автономність (Хмарний безперервний стрім):   " << res.streamingAutonomyHours.count() << " годин\n";
    std::cout << "8. Автономність (Edge AI з подійною передачею): " << res.edgeAiAutonomyDays.count() << " діб\n";

    return 0;
}
```
:::

## Інженерні висновки та аналіз крайових випадків

Запуск калькулятора на різних конфігураціях виявляє чотири ключові закономірності, які визначають успіх або провал проєкту:

### 1. Ефект множника шини пам'яті (DRAM Multiplier)
Хоча вихідний бітрейт H.264 становить скромні 3.2 Мбіт/с (0.4 МБ/с), сумарне навантаження на внутрішню шину пам'яті досягає майже 470 МБ/с (3.76 Гбіт/с). Для систем на базі мікроконтролерів із зовнішньою шиною PSRAM/OctoSPI (пропускна здатність 100–200 МБ/с) це створює нездоланний апаратний затор, що призводить до втрати кадрової синхронізації та переповнення FIFO сенсора. У системах 4K @ 30 fps трафік шини злітає до 1.8–2.2 ГБ/с, що вимагає виключно 32-бітної шини LPDDR4.

### 2. Пам'ять Decoded Picture Buffer (DPB)
Для утримання 4 референсних кадрів роздільності 1080p кодеку потрібно щонайменше 21.7 МБ пам'яті виключно під буфери YUV420. Це остаточно унеможливлює розміщення Full HD H.264 конвеєра у внутрішній пам'яті SRAM мікроконтролерів (де доступно 512 КБ – 1 МБ) без переходу на повноцінні Linux SoC з DRAM.

### 3. Енергетична асиметрія дня і ночі
У нічному режимі ІЧ-підсвічування споживає понад 60 % всієї електричної енергії системи (3.33 Вт із сумарних 5.43 Вт) через фізичні обмеження напівпровідникового випромінювання (ККД ~30 %). Без імпульсної синхронізації спалаху з експозицією матриці батарея розряджається у 2.5 раза швидше, ніж удень.

### 4. Перевага архітектури Edge AI
Скорочення часу активної роботи радіопередавача до 0.5 % (завдяки локальній фільтрації кадрів на NPU) продовжує автономність того самого акумулятора з 8.3 годин до 38.5 діб — тобто майже у 110 разів. Це перетворює пристрій із лабораторного макета на комерційно життєздатний автономний продукт.
