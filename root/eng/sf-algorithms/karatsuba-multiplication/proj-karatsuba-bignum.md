# ⚙️ Реалізація множення великих чисел алгоритмом Карацуби

Робота з криптографічними ключами RSA, еліптичними кривими великої розрядності або науковими обчисленнями довільної точності вимагає швидкого множення масивів слів. Наївна рекурсивна реалізація алгоритму Карацуби часто виявляється повільнішою за класичний стовпчик через неконтрольовані виділення динамічної пам'яті у вузлах рекурсивного дерева та високі накладні витрати для малих розмірів входу. Промислова реалізація поєднує попереднє виділення єдиного лінійного буфера пам'яті (скретчпада) та гібридне перемикання на шкільний метод на нижніх рівнях рекурсії.

---

## Архітектура представлення чисел та структура пам'яті

Велике ціле число представляється у пам'яті як неперервний масив беззнакових 32-розрядних слів (лімбів, `uint32_t`) у прямому порядку розрядів (*little-endian*): наймолодший лімб зберігається за нульовим індексом `0`, а кожне наступне слово відповідає зростанню степеня основи `B = 2³²`. Кожне машинне слово зберігає рівно 32 двійкові розряди числа, а проміжний добуток двох таких слів гарантовано поміщається у стандартний 64-розрядний цілочисельний акумулятор процесора `uint64_t`.

Арифметичний добуток двох чисел довжиною `n` лімбів має максимальну довжину до `2n` лімбів. У рекурсивній схемі Карацуби вхідні масиви розбиваються навпіл на дві рівні частини розміром `m = n/2` лімбів.

Головні інженерні виклики при створенні надійного коду:
1. **Управління пам'яттю без викликів системного алокатора:** Для запобігання деградації продуктивності через тисячі викликів функцій `malloc()` та `free()` у рекурсивних гілках один неперервний робочий масив розміром `4n` слів виділяється один-єдиний раз на початку обчислення і передається вглиб дерева рекурсії у вигляді зміщеного покажчика.
2. **Обробка переповнення при додаванні половин:** Сума двох `m`-значних чисел `X_h + X_l` може вимагати для свого точного представлення `m + 1` лімбів через виникнення вихідного біта перенесення (*carry*). Цей додатковий старший біт враховується спеціальною процедурою корекції проміжного добутку `Z_mid`.
3. **Гібридне відсікання (*crossover threshold*):** Для операндів розміром `n ≤ 32` слів рекурсія припиняється, і керування передається базовому шкільному множенню у стовпчик, яке ефективно використовує регістри загального призначення процесора та інструкції злитого множення й накопичення.

---

## Робочий код: C та ідіоматичний C++

