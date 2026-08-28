#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <limits.h>

/* Структура для збереження результату Евклідового ділення */
typedef struct {
    int64_t quot; /* Частка q */
    int64_t rem;  /* Остача r, гарантовано 0 <= rem < |b| */
} EuclideanResult;

/*
 * Евклідове ділення: повертає q та r такі, що a = q*b + r та 0 <= r < |b|.
 * Коректно обробляє будь-які комбінації знаків a та b.
 */
EuclideanResult euclidean_div(int64_t a, int64_t b) {
    if (b == 0) {
        fprintf(stderr, "Критична помилка: ділення на нуль!\n");
        exit(EXIT_FAILURE);
    }

    int64_t q = a / b;
    int64_t r = a % b;

    /*
     * Якщо остача r від'ємна, коригуємо частку та остачу:
     * - Якщо d>0: q = q - 1, r = r + b
     * - Якщо d<0: q = q + 1, r = r - b
     */
    if (r < 0) {
        if (b > 0) {
            q -= 1;
            r += b;
        } else {
            q += 1;
            r -= b;
        }
    }

    EuclideanResult res = {q, r};
    return res;
}

/*
 * Безпечне додавання знакових 64-бітних чисел із детекцією переповнення.
 * Повертає false у разі виникнення переповнення.
 */
bool safe_add_int64(int64_t a, int64_t b, int64_t *out_result) {
    if ((b > 0 && a > INT64_MAX - b) || (b < 0 && a < INT64_MIN - b)) {
        return false; /* Переповнення виявлено */
    }
    *out_result = a + b;
    return true;
}

/*
 * Безпечне віднімання знакових 64-бітних чисел із детекцією переповнення.
 */
bool safe_sub_int64(int64_t a, int64_t b, int64_t *out_result) {
    if ((b > 0 && a < INT64_MIN + b) || (b < 0 && a > INT64_MAX + b)) {
        return false; /* Переповнення виявлено */
    }
    *out_result = a - b;
    return true;
}

/*
 * Безпечне множення знакових 64-бітних чисел із детекцією переповнення.
 */
bool safe_mul_int64(int64_t a, int64_t b, int64_t *out_result) {
    if (a == 0 || b == 0) {
        *out_result = 0;
        return true;
    }
    if (a > 0) {
        if (b > 0 && a > INT64_MAX / b) return false;
        if (b < 0 && b < INT64_MIN / a) return false;
    } else {
        if (b > 0 && a < INT64_MIN / b) return false;
        if (b < 0 && a < INT64_MAX / b) return false;
    }
    *out_result = a * b;
    return true;
}

/*
 * Апаратне бітове оперування: обчислення додаткового коду (~val + 1)
 * з попереднім зведенням до uint64_t для уникнення Undefined Behavior.
 */
uint64_t negate_twos_complement(int64_t val) {
    uint64_t uval = (uint64_t)val;
    return (~uval) + 1U;
}

/* Перевірка знакового біта (старший біт 63) */
bool is_sign_bit_set(int64_t val) {
    return ((uint64_t)val >> 63) != 0;
}

int main(void) {
    int64_t dividend = -13;
    int64_t divisor = 5;

    /* Демонстрація відмінності стандартного ділення C від Евклідового */
    int64_t c_quot = dividend / divisor;
    int64_t c_rem = dividend % divisor;
    printf("Стандартне ділення C (-13 / 5): q = %lld, r = %lld\n",
           (long long)c_quot, (long long)c_rem);

    EuclideanResult eucl = euclidean_div(dividend, divisor);
    printf("Математичне Евклідове (-13 / 5): q = %lld, r = %lld (0 <= r < %lld)\n",
           (long long)eucl.quot, (long long)eucl.rem, (long long)llabs(divisor));

    /* Демонстрація безпечного додавання та множення */
    int64_t res = 0;
    if (safe_add_int64(INT64_MAX - 10, 20, &res)) {
        printf("Результат додавання: %lld\n", (long long)res);
    } else {
        printf("Виявлено знакове переповнення при додаванні!\n");
    }

    if (safe_mul_int64(-1000000000LL, 10000000000LL, &res)) {
        printf("Результат множення: %lld\n", (long long)res);
    } else {
        printf("Виявлено знакове переповнення при множенні!\n");
    }

    /* Демонстрація бітових операцій додаткового коду */
    int64_t neg_val = -42;
    uint64_t raw_twos = (uint64_t)neg_val;
    printf("Число -42 в шестнадцятковому додатковому коді: 0x%016llX\n",
           (unsigned long long)raw_twos);
    printf("Знаковий біт встановлений: %s\n", is_sign_bit_set(neg_val) ? "так" : "ні");

    return 0;
}
