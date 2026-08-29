#pragma once

#include <expected>
#include <string_view>

// Фізика вузла: еквівалент Тевеніна, вплив приладу на вимірюване коло
// й оцінка паразитних опорів монтажу. Про протокол і вердикти цей
// модуль не знає нічого — це справа verification.hpp.
namespace bench {

enum class CalcError {
    NonPositiveResistance,  // опір мусить бути додатним
    CurrentTooSmall,        // струм тоне в розрядності мілівольтметра
    NegativeDrop,           // на виводі чипа напруга вища за джерело
    BadContactCount         // контактів у шляху не буває нуль чи менше
};

[[nodiscard]] std::string_view describe(CalcError err) noexcept;

// Еквівалент Тевеніна вузла: генератор напруги плюс вихідний опір.
struct Node {
    double u_th{};  // напруга холостого ходу, В
    double r_th{};  // вихідний опір вузла, Ом
};

// Показ вольтметра поруч з істинним значенням вузла.
struct Loading {
    double u_true{};
    double u_meas{};
    double error_pct{};  // (u_meas - u_true) / u_true, % — завжди <= 0
    double ratio{};      // R_m / R_th
};

struct ContactEstimate {
    double current{};      // струм гілки, А
    double drop{};         // просідання шини до виводу чипа, В
    double path{};         // сумарний опір шляху живлення, Ом
    double per_contact{};  // на один контакт, Ом
};

[[nodiscard]] std::expected<Node, CalcError>
divider(double u_supply, double r_top, double r_bottom) noexcept;

// Пряма задача: яким вузол побачить прилад із вхідним опором r_meter.
[[nodiscard]] std::expected<Loading, CalcError>
reading_of(Node node, double r_meter) noexcept;

// Обернена задача: за самим лише показом відновити напругу холостого ходу.
[[nodiscard]] std::expected<Loading, CalcError>
restore_open_circuit(double u_meas, double r_th, double r_meter) noexcept;

[[nodiscard]] std::expected<double, CalcError>
shunt_current(double u_shunt, double r_shunt) noexcept;

[[nodiscard]] std::expected<ContactEstimate, CalcError>
contact_resistance(double u_supply, double u_shunt, double u_pin,
                   double r_shunt, int contacts) noexcept;

}  // namespace bench
