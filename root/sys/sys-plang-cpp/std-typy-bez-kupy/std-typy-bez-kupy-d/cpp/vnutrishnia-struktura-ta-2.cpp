#include <variant>
#include <cstdint>

struct DataMsg { uint8_t payload[16]; };
struct ErrorMsg { uint32_t error_code; };
struct PingMsg { uint32_t sequence_id; };

using EventCpp = std::variant<DataMsg, ErrorMsg, PingMsg>;

template<class... Ts> struct Overload : Ts... { using Ts::operator()...; };
template<class... Ts> Overload(Ts...) -> Overload<Ts...>;

void handle_event_cpp(const EventCpp& ev) noexcept {
    std::visit(Overload{
        [](const DataMsg&) noexcept {},
        [](const ErrorMsg&) noexcept {},
        [](const PingMsg&) noexcept {}
    }, ev);
}