:::tabs
```c
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <string.h>

#define KARATSUBA_THRESHOLD 32

/* Базове множення у стовпчик O(n^2) для малого розміру n */
void schoolbook_mul(const uint32_t *a, const uint32_t *b, uint32_t *out, size_t n) {
    memset(out, 0, 2 * n * sizeof(uint32_t));
    for (size_t i = 0; i < n; ++i) {
        if (a[i] == 0) continue;
        uint64_t carry = 0;
        for (size_t j = 0; j < n; ++j) {
            uint64_t cur = (uint64_t)out[i + j] + (uint64_t)a[i] * (uint64_t)b[j] + carry;
            out[i + j] = (uint32_t)cur;
            carry = cur >> 32;
        }
        out[i + n] += (uint32_t)carry;
    }
}

/* Додавання двох масивів довжини n з поверненням біта перенесення */
uint32_t bignum_add_n(const uint32_t *a, const uint32_t *b, uint32_t *out, size_t n) {
    uint64_t carry = 0;
    for (size_t i = 0; i < n; ++i) {
        uint64_t sum = (uint64_t)a[i] + (uint64_t)b[i] + carry;
        out[i] = (uint32_t)sum;
        carry = sum >> 32;
    }
    return (uint32_t)carry;
}

/* Віднімання bignum: a - b, повертає запозичення (borrow: 0 або 1) */
uint32_t bignum_sub_n(const uint32_t *a, const uint32_t *b, uint32_t *out, size_t n) {
    int64_t borrow = 0;
    for (size_t i = 0; i < n; ++i) {
        int64_t diff = (int64_t)a[i] - (int64_t)b[i] - borrow;
        if (diff < 0) {
            out[i] = (uint32_t)(diff + 0x100000000ULL);
            borrow = 1;
        } else {
            out[i] = (uint32_t)diff;
            borrow = 0;
        }
    }
    return (uint32_t)borrow;
}

/* Додавання до акумулятора з позиції offset */
void bignum_add_offset(uint32_t *dst, const uint32_t *src, size_t n, size_t offset, size_t dst_len) {
    uint64_t carry = 0;
    for (size_t i = 0; i < n && (offset + i) < dst_len; ++i) {
        uint64_t sum = (uint64_t)dst[offset + i] + (uint64_t)src[i] + carry;
        dst[offset + i] = (uint32_t)sum;
        carry = sum >> 32;
    }
    for (size_t i = offset + n; carry != 0 && i < dst_len; ++i) {
        uint64_t sum = (uint64_t)dst[i] + carry;
        dst[i] = (uint32_t)sum;
        carry = sum >> 32;
    }
}

/* Рекурсивне множення Карацуби зі скретчпадом */
void karatsuba_rec(const uint32_t *a, const uint32_t *b, uint32_t *out, size_t n, uint32_t *scratch) {
    if (n <= KARATSUBA_THRESHOLD) {
        schoolbook_mul(a, b, out, n);
        return;
    }

    size_t m = n / 2;
    const uint32_t *a_l = a;
    const uint32_t *a_h = a + m;
    const uint32_t *b_l = b;
    const uint32_t *b_h = b + m;

    uint32_t *z0 = out;
    uint32_t *z2 = out + 2 * m;

    /* Робоча пам'ять:
       scratch[0 .. 2m-1] -> z_mid
       scratch[2m .. 3m-1] -> sum_a (m лімбів)
       scratch[3m .. 4m-1] -> sum_b (m лімбів)
       scratch[4m .. ] -> вкладений скретчпад для рекурсії */
    uint32_t *z_mid = scratch;
    uint32_t *sum_a = scratch + 2 * m;
    uint32_t *sum_b = scratch + 3 * m;
    uint32_t *sub_scratch = scratch + 4 * m;

    /* 1. Обчислення Z0 = a_l * b_l */
    karatsuba_rec(a_l, b_l, z0, m, sub_scratch);

    /* 2. Обчислення Z2 = a_h * b_h */
    karatsuba_rec(a_h, b_h, z2, m, sub_scratch);

    /* 3. Формування сум половин */
    uint32_t carry_a = bignum_add_n(a_l, a_h, sum_a, m);
    uint32_t carry_b = bignum_add_n(b_l, b_h, sum_b, m);

    /* 4. Обчислення Z_mid = (a_l + a_h) * (b_l + b_h) */
    karatsuba_rec(sum_a, sum_b, z_mid, m, sub_scratch);

    /* Корекція Z_mid для старших бітів перенесення carry_a та carry_b */
    if (carry_a) bignum_add_offset(z_mid, sum_b, m, m, 2 * m);
    if (carry_b) bignum_add_offset(z_mid, sum_a, m, m, 2 * m);

    /* 5. Z1 = Z_mid - Z0 - Z2 */
    bignum_sub_n(z_mid, z0, z_mid, 2 * m);
    bignum_sub_n(z_mid, z2, z_mid, 2 * m);

    /* 6. Додавання Z1 зі зсувом на m слів */
    bignum_add_offset(out, z_mid, 2 * m, m, 2 * n);
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <vector>
#include <span>
#include <algorithm>

class KaratsubaEngine {
public:
    static constexpr size_t Threshold = 32;

    static void multiply(std::span<const uint32_t> a,
                         std::span<const uint32_t> b,
                         std::span<uint32_t> out) {
        size_t n = a.size();
        std::vector<uint32_t> scratch(4 * n, 0);
        multiplyRecursive(a, b, out, scratch.data());
    }

private:
    static void schoolbook(std::span<const uint32_t> a,
                           std::span<const uint32_t> b,
                           std::span<uint32_t> out) {
        size_t n = a.size();
        std::fill(out.begin(), out.end(), 0);
        for (size_t i = 0; i < n; ++i) {
            if (a[i] == 0) continue;
            uint64_t carry = 0;
            for (size_t j = 0; j < n; ++j) {
                uint64_t cur = static_cast<uint64_t>(out[i + j]) +
                               static_cast<uint64_t>(a[i]) * b[j] + carry;
                out[i + j] = static_cast<uint32_t>(cur);
                carry = cur >> 32;
            }
            out[i + n] += static_cast<uint32_t>(carry);
        }
    }

    static uint32_t addN(std::span<const uint32_t> a,
                         std::span<const uint32_t> b,
                         std::span<uint32_t> out) {
        uint64_t carry = 0;
        for (size_t i = 0; i < a.size(); ++i) {
            uint64_t sum = static_cast<uint64_t>(a[i]) + b[i] + carry;
            out[i] = static_cast<uint32_t>(sum);
            carry = sum >> 32;
        }
        return static_cast<uint32_t>(carry);
    }

    static void subN(std::span<uint32_t> dst, std::span<const uint32_t> src) {
        int64_t borrow = 0;
        for (size_t i = 0; i < dst.size(); ++i) {
            int64_t diff = static_cast<int64_t>(dst[i]) - src[i] - borrow;
            if (diff < 0) {
                dst[i] = static_cast<uint32_t>(diff + 0x100000000ULL);
                borrow = 1;
            } else {
                dst[i] = static_cast<uint32_t>(diff);
                borrow = 0;
            }
        }
    }

    static void addWithOffset(std::span<uint32_t> dst,
                              std::span<const uint32_t> src,
                              size_t offset) {
        uint64_t carry = 0;
        for (size_t i = 0; i < src.size() && (offset + i) < dst.size(); ++i) {
            uint64_t sum = static_cast<uint64_t>(dst[offset + i]) + src[i] + carry;
            dst[offset + i] = static_cast<uint32_t>(sum);
            carry = sum >> 32;
        }
        for (size_t i = offset + src.size(); carry != 0 && i < dst.size(); ++i) {
            uint64_t sum = static_cast<uint64_t>(dst[i]) + carry;
            dst[i] = static_cast<uint32_t>(sum);
            carry = sum >> 32;
        }
    }

    static void multiplyRecursive(std::span<const uint32_t> a,
                                  std::span<const uint32_t> b,
                                  std::span<uint32_t> out,
                                  uint32_t* scratch) {
        size_t n = a.size();
        if (n <= Threshold) {
            schoolbook(a, b, out);
            return;
        }

        size_t m = n / 2;
        auto a_l = a.subspan(0, m);
        auto a_h = a.subspan(m, m);
        auto b_l = b.subspan(0, m);
        auto b_h = b.subspan(m, m);

        auto z0 = out.subspan(0, 2 * m);
        auto z2 = out.subspan(2 * m, 2 * m);

        uint32_t* z_mid_ptr = scratch;
        uint32_t* sum_a_ptr = scratch + 2 * m;
        uint32_t* sum_b_ptr = scratch + 3 * m;
        uint32_t* sub_scratch = scratch + 4 * m;

        std::span<uint32_t> z_mid(z_mid_ptr, 2 * m);
        std::span<uint32_t> sum_a(sum_a_ptr, m);
        std::span<uint32_t> sum_b(sum_b_ptr, m);

        // 1. Z0 = a_l * b_l
        multiplyRecursive(a_l, b_l, z0, sub_scratch);

        // 2. Z2 = a_h * b_h
        multiplyRecursive(a_h, b_h, z2, sub_scratch);

        // 3. Суми половин
        uint32_t carry_a = addN(a_l, a_h, sum_a);
        uint32_t carry_b = addN(b_l, b_h, sum_b);

        // 4. Z_mid = (a_l + a_h) * (b_l + b_h)
        multiplyRecursive(sum_a, sum_b, z_mid, sub_scratch);

        // Корекція перенесень
        if (carry_a != 0) addWithOffset(z_mid, sum_b, m);
        if (carry_b != 0) addWithOffset(z_mid, sum_a, m);

        // 5. Z1 = Z_mid - Z0 - Z2
        subN(z_mid, z0);
        subN(z_mid, z2);

        // 6. Додавання Z1 зі зсувом
        addWithOffset(out, z_mid, m);
    }
};
```
:::

