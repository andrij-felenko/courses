#include "protocol.hpp"

#include <charconv>
#include <format>
#include <iostream>
#include <mutex>
#include <optional>

namespace cp {
namespace {

/* Повноцінний парсер тут зайвий: формат наказу ми задаємо самі, полів чотири.
   string_view дозволяє різати кадр без жодного копіювання. */
std::optional<std::string_view> fieldTail(std::string_view json, std::string_view key)
{
    const std::string pattern = std::format("\"{}\"", key);
    const auto at = json.find(pattern);
    if (at == std::string_view::npos) {
        return std::nullopt;
    }
    auto tail = json.substr(at + pattern.size());

    const auto colon = tail.find_first_not_of(" \t");
    if (colon == std::string_view::npos || tail[colon] != ':') {
        return std::nullopt;
    }
    tail.remove_prefix(colon + 1);

    const auto value = tail.find_first_not_of(" \t");
    if (value == std::string_view::npos) {
        return std::nullopt;
    }
    tail.remove_prefix(value);
    return tail;
}

std::optional<std::string_view> stringField(std::string_view json, std::string_view key)
{
    const auto tail = fieldTail(json, key);
    if (!tail || tail->empty() || tail->front() != '"') {
        return std::nullopt;
    }
    const auto body = tail->substr(1);
    const auto end = body.find('"');
    if (end == std::string_view::npos) {
        return std::nullopt;
    }
    return body.substr(0, end);
}

std::optional<long long> intField(std::string_view json, std::string_view key)
{
    const auto tail = fieldTail(json, key);
    if (!tail) {
        return std::nullopt;
    }
    long long value = 0;
    const auto [ptr, ec] = std::from_chars(tail->data(), tail->data() + tail->size(), value);
    if (ec != std::errc{} || ptr == tail->data()) {
        return std::nullopt;
    }
    return value;
}

/* Публікують і мережевий потік, і воркер — рядки не повинні перемішатися. */
std::mutex g_output;

}  // namespace

std::string_view describe(ParseError error) noexcept
{
    switch (error) {
    case ParseError::NotJson:          return "кадр не схожий на JSON";
    case ParseError::NoCmdId:          return "немає поля cmd_id";
    case ParseError::NoTarget:         return "немає поля target_pct";
    case ParseError::TargetOutOfRange: return "target_pct поза межами 0..100";
    }
    return "невідома вада кадру";
}

std::expected<Downlink, ParseError> parseDownlink(std::string_view payload)
{
    if (payload.find('{') == std::string_view::npos) {
        return std::unexpected(ParseError::NotJson);
    }
    const auto cmdId = stringField(payload, "cmd_id");
    if (!cmdId || cmdId->empty()) {
        return std::unexpected(ParseError::NoCmdId);
    }
    const auto target = intField(payload, "target_pct");
    if (!target) {
        return std::unexpected(ParseError::NoTarget);
    }
    if (*target < 0 || *target > 100) {
        return std::unexpected(ParseError::TargetOutOfRange);
    }

    Downlink cmd;
    cmd.cmdId.assign(*cmdId);
    cmd.targetPct = static_cast<int>(*target);
    /* Часові поля не обов'язкові: без них наказ вважаємо свіжим на хвилину. */
    cmd.issuedAt = std::chrono::seconds{intField(payload, "issued_at").value_or(0)};
    cmd.ttl = std::chrono::seconds{intField(payload, "ttl_sec").value_or(60)};
    return cmd;
}

/* На платі тут стоїть публікація в MQTT з QoS 1; на стенді ту саму роль
   виконує stdout — його читає mosquitto_sub зі статті. */

void publishAck(std::string_view cmdId, std::string_view status)
{
    const std::scoped_lock lock{g_output};
    std::cout << std::format(R"([MQTT -> devices/zone1/cmd/ack] {{"cmd_id":"{}","status":"{}"}})",
                             cmdId, status)
              << '\n' << std::flush;
}

void publishStatus(std::string_view cmdId, std::string_view state,
                   int progressPct, int valuePct, ErrCode err)
{
    const std::scoped_lock lock{g_output};
    std::cout << std::format(
                     R"([MQTT -> devices/zone1/cmd/status] {{"cmd_id":"{}","state":"{}",)"
                     R"("progress_pct":{},"value_pct":{},"err":{}}})",
                     cmdId, state, progressPct, valuePct, static_cast<int>(err))
              << '\n' << std::flush;
}

void publishNack(std::string_view reason)
{
    const std::scoped_lock lock{g_output};
    std::cout << std::format(R"([MQTT -> devices/zone1/cmd/nack] {{"reason":"{}"}})", reason)
              << '\n' << std::flush;
}

}  // namespace cp
