#define ACCEL_CAL_MAGIC  0xACCE1CA1u   // мітка «тут повний, осмислений набір»

typedef struct {
    uint32_t   magic;     // ACCEL_CAL_MAGIC ⟺ набір повний і пройшов перевірки
    accel_cal_t cal;      // шість чисел
    uint32_t   crc;       // контрольна сума полів вище
} accel_cal_store_t;

// Записати калібрування безпечно: спершу перевірки, тоді атомарний запис із міткою.
static bool accel_cal_commit(const accel_cal_t *cal)
{
    // 1) остаточна перевірка: усі шість чисел у розумних межах
    for (int k = 0; k < 3; k++) {
        float sc = (&cal->scale.x)[k], of = (&cal->offset.x)[k];
        if (!isfinite(sc) || !isfinite(of)) return false;   // NaN/inf — розв'язок не зійшовся
        if (sc < 0.8f || sc > 1.2f)         return false;
        if (fabsf(of) > GRAVITY_MSS)        return false;
    }

    // 2) зібрати повний запис із міткою й CRC — у пам'яті, ще не в параметрах
    accel_cal_store_t rec;
    rec.magic = ACCEL_CAL_MAGIC;
    rec.cal   = *cal;
    rec.crc   = crc32(&rec, offsetof(accel_cal_store_t, crc));

    // 3) атомарний запис: або весь запис ляже, або старий лишиться цілим
    //    (подвійний банк / журнал NVS — деталі в загальному калібрувальному коді)
    return nvs_write_atomic(&rec, sizeof(rec));
}

// На старті: підняти калібрування лише якщо мітка й CRC збіглись.
static bool accel_cal_load(accel_cal_t *out)
{
    accel_cal_store_t rec;
    if (!nvs_read(&rec, sizeof(rec)))                       return false;
    if (rec.magic != ACCEL_CAL_MAGIC)                       return false;  // не наш / недописаний
    if (rec.crc != crc32(&rec, offsetof(accel_cal_store_t, crc))) return false;  // побитий
    *out = rec.cal;
    return true;                                            // лише тут набір вважається чинним
}
