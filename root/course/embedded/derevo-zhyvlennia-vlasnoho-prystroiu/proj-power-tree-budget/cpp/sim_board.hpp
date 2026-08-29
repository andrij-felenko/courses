// sim_board.hpp — модель плати, що задовольняє концепт power::PowerBoard.
//
// Рейка тут — маленький клас із часом наростання й ознакою «не піднімається»,
// ключ периферії просаджує вхід рівно на час заряду ємності навантаження,
// а плата рахує, скільки часу сигнальні лінії стояли активними при
// знеструмленій периферії: це і є той струм витоку через підтяжки.
#pragma once

#include <chrono>
#include <cstdint>
#include <optional>
#include <string_view>

#include "sequencer.hpp"

namespace power::sim {

struct Scenario {
    std::string_view name;
    bool core_rail_dead = false;
    bool io_rail_dead = false;
    std::uint16_t periph_inrush_mv = 0;  // просідання входу від кидка струму
    std::optional<Ms> overcurrent_at{};  // коли смикнути лінію аварії ключа
    std::optional<Ms> vin_collapse_at{}; // коли обвалити вхідну шину 12 В
};

class Rail {
public:
    constexpr Rail(Ms ramp, bool dead) noexcept : ramp_{ramp}, dead_{dead} {}

    constexpr void enable(bool on) noexcept
    {
        if (on != on_) {
            on_ = on;
            since_ = Ms::zero();
        }
    }

    constexpr void advance(Ms dt) noexcept
    {
        if (on_) {
            since_ += dt;
        }
    }

    [[nodiscard]] constexpr bool on() const noexcept { return on_; }
    [[nodiscard]] constexpr bool ramping() const noexcept { return on_ && since_ < ramp_; }
    [[nodiscard]] constexpr bool up() const noexcept { return on_ && !dead_ && since_ >= ramp_; }

private:
    Ms ramp_;
    bool dead_;
    bool on_ = false;
    Ms since_ = Ms::zero();
};

class Board {
public:
    explicit Board(const Scenario& scenario) noexcept
        : sc_{scenario},
          core_{Ms{2}, scenario.core_rail_dead},   // м'який старт першого ступеня
          io_{Ms{3}, scenario.io_rail_dead},       // LDO шини DVDD
          periph_{Ms{3}, false}                    // t_r ключа з керованим dV/dt
    {}

    void advance(Ms dt) noexcept
    {
        if (bus_active_ && !periph_.up()) {
            leak_ += dt;
        }
        now_ += dt;
        core_.advance(dt);
        io_.advance(dt);
        periph_.advance(dt);
    }

    [[nodiscard]] Ms now() const noexcept { return now_; }
    [[nodiscard]] Ms leak() const noexcept { return leak_; }

    // --- контракт power::PowerBoard ---

    void core_rail(bool on) noexcept { core_.enable(on); }
    void io_rail(bool on) noexcept { io_.enable(on); }
    void periph_switch(bool on) noexcept { periph_.enable(on); }
    void reset_line(bool asserted) noexcept { reset_asserted_ = asserted; }
    void bus_pins(bool active) noexcept { bus_active_ = active; }

    [[nodiscard]] bool core_pgood() const noexcept
    {
        return core_.up() && vin_mv() >= kPgoodMinVin;
    }

    // DVDD живиться з першого ступеня: без нього PGOOD не з'явиться.
    [[nodiscard]] bool io_pgood() const noexcept { return core_pgood() && io_.up(); }

    [[nodiscard]] bool fault_irq() const noexcept
    {
        if (!sc_.overcurrent_at || now_ < *sc_.overcurrent_at) {
            return false;
        }
        return periph_.on();  // ключ знятий — аварії більше немає
    }

    [[nodiscard]] std::uint16_t vin_mv() const noexcept
    {
        std::uint32_t v = kVinNominal;
        if (sc_.vin_collapse_at && now_ >= *sc_.vin_collapse_at) {
            v = kVinCollapsed;
        }
        if (periph_.ramping()) {
            v = (v > sc_.periph_inrush_mv) ? v - sc_.periph_inrush_mv : 0u;
        }
        return static_cast<std::uint16_t>(v);
    }

private:
    static constexpr std::uint32_t kVinNominal = 12000;
    static constexpr std::uint32_t kVinCollapsed = 7800;
    static constexpr std::uint32_t kPgoodMinVin = 9000;  // нижче Buck зривається

    Scenario sc_;
    Rail core_;
    Rail io_;
    Rail periph_;
    bool reset_asserted_ = true;
    bool bus_active_ = false;
    Ms now_ = Ms::zero();
    Ms leak_ = Ms::zero();
};

static_assert(PowerBoard<Board>);

}  // namespace power::sim
