#include <iostream>
#include "wieferich_api.h"

int main() {
    wieferich::config cfg{};
    cfg.start_range = 3;
    cfg.end_range = 10000000;
    cfg.base = 2;
    cfg.num_threads = 8;
    cfg.use_montgomery = true;

    auto [status, results] = wieferich::search_range(cfg);

    if (status == wieferich::status::success) {
        std::cout << "Пошук завершено. Знайдено простих Віферіха: " << results.size() << '\n';
        for (const auto& res : results) {
            std::cout << "  - p = " << res.prime << " (час: " << res.execution_time << " us)\n";
        }
    }
    return 0;
}