---

## Покроковий розбір виконання на 4-лімбовому прикладі

Для детального розуміння взаємодії областей пам'яті та порядку викликів простежимо множення двох 4-лімбових чисел `A` та `B` (`n = 4`, розмір половини `m = 2`):

1. **Декомпозиція покажчиків:** Число `A` розбивається на молодшу частину `a_l = A[0..1]` та старшу `a_h = A[2..3]`. Аналогічно число `B` розділяється на `b_l = B[0..1]` та `b_h = B[2..3]`.
2. **Пряме збереження крайніх добутків:** Замість використання тимчасового буфера перший рекурсивний виклик `Z₀ = a_l · b_l` записує результат безпосередньо у молодші 4 лімби результуючого масиву `out[0..3]`. Другий виклик `Z₂ = a_h · b_h` записує результат у старші 4 лімби `out[4..7]`. У цей момент вихідний масив вже містить крайні блоки фінальної відповіді.
3. **Обчислення сум у скретчпаді:** Векторна сума `sum_a = a_l + a_h` зберігається у `scratch[4..5]`, повертаючи біт перенесення `carry_a`. Сума `sum_b = b_l + b_h` зберігається у `scratch[6..7]` із перенесенням `carry_b`.
4. **Обчислення допоміжного добутку:** Рекурсивний виклик обчислює добуток `sum_a · sum_b` розміром 4 лімби й записує його на початок робочої пам'яті — у `scratch[0..3]`. Якщо `carry_a` або `carry_b` були ненульовими, до `scratch[0..3]` додаються відповідні доданки зі зсувом `+2`.
5. **Виділення `Z₁`:** Від масиву `scratch[0..3]` послідовно віднімається блок `out[0..3]` (`Z₀`), а потім блок `out[4..7]` (`Z₂`). У результаті в `scratch[0..3]` формується чистий коефіцієнт `Z₁`.
6. **Фінальне злиття:** Масив `scratch[0..3]` додається до вихідного масиву `out` зі зсувом на `m = 2` слова (тобто додається до розрядів `out[2..5]`) з поширенням біта перенесення на старші розряди `out[6..7]`.

