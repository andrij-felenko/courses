/* ── bq25890H: карта регістрів (даташит SLUSCC5A) ─────────────────────── */
#define BQ_ADDR   0x6A          /* 7-бітна адреса на шині                  */

#define REG01     0x01          /* DP_DAC[7:5] | DM_DAC[4:2] | EN_12V | VINDPM_OS */
#define REG02     0x02          /* CONV_START | CONV_RATE | … | AUTO_DPDM_EN */
#define REG03     0x03          /* … | WD_RST(6) | …                        */
#define REG0B     0x0B          /* VBUS_STAT[7:5] | CHRG_STAT[4:3] | PG_STAT(2) */
#define REG11     0x11          /* VBUS_GD(7) | VBUSV[6:0]                  */

#define REG01_DPDM      0xFCu   /* біти [7:2] — наші; [1:0] — ЧУЖІ         */
#define REG02_CONV_RATE (1u << 6)
#define REG03_WD_RST    (1u << 6)
#define REG0B_PG_STAT   (1u << 2)
#define REG11_VBUS_GD   (1u << 7)

#define VBUS_STAT_DCP    3u     /* звичайний DCP: високої напруги не буде   */
#define VBUS_STAT_HVDCP  4u     /* «Adjustable High Voltage DCP» — уміє     */

/* Стеля САМЕ цього чипа: VBUS_OP = 3.9 … 14 В. Двадцять вольтів — смерть. */
#define QC_VBUS_MAX_MV  12000
#define QC_VBUS_MIN_MV   3600   /* нижня межа безперервного режиму QC3.0    */

/* ── Пресети драйвера D+/D− ───────────────────────────────────────────── */
enum dac {
    DAC_HIZ = 0,  /* 000 — драйвер вимкнено; це НЕ нуль вольтів            */
    DAC_0V0 = 1,  /* 001 — 0 В    (−0.15 … +0.15)                          */
    DAC_0V6 = 2,  /* 010 — 0.6 В  (0.5 … 0.7)                              */
    DAC_1V2 = 3,  /* 011 — 1.2 В                                           */
    DAC_2V0 = 4,  /* 100 — 2.0 В                                           */
    DAC_2V7 = 5,  /* 101 — 2.7 В                                           */
    DAC_3V3 = 6,  /* 110 — 3.3 В  (3.15 … 3.45)                            */
};

struct code { enum dac dp, dm; };

static const struct code CODE_5V   = { DAC_0V6, DAC_0V0 };  /* D− у нуль, не в HiZ */
static const struct code CODE_9V   = { DAC_3V3, DAC_0V6 };
static const struct code CODE_CONT = { DAC_0V6, DAC_3V3 };  /* безперервний режим  */
/* CODE_20V = {DAC_3V3, DAC_3V3} свідомо НЕ оголошено: див. «Пастки».      */

/* ── Витримки: усі в одному місці, жодного «магічного» delay в коді ───── */
#define T_DP_HOLD_MS      1300  /* утримання D+ 0.6 В (специфікація 1000…1500):
                                   потрібне лише ручному шляху — тут його
                                   відлічує кремній, і це єдина причина,
                                   чому автомат нижче такий короткий        */
#define T_MODE_MS           80  /* фільтр коду 20…60 мс + запас             */
#define T_NEW_REQUEST_MS   200  /* блок мусить дійти до нової напруги       */
#define T_ADC_PERIOD_MS   1000  /* CONV_RATE=1: свіжий вимір раз на секунду */
#define T_VERIFY_MS  (T_MODE_MS + T_NEW_REQUEST_MS + T_ADC_PERIOD_MS)
#define T_STEP_US          300  /* імпульс кроку; фільтр блока 100…200 мкс  */
#define T_STEP_SETTLE_MS     3  /* усталення напруги після фронту (≈2 мс)   */
#define T_WD_KICK_MS     20000  /* сторож 40 с — годуємо вдвічі частіше     */
#define T_AUDIT_MS        1000  /* як часто звіряти лік із виміром          */

/* ── Формування рівнів: тінь регістра, рівно одна транзакція ──────────── */
static uint8_t reg01;           /* читаємо ОДИН раз, далі тільки пишемо    */

static int dpdm_sync(void) { return bq_read(REG01, &reg01); }

static int dpdm_set(struct code c) {
    reg01 = (uint8_t)((reg01 & ~REG01_DPDM)
                      | ((uint8_t)c.dp << 5) | ((uint8_t)c.dm << 2));
    return bq_write(REG01, reg01);
}

/* ── Вимір VBUS: REG11, зсув 2600 мВ, крок 100 мВ, стеля 15300 мВ ─────── */
static int vbus_mv(int *out) {
    uint8_t r;
    if (bq_read(REG11, &r) < 0) return -1;
    *out = (r & REG11_VBUS_GD) ? 2600 + (r & 0x7F) * 100 : 0;
    return 0;
}

/* ── Кроки INOV ───────────────────────────────────────────────────────── */
/* Угору: короткий фронт на D+. На час імпульсу на лініях стоїть 3.3/3.3 —
   код ДВАДЦЯТИ вольтів. Рятує лише те, що це ненадовго.                  */
static void step_up(void) {
    dpdm_set((struct code){ DAC_3V3, DAC_3V3 });
    delay_us(T_STEP_US);
    dpdm_set((struct code){ DAC_0V6, DAC_3V3 });
    delay_ms(T_STEP_SETTLE_MS);
}

/* Униз: дзеркальний фронт на D−; на час імпульсу — код дванадцяти вольтів. */
static void step_down(void) {
    dpdm_set((struct code){ DAC_0V6, DAC_0V6 });
    delay_us(T_STEP_US);
    dpdm_set((struct code){ DAC_0V6, DAC_3V3 });
    delay_ms(T_STEP_SETTLE_MS);
}

