// C++20: Описи у просторі назв henon у <henon/map.hpp>

namespace henon {

struct Params {
    double a{1.4}; // Параметр нелінійності зсуву
    double b{0.3}; // Параметр дисипації площі
};

struct Point {
    double x{0.0}; // Координата x
    double y{0.0}; // Координата y
};

struct LyapunovResult {
    double lambda_1{0.0};     // Старший показник Ляпунова
    double lambda_2{0.0};     // Молодший показник Ляпунова
    double kaplan_yorke{0.0}; // Фрактальна розмірність
    bool converged{false};    // Прапорець збіжності
};

struct FixedPoints {
    Point p1{};           // Первинна нерухома точка
    Point p2{};           // Вторинна нерухома точка
    bool is_real{false};  // Прапорець дійсності коренів
};

enum class Status {
    Ok = 0,
    Diverged = 1,
    InvalidParam = 2,
    NullPointer = 3
};

} // namespace henon
