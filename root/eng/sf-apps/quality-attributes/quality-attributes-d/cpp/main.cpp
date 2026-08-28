#include <cstdint>
#include <optional>

struct Cache {
    std::uint32_t value       = 0;      // збережена відповідь
    std::uint32_t stored_at_ms = 0;     // коли поклали в кеш
    bool          valid       = false;  // чи є що віддавати
};

// max_age_ms — контракт свіжості: наскільки застарілі дані ми ще
// згодні віддавати. Це ЧИСЛО зі сценарію атрибута, а не випадкова стала.
// std::optional — природний аналог «bool + out-параметр».
std::optional<std::uint32_t> cache_get(const Cache& c, std::uint32_t now_ms,
                                       std::uint32_t max_age_ms) {
    if (!c.valid)
        return std::nullopt;                // кеш порожній — доведеться рахувати
    if (now_ms - c.stored_at_ms > max_age_ms)
        return std::nullopt;                // застаріло понад дозволене — теж рахувати
    return c.value;                         // свіже — швидкий шлях
}
