#include "l1ca.h"

#include <math.h>
#include <stdio.h>
#include <string.h>

/* ---- далекомірний код Голда -------------------------------------------- */

/* Пара відводів регістра G2, що дає затримку коду для конкретного апарата. */
static const int g2_taps[32][2] = {
    {2,6},{3,7},{4,8},{5,9},{1,9},{2,10},{1,8},{2,9},{3,10},{2,3},
    {3,4},{5,6},{6,7},{7,8},{8,9},{9,10},{1,4},{2,5},{3,6},{4,7},
    {5,8},{6,9},{1,3},{4,6},{5,7},{6,8},{7,9},{8,10},{1,6},{2,7},
    {3,8},{4,9}
};

bool ca_code_generate(int prn, uint8_t out[CA_CODE_LEN])
{
    if (prn < 1 || prn > 32) {
        fprintf(stderr, "PRN %d не має коду C/A\n", prn);
        return false;
    }

    uint8_t g1[11], g2[11];               /* індексація з 1, як у стандарті */
    for (int i = 1; i <= 10; ++i) g1[i] = g2[i] = 1;

    const int t1 = g2_taps[prn - 1][0];
    const int t2 = g2_taps[prn - 1][1];

    for (int i = 0; i < CA_CODE_LEN; ++i) {
        out[i] = (uint8_t)(g1[10] ^ g2[t1] ^ g2[t2]);

        int fb1 = g1[3] ^ g1[10];
        int fb2 = g2[2] ^ g2[3] ^ g2[6] ^ g2[8] ^ g2[9] ^ g2[10];
        for (int k = 10; k > 1; --k) { g1[k] = g1[k - 1]; g2[k] = g2[k - 1]; }
        g1[1] = (uint8_t)fb1;
        g2[1] = (uint8_t)fb2;
    }
    return true;
}

/* ---- укладання бітів ---------------------------------------------------- */

typedef struct { uint8_t *bits; int cur, cap; } bitcur_t;

static void bc_u(bitcur_t *b, uint32_t v, int len)
{
    if (b->cur + len > b->cap) { fprintf(stderr, "підкадр переповнено\n"); return; }
    for (int i = len - 1; i >= 0; --i) b->bits[b->cur++] = (uint8_t)((v >> i) & 1u);
}

static void bc_pad(bitcur_t *b, int len) { bc_u(b, 0, len); }

static uint32_t mask_of(int len) { return (len >= 32) ? 0xFFFFFFFFu : ((1u << len) - 1u); }

/* Ціле зі знаком у доповняльному коді, з насиченням на межах поля. */
static void bc_s(bitcur_t *b, double value, double lsb, int len)
{
    double raw = round(value / lsb);
    int64_t lim = (int64_t)1 << (len - 1);
    if (raw >  (double)(lim - 1)) raw = (double)(lim - 1);
    if (raw < -(double)lim)       raw = -(double)lim;
    bc_u(b, (uint32_t)((int64_t)raw) & mask_of(len), len);
}

static void bc_uf(bitcur_t *b, double value, double lsb, int len)
{
    double raw = round(value / lsb);
    if (raw < 0.0) raw = 0.0;
    if (raw > (double)mask_of(len)) raw = (double)mask_of(len);
    bc_u(b, (uint32_t)raw & mask_of(len), len);
}

/* ---- парність за IS-GPS-200 (розширений код Гемінга) -------------------- */

static const int P25[] = {1,2,3,5,6,10,11,12,13,14,17,18,20,23};
static const int P26[] = {2,3,4,6,7,11,12,13,14,15,18,19,21,24};
static const int P27[] = {1,3,4,5,7,8,12,13,14,15,16,19,20,22};
static const int P28[] = {2,4,5,6,8,9,13,14,15,16,17,20,21,23};
static const int P29[] = {1,3,5,6,7,9,10,14,15,16,17,18,21,22,24};
static const int P30[] = {3,5,6,8,9,10,11,13,15,19,22,23,24};

static int xor_of(const uint8_t d[24], const int *idx, int n, int seed)
{
    int p = seed;
    for (int i = 0; i < n; ++i) p ^= d[idx[i] - 1];
    return p & 1;
}

/* Кодує 24 інформаційні біти у 30-бітне слово; d29/d30 — «хвіст» попереднього. */
static void encode_word(uint8_t word[30], const uint8_t d[24], int *d29p, int *d30p)
{
    const int a = *d29p, b = *d30p;

    for (int i = 0; i < 24; ++i) word[i] = (uint8_t)(d[i] ^ b);
    word[24] = (uint8_t)xor_of(d, P25, 14, a);
    word[25] = (uint8_t)xor_of(d, P26, 14, b);
    word[26] = (uint8_t)xor_of(d, P27, 14, a);
    word[27] = (uint8_t)xor_of(d, P28, 14, b);
    word[28] = (uint8_t)xor_of(d, P29, 15, b);
    word[29] = (uint8_t)xor_of(d, P30, 13, a);

    *d29p = word[28];
    *d30p = word[29];
}

