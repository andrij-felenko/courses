// link.hpp — RAII-обгортка каналу до шлюзу.
//
// Дескриптор закриває деструктор: жодних goto out і close(fd) у кожній
// гілці помилки. Клас лише возить байти — межі кадру знаходить StreamFramer
// із protocol.hpp, тож розкладка тут інша, ніж у сі-версії.
#pragma once

#include <chrono>
#include <expected>
#include <optional>
#include <string>

#include "protocol.hpp"

namespace field {

enum class LinkError { Closed, Io };
[[nodiscard]] std::string_view describe(LinkError err) noexcept;

class TcpLink {
public:
    TcpLink() = default;
    ~TcpLink();

    TcpLink(const TcpLink&) = delete;
    TcpLink& operator=(const TcpLink&) = delete;
    TcpLink(TcpLink&& other) noexcept;
    TcpLink& operator=(TcpLink&& other) noexcept;

    [[nodiscard]] static std::expected<TcpLink, std::string> connect(const std::string& host,
                                                                     const std::string& port);

    [[nodiscard]] std::expected<void, LinkError> send(const Wire& wire);

    // nullopt — за відведений час кадру не було; помилка — канал більше не живий.
    [[nodiscard]] std::expected<std::optional<Wire>, LinkError> read_frame(
        std::chrono::milliseconds timeout);

    [[nodiscard]] std::size_t resync_drops() const noexcept { return framer_.resync_drops(); }

private:
    explicit TcpLink(int fd) noexcept : fd_(fd) {}

    int fd_{-1};
    StreamFramer framer_;
};

}  // namespace field
