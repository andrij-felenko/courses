/* Стенд автомата польотних режимів: замість борту — найпростіша модель
   вертикальної та горизонтальної динаміки, замість пульта й наземної станції —
   сценарій. Автомат при цьому справжній: той самий код, що йде в прошивку.

   Збірка: c++ -std=c++23 -O2 -o fsm src/*.cpp   */

#include <array>
#include <cmath>
#include <cstdint>
#include <format>
#include <iostream>
#include <string_view>

#include "fsm.hpp"
#include "mission.hpp"

namespace {

using namespace fm;

constexpr Millis  kTick{20};
constexpr Seconds kDt{0.02F};

/* Вихідний канал стенда: те, що на борту пішло б у телеметрію. */
class ConsoleReporter final : public Reporter {
public:
    explicit ConsoleReporter(const VehicleState& state) : state_{state} {}

    void commandAck(std::uint16_t command, MavResult result) override
    {
        static constexpr std::array<std::string_view, 5> kNames{
            "ACCEPTED", "TEMPORARILY_REJECTED", "DENIED", "UNSUPPORTED", "FAILED"};

        std::cout << std::format("  [{:6.2f}] COMMAND_ACK cmd={} -> {}\n",
                                 seconds(), command,
                                 kNames.at(static_cast<std::size_t>(result)));
    }

    void statusText(Severity severity, std::string_view text) override
    {
        std::cout << std::format("  [{:6.2f}] STATUSTEXT(sev={}): {}\n",
                                 seconds(), static_cast<int>(severity), text);
    }

    void tone(Tone value) override
    {
        static constexpr std::array<std::string_view, 5> kNames{
            "accepted", "rejected", "throttle lock", "failsafe", "disarm"};

        std::cout << std::format("  [{:6.2f}] BUZZER: {}\n",
                                 seconds(), kNames.at(static_cast<std::size_t>(value)));
    }

private:
    [[nodiscard]] double seconds() const
    {
        return std::chrono::duration<double>{state_.now.time_since_epoch()}.count();
    }

    const VehicleState& state_;
};

/* Модель апарата: вертикаль з тягою й опором, горизонталь з нахилом. */
class Vehicle {
public:
    explicit Vehicle(VehicleState& state) : state_{state} {}

    void step(float throttle, float tiltNorthDeg, float tiltEastDeg)
    {
        const bool grounded = state_.vertical.altitudeRelM <= 0.001F && throttle < kHover;

        float accel = grounded ? 0.0F
                               : (throttle - kHover) * 18.0F - 0.8F * state_.vertical.velocityMs;
        float vz  = state_.vertical.velocityMs + accel * kDt.count();
        float alt = state_.vertical.altitudeRelM + vz * kDt.count();

        if (alt <= 0.0F) {
            alt = 0.0F;
            if (vz < 0.0F) {
                vz    = 0.0F;
                accel = 0.0F;   // реакція опори: удару немає, апарат стоїть
            }
        }

        state_.vertical.velocityMs   = vz;
        state_.vertical.altitudeRelM = alt;
        state_.propulsion.motorOutput = throttle;
        // Дисперсія вертикального прискорення: на землі рама тиха, у польоті — ні.
        state_.imu.accelZVariance = grounded ? 0.03F : (std::fabs(accel) * 0.05F + 0.05F);

        // Нахил перетворюється на прискорення (tan ~ 0.017 на градус).
        HorizontalStatus& h = state_.horizontal;

        h.velNorthMs += (0.171F * tiltNorthDeg - 0.35F * h.velNorthMs) * kDt.count();
        h.velEastMs  += (0.171F * tiltEastDeg - 0.35F * h.velEastMs) * kDt.count();

        // 1 метр по широті — приблизно 1e7/111320 одиниць координати.
        const double latRad = static_cast<double>(h.position.lat1e7) * 1e-7 * 0.017453;

        h.position.lat1e7 += static_cast<std::int32_t>(
            std::lround(h.velNorthMs * kDt.count() * 89.83));
        h.position.lon1e7 += static_cast<std::int32_t>(
            std::lround(h.velEastMs * kDt.count() * 89.83 / std::cos(latRad)));
    }

