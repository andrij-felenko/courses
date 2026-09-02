#include "ew_detector.h"

#include <string.h>

/* Пороги матриці правил. Числа — робоча точка ланки 868 МГц з LoRa-модемом;
   на іншому діапазоні їх перемірюють, але сама логіка правил не міняється. */
#define EW_RSSI_SPOT_MIN_DBM      (-65)  /* «сигнал сильний» для прицільної завади */
#define EW_RSSI_BARRAGE_MIN_DBM   (-40)  /* вхід забитий по самий верх */
#define EW_SNR_JAM_MAX_DB         (0)    /* SNR провалився нижче робочого */
#define EW_AGC_SATURATED_MAX      (30)   /* AGC збив підсилення майже в нуль */
#define EW_PER_JAM_MIN_PCT        (75)
#define EW_PER_PULSE_MIN_PCT      (40)
#define EW_RSSI_PULSE_VAR_MIN     (120u) /* дБ² */
#define EW_RSSI_PULSE_STEP_MIN_DB (20)   /* стрибок між сусідніми вибірками */
#define EW_RSSI_WEAK_MAX_DBM      (-105)
#define EW_ESC_THROTTLE_DELTA_PCT (25)   /* газ на «поганих» вибірках вищий на стільки */

#define EW_GNSS_SPOOF_CNR_X10         (510) /* 51.0 дБ-Гц */
#define EW_GNSS_SPOOF_MAD_MAX         (25u) /* 2.5 дБ-Гц середнього відхилення */
#define EW_GNSS_SPOOF_HIGH_PCT        (70)
#define EW_GNSS_DOPPLER_SPREAD_MIN_HZ (300) /* менший розкид — усе з однієї антени */

/* k-та за старшинством вибірка вікна: k = 0 — найстаріша.
   Порядок важливий: стрибок RSSI шукається між СУСІДНІМИ в часі вибірками,
   а не між сусідніми клітинками масиву. */
static const ew_rf_sample_t *ew_at(const ew_detector_t *det, uint8_t k)
{
    uint8_t idx = (uint8_t)((det->rf_head + EW_WINDOW_SIZE - det->rf_count + k) % EW_WINDOW_SIZE);
    return &det->window[idx];
}

void ew_detector_init(ew_detector_t *det)
{
    if (!det) {
        return;
    }
    memset(det, 0, sizeof(*det));
    det->threat = EW_THREAT_NONE;
}

void ew_detector_push_rf(ew_detector_t *det, const ew_rf_sample_t *sample)
{
    if (!det || !sample) {
        return;
    }
    det->window[det->rf_head] = *sample;
    det->rf_head = (uint8_t)((det->rf_head + 1u) % EW_WINDOW_SIZE);
    if (det->rf_count < EW_WINDOW_SIZE) {
        det->rf_count++;
    }
}

bool ew_detector_stats(const ew_detector_t *det, ew_rf_stats_t *out)
{
    if (!det || !out || det->rf_count < EW_WINDOW_MIN_FILL) {
        return false;
    }

    memset(out, 0, sizeof(*out));
    const uint8_t n = det->rf_count;

    int32_t  rssi_sum = 0;
    int32_t  snr_sum = 0;
    uint32_t agc_sum = 0;
    uint8_t  crc_errors = 0;
    uint8_t  sync_hits = 0;

    for (uint8_t k = 0; k < n; k++) {
        const ew_rf_sample_t *s = ew_at(det, k);
        rssi_sum += s->rssi_dbm;
        snr_sum  += s->snr_db;
        agc_sum  += s->agc_gain_code;
        if (s->crc_error) {
            crc_errors++;
        }
        if (s->preamble_detected) {
            sync_hits++;
        }
    }

    /* Ділення від'ємного цілого в C99 обрізає до нуля — для середнього рівня
       в дБм похибка не більша за 1 дБ, і це дешевше за будь-яке округлення. */
    out->samples       = n;
    out->avg_rssi_dbm  = (int16_t)(rssi_sum / n);
    out->avg_snr_db    = (int8_t)(snr_sum / n);
    out->avg_agc       = (uint8_t)(agc_sum / n);
    out->per_pct       = (uint8_t)(((uint32_t)crc_errors * 100u) / n);
    out->sync_hits     = sync_hits;

    /* Дисперсія — другим проходом по вже відомому середньому: накопичувач
       квадратів різниць не переповнюється навіть на 16 вибірках по 60 дБ. */
    uint32_t var_sum = 0;
    for (uint8_t k = 0; k < n; k++) {
        int32_t diff = (int32_t)ew_at(det, k)->rssi_dbm - (int32_t)out->avg_rssi_dbm;
        var_sum += (uint32_t)(diff * diff);
    }
    out->rssi_variance = var_sum / n;

    /* Найбільший стрибок між сусідніми вибірками. Багатопроменеві провали
       рухаються повільно (доплерівське розширення обмежує швидкість зміни:
       20-30 дБ за секунду, тобто ≈3 дБ за крок 100 мс), а імпульсна завада
       перекидає рівень за один інтервал. */
    uint8_t max_step = 0;
    for (uint8_t k = 1; k < n; k++) {
        int32_t step = (int32_t)ew_at(det, k)->rssi_dbm - (int32_t)ew_at(det, k - 1u)->rssi_dbm;
        if (step < 0) {
            step = -step;
        }
        if (step > 255) {
            step = 255;
        }
        if ((uint8_t)step > max_step) {
            max_step = (uint8_t)step;
        }
    }
    out->max_step_db = max_step;

    return true;
}

