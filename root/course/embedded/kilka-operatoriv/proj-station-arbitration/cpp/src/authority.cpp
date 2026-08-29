#include "authority.hpp"

#include <cstdlib>

#ifdef ARB_USE_FREERTOS
#  include "FreeRTOS.h"
#  include "task.h"
#endif

namespace gcs {

CriticalSection::CriticalSection() noexcept
{
#ifdef ARB_USE_FREERTOS
    taskENTER_CRITICAL();
#endif
}

CriticalSection::~CriticalSection() noexcept
{
#ifdef ARB_USE_FREERTOS
    taskEXIT_CRITICAL();
#endif
}

StationArbiter::StationArbiter(std::uint32_t seed, Millis now) noexcept
    : pilot_lease_deadline_{now}, rng_{seed != 0U ? seed : 1U}
{
    token_ = next_token();
}

Token StationArbiter::next_token() noexcept
{
    // Nonce ховає не таємницю, а вікно, у якому старий пульт міг би вклинитися
    // зі своїм застарілим токеном. Нуль лишаємо як «недійсний».
    std::uniform_int_distribution<std::uint32_t> dist{1U, 0xFFFF'FFFFU};
    return Token{dist(rng_)};
}

void StationArbiter::drop_handover() noexcept
{
    pending_pilot_id_ = 0;
    handover_deadline_ = Millis{0};
    neutral_since_.reset();
}

// Власник і nonce мусять помінятися разом: між двома окремими присвоєннями
// пролізе пакет старого пульта, звірений уже з новим власником.
Token StationArbiter::commit_owner(std::uint8_t new_owner, Millis now, State new_state) noexcept
{
    const Token fresh = next_token();
    {
        CriticalSection guard;
        pilot_id_ = new_owner;
        token_ = fresh;
        pilot_lease_deadline_ = now + kHeartbeatTimeout;
        state_ = new_state;
    }
    resume_state_ = new_state;
    drop_handover();
    return fresh;
}

std::expected<void, Error> StationArbiter::process_heartbeat(std::uint8_t gcs_id, Roles roles,
                                                             Millis now) noexcept
{
    if (!stations_.touch(gcs_id, roles, now)) {
        return std::unexpected(Error::TableFull);
    }
    if (pilot_id_ == 0 || gcs_id != pilot_id_) {
        return {};  // звичайна станція: оновили реєстр, і по всьому
    }

    // Власник токена мусить і далі мати роль, під якою його пустили: станція,
    // що перезапустилася лише як монітор, оренду не продовжує.
    const Role needed = (state_ == State::CommanderLocked) ? Role::Commander : Role::Pilot;
    if (!roles.has(needed)) {
        return std::unexpected(Error::RoleDenied);
    }

    pilot_lease_deadline_ = now + kHeartbeatTimeout;
    if (state_ == State::LinkLost) {
        // Звʼязок повернувся — токен той самий, nonce не міняємо: пульт нічого
        // не втрачав і перезапитувати його не мусить.
        state_ = resume_state_;
    }
    return {};
}

std::expected<Token, Error> StationArbiter::request_pilot_token(std::uint8_t gcs_id,
                                                                Millis now) noexcept
{
    if (state_ == State::CommanderLocked) {
        return std::unexpected(Error::Locked);
    }
    if (!stations_.authorized(gcs_id, Role::Pilot, now, kHeartbeatTimeout)) {
        return std::unexpected(stations_.find(gcs_id) ? Error::RoleDenied : Error::UnknownStation);
    }
    if (state_ != State::Idle && state_ != State::LinkLost) {
        return std::unexpected(Error::Busy);
    }
    // Із LinkLost токен забирає будь-який пілот: старий власник мовчить довше
    // за оренду, і борт не має причин тримати його місце.
    return commit_owner(gcs_id, now, State::PilotActive);
}

std::expected<void, Error> StationArbiter::initiate_handover(std::uint8_t current_pilot,
                                                             std::uint8_t target_gcs,
                                                             Millis now) noexcept
{
    if (state_ == State::CommanderLocked) {
        return std::unexpected(Error::Locked);
    }
    if (state_ != State::PilotActive) {
        return std::unexpected(Error::WrongState);
    }
    if (current_pilot != pilot_id_) {
        return std::unexpected(Error::NotOwner);
    }
    if (target_gcs == current_pilot) {
        return std::unexpected(Error::WrongState);
    }
    if (!stations_.authorized(target_gcs, Role::Pilot, now, kHeartbeatTimeout)) {
        return std::unexpected(stations_.find(target_gcs) ? Error::RoleDenied
                                                          : Error::UnknownStation);
    }

    pending_pilot_id_ = target_gcs;
    handover_deadline_ = now + kHandoverTimeout;
    neutral_since_.reset();
    state_ = State::HandoverWaitStick;
    resume_state_ = State::HandoverWaitStick;
    return {};
}

std::expected<Token, Error> StationArbiter::confirm_handover_sticks(std::uint8_t candidate_id,
                                                                    const StickAxes& sticks,
                                                                    Millis now) noexcept
{
    if (state_ != State::HandoverWaitStick) {
        return std::unexpected(Error::WrongState);
    }
    if (candidate_id != pending_pilot_id_) {
        return std::unexpected(Error::NotOwner);
    }
    if (now >= handover_deadline_) {
        state_ = State::PilotActive;
        resume_state_ = State::PilotActive;
        drop_handover();
        return std::unexpected(Error::HandoverTimeout);
    }
    // Кандидат міг зникнути з ефіру просто під час перевірки.
    if (!stations_.authorized(candidate_id, Role::Pilot, now, kHeartbeatTimeout)) {
        return std::unexpected(Error::UnknownStation);
    }

    // Гістерезис: поки нейтраль не зафіксована, поріг вузький; після фіксації
    // стіку дозволено трохи дрейфувати, не збиваючи витримку часу.
    const std::int16_t limit = neutral_since_ ? kDeadbandExit : kDeadbandEnter;
    if (!sticks.centered(limit)) {
        neutral_since_.reset();
        return std::unexpected(Error::StickNotNeutral);
    }

    // Газ у зависанні стоїть не в центрі, а десь на 45–60%. Порівнюємо його не
    // з нулем, а з поточною тягою: інакше в мить передачі мотори скинуть оберти.
    if (std::abs(int{sticks.throttle} - int{current_thrust_}) > int{kThrottleWindow}) {
        neutral_since_.reset();
        return std::unexpected(Error::ThrottleMismatch);
    }

    if (!neutral_since_) {
        neutral_since_ = now;  // одного вдалого кадру мало — тримай стіки
        return std::unexpected(Error::StickHold);
    }
    if ((now - *neutral_since_) < kNeutralHold) {
        return std::unexpected(Error::StickHold);
    }

    return commit_owner(candidate_id, now, State::PilotActive);
}

std::expected<void, Error> StationArbiter::cancel_handover(std::uint8_t requester_id) noexcept
{
    if (state_ != State::HandoverWaitStick) {
        return std::unexpected(Error::WrongState);
    }
    // Скасувати може або чинний пілот, або сам кандидат.
    if (requester_id != pilot_id_ && requester_id != pending_pilot_id_) {
        return std::unexpected(Error::NotOwner);
    }
    state_ = State::PilotActive;
    resume_state_ = State::PilotActive;
    drop_handover();
    return {};
}

std::expected<Token, Error> StationArbiter::commander_override(std::uint8_t commander_id,
                                                               Millis now) noexcept
{
    // Єдина умова — роль командира за живою станцією. Ні стан машини, ні згода
    // чинного пілота тут не питаються: у цьому й сенс перехоплення.
    if (!stations_.authorized(commander_id, Role::Commander, now, kHeartbeatTimeout)) {
        return std::unexpected(stations_.find(commander_id) ? Error::RoleDenied
                                                            : Error::UnknownStation);
    }
    commander_id_ = commander_id;
    return commit_owner(commander_id, now, State::CommanderLocked);
}

std::expected<void, Error> StationArbiter::release_override(std::uint8_t commander_id) noexcept
{
    if (state_ != State::CommanderLocked) {
        return std::unexpected(Error::WrongState);
    }
    if (commander_id != commander_id_) {
        return std::unexpected(Error::NotOwner);
    }
    const Token fresh = next_token();  // усі старі nonce протухають одразу
    {
        CriticalSection guard;
        pilot_id_ = 0;
        commander_id_ = 0;
        token_ = fresh;
        state_ = State::Idle;
    }
    resume_state_ = State::Idle;
    drop_handover();
    return {};
}

bool StationArbiter::flight_allowed(std::uint8_t src_gcs_id, Token token) const noexcept
{
    switch (state_) {
    case State::PilotActive:
    case State::HandoverWaitStick:
    case State::CommanderLocked:
        break;
    case State::Idle:
    case State::LinkLost:
        return false;  // ці стани керування не пропускають
    }
    return src_gcs_id == pilot_id_ && token == token_;
}

bool StationArbiter::payload_allowed(std::uint8_t src_gcs_id, Millis now) const noexcept
{
    // Навмисно не дивимося ні на state_, ні на токен пілота: оператор камери
    // працює навіть тоді, коли політ заблоковано. Розділення площин.
    return stations_.authorized(src_gcs_id, Role::Payload, now, kHeartbeatTimeout);
}

void StationArbiter::tick(Millis now) noexcept
{
    stations_.expire(now, kStationTtl);

    const bool holds_token = state_ == State::PilotActive ||
                             state_ == State::HandoverWaitStick ||
                             state_ == State::CommanderLocked;
    if (holds_token && now >= pilot_lease_deadline_) {
        // Куди повертатися, коли пульт озветься: під замком командира оренда
        // протухла так само, як у звичайного пілота.
        resume_state_ = (state_ == State::CommanderLocked) ? State::CommanderLocked
                                                           : State::PilotActive;
        state_ = State::LinkLost;
        drop_handover();
        return;
    }

    if (state_ == State::HandoverWaitStick && now >= handover_deadline_) {
        // Кандидат не показав нейтралі — керування лишається в старого пілота.
        state_ = State::PilotActive;
        resume_state_ = State::PilotActive;
        drop_handover();
    }
}

std::string_view to_string(Error error) noexcept
{
    switch (error) {
    case Error::UnknownStation:   return "UNKNOWN_STATION";
    case Error::RoleDenied:       return "ROLE_DENIED";
    case Error::Busy:             return "BUSY";
    case Error::WrongState:       return "WRONG_STATE";
    case Error::NotOwner:         return "NOT_OWNER";
    case Error::StickNotNeutral:  return "STICK_NOT_NEUTRAL";
    case Error::StickHold:        return "STICK_HOLD";
    case Error::ThrottleMismatch: return "THROTTLE_MISMATCH";
    case Error::HandoverTimeout:  return "HANDOVER_TIMEOUT";
    case Error::Locked:           return "LOCKED";
    case Error::TableFull:        return "TABLE_FULL";
    }
    return "?";
}

std::string_view to_string(State state) noexcept
{
    switch (state) {
    case State::Idle:              return "Idle";
    case State::PilotActive:       return "PilotActive";
    case State::HandoverWaitStick: return "HandoverWaitStick";
    case State::LinkLost:          return "LinkLost";
    case State::CommanderLocked:   return "CommanderLocked";
    }
    return "?";
}

}  // namespace gcs
