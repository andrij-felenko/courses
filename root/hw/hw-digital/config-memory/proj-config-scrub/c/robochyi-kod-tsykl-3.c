// Правильні («золоті») кадри в незникній пам'яті поряд із чипом —
// той самий бітстрім, що заливали при старті. Потрібні лише для важких випадків,
// коли покадрового ECC не вистачило.
extern void golden_read_frame(uint32_t frame_addr, uint32_t *dst);

typedef enum {
    SCRUB_CLEAN = 0,   // кадр був цілий — нічого не робили
    SCRUB_FIXED_SBE,   // виправили один біт силами ECC (дешево)
    SCRUB_FIXED_HARD,  // довелось перезалити кадр із золотого еталона (дорого)
    SCRUB_FAILED       // не вдалося виправити навіть перезаливкою (тривога!)
} scrub_result_t;

static uint32_t frame_buf[FRAME_WORDS];   // робочий буфер під один кадр

// Обробити ОДИН кадр: прочитати назад, звірити, за потреби виправити.
static scrub_result_t scrub_one_frame(uint32_t f)
{
    cfg_read_frame(f, frame_buf);                 // зчитати кадр назад
    frame_status_t st = decode_ecc(cfg_frame_ecc(f));

    if (st == FRAME_OK) {
        return SCRUB_CLEAN;                       // цілий — не чіпаємо ЖОДНИМ записом
    }

    if (st == FRAME_SBE) {
        // Однобітовий збій: апаратний ECC уже знає позицію й підправив дані
        // в буфері (або ми правимо самі за синдромом). Повертаємо кадр на місце.
        cfg_write_frame(f, frame_buf);
        return SCRUB_FIXED_SBE;
    }

    // FRAME_DBE_OR_WORSE: місцевого ECC замало — беремо золотий кадр і перезаливаємо.
    golden_read_frame(f, frame_buf);
    cfg_write_frame(f, frame_buf);

    // Переконаймося, що перезаливка справді допомогла (раптом б'ється сам кадр чи еталон).
    cfg_read_frame(f, frame_buf);
    if (decode_ecc(cfg_frame_ecc(f)) == FRAME_OK) {
        return SCRUB_FIXED_HARD;
    }
    return SCRUB_FAILED;                          // не витягли — це вже привід бити на сполох
}
