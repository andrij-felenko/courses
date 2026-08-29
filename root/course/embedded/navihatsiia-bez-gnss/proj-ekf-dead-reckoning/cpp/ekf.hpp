// ekf.hpp — розширений фільтр Калмана для числення координат без GNSS.
//
// Вектор стану (світова система NED, вісь Z вниз):
//
//     x = [ px py pz | vx vy vz | bax bay baz ]ᵀ
//
// Зсув нуля акселерометра тримається в стані навмисно: без нього постійна
// похибка нуля перетворюється на квадратичний по часу відліт координати, а
// з ним оптичний потік поступово «перетікає» в оцінку зсуву.
//
// Клас нічого не виділяє в купі: увесь стан — у std::array фіксованого
// розміру, тож об'єкт можна класти в статичну пам'ять задачі FreeRTOS і
// точно знати його розмір на етапі компіляції. Потрібен C++23 (std::expected).
#pragma once

#include <array>
#include <cmath>
#include <cstdint>
#include <expected>
#include <span>

namespace nav {

using Vec3 = std::array<float, 3>;
using Mat3 = std::array<Vec3, 3>;

// ── Алгебра 3x3 значеннями ──────────────────────────────────────────────
// Коваріація фільтра розбита на блоки 3x3, і вся її екстраполяція — це
// кілька множень і додавань таких блоків. Значення з операторами тут
// доречніші за функції з вихідними параметрами: рядок коду збігається з
// рядком формули, а компілятор усе одно розгортає ці цикли повністю.

constexpr Mat3 operator*(Mat3 const& a, Mat3 const& b) noexcept
{
    Mat3 out{};
    for (std::size_t i = 0; i < 3; ++i) {
        for (std::size_t j = 0; j < 3; ++j) {
            float acc = 0.0f;
            for (std::size_t k = 0; k < 3; ++k) acc += a[i][k] * b[k][j];
            out[i][j] = acc;
        }
    }
    return out;
}

constexpr Mat3 operator*(Mat3 const& a, float k) noexcept
{
    Mat3 out{};
    for (std::size_t i = 0; i < 3; ++i) {
        for (std::size_t j = 0; j < 3; ++j) out[i][j] = a[i][j] * k;
    }
    return out;
}

constexpr Mat3 operator+(Mat3 const& a, Mat3 const& b) noexcept
{
    Mat3 out{};
    for (std::size_t i = 0; i < 3; ++i) {
        for (std::size_t j = 0; j < 3; ++j) out[i][j] = a[i][j] + b[i][j];
    }
    return out;
}

constexpr Vec3 operator*(Mat3 const& m, Vec3 const& v) noexcept
{
    return {m[0][0] * v[0] + m[0][1] * v[1] + m[0][2] * v[2],
            m[1][0] * v[0] + m[1][1] * v[1] + m[1][2] * v[2],
            m[2][0] * v[0] + m[2][1] * v[1] + m[2][2] * v[2]};
}

constexpr Mat3 transpose(Mat3 const& a) noexcept
{
    return {Vec3{a[0][0], a[1][0], a[2][0]},
            Vec3{a[0][1], a[1][1], a[2][1]},
            Vec3{a[0][2], a[1][2], a[2][2]}};
}

bool isFinite(Vec3 const& v) noexcept;

// Матриця справді ортонормальна? Оцінювач орієнтації після втрати
// кватерніона віддає NaN, і таку матрицю треба відкинути ДО того, як вона
// потрапить у коваріацію.
bool isRotation(Mat3 const& m, float tol) noexcept;

// ── Фільтр ──────────────────────────────────────────────────────────────

enum class FuseError : std::uint8_t {
    Gated,      // відкинуто стробуванням Махаланобіса (викид)
    Numeric     // NaN/Inf на вході або вироджена інноваційна дисперсія
};

class Ekf {
public:
    static constexpr std::size_t kDim = 9;
    static constexpr float kGravity = 9.80665f;   // NED: вісь Z вниз, тому «+g»

