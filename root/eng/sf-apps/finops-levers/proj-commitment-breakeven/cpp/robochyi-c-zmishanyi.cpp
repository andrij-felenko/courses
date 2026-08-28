#include <cstdint>
#include <vector>

// Ставки — мілідолари за машино-годину. Гроші — мілідолари.
struct MixPlan {
    std::uint32_t committed_md;   // ставка обіцянки (база)
    std::uint32_t spot_md;        // ставка спота (сплеск)
    std::uint32_t retail_md;      // роздрібна ставка (пік)
    std::uint32_t base_level;     // машин на обіцянці (низ, що завжди ввімкнений)
    std::uint32_t spot_cap;       // стеля спота: усе понад неї йде на роздріб
    std::uint32_t period_hours;   // годин у періоді (для оплати ВСІХ годин обіцянки)
};

// Внесок кожного тарифу окремо — щоб бачити структуру рахунку, не лише суму.
struct MixBill {
    std::uint64_t committed_md;   // за базу: ставка × base_level × ВСІ години періоду
    std::uint64_t spot_md;        // за сплеск: спот-машино-години
    std::uint64_t retail_md;      // за пік: роздрібні машино-години
    std::uint64_t total_md;       // сума трьох
};

// ── Розкласти профіль по трьох тарифах і порахувати рахунок ──────────────
// demand[h] — скільки машин потрібно на годину h (h = 0..hours-1).
MixBill mixed_bill(const std::vector<std::uint32_t> &demand, const MixPlan &p)
{
    MixBill b = {0, 0, 0, 0};

    // БАЗА оплачується наперед за ВЕСЬ строк, байдуже до погодинного попиту:
    // base_level машин × committed-ставка × усі години періоду.
    b.committed_md = static_cast<std::uint64_t>(p.committed_md) * p.base_level * p.period_hours;

    // СПЛЕСК і ПІК рахуємо погодинно — лише за реально спожите понад базу.
    for (std::uint32_t d : demand) {
        if (d <= p.base_level)
            continue;                       // усе покрила база — понад неї нуль

        std::uint32_t above_base = d - p.base_level;    // скільки понад базу

        // спот покриває від бази до spot_cap; понад spot_cap — роздріб
        std::uint32_t spot_ceiling = (p.spot_cap > p.base_level)
                                   ? (p.spot_cap - p.base_level) : 0;

        std::uint32_t on_spot   = (above_base < spot_ceiling) ? above_base : spot_ceiling;
        std::uint32_t on_retail = above_base - on_spot; // залишок понад стелю спота

        b.spot_md   += static_cast<std::uint64_t>(p.spot_md)   * on_spot;  // 1 година кожної машини
        b.retail_md += static_cast<std::uint64_t>(p.retail_md) * on_retail;
    }

    b.total_md = b.committed_md + b.spot_md + b.retail_md;
    return b;
}
