// Накопичувальний котел 3 кВт: таблиця правил приїжджає кадром із хаба,
// рушій крутиться в прошивці й тримає бак навіть без каналу назовні.
#include "rules/frame.hpp"

#include <array>
#include <cstdint>
#include <format>
#include <iostream>
#include <vector>

using namespace rules;

namespace {

// карта регістрів установки
constexpr std::uint8_t kTemp   = 0x00;   // Q16.16 °C
constexpr std::uint8_t kFlow   = 0x01;   // Q16.16 л/хв
constexpr std::uint8_t kPrice  = 0x02;   // Q16.16 $/кВт·год
constexpr std::uint8_t kHeater = 0x10;
constexpr std::uint8_t kPump   = 0x11;
constexpr std::uint8_t kTarget = 0x20;
constexpr std::uint8_t kFlowTimer = kTimerFirst + 0;

constexpr std::uint32_t kHubLeaseMs  = 3000;
constexpr std::int16_t  kFlowGraceMs = 5000;
constexpr std::uint32_t kTickMs      = 100;

std::vector<RuleDescriptor> buildRules() {
    return {
        // 1. Останній рубіж: кипіння. Фіксується, поки людина не скине аварію.
        {.id = 1,
         .flags = RuleFlag::Enabled | RuleFlag::SafetyCritical | RuleFlag::Latching,
         .condOp = ConditionOp::GreaterThan, .inputReg = kTemp, .threshold = q16(85.0),
         .actionOp = ActionOp::EmergencyStop, .outputTarget = kHeater},

        // 2. Протік упав — заводимо витримку 5 с; повернувся — знімаємо.
        {.id = 2,
         .flags = RuleFlag::Enabled | RuleFlag::SafetyCritical | RuleFlag::InvertAction,
         .condOp = ConditionOp::LessThan, .inputReg = kFlow, .threshold = q16(2.0),
         .actionOp = ActionOp::ArmTimer, .outputTarget = kFlowTimer,
         .actionParam = kFlowGraceMs},

        // 3. Витримка вичерпалась — аварійний стоп із фіксацією.
        {.id = 3,
         .flags = RuleFlag::Enabled | RuleFlag::SafetyCritical | RuleFlag::Latching,
         .condOp = ConditionOp::TimerExpired, .inputReg = kFlowTimer,
         .threshold = kFlowGraceMs,
         .actionOp = ActionOp::EmergencyStop, .outputTarget = kHeater},

        // 4. Насос крутиться завжди, поки немає аварії.
        {.id = 4, .flags = Flags{static_cast<std::uint16_t>(RuleFlag::Enabled)},
         .condOp = ConditionOp::Always, .inputReg = 0,
         .actionOp = ActionOp::OutputSet, .outputTarget = kPump, .actionParam = 1},

        // 5. Оптимізація витрат: дешева електрика — гріємо, подорожчала — ні.
        {.id = 5, .flags = RuleFlag::Enabled | RuleFlag::InvertAction,
         .condOp = ConditionOp::LessThan, .inputReg = kPrice, .threshold = q16(0.05),
         .actionOp = ActionOp::OutputSet, .outputTarget = kHeater, .actionParam = 1},

        // 6. Біля порогу кипіння дистанційні уставки не приймаємо.
        {.id = 6, .flags = RuleFlag::Enabled | RuleFlag::InvertAction,
         .condOp = ConditionOp::GreaterThan, .inputReg = kTemp, .threshold = q16(80.0),
         .actionOp = ActionOp::InhibitRemote, .outputTarget = kTarget},

        // 7. Зв'язку немає: ціна застаріла, гріти нічим не виправдано.
        //    Стоїть після правила 5, тож останнє слово за ним.
        {.id = 7, .flags = RuleFlag::Enabled | RuleFlag::FallbackActive,
         .condOp = ConditionOp::Always, .inputReg = 0,
         .actionOp = ActionOp::OutputSet, .outputTarget = kHeater, .actionParam = 0},
    };
}

void hubSend(RuleEngine& engine, std::span<const RuleDescriptor> table,
             bool corrupt, std::string_view what) {
    std::array<std::byte, kMaxFrame> frame{};
    const auto len = encodeRuleTable(table, frame);
    if (!len) {
        std::cout << std::format("  {:<38} кадр не склався: {}\n", what, describe(len.error()));
        return;
    }
    if (corrupt) { frame[kFrameHeader + 3] ^= std::byte{0x20}; }   // один перевернутий біт

    const Reply reply = handleFrame(engine, std::span{frame}.first(*len));
    std::cout << std::format("  {:<38} кадр {:3} Б → {}({} Б) {}\n", what, *len,
                             reply.status == RuleError::None ? "ACK" : "NACK",
                             reply.size, describe(reply.status));
}

// Груба модель бака: 3 кВт у воду, тепловтрати, перегрів без протоку.
void plantStep(RuleEngine& engine) {
    float temp = fromQ16(engine.read(kTemp));
    const float flow = fromQ16(engine.read(kFlow));
    const bool heat = engine.read(kHeater) != 0;

    temp += heat ? (flow >= 2.0f ? 0.15f : 0.45f) : -0.05f;
    engine.setSensor(kTemp, q16(temp));
}

void report(const RuleEngine& engine, std::uint32_t t, std::string_view event) {
    static std::int32_t prev = -1;
    const std::int32_t now = engine.read(kHeater) | (engine.read(kPump) << 1) |
                             (engine.read(kStatusWord) << 2) |
                             (engine.read(kFlowTimer) != 0 ? 1 << 8 : 0);
    if (event.empty() && now == prev) { return; }
    prev = now;

    std::cout << std::format(
        "{:6.1f} с | T={:5.1f}°C  протік={:4.1f}  ціна={:.3f} | ТЕН={} насос={} "
        "витримка={:5} мс |{}{}{} {}\n",
        t / 1000.0, fromQ16(engine.read(kTemp)), fromQ16(engine.read(kFlow)),
        fromQ16(engine.read(kPrice)), engine.read(kHeater), engine.read(kPump),
        engine.read(kFlowTimer),
        engine.inFallback() ? " БЕЗ ЗВ'ЯЗКУ" : "", engine.inEmergency() ? " АВАРІЯ" : "",
        engine.anyLatched() ? " ФІКСАЦІЯ" : "", event);
}

}  // namespace

