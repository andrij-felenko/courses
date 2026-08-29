#include "loading.hpp"

#include <cmath>
#include <limits>

namespace bench {
namespace {

// Похибка навантаження відносно істинного значення вузла.
[[nodiscard]] double loading_error(double u_true, double u_meas) noexcept
{
    if (std::abs(u_true) < 1e-12) {
        return 0.0;
    }
    return (u_meas - u_true) / u_true * 100.0;
}

[[nodiscard]] double meter_ratio(double r_th, double r_meter) noexcept
{
    // Ідеальний вузол (R_th = 0) прилад не навантажує взагалі.
    return (r_th <= 0.0) ? std::numeric_limits<double>::infinity() : r_meter / r_th;
}

}  // namespace

std::string_view describe(CalcError err) noexcept
{
    switch (err) {
    case CalcError::NonPositiveResistance: return "опір мусить бути додатним";
    case CalcError::CurrentTooSmall:       return "струм замалий для оцінки опору";
    case CalcError::NegativeDrop:          return "напруга на виводі вища за напругу джерела";
    case CalcError::BadContactCount:       return "некоректна кількість контактів у шляху";
    }
    return "невідома помилка";
}

std::expected<Node, CalcError> divider(double u_supply, double r_top, double r_bottom) noexcept
{
    if (r_top <= 0.0 || r_bottom <= 0.0) {
        return std::unexpected(CalcError::NonPositiveResistance);
    }
    // Вихідний опір — паралельне з'єднання плечей: для змінної складової
    // джерело живлення є коротким замиканням на землю.
    return Node{
        .u_th = u_supply * r_bottom / (r_top + r_bottom),
        .r_th = (r_top * r_bottom) / (r_top + r_bottom)
    };
}

std::expected<Loading, CalcError> reading_of(Node node, double r_meter) noexcept
{
    if (r_meter <= 0.0 || node.r_th < 0.0) {
        return std::unexpected(CalcError::NonPositiveResistance);
    }
    // Прилад стає нижнім плечем дільника: U = U_th / (1 + R_th/R_m).
    const double u_meas = node.u_th / (1.0 + node.r_th / r_meter);
    return Loading{
        .u_true = node.u_th,
        .u_meas = u_meas,
        .error_pct = loading_error(node.u_th, u_meas),
        .ratio = meter_ratio(node.r_th, r_meter)
    };
}

std::expected<Loading, CalcError>
restore_open_circuit(double u_meas, double r_th, double r_meter) noexcept
{
    if (r_meter <= 0.0 || r_th < 0.0) {
        return std::unexpected(CalcError::NonPositiveResistance);
    }
    // Те саме рівняння, розв'язане відносно напруги холостого ходу.
    const double u_true = u_meas * (1.0 + r_th / r_meter);
    return Loading{
        .u_true = u_true,
        .u_meas = u_meas,
        .error_pct = loading_error(u_true, u_meas),
        .ratio = meter_ratio(r_th, r_meter)
    };
}

std::expected<double, CalcError> shunt_current(double u_shunt, double r_shunt) noexcept
{
    if (r_shunt <= 0.0) {
        return std::unexpected(CalcError::NonPositiveResistance);
    }
    return u_shunt / r_shunt;
}

std::expected<ContactEstimate, CalcError>
contact_resistance(double u_supply, double u_shunt, double u_pin,
                   double r_shunt, int contacts) noexcept
{
    if (contacts <= 0) {
        return std::unexpected(CalcError::BadContactCount);
    }

    const auto current = shunt_current(u_shunt, r_shunt);
    if (!current) {
        return std::unexpected(current.error());
    }
    // Нижче мікроампера просідання на контактах тоне в розрядності
    // мілівольтметра — ділити на такий струм безглуздо.
    if (*current < 1e-6) {
        return std::unexpected(CalcError::CurrentTooSmall);
    }

    // Шунт стоїть у розриві шини, тож його падіння віднімаємо окремо:
    // решта втрати припадає на клеми макетки й перемички.
    const double drop = u_supply - u_shunt - u_pin;
    if (drop < 0.0) {
        return std::unexpected(CalcError::NegativeDrop);
    }

    const double path = drop / *current;
    return ContactEstimate{
        .current = *current,
        .drop = drop,
        .path = path,
        .per_contact = path / static_cast<double>(contacts)
    };
}

}  // namespace bench
