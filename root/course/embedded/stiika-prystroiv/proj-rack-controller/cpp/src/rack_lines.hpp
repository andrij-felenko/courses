// Силові лінії слота: ключ живлення і ключ BOOT0.
#pragma once

#include <cstdint>

#include "posix.hpp"

class RackLines {
public:
    // Захоплює обидві лінії й одразу кладе їх у нуль.
    explicit RackLines(int slotId);

    void vcc(bool on);
    void boot0(bool high);

    // Знеструмити й віддати лінії ядру. Викликається з деструктора, тому мовчить.
    void shutdownQuietly() noexcept;

    ~RackLines() { shutdownQuietly(); }

    RackLines(RackLines&&) = default;
    RackLines& operator=(RackLines&&) = default;
    RackLines(const RackLines&) = delete;
    RackLines& operator=(const RackLines&) = delete;

private:
    void setLines(std::uint64_t mask, std::uint64_t bits);

    UniqueFd lines_;
};