/* Власні регулятори обертів (ESC) шумлять синхронно з газом. Якщо побиті
   кадри лягають саме на високий газ, це не РЕБ, а власна плата. */
static bool ew_esc_noise_suspected(const ew_detector_t *det)
{
    int32_t bad_sum = 0;
    int32_t good_sum = 0;
    uint8_t bad = 0;
    uint8_t good = 0;

    for (uint8_t k = 0; k < det->rf_count; k++) {
        const ew_rf_sample_t *s = ew_at(det, k);
        if (s->crc_error) {
            bad_sum += s->throttle_pct;
            bad++;
        } else {
            good_sum += s->throttle_pct;
            good++;
        }
    }

    /* Без обох груп порівнювати нема з чим — тоді нічого не блокуємо. */
    if (bad == 0 || good == 0) {
        return false;
    }
    return (bad_sum / bad) - (good_sum / good) >= EW_ESC_THROTTLE_DELTA_PCT;
}

static bool ew_gnss_spoofed(const ew_gnss_frame_t *gnss)
{
    if (!gnss || gnss->sat_count < 4u) {
        return false;
    }

    uint8_t n = gnss->sat_count;
    if (n > EW_MAX_GNSS_SATS) {
        n = EW_MAX_GNSS_SATS; /* драйвер NMEA міг нарахувати більше, ніж влізло */
    }

    /* Найгрубіші ознаки: годинник приймача стрибнув або координата поїхала
       без жодного руху за даними інерціального вимірювача. */
    if (gnss->clock_jump_detected || gnss->pos_jump_without_imu) {
        return true;
    }

    uint32_t cnr_sum = 0;
    uint8_t  high_cnr = 0;
    int16_t  dop_min = gnss->sats[0].doppler_hz;
    int16_t  dop_max = gnss->sats[0].doppler_hz;

    for (uint8_t i = 0; i < n; i++) {
        cnr_sum += gnss->sats[i].cnr_x10;
        if (gnss->sats[i].cnr_x10 >= EW_GNSS_SPOOF_CNR_X10) {
            high_cnr++;
        }
        if (gnss->sats[i].doppler_hz < dop_min) {
            dop_min = gnss->sats[i].doppler_hz;
        }
        if (gnss->sats[i].doppler_hz > dop_max) {
            dop_max = gnss->sats[i].doppler_hz;
        }
    }

    const uint16_t cnr_avg = (uint16_t)(cnr_sum / n);

    /* Середнє абсолютне відхилення замість СКВ: без кореня і без плаваючої коми. */
    uint32_t dev_sum = 0;
    for (uint8_t i = 0; i < n; i++) {
        int32_t diff = (int32_t)gnss->sats[i].cnr_x10 - (int32_t)cnr_avg;
        if (diff < 0) {
            diff = -diff;
        }
        dev_sum += (uint32_t)diff;
    }
    const uint32_t mad = dev_sum / n;
    const uint8_t  high_pct = (uint8_t)(((uint32_t)high_cnr * 100u) / n);

    if (high_pct < EW_GNSS_SPOOF_HIGH_PCT) {
        return false;
    }

    /* Однорідна енергетика: справжнє сузір'я розкидане по півсфері, рівні
       не можуть збігтися так щільно. */
    if (mad <= EW_GNSS_SPOOF_MAD_MAX) {
        return true;
    }

    /* Друга ознака тієї ж природи: усі коди приїхали з однієї нерухомої
       антени, тож доплер у них практично однаковий, а справжні супутники
       розходяться на кілька кілогерц. */
    return (int32_t)dop_max - (int32_t)dop_min <= EW_GNSS_DOPPLER_SPREAD_MIN_HZ;
}