/* Слова 2 і 10 мусять закінчуватися нулями D29 і D30: два передостанні
 * інформаційні біти для того й лишили вільними — добираємо їх перебором. */
static void encode_solved_word(uint8_t word[30], uint8_t d[24], int *d29p, int *d30p)
{
    for (int combo = 0; combo < 4; ++combo) {
        d[22] = (uint8_t)(combo >> 1);
        d[23] = (uint8_t)(combo & 1);

        int a = *d29p, b = *d30p;
        encode_word(word, d, &a, &b);
        if (word[28] == 0 && word[29] == 0) { *d29p = a; *d30p = b; return; }
    }
    /* Такого не буває: чотири комбінації покривають обидва біти парності. */
    fprintf(stderr, "не вдалося розв'язати хвостові біти слова\n");
}

/* ---- підкадр ------------------------------------------------------------ */

static void build_subframe(uint8_t out[NAV_SUBFRAME_BITS], int sfid,
                           double tow_subframe, const uint8_t payload[192],
                           int *d29p, int *d30p)
{
    uint8_t d[24];

    /* Слово 1 — TLM: преамбула 10001011, далі поле повідомлення й прапорці. */
    memset(d, 0, sizeof d);
    const uint8_t preamble[8] = {1,0,0,0,1,0,1,1};
    memcpy(d, preamble, 8);
    encode_word(out, d, d29p, d30p);

    /* Слово 2 — HOW: лічильник TOW наступного підкадру в одиницях 6 с. */
    memset(d, 0, sizeof d);
    uint32_t tow_count = ((uint32_t)(tow_subframe / 6.0) + 1u) & 0x1FFFFu;
    bitcur_t hb = { d, 0, 24 };
    bc_u(&hb, tow_count, 17);
    bc_u(&hb, 0, 1);                 /* alert */
    bc_u(&hb, 0, 1);                 /* antispoof */
    bc_u(&hb, (uint32_t)sfid, 3);
    bc_u(&hb, 0, 2);                 /* хвостові біти доберемо нижче */
    encode_solved_word(out + 30, d, d29p, d30p);

    /* Слова 3..10 — корисне навантаження підкадру. */
    for (int w = 0; w < 8; ++w) {
        memcpy(d, payload + w * 24, 24);
        if (w == 7) encode_solved_word(out + (2 + w) * 30, d, d29p, d30p);
        else        encode_word(out + (2 + w) * 30, d, d29p, d30p);
    }
}

/* ---- корисне навантаження підкадрів ------------------------------------- */

static int ura_index(double accuracy_m)
{
    static const double edge[15] = {2.4,3.4,4.85,6.85,9.65,13.65,24.0,48.0,
                                    96.0,192.0,384.0,768.0,1536.0,3072.0,6144.0};
    for (int i = 0; i < 15; ++i) if (accuracy_m <= edge[i]) return i;
    return 15;
}

static void payload_sf1(uint8_t p[192], const ephemeris_t *e)
{
    bitcur_t b = { p, 0, 192 };
    bc_u(&b, (uint32_t)gps_week10(e->week), 10);   /* саме тут переповнюється лічильник */
    bc_u(&b, 1, 2);                                /* коди на L2 */
    bc_u(&b, (uint32_t)ura_index(e->accuracy), 4);
    bc_u(&b, (uint32_t)(e->health & 0x3F), 6);
    bc_u(&b, ((uint32_t)e->iodc >> 8) & 0x3u, 2);  /* старші біти IODC */
    bc_u(&b, 0, 1);                                /* прапорець L2 P */
    bc_pad(&b, 23 + 24 + 24 + 16);                 /* резерв слів 4..7 */
    bc_s(&b, e->tgd, pow(2.0, -31), 8);
    bc_u(&b, (uint32_t)e->iodc & 0xFFu, 8);
    bc_uf(&b, e->toc, 16.0, 16);
    bc_s(&b, e->af2, pow(2.0, -55), 8);
    bc_s(&b, e->af1, pow(2.0, -43), 16);
    bc_s(&b, e->af0, pow(2.0, -31), 22);
    bc_pad(&b, 2);
}

static void payload_sf2(uint8_t p[192], const ephemeris_t *e)
{
    bitcur_t b = { p, 0, 192 };
    bc_u(&b, (uint32_t)e->iode & 0xFFu, 8);
    bc_s(&b, e->crs, pow(2.0, -5), 16);
    bc_s(&b, e->delta_n / M_PI, pow(2.0, -43), 16);   /* назад у напівоберти */
    bc_s(&b, e->m0 / M_PI, pow(2.0, -31), 32);
    bc_s(&b, e->cuc, pow(2.0, -29), 16);
    bc_uf(&b, e->ecc, pow(2.0, -33), 32);
    bc_s(&b, e->cus, pow(2.0, -29), 16);
    bc_uf(&b, e->sqrt_a, pow(2.0, -19), 32);
    bc_uf(&b, e->toe, 16.0, 16);
    bc_u(&b, 0, 1);                                   /* fit interval = 4 год */
    bc_u(&b, 31, 5);                                  /* AODO */
    bc_pad(&b, 2);
}

