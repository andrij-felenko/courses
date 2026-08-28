constexpr uint32_t timclk_hz = 84'000'000;
constexpr uint32_t tick_hz   = 1'000'000;
constexpr uint32_t period_hz = 1'000;

constexpr uint32_t psc_val = (timclk_hz / tick_hz) - 1;
constexpr uint32_t arr_val = (tick_hz / period_hz) - 1;
constexpr uint32_t ccr_val = 250;

static_assert(timclk_hz % tick_hz == 0, "передільник не цілий");
static_assert(tick_hz % period_hz == 0, "межа не ціла");
static_assert(psc_val <= 0xFFFF,        "PSC не влазить у 16 бітів");
static_assert(arr_val <= 0xFFFF,        "ARR не влазить у 16 бітів");
static_assert(ccr_val <= arr_val + 1,   "поріг за межею періоду");
