#pragma once

// Потоковий верифікатор і встановлювач офлайн-пакета.
// Порти платформи — чотири вузькі інтерфейси: звідки байти пакета, куди
// їх писати, хто рахує підписи і де живе стан завантаження.

#include <optional>
#include <span>

#include "package_format.hpp"
#include "sha256.hpp"

namespace upkg {

// Носій із пакетом: FatFS на USB-флешці техніка або буфер шлюзу.
// Верифікатору байдуже, звідки байти, — він просить діапазон.
class PackageMedia {
public:
    virtual ~PackageMedia() = default;
    [[nodiscard]] virtual bool read(std::uint32_t offset,
                                    std::span<std::uint8_t> dst) = 0;
    [[nodiscard]] virtual bool write(std::uint32_t offset,
                                     std::span<const std::uint8_t> src) = 0;
};

// Неактивний банк Slot B. Slot A з робочою прошивкою сюди не потрапляє
// взагалі — саме тому обрив живлення нікого не вбиває.
class FlashSlot {
public:
    virtual ~FlashSlot() = default;
    [[nodiscard]] virtual bool erase(std::uint32_t offset,
                                     std::uint32_t length) = 0;
    [[nodiscard]] virtual bool program(std::uint32_t offset,
                                       std::span<const std::uint8_t> src) = 0;
    [[nodiscard]] virtual bool read(std::uint32_t offset,
                                    std::span<std::uint8_t> dst) = 0;
};

// Криптографія платформи: ROM MCU, апаратний прискорювач або Monocypher.
// Своєї арифметики кривих верифікатор не має й мати не повинен.
class CryptoEngine {
public:
    virtual ~CryptoEngine() = default;
    [[nodiscard]] virtual bool verify(std::span<const std::uint8_t> message,
                                      const Signature& signature,
                                      const PublicKey& key) const = 0;
    [[nodiscard]] virtual std::optional<Signature> signReceipt(
        std::span<const std::uint8_t> message) const = 0;
};

// Незалежна область конфігурації (NVS) із прапорцем слота.
class BootConfig {
public:
    virtual ~BootConfig() = default;
    [[nodiscard]] virtual bool store(const BootState& state) = 0;
};

class Installer {
public:
    // Fresh — чиста прошивка, Resume — продовження після знеструмлення.
    enum class Mode { Fresh, Resume };

    Installer(Policy policy, PackageMedia& media, FlashSlot& flash,
              const CryptoEngine& crypto, BootConfig& boot)
        : policy_(policy), media_(media), flash_(flash),
          crypto_(crypto), boot_(boot) {}

    // Усі чотири фази поспіль. Квитанція повертається й тоді, коли фаза
    // даних провалилася, — але тільки після дійсного підпису заголовка.
    [[nodiscard]] Result<Receipt> install(Mode mode);

private:
    struct Prefix {
        Header header;
        Signature signature;
    };

    [[nodiscard]] Result<Prefix> readPrefix();
    [[nodiscard]] Result<void> validate(const Prefix& prefix) const;
    [[nodiscard]] Result<void> verifyHashTable(const Header& header);
    [[nodiscard]] Result<Hash> streamChunks(const Header& header, Mode mode);
    [[nodiscard]] Result<Receipt> emitReceipt(const Header& header,
                                              std::optional<Error> failure,
                                              const Hash& image_hash);

    Policy policy_;
    PackageMedia& media_;
    FlashSlot& flash_;
    const CryptoEngine& crypto_;
    BootConfig& boot_;

    // Єдиний буфер сектора — це вся ціна операції в пам'яті.
    std::array<std::uint8_t, kChunkSize> buffer_{};
};

}  // namespace upkg