static void payload_sf3(uint8_t p[192], const ephemeris_t *e)
{
    bitcur_t b = { p, 0, 192 };
    bc_s(&b, e->cic, pow(2.0, -29), 16);
    bc_s(&b, e->omega0 / M_PI, pow(2.0, -31), 32);
    bc_s(&b, e->cis, pow(2.0, -29), 16);
    bc_s(&b, e->i0 / M_PI, pow(2.0, -31), 32);
    bc_s(&b, e->crc, pow(2.0, -5), 16);
    bc_s(&b, e->omega_arg / M_PI, pow(2.0, -31), 32);
    bc_s(&b, e->omega_dot / M_PI, pow(2.0, -43), 24);
    bc_u(&b, (uint32_t)e->iode & 0xFFu, 8);
    bc_s(&b, e->idot / M_PI, pow(2.0, -43), 14);
    bc_pad(&b, 2);
}

/* Сторінка 18 підкадру 4: коефіцієнти іоносфери та поправки шкали UTC —
 * тут же їде секунда координації, теперішня й майбутня. */
static void payload_sf4_p18(uint8_t p[192], const nav_context_t *ctx, gps_time_t t)
{
    static const double a_lsb[4] = {0x1p-30, 0x1p-27, 0x1p-24, 0x1p-24};
    static const double b_lsb[4] = {2048.0, 16384.0, 65536.0, 65536.0};

    bitcur_t b = { p, 0, 192 };
    bc_u(&b, 1, 2);                 /* data ID */
    bc_u(&b, 56, 6);                /* SV ID сторінки 18 */
    for (int i = 0; i < 4; ++i) bc_s(&b, ctx->hdr->alpha[i], a_lsb[i], 8);
    for (int i = 0; i < 4; ++i) bc_s(&b, ctx->hdr->beta[i],  b_lsb[i], 8);
    bc_s(&b, 0.0, 0x1p-50, 24);     /* A1 розходження шкал UTC/GPS */
    bc_s(&b, 0.0, 0x1p-30, 32);     /* A0 */
    bc_uf(&b, 0.0, 4096.0, 8);      /* tot */
    bc_u(&b, (uint32_t)gps_week10(t.week) & 0xFFu, 8);
    bc_s(&b, (double)ctx->leap.delta_t_ls,  1.0, 8);
    bc_u(&b, (uint32_t)(ctx->leap.wn_lsf & 0xFF), 8);
    bc_u(&b, (uint32_t)(ctx->leap.dn & 0xFF), 8);
    bc_s(&b, (double)ctx->leap.delta_t_lsf, 1.0, 8);
    bc_pad(&b, 14);
    bc_pad(&b, 2);
}

/* Сторінка 25 підкадру 5: стан сузір'я — здоров'я всіх апаратів. */
static void payload_sf5_p25(uint8_t p[192], const nav_context_t *ctx, gps_time_t t)
{
    bitcur_t b = { p, 0, 192 };
    bc_u(&b, 1, 2);
    bc_u(&b, 51, 6);
    bc_uf(&b, fmod(t.tow, 604800.0), 4096.0, 8);      /* toa */
    bc_u(&b, (uint32_t)gps_week10(t.week) & 0xFFu, 8);
    for (int i = 0; i < 24; ++i) bc_u(&b, (uint32_t)(ctx->sv_health[i] & 0x3F), 6);
    bc_pad(&b, 22);
    bc_pad(&b, 2);
}

/* ---- кадр --------------------------------------------------------------- */

void nav_frame_build(nav_frame_t *fr, const ephemeris_t *e,
                     const nav_context_t *ctx, gps_time_t frame_start)
{
    /* Кадр завжди починається на межі 30 с — інакше приймач не зловить преамбулу. */
    frame_start.tow = floor(frame_start.tow / 30.0) * 30.0;
    fr->start = frame_start;

    uint8_t payload[5][192];
    memset(payload, 0, sizeof payload);
    payload_sf1(payload[0], e);
    payload_sf2(payload[1], e);
    payload_sf3(payload[2], e);
    payload_sf4_p18(payload[3], ctx, frame_start);
    payload_sf5_p25(payload[4], ctx, frame_start);

    int d29 = 0, d30 = 0;
    for (int sf = 0; sf < 5; ++sf) {
        build_subframe(fr->bits + sf * NAV_SUBFRAME_BITS, sf + 1,
                       frame_start.tow + sf * 6.0, payload[sf], &d29, &d30);
    }
}

int nav_bit_index(const nav_frame_t *fr, gps_time_t t_tx)
{
    double dt = gps_time_diff(t_tx, fr->start);
    if (dt < 0.0 || dt >= 30.0) return -1;      /* кадр треба перебудувати */
    return (int)(dt * NAV_BIT_RATE_HZ);
}

int nav_bit(const nav_frame_t *fr, long index)
{
    long i = index % NAV_FRAME_BITS;
    if (i < 0) i += NAV_FRAME_BITS;
    return fr->bits[i];
}
