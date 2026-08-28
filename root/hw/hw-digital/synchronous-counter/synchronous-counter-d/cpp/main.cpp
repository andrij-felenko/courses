#include <cstdint>

// Один «фронт такту» синхронного лічильника: усі рішення — одночасно.
// load_val — число для завантаження; en/load/up — керувальні входи.
uint8_t sync_count_step(uint8_t q, uint8_t load_val,
                        bool en, bool load, bool up) {
    if (load)                 // завантаження має пріоритет — чистий стрибок
        return load_val & 0x0F;
    if (!en)                  // дозволу нема — лічильник завмирає синхронно
        return q;
    if (up)                   // рахунок угору за модулем 16
        return (q + 1) & 0x0F;
    else                      // рахунок униз за модулем 16
        return (q - 1) & 0x0F;
}
