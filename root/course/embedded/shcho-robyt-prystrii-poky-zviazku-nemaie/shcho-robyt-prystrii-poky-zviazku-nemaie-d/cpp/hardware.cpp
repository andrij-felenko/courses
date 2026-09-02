#include "hardware.hpp"

#include <algorithm>

namespace cart {

std::string_view describe(FlashError e) noexcept {
    switch (e) {
    case FlashError::OutOfRange: return "вихід за межі сектора";
    case FlashError::NotErased:  return "спроба писати в нестерті байти";
    }
    return "?";
}

void Board::reset() noexcept {
    for (auto& sector : flash_) sector.fill(std::byte{0xFF});   // стерта комірка NOR
    erases_.fill(0);
}

void Board::advance(Millis dt) noexcept {
    now_ += dt;
    serviceInterlock();
}

void Board::serviceInterlock() noexcept {
    // Логіка зовнішньої мікросхеми: витримка минула без імпульсу — ENABLE у нуль.
    if (now_ - lastPulse_ > kInterlockHold) interlockEnable_ = false;
}

void Board::pulseInterlock() noexcept {
    lastPulse_ = now_;
    interlockEnable_ = true;
}

void Board::setActuators(float throttle, float steering) noexcept {
    // У регістри ШІМ значення лягають завжди, але на затвори вони потраплять
    // лише тоді, коли активні обидва дозволи — програмний і апаратний.
    throttle_ = std::clamp(throttle, -1.0f, 1.0f);
    steering_ = std::clamp(steering, -1.0f, 1.0f);
}

std::expected<void, FlashError> Board::erase(std::size_t sector) noexcept {
    if (sector >= kSectorCount) return std::unexpected(FlashError::OutOfRange);
    flash_[sector].fill(std::byte{0xFF});
    ++erases_[sector];
    return {};
}

std::expected<void, FlashError> Board::write(std::size_t sector, std::size_t offset,
                                             std::span<const std::byte> src) noexcept {
    if (sector >= kSectorCount || offset + src.size() > kSectorSize)
        return std::unexpected(FlashError::OutOfRange);

    // NOR уміє лише гасити одиниці в нулі: запис поверх зайнятих байтів
    // мовчки зіпсував би сусідній запис, тому це помилка, а не «якось буде».
    const auto target = std::span{flash_[sector]}.subspan(offset, src.size());
    if (std::ranges::any_of(target, [](std::byte b) { return b != std::byte{0xFF}; }))
        return std::unexpected(FlashError::NotErased);

    std::ranges::copy(src, target.begin());
    return {};
}

std::expected<void, FlashError> Board::read(std::size_t sector, std::size_t offset,
                                            std::span<std::byte> dst) const noexcept {
    if (sector >= kSectorCount || offset + dst.size() > kSectorSize)
        return std::unexpected(FlashError::OutOfRange);
    std::ranges::copy(std::span{flash_[sector]}.subspan(offset, dst.size()), dst.begin());
    return {};
}

std::uint32_t Board::eraseCount(std::size_t sector) const noexcept {
    return sector < kSectorCount ? erases_[sector] : 0U;
}

std::size_t Board::send(std::span<const std::byte> data) noexcept {
    if (!radioUp_) return 0U;                       // ефір мовчить — нічого не пішло
    const auto accepted = std::min(data.size(), kRadioMtu);
    radioBytes_ += static_cast<std::uint32_t>(accepted);
    return accepted;
}

}  // namespace cart
