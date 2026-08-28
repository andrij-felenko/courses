#include <cstdint>

constexpr int WIN = 11;        // довжина вікна: компроміс згладження↔затримка

static uint16_t buf[WIN];      // кільцевий буфер останніх WIN відліків
static uint32_t sum = 0;       // збережена сума вмісту вікна (широка — проти переповнення)
static int      pos = 0;       // куди ляже наступний відлік

// Згодувати новий відлік, дістати ковзне середнє по останніх WIN.
uint16_t moving_average(uint16_t sample)
{
    sum -= buf[pos];           // прибрати найстаріший відлік (той, що випадає з вікна)
    sum += sample;             // додати найновіший
    buf[pos] = sample;         // затерти найстаріший новим
    pos = (pos + 1) % WIN;     // зсунути вікно по колу
    return static_cast<uint16_t>(sum / WIN);   // свіже середнє вікна
}
