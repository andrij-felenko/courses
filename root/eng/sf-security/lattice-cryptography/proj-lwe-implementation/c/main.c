#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

#define N 32        // Розмірність секретного вектора
#define M 64        // Кількість LWE рівнянь
#define Q 3329      // Модуль (просте число, аналог Kyber)
#define SIGMA 2.0   // Середньоквадратичне відхилення гаусового шуму

// Безпечне обчислення залишки від ділення для від'ємних чисел
static inline int mod_q(int x) {
    int r = x % Q;
    return (r < 0) ? (r + Q) : r;
}

// Генерація гаусового шуму методом Бокса-Мюллера
int sample_gaussian(double sigma) {
    double u1 = (double)rand() / RAND_MAX;
    double u2 = (double)rand() / RAND_MAX;
    if (u1 < 1e-10) u1 = 1e-10; // Запобігання log(0)
    double z = sqrt(-2.0 * log(u1)) * cos(2.0 * M_PI * u2);
    return (int)round(z * sigma);
}

typedef struct {
    int s[N];
} SecretKey;

typedef struct {
    int A[M][N];
    int b[M];
} PublicKey;

typedef struct {
    int c1[N];
    int c2;
} Ciphertext;

// Процедура генерації ключів
void keygen(PublicKey *pk, SecretKey *sk) {
    for (int j = 0; j < N; j++) {
        sk->s[j] = rand() % Q;
    }

    for (int i = 0; i < M; i++) {
        long long ax = 0;
        for (int j = 0; j < N; j++) {
            pk->A[i][j] = rand() % Q;
            ax = (ax + (long long)pk->A[i][j] * sk->s[j]) % Q;
        }
        int noise = sample_gaussian(SIGMA);
        pk->b[i] = mod_q((int)ax + noise);
    }
}

// Процедура шифрування біта
void encrypt(Ciphertext *ct, const PublicKey *pk, int bit) {
    int r[M];
    for (int i = 0; i < M; i++) {
        r[i] = rand() % 2; // Маскувальний вектор 0/1
    }

    for (int j = 0; j < N; j++) {
        long long sum = 0;
        for (int i = 0; i < M; i++) {
            sum = (sum + (long long)pk->A[i][j] * r[i]) % Q;
        }
        ct->c1[j] = (int)sum;
    }

    long long b_r = 0;
    for (int i = 0; i < M; i++) {
        b_r = (b_r + (long long)pk->b[i] * r[i]) % Q;
    }
    int scale = (bit == 1) ? (Q / 2) : 0;
    ct->c2 = mod_q((int)b_r + scale);
}

// Процедура розшифрування
int decrypt(const Ciphertext *ct, const SecretKey *sk) {
    long long c1_s = 0;
    for (int j = 0; j < N; j++) {
        c1_s = (c1_s + (long long)ct->c1[j] * sk->s[j]) % Q;
    }
    int diff = mod_q(ct->c2 - (int)c1_s);

    int dist_to_half = abs(diff - Q / 2);
    if (dist_to_half < Q / 4) {
        return 1;
    } else {
        return 0;
    }
}

int main() {
    srand((unsigned int)time(NULL));
    SecretKey sk;
    PublicKey pk;

    keygen(&pk, &sk);

    int test_bits[8] = {1, 0, 1, 1, 0, 0, 1, 0};
    printf("--- Тест C-реалізації LWE ---\n");

    for (int i = 0; i < 8; i++) {
        Ciphertext ct;
        encrypt(&ct, &pk, test_bits[i]);
        int decrypted = decrypt(&ct, &sk);
        printf("Біт %d: Вхід = %d, Розшифровано = %d [%s]\n",
               i, test_bits[i], decrypted, (test_bits[i] == decrypted) ? "OK" : "ПОМИЛКА");
    }

    return 0;
}