    static constexpr float kHover = 0.5F;

private:
    VehicleState& state_;
};

struct Sim {
    VehicleState  state{};
    MissionPlan   mission{};
    bool          rcAlive{true};
    bool          gcsAlive{true};
    bool          guidedAlive{true};
};

void initState(Sim& sim)
{
    VehicleState& s = sim.state;

    s.now = TimePoint{Millis{1000}};

    s.battery = Battery{.cellVoltage = 4.05F, .remaining = 0.92F};
    s.imu     = ImuStatus{.gyroHealthy = true, .accelHealthy = true,
                          .attitudeValid = true, .accelZVariance = 0.03F};
    s.vertical = VerticalStatus{.baroHealthy = true, .rangefinderHealthy = true,
                                .ekfPosValid = true, .altitudeRelM = 0.0F, .velocityMs = 0.0F};

    s.horizontal = HorizontalStatus{
        .fixType = 3, .sats = 14, .hdop = 0.8F, .vdop = 1.2F,
        .ekfPosValid = true, .innovPosNorm = 0.08F, .innovVelNorm = 0.11F,
        .compassHealthy = true, .compassYawErrorDeg = 2.0F,
        .position = GeoPoint{504500000, 303000000},   // умовна точка старту
        .velNorthMs = 0.0F, .velEastMs = 0.0F};

    s.sticks     = Sticks{};
    s.links      = Links{s.now, s.now, s.now};
    s.propulsion = Propulsion{.armed = false, .motorOutput = 0.0F,
                              .hoverThrottle = Vehicle::kHover};
    s.home       = s.horizontal.position;
    s.mission    = &sim.mission;
}

void loadMission(Sim& sim, bool validCrc)
{
    sim.mission.clear();

    const GeoPoint home = sim.state.home.value();

    for (int i = 1; i <= 3; ++i) {
        sim.mission.add(Waypoint{
            .at      = GeoPoint{home.lat1e7 + i * 900, home.lon1e7 + i * 400},
            .altRelM = 25.0F,
            .command = 16u});   // MAV_CMD_NAV_WAYPOINT
    }
    sim.mission.setStoredCrc(validCrc ? sim.mission.crc()
                                      : static_cast<std::uint16_t>(sim.mission.crc() ^ 0x00FFU));
}

void run(Sim& sim, FlightModeFsm& fsm, Vehicle& vehicle, Millis duration)
{
    for (Millis elapsed{0}; elapsed < duration; elapsed += kTick) {
        sim.state.now += kTick;

        if (sim.rcAlive) {
            sim.state.links.lastRcFrame = sim.state.now;
        }
        if (sim.gcsAlive) {
            sim.state.links.lastGcsHeartbeat = sim.state.now;
        }
        if (sim.guidedAlive) {
            sim.state.links.lastGuidedSetpoint = sim.state.now;
        }

        fsm.update(sim.state);

        // Силовий каскад повідомляє автоматові, чи справді йдуть сигнали.
        sim.state.propulsion.armed = fsm.armed();
        vehicle.step(fsm.throttle(), fsm.controllers().tiltNorthDeg(),
                     fsm.controllers().tiltEastDeg());
    }
}

void show(const Sim& sim, const FlightModeFsm& fsm, std::string_view tag)
{
    std::cout << std::format(
        "  [{:6.2f}] {:<22} mode={:<9} prio={:<16} thr={:.2f} alt={:5.1f} vz={:+5.2f} land={}\n",
        std::chrono::duration<double>{sim.state.now.time_since_epoch()}.count(), tag,
        name(fsm.mode()), name(fsm.priority()), fsm.throttle(),
        sim.state.vertical.altitudeRelM, sim.state.vertical.velocityMs,
        LandDetector::name(fsm.landPhase()));
}

void act(std::string_view title)
{
    std::cout << std::format("\n=== {} ===\n", title);
}

}  // namespace