/* ── Автомат ──────────────────────────────────────────────────────────── */
enum st { S_IDLE, S_DETECT, S_CLASSIFY, S_VERIFY, S_CONT, S_TUNE, S_LEGACY, S_RESYNC };

struct qc {
    enum st  st;
    uint32_t t_mark, t_wd, t_audit;
    int      belief_mv;     /* НАШ лік. У протоколі його не існує.         */
    int      target_mv;
};

static void go(struct qc *q, enum st s, uint32_t now) { q->st = s; q->t_mark = now; }
static int  gap(int a, int b) { return a > b ? a - b : b - a; }

void qc_init(struct qc *q, uint32_t now) {
    uint8_t r;
    /* Безперервний АЦП: свіжий VBUS раз на секунду, без опитувань.
       Увага: перший же запис переводить чип у host mode — і вмикає сторожа. */
    if (bq_read(REG02, &r) == 0) bq_write(REG02, (uint8_t)(r | REG02_CONV_RATE));
    q->st = S_IDLE;
    q->t_mark = q->t_wd = q->t_audit = now;
    q->belief_mv = 0;
    q->target_mv = 6400;
}

void qc_tick(struct qc *q, uint32_t now) {
    uint8_t r;
    int mv;

    /* Сторож не залежить від стану — годуємо його поза автоматом. */
    if (now - q->t_wd >= T_WD_KICK_MS) {
        if (bq_read(REG03, &r) == 0) bq_write(REG03, (uint8_t)(r | REG03_WD_RST));
        q->t_wd = now;
    }

    /* Шнур можуть висмикнути в БУДЬ-ЯКОМУ стані — і це не помилка. */
    if (q->st != S_IDLE && bq_read(REG11, &r) == 0 && !(r & REG11_VBUS_GD)) {
        q->belief_mv = 0;
        go(q, S_IDLE, now);
        return;
    }

    switch (q->st) {

    case S_IDLE:
        if (bq_read(REG11, &r) == 0 && (r & REG11_VBUS_GD)) go(q, S_DETECT, now);
        break;

    case S_DETECT:
        /* Ті самі 1.25 с відлічує кремній: BC1.2, утримання D+, проба D−.
           Хостові лишається дочекатися вердикту — або здатися.            */
        if (bq_read(REG0B, &r) == 0 && (r & REG0B_PG_STAT)) go(q, S_CLASSIFY, now);
        else if (now - q->t_mark > 3000) { q->belief_mv = 5000; go(q, S_LEGACY, now); }
        break;

    case S_CLASSIFY:
        if (bq_read(REG0B, &r) < 0) break;
        if (dpdm_sync() < 0) break;         /* тінь REG01 — рівно тут, один раз */
        if ((r >> 5) == VBUS_STAT_HVDCP) {
            dpdm_set(CODE_9V);
            q->belief_mv = 9000;
            go(q, S_VERIFY, now);
        } else {
            /* DCP/SDP/CDP: лінії або замкнені перемичкою, або зайняті даними.
               Драйвери — в HiZ, і руки геть.                              */
            dpdm_set((struct code){ DAC_HIZ, DAC_HIZ });
            q->belief_mv = 5000;
            go(q, S_LEGACY, now);
        }
        break;

    case S_VERIFY:
        /* Фільтр коду + перехід блока + ЦІЛИЙ період АЦП: раніше REG11
           покаже старе значення, і «перевірка» перевірить минуле.         */
        if (now - q->t_mark < T_VERIFY_MS) break;
        if (vbus_mv(&mv) < 0) break;
        if (gap(mv, 9000) < 1000) {
            dpdm_set(CODE_CONT);
            go(q, S_CONT, now);
        } else {
            /* Просили дев'ять, стоїть п'ять. Хоч що казав VBUS_STAT — це не HVDCP. */
            dpdm_set(CODE_5V);
            q->belief_mv = 5000;
            go(q, S_LEGACY, now);
        }
        break;

    case S_CONT:
        /* Не вгадуємо, з якої напруги почався безперервний режим, — питаємо.
           Це ЄДИНЕ місце, де лік можна засіяти правдою, а не здогадом.    */
        if (now - q->t_mark < T_MODE_MS + T_ADC_PERIOD_MS) break;
        if (vbus_mv(&mv) < 0) break;
        q->belief_mv = mv;
        q->t_audit = now;
        go(q, S_TUNE, now);
        break;

    case S_TUNE:
        /* Один крок на такт: 200 мВ — це 3 мс роботи, а не 3 мс чекання.  */
        if (q->belief_mv + 100 < q->target_mv && q->belief_mv < QC_VBUS_MAX_MV) {
            step_up();   q->belief_mv += 200;  break;
        }
        if (q->belief_mv - 100 > q->target_mv && q->belief_mv > QC_VBUS_MIN_MV) {
            step_down(); q->belief_mv -= 200;  break;
        }
        /* Ціль досягнуто — за НАШИМ ліком. Раз на секунду питаємо світ.   */
        if (now - q->t_audit >= T_AUDIT_MS) {
            q->t_audit = now;
            if (vbus_mv(&mv) == 0 && gap(mv, q->belief_mv) > 600) {
                dpdm_set(CODE_5V);            /* єдиний спосіб отямитись   */
                q->belief_mv = 5000;
                go(q, S_RESYNC, now);
            }
        }
        break;

    case S_RESYNC:
        if (now - q->t_mark < T_MODE_MS + T_NEW_REQUEST_MS) break;
        dpdm_set(CODE_CONT);
        go(q, S_CONT, now);
        break;

    case S_LEGACY:
        /* Нічого не робимо — і це вся робота. П'ять вольтів теж заряджають. */
        break;
    }
}
