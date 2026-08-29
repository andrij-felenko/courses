#pragma once

#include <chrono>
#include <expected>
#include <string>
#include <string_view>

namespace cp {

/* Коди відмов, які врешті бачить оператор у панелі. */
enum class ErrCode : int {
    None = 0,
    TtlExpired = 104,
    Busy = 105,
    BadPayload = 106,
    HardwareFault = 301,
};

/* Наказ, що прийшов темою devices/<id>/cmd/req. */
struct Downlink {
    std::string       cmdId;
    int               targetPct{0};
    std::chrono::seconds issuedAt{0};
    std::chrono::seconds ttl{60};
};

enum class ParseError {
    NotJson,
    NoCmdId,
    NoTarget,
    TargetOutOfRange,
};

std::string_view describe(ParseError error) noexcept;

/* Замість -1 з errno — очікуваний результат: або наказ, або назва вади. */
std::expected<Downlink, ParseError> parseDownlink(std::string_view payload);

/* Фаза 1: квитанція прийому (ACK_RECEIVED / ACK_DUPLICATE). */
void publishAck(std::string_view cmdId, std::string_view status);

/* Проміжні звіти й фаза 2: STARTED / IN_PROGRESS / COMPLETED / FAILED / EXPIRED. */
void publishStatus(std::string_view cmdId, std::string_view state,
                   int progressPct, int valuePct, ErrCode err);

/* Кадр, з якого не вдалося дістати навіть cmd_id. */
void publishNack(std::string_view reason);

}  // namespace cp
