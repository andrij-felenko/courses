#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

/* Прості криптографічні параметри для демонстрації */
/* p = 23, q = 11, g = 2 (порядок елемента 2 у Z_23* дорівнює 11) */
#define MOD_P 23LL
#define ORDER_Q 11LL
#define GEN_G 2LL

/* Швидке піднесення до степеня за модулем: (base^exp) % mod */
static int64_t power_mod(int64_t base, int64_t exp, int64_t mod) {
    int64_t result = 1;
    base = base % mod;
    while (exp > 0) {
        if (exp % 2 == 1) {
            result = (result * base) % mod;
        }
        base = (base * base) % mod;
        exp /= 2;
    }
    return result;
}

/* Обчислення оберненого елемента за модулем через розширений алгоритм Евкліда */
static int64_t mod_inverse(int64_t a, int64_t m) {
    int64_t m0 = m, t, q;
    int64_t x0 = 0, x1 = 1;
    if (m == 1) return 0;
    while (a > 1) {
        q = a / m;
        t = m;
        m = a % m;
        a = t;
        t = x0;
        x0 = x1 - q * x0;
        x1 = t;
    }
    if (x1 < 0) x1 += m0;
    return x1;
}

/* Структура для зберігання транскрипту взаємодії */
typedef struct {
    int64_t commitment_R;  /* R = g^r mod p */
    int64_t challenge_e;   /* e ∈ [0, q-1] */
    int64_t response_s;    /* s = (r + e * x) mod q */
} SchnorrTranscript;

/* Крок 1: Реальне виконання між Доводжувачем та Верифікатором */
bool run_real_protocol(int64_t secret_x, int64_t random_r, int64_t challenge_e, SchnorrTranscript *out_transcript) {
    /* Обчислення публічного ключа Y = g^x mod p */
    int64_t public_Y = power_mod(GEN_G, secret_x, MOD_P);

    /* 1. Доводжувач надсилає зобов'язання R = g^r mod p */
    int64_t R = power_mod(GEN_G, random_r, MOD_P);

    /* 2. Доводжувач обчислює відповідь s = (r + e * x) mod q */
    int64_t s = (random_r + challenge_e * secret_x) % ORDER_Q;

    out_transcript->commitment_R = R;
    out_transcript->challenge_e = challenge_e;
    out_transcript->response_s = s;

    /* 3. Верифікатор перевіряє: g^s ≡ R * Y^e (mod p) */
    int64_t left_side = power_mod(GEN_G, s, MOD_P);
    int64_t Y_to_e = power_mod(public_Y, challenge_e, MOD_P);
    int64_t right_side = (R * Y_to_e) % MOD_P;

    printf("[Реальний протокол] P(x=%lld): R=%lld, e=%lld, s=%lld -> Перевірка: %lld == %lld\n",
           secret_x, R, challenge_e, s, left_side, right_side);

    return left_side == right_side;
}

/* Крок 2: Симулятор чесного верифікатора (HVZK Simulator) */
/* Симулятор НЕ ZНАЄ secret_x! Він згенеровує валідний транскрипт навпаки */
SchnorrTranscript run_hvzk_simulator(int64_t public_Y, int64_t sim_challenge_e, int64_t sim_response_s) {
    SchnorrTranscript transcript;
    transcript.challenge_e = sim_challenge_e;
    transcript.response_s = sim_response_s;

    /* Симулятор обчислює фальшиве зобов'язання R = g^s * Y^(-e) mod p */
    int64_t g_to_s = power_mod(GEN_G, sim_response_s, MOD_P);
    int64_t Y_to_e = power_mod(public_Y, sim_challenge_e, MOD_P);
    int64_t Y_to_minus_e = mod_inverse(Y_to_e, MOD_P);

    transcript.commitment_R = (g_to_s * Y_to_minus_e) % MOD_P;

    /* Перевіряємо рівність верифікатора для симульованого транскрипту */
    int64_t check_left = power_mod(GEN_G, transcript.response_s, MOD_P);
    int64_t check_right = (transcript.commitment_R * Y_to_e) % MOD_P;

    printf("[Симулятор HVZK] БЕЗ СЕКРЕТУ: R=%lld, e=%lld, s=%lld -> Перевірка: %lld == %lld\n",
           transcript.commitment_R, transcript.challenge_e, transcript.response_s, check_left, check_right);

    return transcript;
}

/* Крок 3: Екстрактор знань (Knowledge Extractor) */
/* Видобуває секрет x з двох транскриптів із однаковим R, але різними e1 != e2 */
int64_t extract_secret(const SchnorrTranscript *t1, const SchnorrTranscript *t2) {
    if (t1->commitment_R != t2->commitment_R) {
        fprintf(stderr, "Помилка екстрактора: зобов'язання R не збігаються!\n");
        return -1;
    }
    if (t1->challenge_e == t2->challenge_e) {
        fprintf(stderr, "Помилка екстрактора: однакові виклики e!\n");
        return -1;
    }

    int64_t delta_s = (t1->response_s - t2->response_s + ORDER_Q) % ORDER_Q;
    int64_t delta_e = (t1->challenge_e - t2->challenge_e + ORDER_Q) % ORDER_Q;
    int64_t inv_delta_e = mod_inverse(delta_e, ORDER_Q);

    int64_t extracted_x = (delta_s * inv_delta_e) % ORDER_Q;
    return extracted_x;
}

int main(void) {
    int64_t secret_x = 7; /* Секретний ключ доводжувача */
    int64_t public_Y = power_mod(GEN_G, secret_x, MOD_P);
    printf("--- Запуск реального протоколу Шнорра ---\n");
    printf("Публічний ключ Y = g^x mod p -> %lld = %lld^%lld mod %lld\n", public_Y, GEN_G, secret_x, MOD_P);

    SchnorrTranscript t1, t2;
    int64_t random_r = 4;

    /* Виконання 1: e = 3 */
    bool ok1 = run_real_protocol(secret_x, random_r, 3, &t1);
    /* Виконання 2 (з тим самим r): e = 8 */
    bool ok2 = run_real_protocol(secret_x, random_r, 8, &t2);

    if (ok1 && ok2) {
        printf("\n--- Запуск екстрактора знань ---\n");
        int64_t recovered_x = extract_secret(&t1, &t2);
        printf("Відновлений секретний ключ x = %lld (Очікувалось: %lld)\n", recovered_x, secret_x);
    }

    printf("\n--- Запуск симулятора (без секретного ключа) ---\n");
    SchnorrTranscript sim_t = run_hvzk_simulator(public_Y, 5, 9);
    (void)sim_t;

    return 0;
}
