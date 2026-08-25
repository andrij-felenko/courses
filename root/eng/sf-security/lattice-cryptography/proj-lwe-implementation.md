# Проєкт реалізації криптосистеми LWE (Learning With Errors)

Цей проєкт містить повну, працездатну та навчальну реалізацію базової асиметричної криптосистеми шифрування на основі проблеми навчання з помилками (LWE) мовами C та C++.

## 1. Архітектурна ідея та математичний регламент

Криптосистема виконує побітове шифрування повідомлення за допомогою модулярних лінійних рівнянь з додаванням дискретного гаусового шуму.

### Основні компоненти алгоритму

1. **Генерація ключів (Key Generation)**:
   - Секретний ключ `sk` створюється як випадковий вектор `s ∈ Z_qⁿ`, де `n = 32` — розмірність секрету, `q = 3329` — модулярне просте число (аналог параметра стандарту Kyber).
   - Публічний ключ `pk` будується з випадкової матриці `A ∈ Z_q^(m × n)` (де `m = 64` — кількість LWE рівнянь) та зашумленого вектора `b ∈ Z_qᵐ`:
     ```
     b = A · s + e  (mod q)
     ```
     де `e ∈ Z^m` — малий вектор шуму, кожен елемент якого згенеровано з дискретного гаусового розподілу зі середньоквадратичним відхиленням `σ = 2.0`.
   - Публічним ключем є пара `(A, b)`, а секретним ключем — вектор `s`.

2. **Шифрування (Encryption)**:
   - Для шифрування одного біта повідомлення `m_bit ∈ {0, 1}` обирається випадковий маскувальний вектор `r ∈ {0, 1}ᵐ`.
   - Обчислюються два шифротекстові елементи `(c₁, c₂)`:
     ```
     c₁ = Aᵀ · r  (mod q)
     c₂ = bᵀ · r + m_bit · ⌊q / 2⌋  (mod q)
     ```
   - Вектор `c₁` має розмірність `n`, а `c₂` є скаляром у `Z_q`.

3. **Розшифрування (Decryption)**:
   - Володар секретного ключа `s` відновлює значення `d` за допомогою скалярного добутку:
     ```
     d = c₂ - c₁ᵀ · s  (mod q)
     ```
   - Завдяки математичній тотожності `d = m_bit · ⌊q / 2⌋ + eᵀ · r (mod q)`.
   - Якщо відстань від `d` до `q / 2` менша за `q / 4`, розшифрований біт дорівнює `1`, інакше — `0`.

## 2. Реалізація мовами C та C++

Нижче наведено ідіоматичні реалізації криптосистеми. Таб C показує низькорівневе управління масивами та обчисленням арифметики за модулем, а таб C++ використовує концепції RAII, безпечні контейнери `std::vector` та стандартні генератори `std::mt19937`.

:::tabs
```c
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
```
```cpp
#include <iostream>
#include <vector>
#include <random>
#include <cmath>
#include <memory>
#include <numeric>

class LWEEngine {
public:
    static constexpr int N = 32;
    static constexpr int M = 64;
    static constexpr int Q = 3329;
    static constexpr double SIGMA = 2.0;

    struct SecretKey {
        std::vector<int> s;
        SecretKey() : s(N) {}
    };

    struct PublicKey {
        std::vector<std::vector<int>> A;
        std::vector<int> b;
        PublicKey() : A(M, std::vector<int>(N)), b(M) {}
    };

    struct Ciphertext {
        std::vector<int> c1;
        int c2;
        Ciphertext() : c1(N), c2(0) {}
    };

    LWEEngine() : rng(std::random_device{}()) {}

    void keygen(PublicKey& pk, SecretKey& sk) {
        std::uniform_int_distribution<int> dist_q(0, Q - 1);
        std::normal_distribution<double> dist_gauss(0.0, SIGMA);

        for (int j = 0; j < N; ++j) {
            sk.s[j] = dist_q(rng);
        }

        for (int i = 0; i < M; ++i) {
            long long ax = 0;
            for (int j = 0; j < N; ++j) {
                pk.A[i][j] = dist_q(rng);
                ax = (ax + static_cast<long long>(pk.A[i][j]) * sk.s[j]) % Q;
            }
            int noise = static_cast<int>(std::round(dist_gauss(rng)));
            pk.b[i] = mod_q(static_cast<int>(ax) + noise);
        }
    }

    Ciphertext encrypt(const PublicKey& pk, int bit) {
        Ciphertext ct;
        std::uniform_int_distribution<int> dist_bin(0, 1);
        std::vector<int> r(M);
        for (int i = 0; i < M; ++i) r[i] = dist_bin(rng);

        for (int j = 0; j < N; ++j) {
            long long sum = 0;
            for (int i = 0; i < M; ++i) {
                sum = (sum + static_cast<long long>(pk.A[i][j]) * r[i]) % Q;
            }
            ct.c1[j] = static_cast<int>(sum);
        }

        long long b_r = 0;
        for (int i = 0; i < M; ++i) {
            b_r = (b_r + static_cast<long long>(pk.b[i]) * r[i]) % Q;
        }
        int scale = (bit == 1) ? (Q / 2) : 0;
        ct.c2 = mod_q(static_cast<int>(b_r) + scale);
        return ct;
    }

    int decrypt(const Ciphertext& ct, const SecretKey& sk) const {
        long long c1_s = 0;
        for (int j = 0; j < N; ++j) {
            c1_s = (c1_s + static_cast<long long>(ct.c1[j]) * sk.s[j]) % Q;
        }
        int diff = mod_q(ct.c2 - static_cast<int>(c1_s));

        int dist_to_half = std::abs(diff - Q / 2);
        return (dist_to_half < Q / 4) ? 1 : 0;
    }

private:
    static inline int mod_q(int x) {
        int r = x % Q;
        return (r < 0) ? (r + Q) : r;
    }

    std::mt19937 rng;
};

int main() {
    LWEEngine engine;
    LWEEngine::SecretKey sk;
    LWEEngine::PublicKey pk;

    engine.keygen(pk, sk);

    std::vector<int> test_bits = {1, 0, 1, 1, 0, 0, 1, 0};
    std::cout << "--- Тест C++ LWE Engine ---\n";

    for (size_t i = 0; i < test_bits.size(); ++i) {
        auto ct = engine.encrypt(pk, test_bits[i]);
        int decrypted = engine.decrypt(ct, sk);
        std::cout << "Bit " << i << ": Input = " << test_bits[i] 
                  << ", Decrypted = " << decrypted 
                  << " [" << (test_bits[i] == decrypted ? "OK" : "FAIL") << "]\n";
    }

    return 0;
}
```
:::

