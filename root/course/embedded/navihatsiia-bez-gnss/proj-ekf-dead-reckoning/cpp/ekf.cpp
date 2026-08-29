#include "ekf.hpp"

#include <algorithm>

namespace nav {

bool isFinite(Vec3 const& v) noexcept
{
    return std::isfinite(v[0]) && std::isfinite(v[1]) && std::isfinite(v[2]);
}

bool isRotation(Mat3 const& m, float tol) noexcept
{
    for (auto const& row : m) {
        if (!isFinite(row)) return false;
    }

    // Стовпці одиничні й попарно ортогональні. Третій стовпець
    // ортонормальної матриці визначений двома першими, тож псування в ньому
    // видно з норми — окремої перевірки визначника не потрібно.
    for (std::size_t c = 0; c < 3; ++c) {
        float n = 0.0f;
        for (std::size_t i = 0; i < 3; ++i) n += m[i][c] * m[i][c];
        if (std::fabs(n - 1.0f) > tol) return false;
    }
    for (std::size_t a = 0; a < 3; ++a) {
        for (std::size_t b = a + 1; b < 3; ++b) {
            float d = 0.0f;
            for (std::size_t i = 0; i < 3; ++i) d += m[i][a] * m[i][b];
            if (std::fabs(d) > tol) return false;
        }
    }
    return true;
}

Ekf::Ekf() noexcept
{
    // Початкова невизначеність: координата ±1 м, швидкість ±0.1 м/с, зсув
    // акселерометра ±0.05 м/с² — типове залишкове після заводського
    // калібрування MEMS-давача середнього класу.
    for (std::size_t i = kPx; i <= kPz; ++i) P_[i][i] = 1.0f;
    for (std::size_t i = kVx; i <= kVz; ++i) P_[i][i] = 0.01f;
    for (std::size_t i = kBax; i <= kBaz; ++i) P_[i][i] = 0.0025f;
}

Mat3 Ekf::block(std::size_t r, std::size_t c) const noexcept
{
    Mat3 m{};
    for (std::size_t i = 0; i < 3; ++i) {
        for (std::size_t j = 0; j < 3; ++j) m[i][j] = P_[r + i][c + j];
    }
    return m;
}

void Ekf::setBlock(std::size_t r, std::size_t c, Mat3 const& m) noexcept
{
    for (std::size_t i = 0; i < 3; ++i) {
        for (std::size_t j = 0; j < 3; ++j) P_[r + i][c + j] = m[i][j];
    }
}

// Кладе блок і його транспозицію у дзеркальну позицію: коваріація
// симетрична, і зберігаємо ми це точно, а не «майже».
void Ekf::setBlockSym(std::size_t r, std::size_t c, Mat3 const& m) noexcept
{
    setBlock(r, c, m);
    setBlock(c, r, transpose(m));
}

// ── Гігієна коваріації ──────────────────────────────────────────────────
// Три різні хвороби float32, і кожна лікується окремо.
//
//  1. Асиметрія. (I − KH)P математично симетрична, у машинній арифметиці —
//     ні; розбіжність P[i][j] і P[j][i] росте від кроку до кроку.
//  2. Колапс діагоналі. Дисперсія, підтиснута до нуля (або від'ємна через
//     округлення), означає K → 0: фільтр перестає слухати давачі й назавжди
//     застигає на своїй помилковій оцінці.
//  3. Розліт кореляцій. |P[i][j]| не може перевищувати √(P[i][i]·P[j][j]);
//     якщо перевищив — наступний крок дасть від'ємну інноваційну дисперсію.
void Ekf::condition() noexcept
{
    for (std::size_t i = 0; i < kDim; ++i) {
        for (std::size_t j = i + 1; j < kDim; ++j) {
            float avg = 0.5f * (P_[i][j] + P_[j][i]);
            if (!std::isfinite(avg)) avg = 0.0f;
            P_[i][j] = P_[j][i] = avg;
        }
    }

    for (std::size_t i = 0; i < kDim; ++i) {
        if (!std::isfinite(P_[i][i]) || P_[i][i] < kPmin) {
            P_[i][i] = kPmin;
            ++stats_.healed;
        } else {
            P_[i][i] = std::min(P_[i][i], kPmax);
        }
    }

    for (std::size_t i = 0; i < kDim; ++i) {
        for (std::size_t j = i + 1; j < kDim; ++j) {
            const float lim = std::sqrt(P_[i][i] * P_[j][j]);
            P_[i][j] = P_[j][i] = std::clamp(P_[i][j], -lim, lim);
        }
    }

    // Стан теж має лишатися фізичним. Якщо оцінка зсуву вперлася в межу —
    // це майже завжди похибка орієнтації, яку фільтр списує на зсув.
    for (std::size_t i = kBax; i <= kBaz; ++i) {
        if (!std::isfinite(x_[i])) {
            x_[i] = 0.0f;
            ++stats_.healed;
        } else {
            x_[i] = std::clamp(x_[i], -kBiasMax, kBiasMax);
        }
    }
}

bool Ekf::predict(Vec3 const& aBody, Mat3 const& Rwb, float dt) noexcept
{
    // Драйвер IMU при збої SPI віддає нулі або старий буфер, оцінювач
    // орієнтації — NaN; ні те, ні те не має права дійти до коваріації.
    if (!(dt > 0.0f) || dt > 0.1f) return false;
    if (!isFinite(aBody) || !isRotation(Rwb, 1.0e-2f)) return false;

    // 1. Компенсація оціненого зсуву нуля.
    const Vec3 aUnbiased{aBody[0] - x_[kBax], aBody[1] - x_[kBay], aBody[2] - x_[kBaz]};

    // 2. Поворот у світ і додавання гравітації. Акселерометр міряє питому
    //    силу; у спокої це −g уздовж осі «вниз», тому «+g» повертає нам
    //    справжнє прискорення руху.
    Vec3 aWorld = Rwb * aUnbiased;
    aWorld[2] += kGravity;

    // 3. Кінематична інтеграція.
    const float halfDt2 = 0.5f * dt * dt;
    for (std::size_t i = 0; i < 3; ++i) {
        x_[kPx + i] += x_[kVx + i] * dt + aWorld[i] * halfDt2;
        x_[kVx + i] += aWorld[i] * dt;
    }

    // 4. Екстраполяція коваріації P = F·P·Fᵀ + Q·dt у блоках 3x3:
    //
    //        F = [ I   I·dt   A ]     A = −0.5·dt²·R_wb
    //            [ 0   I      B ]     B = −dt·R_wb
    //            [ 0   0      I ]
    //
    //    Блоки A і B — похідні координати й швидкості по зсуву: зсув
    //    входить у прискорення зі знаком «мінус» і повертається у світ тією
    //    самою матрицею R_wb. Саме через них у P з'являються кореляції
    //    швидкість↔зсув, без яких потік ніколи не «навчив» би фільтр зсуву.
    const Mat3 A = Rwb * (-halfDt2);
    const Mat3 B = Rwb * (-dt);

    const Mat3 Ppp = block(0, 0), Ppv = block(0, 3), Ppb = block(0, 6);
    const Mat3 Pvv = block(3, 3), Pvb = block(3, 6), Pbb = block(6, 6);

    // T = F·P; рядок зсувів лишається як був, бо його рядок у F одиничний.
    const Mat3 T1p = Ppp + transpose(Ppv) * dt + A * transpose(Ppb);
    const Mat3 T1v = Ppv + Pvv * dt + A * transpose(Pvb);
    const Mat3 T1b = Ppb + Pvb * dt + A * Pbb;
    const Mat3 T2v = Pvv + B * transpose(Pvb);
    const Mat3 T2b = Pvb + B * Pbb;

    // P' = T·Fᵀ + Q·dt (шум процесу входить лише в діагональ блоків).
    Mat3 Npp = T1p + T1v * dt + T1b * transpose(A);
    Mat3 Npv = T1v + T1b * transpose(B);
    Mat3 Nvv = T2v + T2b * transpose(B);
    Mat3 Nbb = Pbb;

    for (std::size_t i = 0; i < 3; ++i) {
        Npp[i][i] += kQpos * dt;
        Nvv[i][i] += kQvel * dt;
        Nbb[i][i] += kQbias * dt;
    }

    setBlock(0, 0, Npp);
    setBlockSym(0, 3, Npv);
    setBlockSym(0, 6, T1b);
    setBlock(3, 3, Nvv);
    setBlockSym(3, 6, T2b);
    setBlock(6, 6, Nbb);

    condition();
    return true;
}

std::expected<float, FuseError> Ekf::fuse(std::span<const float, kDim> H,
                                          float z, float r, float gate) noexcept
{
    if (!std::isfinite(z) || !std::isfinite(r) || !(r > 0.0f)) {
        ++stats_.numeric;
        return std::unexpected(FuseError::Numeric);
    }

    // PHᵀ — вектор 9x1, спільний і для S, і для коефіцієнта Калмана.
    std::array<float, kDim> PHt{};
    for (std::size_t i = 0; i < kDim; ++i) {
        float acc = 0.0f;
        for (std::size_t j = 0; j < kDim; ++j) acc += P_[i][j] * H[j];
        PHt[i] = acc;
    }

    float S = r;                     // S = H·P·Hᵀ + R
    float Hx = 0.0f;
    for (std::size_t j = 0; j < kDim; ++j) {
        S += H[j] * PHt[j];
        Hx += H[j] * x_[j];
    }

    if (!std::isfinite(S) || S <= 0.0f) {
        // Коваріація зіпсована настільки, що дисперсія інновації не додатна.
        // Єдине чесне тут — не чіпати стан: гігієна витягне діагональ, а
        // наступні вимірювання відновлять довіру.
        ++stats_.numeric;
        condition();
        return std::unexpected(FuseError::Numeric);
    }

    const float y = z - Hx;          // інновація (нев'язка)
    const float d2 = (y * y) / S;    // квадрат відстані Махаланобіса

    if (gate > 0.0f && d2 > gate) {
        ++stats_.gated;
        return std::unexpected(FuseError::Gated);
    }

    // K = P·Hᵀ·S⁻¹; для скаляра S⁻¹ — просто ділення.
    std::array<float, kDim> K{};
    for (std::size_t i = 0; i < kDim; ++i) K[i] = PHt[i] / S;
    for (std::size_t i = 0; i < kDim; ++i) x_[i] += K[i] * y;

    // P = (I − K·H)·P. Для симетричної P це (K·H)·P = K·(PHᵀ)ᵀ, тобто одне
    // зовнішнє множення векторів.
    for (std::size_t i = 0; i < kDim; ++i) {
        for (std::size_t j = 0; j < kDim; ++j) P_[i][j] -= K[i] * PHt[j];
    }

    condition();
    return d2;
}

std::expected<void, FuseError> Ekf::updateVelocity2d(float vx, float vy,
                                                     float r, float gate) noexcept
{
    const std::array<float, 2> z{vx, vy};
    const std::array<std::size_t, 2> idx{kVx, kVy};
    std::expected<void, FuseError> worst{};

    for (std::size_t axis = 0; axis < 2; ++axis) {
        std::array<float, kDim> H{};
        H[idx[axis]] = 1.0f;                    // H_vel = [0₃ | e_axis | 0₃]

        auto res = fuse(std::span<const float, kDim>{H}, z[axis], r, gate);
        if (!res && worst) worst = std::unexpected(res.error());
    }
    return worst;
}

std::expected<float, FuseError> Ekf::updateAltitude(float pz, float r, float gate) noexcept
{
    std::array<float, kDim> H{};
    H[kPz] = 1.0f;                              // H_alt = [0 0 1 | 0₃ | 0₃]
    return fuse(std::span<const float, kDim>{H}, pz, r, gate);
}

std::expected<void, FuseError> Ekf::updateZupt(float r) noexcept
{
    std::expected<void, FuseError> worst{};

    for (std::size_t axis = 0; axis < 3; ++axis) {
        std::array<float, kDim> H{};
        H[kVx + axis] = 1.0f;

        // Строб ширший, ніж для потоку (5σ): детектор нерухомості іноді
        // спрацьовує на кінці гальмування, і жорсткий строб тоді викидав би
        // найцінніше вимірювання.
        auto res = fuse(std::span<const float, kDim>{H}, 0.0f, r, 25.0f);
        if (!res && worst) worst = std::unexpected(res.error());
    }
    return worst;
}

}  // namespace nav