int main() {
    RuleEngine engine{kHubLeaseMs, Timestamp{0}};
    engine.setSensor(kTemp, q16(40.0));
    engine.setSensor(kFlow, q16(6.0));
    engine.setSensor(kPrice, q16(0.08));

    const auto table = buildRules();

    std::cout << "=== завантаження таблиці правил ===\n";
    hubSend(engine, table, false, "повна таблиця");
    hubSend(engine, table, true, "той самий кадр з побитим байтом");

    // Хаб пробує лишити тільки «зручні» правила — захист має встояти.
    std::vector<RuleDescriptor> stripped;
    for (const auto& r : table) {
        if (!r.flags.has(RuleFlag::SafetyCritical)) { stripped.push_back(r); }
    }
    hubSend(engine, stripped, false, "таблиця без правил безпеки");

    // І спроба підсунути неіснуючий код умови.
    auto bogus = table;
    bogus[4].condOp = static_cast<ConditionOp>(0x7F);
    hubSend(engine, bogus, false, "правило з чужим кодом умови");

    std::cout << std::format("активних правил у прошивці: {}\n\n=== робота установки ===\n",
                             engine.ruleCount());

    for (std::uint32_t t = 0; t <= 34000; t += kTickMs) {
        std::string_view event;

        switch (t) {
            case 1000:
                engine.setSensor(kPrice, q16(0.045));
                event = "<- ціна впала до 0.045 $/кВт·год";
                break;
            case 9000:
                event = "<- обрив магістрального каналу: хаб замовк";
                break;
            case 14000:
                event = "<- канал відновлено";
                break;
            case 16000:
                engine.setSensor(kFlow, q16(0.3));
                event = "<- заклинило підшипник насоса";
                break;
            case 28000:
                engine.resetAlarm();
                event = "<- оператор скидає аварію (протоку ще немає)";
                break;
            case 30000:
                engine.setSensor(kFlow, q16(6.0));
                event = "<- насос замінено";
                break;
            case 31000:
                engine.resetAlarm();
                event = "<- скидання аварії";
                break;
            default:
                break;
        }

        // Серцебиття від хаба поновлює оренду керування щотакту.
        if (t < 9000 || t >= 14000) { engine.hubHeartbeat(Timestamp{t}); }

        engine.tick(Timestamp{t});
        plantStep(engine);
        report(engine, t, event);
    }

    // Хаб намагається підняти уставку, коли бак уже гарячий.
    const auto w = engine.remoteWrite(kTarget, q16(90.0));
    std::cout << std::format("\nдистанційна уставка 90 °C: {}\n",
                             w ? describe(RuleError::None) : describe(w.error()));
    return 0;
}
