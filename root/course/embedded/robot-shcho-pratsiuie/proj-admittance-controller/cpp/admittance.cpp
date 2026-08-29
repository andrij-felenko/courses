#include "admittance.hpp"

#include <algorithm>
#include <cmath>
#include <numbers>

namespace robot::compliance {

bool Config::valid() const noexcept
{
    if (!(filter_alpha > 0.0f) || filter_alpha > 1.0f) {
        return false;
    }
    if (!(retract_speed > 0.0f)) {
        return false;
    }
    for (std::size_t i = 0; i < kDof; ++i) {
        // На віртуальну масу ділимо щотакту — нуль тут це NaN у команді приводам.
        if (!(virtual_mass[i] > 0.0f)) {
            return false;
        }
        if (virtual_damping[i] < 0.0f || virtual_stiffness[i] < 0.0f) {
            return false;
        }
        if (!(max_disp[i] > 0.0f) || !(max_vel[i] > 0.0f)) {
            return false;
        }
        if (deadband[i] < 0.0f || !(max_force[i] > deadband[i])) {
            return false;
        }
    }
    return true;
}

void Config::set_critical_damping() noexcept
{
    for (std::size_t i = 0; i < kDof; ++i) {
        virtual_damping[i] = 2.0f * std::sqrt(virtual_mass[i] * virtual_stiffness[i]);
    }
}

float Config::alpha_for_cutoff(float cutoff_hz) noexcept
{
    if (!(cutoff_hz > 0.0f)) {
        return 1.0f; // фільтр вимкнено
    }
    const float rc = 1.0f / (2.0f * std::numbers::pi_v<float> * cutoff_hz);
    return kDtSec / (rc + kDtSec);
}

std::expected<Controller, Fault> Controller::create(const Config& cfg) noexcept
{
    if (!cfg.valid()) {
        return std::unexpected(Fault::InvalidConfig);
    }
    return Controller{cfg};
}

void Controller::start_tare() noexcept
{
    tare_accum_.fill(0.0f);
    tare_counter_ = 0;
    mode_ = Mode::Taring;
}

void Controller::acknowledge() noexcept
{
    if (mode_ != Mode::Retract) {
        return;
    }
    vel_.fill(0.0f);
    retract_dir_.fill(0.0f);
    mode_ = Mode::Active;
}

bool Controller::retract_finished() const noexcept
{
    if (mode_ != Mode::Retract) {
        return false;
    }
    for (std::size_t i = 0; i < kDof; ++i) {
        if (retract_dir_[i] != 0.0f && std::abs(disp_[i]) < 0.999f * cfg_.max_disp[i]) {
            return false;
        }
    }
    return true;
}

Command Controller::hold(Vector6View x_nominal) const noexcept
{
    Command out{};
    for (std::size_t i = 0; i < kDof; ++i) {
        out.pose[i] = x_nominal[i] + disp_[i];
    }
    return out; // twist лишається нульовим
}

std::expected<Command, Fault> Controller::step_tare(Vector6View f_ext,
                                                    Vector6View x_nominal,
                                                    Vector6View v_nominal) noexcept
{
    Command out{};
    for (std::size_t i = 0; i < kDof; ++i) {
        // Тарування має відбуватися у вільному просторі: інакше хибний нуль
        // тихо поїде з нами весь сеанс.
        if (std::abs(f_ext[i]) > cfg_.max_force[i]) {
            mode_ = Mode::Fault;
            return std::unexpected(Fault::TareDisturbed);
        }
        tare_accum_[i] += f_ext[i];
        out.pose[i] = x_nominal[i];
        out.twist[i] = v_nominal[i];
    }

    if (++tare_counter_ >= kTareSamples) {
        for (std::size_t i = 0; i < kDof; ++i) {
            f_raw_offset_[i] = tare_accum_[i] / static_cast<float>(kTareSamples);
        }
        f_filt_.fill(0.0f);
        disp_.fill(0.0f);
        vel_.fill(0.0f);
        mode_ = Mode::Active;
    }
    return out;
}

void Controller::latch_retract_direction() noexcept
{
    retract_dir_.fill(0.0f);
    const float norm = std::sqrt(f_filt_[0] * f_filt_[0] + f_filt_[1] * f_filt_[1] +
                                 f_filt_[2] * f_filt_[2]);
    if (norm < 1.0e-6f) {
        return; // перевищив момент, а не сила — відходити нікуди
    }
    // Уздовж нормалі контакту, тобто протилежно виміряній реакції.
    for (std::size_t i = 0; i < 3; ++i) {
        retract_dir_[i] = -f_filt_[i] / norm;
    }
}

Command Controller::step_retract(Vector6View x_nominal) noexcept
{
    mode_ = Mode::Retract;
    Command out{};
    for (std::size_t i = 0; i < kDof; ++i) {
        float delta = retract_dir_[i] * cfg_.retract_speed * kDtSec;
        float next = disp_[i] + delta;
        if (std::abs(next) > cfg_.max_disp[i]) {
            next = std::clamp(next, -cfg_.max_disp[i], cfg_.max_disp[i]);
            delta = 0.0f;
        }
        disp_[i] = next;
        vel_[i] = delta / kDtSec;
        // Номінальну траєкторію в аварії скасовано: рухаємось лише від деталі.
        out.pose[i] = x_nominal[i] + disp_[i];
        out.twist[i] = vel_[i];
    }
    return out;
}

std::expected<Command, Fault> Controller::step_active(Vector6View f_ext,
                                                      Vector6View x_nominal,
                                                      Vector6View v_nominal) noexcept
{
    // 1. Зняття нуля і фільтрація — по ВСІХ осях, перш ніж щось вирішувати:
    // інакше при спрацюванні ліміту на одній осі стан фільтра решти
    // лишиться від попереднього такту.
    bool exceeded = false;
    for (std::size_t i = 0; i < kDof; ++i) {
        const float unbiased = f_ext[i] - f_raw_offset_[i];
        f_filt_[i] = (1.0f - cfg_.filter_alpha) * f_filt_[i] + cfg_.filter_alpha * unbiased;
        exceeded = exceeded || std::abs(f_filt_[i]) > cfg_.max_force[i];
    }

    // 2. Скінченний автомат безпеки.
    if (exceeded) {
        latch_retract_direction();
        vel_.fill(0.0f);
        mode_ = Mode::ForceExceeded;
        return std::unexpected(Fault::ForceLimit);
    }

    Command out{};
    for (std::size_t i = 0; i < kDof; ++i) {
        // 3. Зона нечутливості: шум давача не має інтегруватися в дрейф.
        float f_active = 0.0f;
        if (f_filt_[i] > cfg_.deadband[i]) {
            f_active = f_filt_[i] - cfg_.deadband[i];
        } else if (f_filt_[i] < -cfg_.deadband[i]) {
            f_active = f_filt_[i] + cfg_.deadband[i];
        }

        // 4. Динаміка адмітансу: M·a + D·v + K·p = −F.
        const float accel = (-f_active - cfg_.virtual_damping[i] * vel_[i] -
                             cfg_.virtual_stiffness[i] * disp_[i]) / cfg_.virtual_mass[i];

        // Напівнеявний Ейлер: координата інтегрується вже НОВОЮ швидкістю.
        vel_[i] = std::clamp(vel_[i] + accel * kDtSec, -cfg_.max_vel[i], cfg_.max_vel[i]);
        disp_[i] += vel_[i] * kDtSec;

        // 5. Упор ходу з гасінням швидкості в бік упору: інакше віртуальна
        // маса накопичить енергію на межі й вистрілить, щойно сила зникне.
        if (disp_[i] > cfg_.max_disp[i]) {
            disp_[i] = cfg_.max_disp[i];
            vel_[i] = std::min(vel_[i], 0.0f);
        } else if (disp_[i] < -cfg_.max_disp[i]) {
            disp_[i] = -cfg_.max_disp[i];
            vel_[i] = std::max(vel_[i], 0.0f);
        }

        out.pose[i] = x_nominal[i] + disp_[i];
        out.twist[i] = v_nominal[i] + vel_[i];
    }

    mode_ = Mode::Active;
    return out;
}

std::expected<Command, Fault> Controller::step(Vector6View f_ext,
                                               Vector6View x_nominal,
                                               Vector6View v_nominal) noexcept
{
    switch (mode_) {
    case Mode::Taring:
        return step_tare(f_ext, x_nominal, v_nominal);
    case Mode::ForceExceeded:
    case Mode::Retract:
        return step_retract(x_nominal);
    case Mode::Active:
        return step_active(f_ext, x_nominal, v_nominal);
    case Mode::Idle:
    case Mode::Fault:
    default:
        return hold(x_nominal);
    }
}

} // namespace robot::compliance
