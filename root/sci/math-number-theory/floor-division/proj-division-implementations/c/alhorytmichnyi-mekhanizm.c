#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint32_t modulus;
    uint32_t k;       // Кількість бітів дільника
    uint64_t mu;      // Попередньо обчислена константа μ = ⌊2^(2k) / m⌋
} barrett_config_t;

// Ініціалізація констант Барретта
barrett_config_t barrett_init(uint32_t m) {
    barrett_config_t cfg;
    cfg.modulus = m;
    
    uint32_t k = 0;
    uint32_t temp = m;
    while (temp > 0) {
        k++;
        temp >>= 1;
    }
    cfg.k = k;
    cfg.mu = (1ULL << (2 * k)) / m;
    return cfg;
}

// Швидке обчислення остачі x % m за Барреттом без апаратного ділення
uint32_t barrett_reduce(uint64_t x, const barrett_config_t* cfg) {
    uint32_t k = cfg->k;
    uint32_t m = cfg->modulus;
    
    // Обчислимо приблизну частку q = ⌊ (⌊x / 2^(k-1)⌋ * μ) / 2^(k+1) ⌋
    uint64_t q = ((x >> (k - 1)) * cfg->mu) >> (k + 1);
    
    // Остача r = x - q * m
    int64_t r = (int64_t)x - (int64_t)(q * m);
    
    // Корекція якщо r >= m або r < 0
    while (r >= m) {
        r -= m;
    }
    while (r < 0) {
        r += m;
    }
    return (uint32_t)r;
}
