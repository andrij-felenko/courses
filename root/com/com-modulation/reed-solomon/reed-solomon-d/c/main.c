#include <stdint.h>
#include <string.h>
#include <stdio.h>

/* Поле GF(2^8) з примітивним поліномом x^8+x^4+x^3+x^2+1 (0x11D), генератор α = 2. */
static uint8_t gf_exp[512];   /* антилогарифм: gf_exp[i] = α^i        */
static uint8_t gf_log[256];   /* логарифм:     gf_log[α^i] = i         */

static void gf_init(void) {
    uint16_t x = 1;
    for (int i = 0; i < 255; i++) {
        gf_exp[i] = (uint8_t)x;
        gf_log[x] = (uint8_t)i;
        x <<= 1;                       /* множення на α — це зсук уліво… */
        if (x & 0x100) x ^= 0x11D;     /* …з редукцією за модулем полінома поля */
    }
    for (int i = 255; i < 512; i++)    /* подвоєна таблиця — щоб не брати mod 255 */
        gf_exp[i] = gf_exp[i - 255];
}

/* Множення в полі: α^(log a + log b). Нуль поглинає. */
static uint8_t gf_mul(uint8_t a, uint8_t b) {
    if (a == 0 || b == 0) return 0;
    return gf_exp[gf_log[a] + gf_log[b]];   /* сума логарифмів < 510 — індекс безпечний */
}

/* Породжувальний поліном g(x) = Π_{j=1}^{nsym} (x − α^j), коефіцієнти від старшого. */
static void rs_gen_poly(uint8_t *gen, int nsym) {   /* gen має nsym+1 комірок, gen[0]=1 */
    gen[0] = 1;
    int len = 1;
    for (int j = 1; j <= nsym; j++) {
        uint8_t root = gf_exp[j];      /* черговий корінь α^j */
        gen[len] = 0;                  /* множення на (x − α^j) підіймає степінь на 1 */
        for (int i = len; i > 0; i--)
            gen[i] ^= gf_mul(gen[i - 1], root);   /* − дорівнює + над GF(2^m) */
        len++;
    }
}

/* Систематичне кодування: out[0..k-1] = дані, out[k..n-1] = контрольні символи. */
static void rs_encode(const uint8_t *msg, int k,
                      const uint8_t *gen, int nsym, uint8_t *out) {
    memcpy(out, msg, k);
    memset(out + k, 0, nsym);          /* зсув на nsym: дописуємо nsym нулів */
    for (int i = 0; i < k; i++) {      /* синтетичне ділення на g(x) */
        uint8_t coef = out[i];         /* провідний коефіцієнт поточного залишку */
        if (coef != 0)
            for (int j = 0; j <= nsym; j++)
                out[i + j] ^= gf_mul(gen[j], coef);   /* віднімаємо coef·g, зсунутий на i */
    }
    memcpy(out, msg, k);               /* остача лягла в хвіст; дані вертаємо поверх */
}

int main(void) {
    gf_init();
    int k = 223, nsym = 32, n = k + nsym;   /* RS(255, 223) */
    uint8_t gen[33], msg[223], code[255];
    for (int i = 0; i < k; i++) msg[i] = (uint8_t)(i * 7 + 1);   /* якісь дані */
    rs_gen_poly(gen, nsym);
    rs_encode(msg, k, gen, nsym, code);
    printf("32 контрольні байти:");
    for (int i = k; i < n; i++) printf(" %02X", code[i]);
    printf("\n");
    return 0;
}
