// Бік пульта: складання запитів і пам'ять про поточну селекцію.
#pragma once

#include "protocol.hpp"

#include <optional>

namespace sbo {

class Gcs {
public:
    explicit Gcs(std::uint8_t source) : source_{source} {}

    [[nodiscard]] std::vector<std::uint8_t> select(std::uint8_t target, Comp comp,
                                                   Cmd cmd, Ms window);
    [[nodiscard]] std::vector<std::uint8_t> operate(std::vector<std::uint8_t> params = {});
    [[nodiscard]] std::vector<std::uint8_t> cancel();
    [[nodiscard]] std::vector<std::uint8_t> ping(std::uint8_t target);

    // Оновлює уявлення пульта про замок за квитанцією борту.
    void on_reply(const Frame& r);

    [[nodiscard]] bool armed() const noexcept { return armed_; }
    [[nodiscard]] std::uint32_t token() const noexcept { return token_; }
    [[nodiscard]] std::optional<Error> last_error() const noexcept { return last_error_; }

    // Для сценарію Б: пульт іще вірить у токен, який на борту вже згорів.
    void restore_token(std::uint32_t token) noexcept { token_ = token; }

private:
    Frame skeleton(MsgType type, std::uint8_t target);

    std::uint8_t source_;
    std::uint8_t seq_{0};
    std::uint8_t target_{0};
    Comp comp_{Comp::Fc};
    Cmd cmd_{Cmd::None};
    Ms window_{};
    std::uint32_t token_{0};
    bool armed_{false};
    std::optional<Error> last_error_{};
};

}  // namespace sbo