## 3. Покрокове простеження роботи алгоритму (Execution Trace)

Для кращого розуміння простежимо рух даних під час шифрування одного біта `m_bit = 1`:

1. **Фаза KeyGen**:
   - Нехай `n = 2, m = 3, q = 17`.
   - Згенеровано секретний вектор `s = [3, 5]ᵀ`.
   - Випадкова матриця `A`:
     ```
     A = [[2, 4],
          [6, 1],
          [3, 2]]
     ```
   - Обчислюється `A · s mod 17`:
     - Рядок 0: `2·3 + 4·5 = 26 ≡ 9 (mod 17)`.
     - Рядок 1: `6·3 + 1·5 = 23 ≡ 6 (mod 17)`.
     - Рядок 2: `3·3 + 2·5 = 19 ≡ 2 (mod 17)`.
   - Згенеровано вектор шуму `e = [1, -1, 0]ᵀ`.
   - Вектор `b = [9+1, 6-1, 2+0]ᵀ = [10, 5, 2]ᵀ (mod 17)`.
   - Публічний ключ: пара `(A, b)`.

2. **Фаза Encrypt (для m_bit = 1)**:
   - Маскувальний вектор `r = [1, 0, 1]ᵀ`.
   - `c₁ = Aᵀ · r = [2·1 + 6·0 + 3·1, 4·1 + 1·0 + 2·1]ᵀ = [5, 6]ᵀ (mod 17)`.
   - `bᵀ · r = 10·1 + 5·0 + 2·1 = 12 (mod 17)`.
   - Значення масштабування для `m_bit = 1`: `⌊17 / 2⌋ = 8`.
   - `c₂ = 12 + 8 = 20 ≡ 3 (mod 17)`.
   - Шифротекст: `(c₁ = [5, 6]ᵀ, c₂ = 3)`.

3. **Фаза Decrypt**:
   - `c₁ᵀ · s = 5·3 + 6·5 = 15 + 30 = 45 ≡ 11 (mod 17)`.
   - `diff = c₂ - c₁ᵀ · s = 3 - 11 = -8 ≡ 9 (mod 17)`.
   - Відстань від `diff = 9` до `q / 2 = 8` дорівнює `|9 - 8| = 1`.
   - Оскільки `1 < 17 / 4 = 4.25`, алгоритм упевнено повертає біт `1`.

## 4. Перехід до Ring-LWE та оптимізація пам'яті

У стандартному LWE матриця `A` вимагає збереження `m × n` коефіцієнтів, що при `m = 1024, n = 512` дає `524 288` елементів у пам'яті (понад 1 мегабайт).

У кільцевих версіях Ring-LWE матриця `A` замінюється циклічними зсувами одного полінома `a(X) ∈ Z_q[X] / (Xⁿ + 1)`.

Множення `A · s` перетворюється на поліноміальне множення `a(X) · s(X) mod (Xⁿ + 1)`.