static ew_threat_t ew_classify(const ew_detector_t *det, const ew_rf_stats_t *st)
{
    /* Загороджувальна: рівень уперся у стелю, AGC збив підсилення до підлоги,
       синхрослова не знайдено жодного разу. */
    if (st->avg_rssi_dbm >= EW_RSSI_BARRAGE_MIN_DBM &&
        st->avg_agc <= EW_AGC_SATURATED_MAX &&
        st->sync_hits == 0) {
        return EW_THREAT_BARRAGE_BLOCKING;
    }

    /* Прицільна: сигнал сильний, а SNR провалився. Саме ця пара відрізняє
       глушіння від затінення корпусом, де RSSI і SNR падають разом. */
    if (st->avg_rssi_dbm >= EW_RSSI_SPOT_MIN_DBM &&
        st->avg_snr_db <= EW_SNR_JAM_MAX_DB &&
        st->per_pct >= EW_PER_JAM_MIN_PCT &&
        st->sync_hits <= 1) {
        return EW_THREAT_SPOT_JAMMING;
    }

    /* Імпульсна: велика дисперсія ПЛЮС миттєвий стрибок між сусідніми
       вибірками (інакше це багатопроменевість), і не власні ESC. */
    if (st->rssi_variance >= EW_RSSI_PULSE_VAR_MIN &&
        st->max_step_db >= EW_RSSI_PULSE_STEP_MIN_DB &&
        st->per_pct >= EW_PER_PULSE_MIN_PCT &&
        !ew_esc_noise_suspected(det)) {
        return EW_THREAT_PULSE_JAMMING;
    }

    /* Просто далеко або затінило конструкцією: рівень і SNR просіли разом. */
    if (st->avg_rssi_dbm <= EW_RSSI_WEAK_MAX_DBM &&
        st->per_pct >= EW_PER_JAM_MIN_PCT) {
        return EW_THREAT_WEAK_SIGNAL;
    }

    return EW_THREAT_NONE;
}

ew_threat_t ew_detector_evaluate(ew_detector_t *det, const ew_gnss_frame_t *gnss,
                                 uint32_t now_ms)
{
    if (!det) {
        return EW_THREAT_NONE;
    }

    ew_threat_t verdict;
    ew_rf_stats_t st;

    /* Спуфінг навігації не залежить від радіовікна: кадр GNSS самодостатній,
       тож перевіряємо його навіть на холодному старті. */
    if (ew_gnss_spoofed(gnss)) {
        verdict = EW_THREAT_GNSS_SPOOFING;
    } else if (ew_detector_stats(det, &st)) {
        verdict = ew_classify(det, &st);
    } else {
        /* Вікно ще заповнюється — мовчимо, а не панікуємо. */
        verdict = EW_THREAT_NONE;
    }

    if (verdict != det->threat) {
        det->threat = verdict;
        det->threat_since_ms = now_ms;
    }
    return det->threat;
}

uint32_t ew_detector_threat_held_ms(const ew_detector_t *det, uint32_t now_ms)
{
    if (!det) {
        return 0;
    }
    /* Віднімання беззнакових дає правильну різницю і після переповнення
       32-бітного лічильника мілісекунд (це станеться за 49 діб роботи). */
    return now_ms - det->threat_since_ms;
}

const char *ew_threat_name(ew_threat_t threat)
{
    switch (threat) {
        case EW_THREAT_NONE:             return "none";
        case EW_THREAT_WEAK_SIGNAL:      return "weak";
        case EW_THREAT_SPOT_JAMMING:     return "spot";
        case EW_THREAT_BARRAGE_BLOCKING: return "barrage";
        case EW_THREAT_PULSE_JAMMING:    return "pulse";
        case EW_THREAT_GNSS_SPOOFING:    return "spoof";
        default:                         return "?";
    }
}
