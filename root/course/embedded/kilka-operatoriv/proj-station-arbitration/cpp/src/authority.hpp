// Бортовий арбітр повноважень наземних станцій.
//
// Стоїть між парсером кадрів і виконавчими контурами: жоден пакет керування
// польотом не потрапляє в мікшер, поки арбітр не підтвердив, що саме ця
// станція тримає токен пілота.
#pragma once

#include <cstdint>
#include <expected>
#include <random>
#include <string_view>

#include "station_table.hpp"

namespace gcs {

// Оренда токена: не почули heartbeat власника довше — звʼязок утрачено.
inline constexpr Millis kHeartbeatTimeout{1000};
// Скільки в змінного пілота часу на перевірку стіків.
inline constexpr Millis kHandoverTimeout{5000};
// Скільки станція лежить у реєстрі без heartbeat (це не оренда, а прибирання).
inline constexpr Millis kStationTtl{30000};
// Стіки мусять простояти в нейтралі стільки, перш ніж борт віддасть токен.
inline constexpr Millis kNeutralHold{300};

// Мертва зона з гістерезисом: увійти в нейтраль важче, ніж у ній лишитися.
// 3% від шкали ±1000 на вхід, 4.5% на утримання — дрейф потенціометрів
// (-18…+24 одиниці на бюджетному пульті) перевірку не зриває.
inline constexpr std::int16_t kDeadbandEnter = 30;
inline constexpr std::int16_t kDeadbandExit  = 45;
// Газ не центрується — його звіряють із поточною тягою, 8% від шкали 0…1000.
inline constexpr std::int16_t kThrottleWindow = 80;

enum class State : std::uint8_t {
    Idle,               // токена не тримає ніхто
    PilotActive,        // є власник, оренда свіжа
    HandoverWaitStick,  // передача зміни: чекаємо нейтралі в кандидата
    LinkLost,           // оренда протермінована, керування заборонено
    CommanderLocked,    // командир перехопив борт
};

enum class Error : std::uint8_t {
    UnknownStation,    // станції немає в реєстрі або її heartbeat протух
    RoleDenied,        // станція є, але такої ролі за нею не записано
    Busy,              // токен уже в когось
    WrongState,        // операція не має сенсу в поточному стані
    NotOwner,          // просить не той, хто має право просити
    StickNotNeutral,   // крен/тангаж/рискання поза мертвою зоною
    StickHold,         // нейтраль є, але ще не витримана за часом
    ThrottleMismatch,  // газ не збігається з поточною тягою
    HandoverTimeout,   // вікно передачі зміни згоріло
    Locked,            // борт під командиром
    TableFull,         // реєстр станцій забитий
};

// Строгий тип замість голого uint32_t: переплутати nonce з ідентифікатором
// станції компілятор більше не дасть.
struct Token {
    std::uint32_t value{0};
    [[nodiscard]] friend constexpr bool operator==(Token, Token) noexcept = default;
};

struct StickAxes {
    std::int16_t roll{0};      // -1000 .. +1000
    std::int16_t pitch{0};     // -1000 .. +1000
    std::int16_t yaw{0};       // -1000 .. +1000
    std::int16_t throttle{0};  //     0 .. +1000

    [[nodiscard]] constexpr bool centered(std::int16_t limit) const noexcept {
        auto within = [limit](std::int16_t v) { return v >= -limit && v <= limit; };
        return within(roll) && within(pitch) && within(yaw);
    }
};

// Критична секція як RAII замість пари макросів enter/exit: із неї не можна
// вийти, забувши закрити, — навіть по винятку.
class CriticalSection {
public:
    CriticalSection() noexcept;
    ~CriticalSection() noexcept;
    CriticalSection(const CriticalSection&) = delete;
    CriticalSection& operator=(const CriticalSection&) = delete;
};

class StationArbiter {
public:
    // seed бери з реального джерела ентропії (UID кристала, шум АЦП), а не з
    // константи: інакше nonce передбачуваний.
    explicit StationArbiter(std::uint32_t seed, Millis now) noexcept;

    // Кожен heartbeat від будь-якої станції. Статусів лінка, які станція
    // повідомляє про себе, арбітр не читає: рішення про звʼязок ухвалює лише
    // бортовий таймер.
    std::expected<void, Error> process_heartbeat(std::uint8_t gcs_id, Roles roles, Millis now) noexcept;

    std::expected<Token, Error> request_pilot_token(std::uint8_t gcs_id, Millis now) noexcept;

    std::expected<void, Error> initiate_handover(std::uint8_t current_pilot,
                                                 std::uint8_t target_gcs, Millis now) noexcept;

    // Кандидат шле положення стіків десятки разів на секунду; токен
    // повертається один-єдиний раз — у мить передачі.
    std::expected<Token, Error> confirm_handover_sticks(std::uint8_t candidate_id,
                                                        const StickAxes& sticks,
                                                        Millis now) noexcept;

    std::expected<void, Error> cancel_handover(std::uint8_t requester_id) noexcept;

    // Безумовне перехоплення: токен переходить до командира незалежно від
    // стану, старий nonce миттєво стає недійсним.
    std::expected<Token, Error> commander_override(std::uint8_t commander_id, Millis now) noexcept;
    std::expected<void, Error> release_override(std::uint8_t commander_id) noexcept;

    // Гарячий шлях, 50 Гц: усередині лише порівняння цілих.
    [[nodiscard]] bool flight_allowed(std::uint8_t src_gcs_id, Token token) const noexcept;

    // Канал корисного навантаження живе окремо: він не залежить ні від токена
    // пілота, ні від командирського замка.
    [[nodiscard]] bool payload_allowed(std::uint8_t src_gcs_id, Millis now) const noexcept;

    void set_current_thrust(std::int16_t thrust) noexcept { current_thrust_ = thrust; }

    // Тільки з таймера або високопріоритетної задачі: поруч із записом логів
    // на SD 150 мс запису дадуть фальшивий тайм-аут оренди.
    void tick(Millis now) noexcept;

    [[nodiscard]] State state() const noexcept { return state_; }
    [[nodiscard]] std::uint8_t active_pilot() const noexcept { return pilot_id_; }
    [[nodiscard]] Token token() const noexcept { return token_; }

private:
    [[nodiscard]] Token next_token() noexcept;
    Token commit_owner(std::uint8_t new_owner, Millis now, State new_state) noexcept;
    void drop_handover() noexcept;

    StationTable stations_{};

    std::uint8_t pilot_id_{0};
    std::uint8_t pending_pilot_id_{0};
    std::uint8_t commander_id_{0};

    Millis pilot_lease_deadline_{0};
    Millis handover_deadline_{0};
    std::optional<Millis> neutral_since_{};  // порожньо — нейтраль не зафіксована

    Token token_{};
    std::int16_t current_thrust_{0};

    State state_{State::Idle};
    State resume_state_{State::Idle};  // куди вернутися після LinkLost

    std::minstd_rand rng_;
};

[[nodiscard]] std::string_view to_string(Error error) noexcept;
[[nodiscard]] std::string_view to_string(State state) noexcept;

}  // namespace gcs