Замість виконання квадратичного множення `O(n²)` застосовується алгоритм **NTT (Number Theoretic Transform)**, який виконує перетворення за крок `O(n log n)`:

```
c(X) = NTT⁻¹( NTT(a) ⊙ NTT(s) )
```

Де `⊙` позначає покомпонентне множення векторів довжини `n`. Завдяки NTT розміри публічних ключів у сучасних системах ML-KEM-768 скорочуються до 1184 байт, а швидкість шифрування досягає мільйонів операцій на секунду.

## 5. Детальний аналіз реалізації та алгоритмічний розбір

### Генерація дискретного гаусового шуму

У табі мови C генерація шуму виконується за допомогою методом Бокса–Мюллера (Box-Muller transform). Метод перетворює дві незалежні випадкові величини `u₁, u₂`, рівномірно розподілені на інтервалі `(0, 1]`, у псевдовипадкову величину з нормальним гаусовим розподілом:

```
z = √(-2 · ln(u₁)) · cos(2π · u₂)
```

Отримане значення `z` множиться на потрібне середньоквадратичне відхилення `σ = 2.0` і округлюється до найближчого цілого числа.

У табі C++ генерація виконується ідіоматично за допомогою стандартного компонента `<random>`: `std::normal_distribution<double> dist_gauss(0.0, SIGMA)` в зв'язці з генератором вихрового Мерсенна `std::mt19937`.

### Детальний аналіз крайових випадків та пасток реалізації

#### 1. Переповнення цілочисельних типів (Integer Overflow)

У коді обчислення скалярного добутку `A · s` сума добутків виконується для `N = 32` елементів. Оскільки кожен коефіцієнт `A[i][j]` та `s[j]` може досягати `Q - 1 = 3328`, добуток `A[i][j] · s[j]` досягає `3328² ≈ 11.07 · 10⁶`. 

Для `N = 32` максимальна сума без приведення за модулем становить `32 · 11.07 · 10⁶ ≈ 354 · 10⁶`, що ще вміщується у 32-бітне знакова ціле число `int32_t` (максимум `2.14 · 10⁹`). Проте для криптографічних параметрів `N = 512` сума досягає `5.6 · 10⁹`, що призводить до негайного переповнення `int32_t` та невизначеної поведінки (undefined behavior).

Тому в коді застосовано розширення типів при проміжних обчисленнях:

:::tabs
```c
long long ax = 0;
ax = (ax + (long long)pk->A[i][j] * sk->s[j]) % Q;
```
```cpp
long long ax = 0;
ax = (ax + static_cast<long long>(pk.A[i][j]) * sk.s[j]) % Q;
```
:::

#### 2. Специфіка оператора залишку від ділення `%` у мові C

У мовах C та C++ оператор `%` реалізує усічене ділення (truncated division), а не математичний залишок. Для від'ємного числа `x = -5` вираз `-5 % 3329` повертає `-5`, а не `3324`.

Це призводить до помилок при відніманні `diff = c2 - c1ᵀ · s`. Щоб гарантувати, що результат завжди лежить у діапазоні `[0, Q - 1]`, використовується допоміжна функція `mod_q`:

:::tabs
```c
static inline int mod_q(int x) {
    int r = x % Q;
    return (r < 0) ? (r + Q) : r;
}
```
```cpp
static inline int mod_q(int x) {
    int r = x % Q;
    return (r < 0) ? (r + Q) : r;
}
```
:::

#### 3. Криптографічна стійкість генератора випадкових чисел

У наведеному навчальному коді використовується виклик `rand()` та `std::mt19937`. Навчальний `rand()` є генератором Лінійного Конгруентного Метод (LCG), стан якого легко відновлюється за кількома виходами.

У виробничих постквантових системах вимагається використання криптографічно стійких генераторів псевдовипадкових чисел (CSPRNG):
- На операційних системах Unix/Linux: виклик `getrandom()` або читання з `/dev/urandom`.
- На Windows: виклики `BCryptGenRandom()`.
- Крім того, гаусові шуми вибіраються не через логарифмічний алгоритм Бокса-Мюллера (який використовує числа з плаваючою крапкою й відкритий до хронометричних атак), а через біноміальний розподіл `Centered Binomial Distribution (CBD)`, який реалізується підрахунком одиничних бітів у згенерованому байтовому масиві.

#### 4. Векторна оптимізація (SIMD / AVX2)

Множення матриці на вектор `A · s` є основною гарячою точкою (hotspot) алгоритму. На сучасних процесорах x86-64 операція виконується за допомогою AVX2 інструкцій `_mm256_madd_epi16` та `_mm256_mullo_epi32`, які дозволяють обробляти по 8 або 16 коефіцієнтів за один такт процесора, що прискорює виконання процедури шифрування у 10-15 разів.
