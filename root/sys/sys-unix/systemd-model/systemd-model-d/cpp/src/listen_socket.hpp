#pragma once

#include "unique_fd.hpp"

#include <expected>
#include <filesystem>
#include <optional>
#include <string_view>
#include <system_error>
#include <utility>

// Слухаючий сокет служби. Звідки він узявся, знає лише цей клас: решта коду
// бачить просто дескриптор, готовий до accept4().
class ListenSocket {
public:
    enum class Source { Systemd, Own };

    // Помилка налаштування — очікуваний результат, а не виняток: викликач
    // мусить розрізнити «менеджер передав не те» й «немає прав на каталог».
    static std::expected<ListenSocket, std::error_code> acquire(
        const std::filesystem::path& fallback_path);

    ListenSocket(const ListenSocket&) = delete;
    ListenSocket& operator=(const ListenSocket&) = delete;

    ListenSocket(ListenSocket&& other) noexcept;
    ListenSocket& operator=(ListenSocket&& other) noexcept;

    ~ListenSocket();

    [[nodiscard]] int fd() const noexcept { return fd_.get(); }
    [[nodiscard]] Source source() const noexcept { return source_; }
    [[nodiscard]] std::string_view source_name() const noexcept {
        return source_ == Source::Systemd ? "від менеджера" : "власний";
    }

private:
    ListenSocket(UniqueFd fd, Source source, std::optional<std::filesystem::path> owned)
        : fd_{std::move(fd)}, source_{source}, owned_path_{std::move(owned)} {}

    UniqueFd fd_;
    Source source_{Source::Systemd};
    // Заповнений лише тоді, коли сокет створили ми: файл менеджера не наш.
    std::optional<std::filesystem::path> owned_path_;
};
