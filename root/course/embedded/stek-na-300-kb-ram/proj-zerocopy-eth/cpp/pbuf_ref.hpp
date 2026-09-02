#pragma once

#include <cstddef>
#include <cstdint>
#include <span>
#include <utility>

extern "C" {
#include "lwip/pbuf.h"
}

namespace net {

/// Одноосібне володіння посиланням на pbuf.
///
/// У драйвері зустрічаються рівно два джерела посилань: щойно виділений буфер
/// (pbuf_alloc уже дав ref = 1) і чужий кадр зі стека, на який передача бере
/// ДОДАТКОВЕ посилання на час роботи DMA. Обидва звільняються однаково, тож
/// «забув pbuf_free на гілці помилки» тут просто не виражається.
class PbufRef {
public:
    PbufRef() noexcept = default;

    /// Перебирає готове посилання; лічильник не чіпаємо.
    explicit PbufRef(pbuf* p) noexcept : p_{p} {}

    /// Додаткове посилання на чужий кадр — це і є TX zero-copy.
    [[nodiscard]] static PbufRef share(pbuf* p) noexcept
    {
        if (p != nullptr) {
            pbuf_ref(p);
        }
        return PbufRef{p};
    }

    PbufRef(const PbufRef&) = delete;
    PbufRef& operator=(const PbufRef&) = delete;

    PbufRef(PbufRef&& other) noexcept : p_{std::exchange(other.p_, nullptr)} {}

    PbufRef& operator=(PbufRef&& other) noexcept
    {
        if (this != &other) {
            reset();
            p_ = std::exchange(other.p_, nullptr);
        }
        return *this;
    }

    ~PbufRef() { reset(); }

    void reset() noexcept
    {
        if (p_ != nullptr) {
            pbuf_free(p_);
            p_ = nullptr;
        }
    }

    /// Віддає володіння назовні — саме так кадр іде в netif->input.
    [[nodiscard]] pbuf* release() noexcept { return std::exchange(p_, nullptr); }

    [[nodiscard]] pbuf* get() const noexcept { return p_; }
    explicit operator bool() const noexcept { return p_ != nullptr; }

    /// Область корисних даних. Довжина йде разом із вказівником, тож
    /// «передав буфер, забув розмір» тут не буває.
    [[nodiscard]] std::span<std::byte> payload() const noexcept
    {
        return {static_cast<std::byte*>(p_->payload), p_->len};
    }

    [[nodiscard]] std::uint32_t address() const noexcept
    {
        return reinterpret_cast<std::uint32_t>(p_->payload);
    }

    /// Обрізає ланку до справжньої довжини кадру (без FCS).
    void resize(std::uint16_t len) noexcept
    {
        p_->len = len;
        p_->tot_len = len;
    }

private:
    pbuf* p_{nullptr};
};

}  // namespace net
