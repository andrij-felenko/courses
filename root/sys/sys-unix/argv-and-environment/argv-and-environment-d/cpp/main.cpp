// C++ структура допоміжного вектора (з підтримкою std::cstdint)
#include <cstdint>

typedef struct {
    uint64_t a_type;
    union {
        uint64_t a_val;
        void *a_ptr;
    } a_un;
} Elf64_auxv_t;
