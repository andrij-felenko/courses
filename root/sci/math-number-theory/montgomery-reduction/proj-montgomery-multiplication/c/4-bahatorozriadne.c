#include <string.h>

#define LIMBS256 4

typedef struct {
    uint64_t d[LIMBS256];
} uint256_t;

/* Додавання двох 256-бітових чисел з поверненням біта переносу */
uint64_t add256(uint256_t *res, const uint256_t *a, const uint256_t *b) {
    uint64_t carry = 0;
    for (int i = 0; i < LIMBS256; ++i) {
        unsigned __int128 sum = (unsigned __int128)a->d[i] + b->d[i] + carry;
        res->d[i] = (uint64_t)sum;
        carry = (uint64_t)(sum >> 64);
    }
    return carry;
}

/* Віднімання b від a: res = a - b з поверненням запозичення */
uint64_t sub256(uint256_t *res, const uint256_t *a, const uint256_t *b) {
    uint64_t borrow = 0;
    for (int i = 0; i < LIMBS256; ++i) {
        unsigned __int128 diff = (unsigned __int128)a->d[i] - b->d[i] - borrow;
        res->d[i] = (uint64_t)diff;
        borrow = (diff >> 64) ? 1 : 0;
    }
    return borrow;
}

/* Багаторозрядне множення Монтгомері CIOS (256 бітів): res = (a * b * R^-1) mod n */
void mont_mul256_cios(uint256_t *res, const uint256_t *a, const uint256_t *b,
                      const uint256_t *n, uint64_t n_prime0) {
    uint64_t t[LIMBS256 + 2] = {0};
    
    for (int i = 0; i < LIMBS256; ++i) {
        /* Крок 1: Множення a[i] * b і накопичення в t */
        uint64_t carry = 0;
        for (int j = 0; j < LIMBS256; ++j) {
            unsigned __int128 prod = (unsigned __int128)a->d[i] * b->d[j] + t[j] + carry;
            t[j] = (uint64_t)prod;
            carry = (uint64_t)(prod >> 64);
        }
        unsigned __int128 sum = (unsigned __int128)t[LIMBS256] + carry;
        t[LIMBS256] = (uint64_t)sum;
        t[LIMBS256 + 1] += (uint64_t)(sum >> 64);
        
        /* Крок 2: Обчислення множника зведення m = (t[0] * n_prime0) mod 2^64 */
        uint64_t m = t[0] * n_prime0;
        
        /* Крок 3: Додавання m * n для обнулення t[0] та зсув праворуч */
        unsigned __int128 prod_n = (unsigned __int128)m * n->d[0] + t[0];
        carry = (uint64_t)(prod_n >> 64);
        
        for (int j = 1; j < LIMBS256; ++j) {
            prod_n = (unsigned __int128)m * n->d[j] + t[j] + carry;
            t[j - 1] = (uint64_t)prod_n; /* Зсув на 1 розряд праворуч */
            carry = (uint64_t)(prod_n >> 64);
        }
        
        sum = (unsigned __int128)t[LIMBS256] + carry;
        t[LIMBS256 - 1] = (uint64_t)sum;
        t[LIMBS256] = t[LIMBS256 + 1] + (uint64_t)(sum >> 64);
        t[LIMBS256 + 1] = 0;
    }
    
    /* Копіюємо проміжний результат */
    uint256_t temp;
    for (int i = 0; i < LIMBS256; ++i) {
        temp.d[i] = t[i];
    }
    
    /* Фінальне умовне віднімання: якщо temp >= n, то temp -= n */
    uint256_t sub_res;
    uint64_t borrow = sub256(&sub_res, &temp, n);
    
    /* Якщо переповнення t[LIMBS256] != 0 або temp >= n (borrow == 0), обираємо sub_res */
    uint64_t take_sub = (t[LIMBS256] != 0) || (borrow == 0);
    uint64_t mask = -take_sub;
    
    for (int i = 0; i < LIMBS256; ++i) {
        res->d[i] = (sub_res.d[i] & mask) | (temp.d[i] & ~mask);
    }
}
