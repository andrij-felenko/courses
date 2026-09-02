// Стендовий прогін: чистий сектор, збереження конфігурації, деградація
// комірки Flash, передпольотна валідація і сценарій обриву керування
// на тлі глушіння GNSS.

#include "params.hpp"
#include "status.hpp"
#include "storage.hpp"

#include <format>
#include <iostream>

namespace {

using namespace autopilot::failsafe;

constexpr float kRtlAltM = 60.0f;

void cliStatus(const ParamBlock& p, const TelemetryFrame& t)
{
    std::cout << std::format("[failsafe] Active faults mask : 0x{:08X} ({})\n",
                             std::to_underlying(t.active_faults),
                             t.active_faults == Fault::None ? "CLEAN" : "FAULT");
    for (Fault f : kAllFaults)
        if (has(t.active_faults, f))
            std::cout << std::format("[failsafe]   fault             : {}\n", toString(f));

    std::cout << std::format("[failsafe] Active action      : {} (arbiter: {})\n",
                             toString(t.active_action), toString(t.arbiter));
    std::cout << std::format("[failsafe] RC link quality    : {} fps, timeout: {:.1f}s\n",
                             t.rc_valid_frames_sec, p.get(ParamId::RcTimeout));
    std::cout << std::format("[failsafe] GNSS fix           : HDOP {:.2f} (max {:.2f})\n",
                             t.gnss_hdop, p.get(ParamId::GnssHdopMax));
    std::cout << std::format("[failsafe] Battery voltage    : {:.2f}V/cell, Crit: {:.2f}V\n",
                             t.batt_cell_min_v, p.get(ParamId::BattCritV));
    std::cout << std::format("[failsafe] Geofence           : {} (dist to breach: {:.1f}m)\n",
                             p.getInt(ParamId::FenceEnable) != 0 ? "ENABLED" : "DISABLED",
                             t.distance_to_fence_m);
}

void announce(const ParamBlock& p, const TelemetryFrame& t)
{
    for (Fault f : kAllFaults) {
        if (!has(t.active_faults, f))
            continue;
        const Notice n = statusText(f, t.active_faults, p, t);
        std::cout << std::format("STATUSTEXT[{} {:<9}] {}\n",
                                 std::to_underlying(n.severity), toString(n.severity), n.text);
    }
}

} // namespace

int main()
{
    ParamStore store;
    ParamBlock params;

    // --- Перше вмикання: сектор стертий, беремо заводські значення ---
    if (auto loaded = store.load()) {
        params = loaded->block;
        std::cout << std::format("boot: load OK, bank={}\n", loaded->bank);
    } else {
        std::cout << std::format("boot: load -> {}, заводські дефолти\n",
                                 toString(loaded.error()));
    }

    // Оператор підтягує конфігурацію під довшу місію.
    if (auto r = params.set("FS_FENCE_RADIUS", 4000.0f); !r)
        std::cout << std::format("param: FS_FENCE_RADIUS -> {}\n", toString(r.error()));
    if (auto r = params.set("FS_BATT_CRIT_V", 2.9f); !r)
        std::cout << std::format("param: FS_BATT_CRIT_V=2.90 -> {}\n", toString(r.error()));

    if (auto r = store.save(params); !r)
        std::cout << std::format("save: {}\n", toString(r.error()));
    else
        std::cout << std::format("save: OK, active bank={}, seq={}\n",
                                 store.activeBank(), store.sequence());

    // --- Деградація комірки в активному банку: CRC ловить, живе дзеркало ---
    store.bank(store.activeBank())
        .flipBit(kHeaderSize + 4 * static_cast<std::size_t>(ParamId::FenceRadius), 3);
    if (auto loaded = store.load()) {
        params = loaded->block;
        std::cout << std::format("reload after bit-flip: bank={}, radius={:.0f}, замін={}\n",
                                 loaded->bank, params.get(ParamId::FenceRadius), loaded->clamped);
    } else {
        std::cout << std::format("reload after bit-flip: {}\n", toString(loaded.error()));
    }

    // --- Передпольотна валідація ---
    const auto problems = params.validate(kRtlAltM);
    std::cout << std::format("pre-arm: {} порушень\n", problems.size());
    for (const auto& s : problems)
        std::cout << "  " << s << '\n';

    // --- Сценарій: 3.5 км від дому, обрив керування під час глушіння GNSS ---
    TelemetryFrame t{};
    t.timestamp_us = 742'315'000ull;
    t.rc_valid_frames_sec = 0;
    t.gnss_hdop = 4.8f;
    t.batt_cell_min_v = 3.62f;
    t.distance_to_fence_m = 500.0f;
    t.active_faults = Fault::RcLost | Fault::GnssHdop | Fault::GnssLost | Fault::EkfDiverged;

    const Decision d = decide(t.active_faults, params);
    t.active_action = d.action;
    t.arbiter = d.arbiter;

    std::cout << "\nnsh> failsafe status\n";
    cliStatus(params, t);
    std::cout << '\n';
    announce(params, t);

    // Кадр FAILSAFE_STATUS в ефір і назад — так його бачить наземна станція.
    const auto frame = pack(t);
    std::cout << std::format("\nFAILSAFE_STATUS ({} B):", frame.size());
    for (std::byte b : frame)
        std::cout << std::format(" {:02X}", std::to_integer<unsigned>(b));
    std::cout << '\n';

    if (auto back = unpack(frame))
        std::cout << std::format("decode: {}\n", toString(back->active_action));
    else
        std::cout << "decode: REJECTED\n";

    // Зв'язок відновився: після гістерезису повертаємо ручне керування.
    const Notice rec = recoveryNotice(params);
    std::cout << std::format("STATUSTEXT[{} {:<9}] {}\n",
                             std::to_underlying(rec.severity), toString(rec.severity), rec.text);
    return 0;
}