int main()
{
    Sim sim;

    initState(sim);

    ConsoleReporter reporter{sim.state};
    FlightModeFsm   fsm{Params{}, reporter, sim.state};
    Vehicle         vehicle{sim.state};

    act("1. Озброєння і зліт у Stabilize");
    (void)fsm.requestArm(sim.state);
    sim.state.propulsion.armed = true;
    sim.state.sticks.throttle  = 0.68F;          // ручка вгору: набір висоти
    run(sim, fsm, vehicle, Millis{4000});
    show(sim, fsm, "після набору");

    act("2. Перехід у AltHold: уставка й інтегратор фіксуються");
    sim.state.sticks.throttle = 0.50F;           // ручка в мертву зону
    (void)fsm.request(Mode::AltHold, Priority::Routine, sim.state);
    run(sim, fsm, vehicle, Millis{3000});
    show(sim, fsm, "утримання висоти");

    act("3. Перехід у PosHold, потім у Auto з валідним планом");
    (void)fsm.request(Mode::PosHold, Priority::Routine, sim.state);
    run(sim, fsm, vehicle, Millis{1000});
    loadMission(sim, false);
    std::cout << "  -- план із зіпсованою контрольною сумою:\n";
    (void)fsm.request(Mode::Auto, Priority::Routine, sim.state);
    loadMission(sim, true);
    std::cout << "  -- той самий план із правильною сумою:\n";
    (void)fsm.request(Mode::Auto, Priority::Routine, sim.state);
    run(sim, fsm, vehicle, Millis{2000});
    show(sim, fsm, "автономна місія");

    act("4. Стрибок газу: спроба перейти в Manual зі скинутою ручкою");
    sim.state.sticks.throttle = 0.0F;
    (void)fsm.request(Mode::Manual, Priority::Routine, sim.state);
    show(sim, fsm, "після відмови");
    std::cout << "  -- пілот зводить ручку з поточною тягою:\n";
    sim.state.sticks.throttle = fsm.throttle();
    (void)fsm.request(Mode::Stabilize, Priority::Routine, sim.state);
    run(sim, fsm, vehicle, Millis{500});
    show(sim, fsm, "після узгодження");

    act("5. Роззброєння в повітрі: комбінація стіків ігнорується");
    sim.state.sticks.disarmCombo = true;
    run(sim, fsm, vehicle, Millis{100});
    sim.state.sticks.disarmCombo = false;
    show(sim, fsm, "мотори працюють");

    act("6. Втрата супутників у польоті: каскадна деградація");
    (void)fsm.request(Mode::PosHold, Priority::Routine, sim.state);
    run(sim, fsm, vehicle, Millis{500});
    show(sim, fsm, "утримання точки");
    sim.state.horizontal.sats         = 3;
    sim.state.horizontal.hdop         = 3.4F;
    sim.state.horizontal.innovPosNorm = 1.4F;
    sim.state.horizontal.ekfPosValid  = false;
    run(sim, fsm, vehicle, Millis{500});
    show(sim, fsm, "після збою GNSS");

    act("7. Гістерезис: повернення нагору лише після витриманої умови");
    sim.state.horizontal.sats         = 12;
    sim.state.horizontal.hdop         = 0.9F;
    sim.state.horizontal.innovPosNorm = 0.10F;
    sim.state.horizontal.ekfPosValid  = true;
    std::cout << "  -- запит одразу після відновлення сигналу:\n";
    (void)fsm.request(Mode::PosHold, Priority::Routine, sim.state);
    run(sim, fsm, vehicle, Millis{2500});
    std::cout << "  -- запит після витримки:\n";
    (void)fsm.request(Mode::PosHold, Priority::Routine, sim.state);
    show(sim, fsm, "повернення в PosHold");

    act("8. Втрата пульта: витіснення рівня 3");
    sim.rcAlive = false;
    run(sim, fsm, vehicle, Millis{2000});
    show(sim, fsm, "аварійне повернення");
    std::cout << "  -- пілот намагається перемкнутися, поки лінк мертвий:\n";
    (void)fsm.request(Mode::Auto, Priority::Routine, sim.state);

    act("9. Критичний розряд: витіснення рівня 4 блокує все");
    sim.rcAlive                  = true;
    sim.state.battery.cellVoltage = 3.22F;
    sim.state.battery.remaining   = 0.07F;
    run(sim, fsm, vehicle, Millis{200});
    show(sim, fsm, "примусова посадка");
    std::cout << "  -- спроба повернутися в місію під критичним failsafe:\n";
    (void)fsm.request(Mode::Auto, Priority::Routine, sim.state);

    act("10. Детектор посадки: контакт, витримка, роззброєння");
    run(sim, fsm, vehicle, Millis{60000});
    show(sim, fsm, "цикл завершено");

    act("11. Апаратна відсічка перекриває навіть штатний запит");
    sim.state.killSwitch = true;
    run(sim, fsm, vehicle, Millis{100});
    show(sim, fsm, "після відсічки");
    (void)fsm.request(Mode::Stabilize, Priority::Routine, sim.state);
    (void)fsm.requestArm(sim.state);

    std::cout << "\nсценарій завершено\n";
    return 0;
}
