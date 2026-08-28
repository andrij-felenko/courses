// legacy_adapter.hpp — чистий C++20 інтерфейс
#pragma once
#include <memory>
#include <string>
#include <string_view>

namespace modern_app {

class LegacyDatabaseBridge {
public:
    LegacyDatabaseBridge();
    ~LegacyDatabaseBridge();

    LegacyDatabaseBridge(const LegacyDatabaseBridge&) = delete;
    LegacyDatabaseBridge& operator=(const LegacyDatabaseBridge&) = delete;
    LegacyDatabaseBridge(LegacyDatabaseBridge&&) noexcept;
    LegacyDatabaseBridge& operator=(LegacyDatabaseBridge&&) noexcept;

    [[nodiscard]] bool connect(std::string_view connection_string);
    [[nodiscard]] std::string execute(std::string_view query);

private:
    struct Impl;
    std::unique_ptr<Impl> pimpl_;
};

} // namespace modern_app