---

## Векторизація базового випадку інструкціями SIMD

Для досягнення максимальної швидкодії на сучасних процесорах функція `schoolbook_mul` може бути векторизована за допомогою розширень AVX-512IFMA (Integer Fused Multiply-Add). Інструкції `_mm512_madd52lo_epu64` та `_mm512_madd52hi_epu64` дозволяють перемножувати вісім 52-бітних чисел одночасно за один такт процесора з накопиченням у 64-розрядні вектори.

При використанні SIMD-прискореного базового випадку поріг відсікання `KARATSUBA_THRESHOLD` зазвичай зміщується вгору — від 32 до 64 або навіть 96 лімбів. Це пов'язано з тим, що векторизований стовпчик настільки ефективно утилізує конвеєри векторних модулів FMA, що рекурсивна декомпозиція Карацуби стає вигідною лише на більших обсягах вхідних даних.

---

## Інженерні пастки реалізації

1. **Непарна довжина операндів:** Якщо розмір `n` є непарним числом, операнди не можна розділити на дві однакові цілі половини. У такому випадку застосовують несиметричне розбиття: молодша частина отримує розмір `m = (n + 1) / 2`, а старша частина — `n - m`. Старшу частину перед виконанням додавання віртуально доповнюють нулями до довжини `m`.
2. **Абсолютні різниці замість сум (Варіант із модулем):** Щоб повністю усунути необхідність обробки бітів перенесення `carry_a` та `carry_b`, у деяких бібліотеках (зокрема у вихідному коді Python та GMP) обчислюють не добуток сум, а добуток абсолютних різниць: `Z_diff = |a_h - a_l| · |b_h - b_l|`. Оскільки різниця двох `m`-значних чисел завжди строго менша за основу `B^m`, довжина різниці гарантовано не перевищує `m` лімбів. Однак цей підхід вимагає збереження знакового біта: якщо знаки різниць однакові, середній член обчислюється як `Z₁ = Z₀ + Z₂ - Z_diff`, а якщо різні — як `Z₁ = Z₀ + Z₂ + Z_diff`.
3. **Кеш-локальність скретчпада:** Послідовний розподіл пам'яті у лінійному масиві дозволяє всім рекурсивним операціям залишатися всередині надшвидкої кеш-пам'яті L1 та L2 процесора. Оскільки робочі буфери багаторазово перезаписуються на кожному рівні рекурсії, рядки кешу залишаються «гарячими», що запобігає дорогим зверненням до оперативної пам'яті DDR.
4. **Контроль вирівнювання покажчиків:** Для забезпечення коректної роботи векторних завантажень масив скретчпада та вихідні буфери мають бути вирівняні за межею 64 байтів (розмір рядка кешу L1). Використання невирівняного доступу на деяких архітектурах спричиняє додаткові штрафні цикли конвеєра при перетині меж рядків кешу (*cache line splits*).
