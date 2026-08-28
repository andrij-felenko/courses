#include <stddef.h>

long long sum_array(const int *data, size_t size, int factor) {
    long long total = 0;
    for (size_t i = 0; i < size; ++i) {
        // Множення на незмінний factor всередині циклу
        total += (long long)data[i] * factor;
    }
    return total;
}