    enum Index : std::size_t {
        kPx = 0, kPy, kPz,
        kVx, kVy, kVz,
        kBax, kBay, kBaz
    };

    struct Stats {
        std::uint32_t gated{};
        std::uint32_t numeric{};
        std::uint32_t healed{};    // скільки разів коваріацію рятувала гігієна
    };

    Ekf() noexcept;

    // Крок передбачення за даними IMU: питома сила в системі тіла, поворот
    // «тіло → світ» від оцінювача орієнтації, крок 0.002–0.005 с.
    // false — вхід не пройшов перевірку, крок пропущено.
    bool predict(Vec3 const& aBody, Mat3 const& Rwb, float dt) noexcept;

    // Скалярне злиття одного вимірювання з рядком спостереження H.
    // Послідовне скалярне злиття дає для некорельованих вимірювань той
    // самий результат, що й матричне, але не потребує обертання S — на MCU
    // це різниця між сотнею мікросекунд і кількома.
    // Успіх повертає квадрат відстані Махаланобіса: саме його пишуть у
    // телеметрію, коли розбираються, чому фільтр не повірив давачу.
    std::expected<float, FuseError> fuse(std::span<const float, kDim> H,
                                         float z, float r, float gate) noexcept;

    // Оптичний потік: горизонтальна швидкість у світовій системі. Осі
    // зливаються послідовно й незалежно — змазаний кадр псує зазвичай одну
    // вісь, і другу через це втрачати немає причини.
    std::expected<void, FuseError> updateVelocity2d(float vx, float vy,
                                                    float r, float gate) noexcept;

    // Далекомір ToF або барометр: вимірюється pz (вниз-додатна).
    std::expected<float, FuseError> updateAltitude(float pz, float r, float gate) noexcept;

    // ZUPT: «швидкість дорівнює нулю» по всіх трьох осях. Саме на стоянці
    // фільтр найкраще бачить зсув акселерометра — будь-яке ненульове
    // прискорення там є або зсувом, або похибкою орієнтації.
    std::expected<void, FuseError> updateZupt(float r) noexcept;

    Vec3 position() const noexcept { return {x_[kPx], x_[kPy], x_[kPz]}; }
    Vec3 velocity() const noexcept { return {x_[kVx], x_[kVy], x_[kVz]}; }
    Vec3 bias() const noexcept { return {x_[kBax], x_[kBay], x_[kBaz]}; }

    float posSigma(std::size_t axis) const noexcept { return std::sqrt(P_[kPx + axis][kPx + axis]); }
    float velSigma(std::size_t axis) const noexcept { return std::sqrt(P_[kVx + axis][kVx + axis]); }

    void setDown(float pz) noexcept { x_[kPz] = pz; }

    Stats const& stats() const noexcept { return stats_; }

private:
    // Спектральні густини шумів процесу (множаться на dt).
    static constexpr float kQpos = 1.0e-3f;    // м²/с³
    static constexpr float kQvel = 5.0e-2f;    // (м/с²)²·с
    static constexpr float kQbias = 1.0e-5f;   // (м/с²)²/с

    // Запобіжники чисельного колапсу.
    static constexpr float kPmin = 1.0e-6f;
    static constexpr float kPmax = 1.0e4f;
    static constexpr float kBiasMax = 0.5f;    // м/с², паспортна межа давача

    Mat3 block(std::size_t r, std::size_t c) const noexcept;
    void setBlock(std::size_t r, std::size_t c, Mat3 const& m) noexcept;
    void setBlockSym(std::size_t r, std::size_t c, Mat3 const& m) noexcept;
    void condition() noexcept;

    std::array<float, kDim> x_{};
    std::array<std::array<float, kDim>, kDim> P_{};
    Stats stats_{};
};

}  // namespace nav
