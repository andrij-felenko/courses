#include <iostream>
#include <cmath>
#include <string_view>
#include <expected>
#include <format>
#include <vector>

namespace photonics {

enum class LinkStatus {
    Ok,             // Лінія працює, запас достатній (>= Target Margin)
    LowMargin,      // Зв'язок є, але інженерний запас нижче норми
    Unreachable,    // Згасання перевищує поріг чутливості
    Overloaded      // Потужність вища за поріг насичення (overload)
};

struct TransceiverSpec {
    float tx_power_dbm{0.0f};
    float rx_sensitivity_dbm{-28.0f};
    float rx_overload_dbm{-8.0f};
};

struct FiberPath {
    float length_km{0.0f};
    float attenuation_per_km{0.35f};
    int splice_count{0};
    float splice_loss_db{0.05f};
    int connector_count{0};
    float connector_loss_db{0.3f};
    int splitter_ratio{1};
    float splitter_excess_db{1.5f};
    float system_margin_target{3.0f};
};

struct LinkBudgetResult {
    float total_attenuation_db{0.0f};
    float rx_power_dbm{0.0f};
    float margin_db{0.0f};
    LinkStatus status{LinkStatus::Ok};

    [[nodiscard]] constexpr std::string_view status_to_string() const noexcept {
        switch (status) {
            case LinkStatus::Ok:          return "OK: Лінія надійна";
            case LinkStatus::LowMargin:   return "WARNING: Запас нижче нормативу";
            case LinkStatus::Unreachable: return "ERROR: Сигнал загас повністю";
            case LinkStatus::Overloaded:  return "CRITICAL: Перевантаження приймача";
        }
        return "Unknown";
    }
};

class LinkBudgetCalculator {
public:
    [[nodiscard]] static float calculate_splitter_loss(int ratio, float excess_loss_db) noexcept {
        if (ratio <= 1) return 0.0f;
        return 10.0f * std::log10(static_cast<float>(ratio)) + excess_loss_db;
    }

    [[nodiscard]] static std::expected<LinkBudgetResult, std::string_view>
    analyze_link(const TransceiverSpec& tx_rx, const FiberPath& path) noexcept {
        if (path.length_km < 0.0f || path.attenuation_per_km < 0.0f) {
            return std::unexpected("Некоректна довжина або загасання волокна");
        }

        LinkBudgetResult result{};

        const float fiber_loss = path.length_km * path.attenuation_per_km;
        const float splices_loss = static_cast<float>(path.splice_count) * path.splice_loss_db;
        const float connectors_loss = static_cast<float>(path.connector_count) * path.connector_loss_db;
        const float splitter_loss = calculate_splitter_loss(path.splitter_ratio, path.splitter_excess_db);

        result.total_attenuation_db = fiber_loss + splices_loss + connectors_loss + splitter_loss;
        result.rx_power_dbm = tx_rx.tx_power_dbm - result.total_attenuation_db;
        result.margin_db = result.rx_power_dbm - tx_rx.rx_sensitivity_dbm;

        if (result.rx_power_dbm > tx_rx.rx_overload_dbm) {
            result.status = LinkStatus::Overloaded;
        } else if (result.rx_power_dbm < tx_rx.rx_sensitivity_dbm) {
            result.status = LinkStatus::Unreachable;
        } else if (result.margin_db < path.system_margin_target) {
            result.status = LinkStatus::LowMargin;
        } else {
            result.status = LinkStatus::Ok;
        }

        return result;
    }
};

} // namespace photonics

int main() {
    using namespace photonics;

    const TransceiverSpec xgs_pon_class_n1{
        .tx_power_dbm = 4.0f,          // +4.0 дБм (XGS-PON OLT 1577 нм)
        .rx_sensitivity_dbm = -28.0f,  // -28.0 дБм (XGS-PON ONU)
        .rx_overload_dbm = -7.0f
    };

    const FiberPath metro_path{
        .length_km = 18.5f,
        .attenuation_per_km = 0.22f,   // 1577 нм у C/L діапазоні
        .splice_count = 8,
        .splice_loss_db = 0.03f,
        .connector_count = 6,
        .connector_loss_db = 0.20f,
        .splitter_ratio = 64,          // 1:64 сплітер
        .splitter_excess_db = 2.1f,
        .system_margin_target = 3.0f
    };

    auto analysis = LinkBudgetCalculator::analyze_link(xgs_pon_class_n1, metro_path);

    if (analysis) {
        const auto& res = analysis.value();
        std::cout << std::format("=== РЕЗУЛЬТАТ XGS-PON (1:64, 18.5 км) ===\n");
        std::cout << std::format("Загасання тракту:  {:.2f} дБ\n", res.total_attenuation_db);
        std::cout << std::format("Потужність на ONU: {:.2f} дБм\n", res.rx_power_dbm);
        std::cout << std::format("Запас лінії:       {:.2f} дБ\n", res.margin_db);
        std::cout << std::format("Статус:            {}\n", res.status_to_string());
    } else {
        std::cerr << "Помилка аналізу: " << analysis.error() << '\n';
    }

    return 0;
}
