#include "installer.hpp"

#include <cstring>

namespace upkg {
namespace {

template <class T>
std::span<const std::uint8_t> rawBytes(const T& value) {
    return {reinterpret_cast<const std::uint8_t*>(&value), sizeof(T)};
}

std::uint16_t statusCode(std::optional<Error> failure) {
    return failure ? static_cast<std::uint16_t>(*failure) : std::uint16_t{0};
}

}  // namespace

Result<Installer::Prefix> Installer::readPrefix() {
    // Читаємо в сирий буфер і копіюємо: пакована структура не терпить
    // ні чужого вирівнювання, ні гри з псевдонімами вказівників.
    std::array<std::uint8_t, kHeaderSize> raw{};
    if (!media_.read(0, raw)) {
        return std::unexpected(Error::Io);
    }
    Prefix prefix{};
    std::memcpy(&prefix.header, raw.data(), raw.size());

    if (!media_.read(kHeaderSize, prefix.signature)) {
        return std::unexpected(Error::Io);
    }
    return prefix;
}

Result<void> Installer::validate(const Prefix& prefix) const {
    const Header& h = prefix.header;

    if (h.magic != kMagic) {
        return std::unexpected(Error::InvalidMagic);
    }
    if (h.format_version != kFormatVersion || h.chunk_size != kChunkSize) {
        return std::unexpected(Error::Format);
    }
    if (h.payload_size == 0 || h.chunk_count == 0 || h.chunk_count > kMaxChunks) {
        return std::unexpected(Error::Format);
    }
    // Кількість чанків мусить точно відповідати довжині навантаження:
    // інакше підроблений заголовок пожене нас читати повз кінець файла.
    const std::uint32_t expected =
        (h.payload_size + kChunkSize - 1) / kChunkSize;
    if (h.chunk_count != expected) {
        return std::unexpected(Error::Format);
    }

    if (h.target_hw_id != policy_.hardware_id) {
        return std::unexpected(Error::HardwareMismatch);
    }
    // Строго "менше або дорівнює": повторний випуск із тим самим номером
    // теж відкат — саме ним повертають уже закриту вразливість.
    if (h.version_monotonic <= policy_.min_version) {
        return std::unexpected(Error::RollbackDetected);
    }

    // Підпис накладено рівно на 128 байтів заголовка.
    if (!crypto_.verify(rawBytes(h), prefix.signature, policy_.root_public_key)) {
        return std::unexpected(Error::SignatureInvalid);
    }
    return {};
}

Result<void> Installer::verifyHashTable(const Header& header) {
    // Підписаний заголовок ручається за хеш таблиці, а таблиця — за
    // кожен сектор окремо. Тому таблицю звіряємо цілком, ще до стирання.
    Sha256 hasher;
    std::uint32_t offset = tableOffset();
    std::uint32_t left = tableBytes(header);

    while (left > 0) {
        const std::uint32_t n = std::min<std::uint32_t>(left, kChunkSize);
        const std::span<std::uint8_t> part{buffer_.data(), n};
        if (!media_.read(offset, part)) {
            return std::unexpected(Error::Io);
        }
        hasher.update(part);
        offset += n;
        left -= n;
    }

    if (hasher.finish() != header.table_sha256) {
        return std::unexpected(Error::TableHashMismatch);
    }
    return {};
}

Result<Hash> Installer::streamChunks(const Header& header, Mode mode) {
    Sha256 image;
    const std::uint32_t data_offset = payloadOffset(header);

    for (std::uint32_t i = 0; i < header.chunk_count; ++i) {
        Hash expected{};
        if (!media_.read(tableOffset() + i * kHashSize, expected)) {
            return std::unexpected(Error::Io);
        }

        const std::uint32_t length = chunkLength(header, i);
        const std::uint32_t flash_offset = i * kChunkSize;
        const std::span<std::uint8_t> sector{buffer_.data(), length};

        if (mode == Mode::Resume) {
            // Продовження після знеструмлення: сектор, що вже лежить
            // у Slot B і збігається з таблицею, не переписуємо — байти
            // в ньому правильні, а ресурс NOR не безмежний. Недописаний
            // сектор хеш не пройде, і його стираємо точково.
            if (flash_.read(flash_offset, sector) &&
                Sha256::of(sector) == expected) {
                image.update(sector);
                continue;
            }
            if (!flash_.erase(flash_offset, kChunkSize)) {
                return std::unexpected(Error::FlashErase);
            }
        }

        if (!media_.read(data_offset + flash_offset, sector)) {
            return std::unexpected(Error::Io);
        }
        if (Sha256::of(sector) != expected) {
            return std::unexpected(Error::ChunkHashMismatch);
        }
        // Спершу хеш, і лише потім програмування сектора.
        if (!flash_.program(flash_offset, sector)) {
            return std::unexpected(Error::FlashWrite);
        }
        image.update(sector);
    }

    const Hash digest = image.finish();
    if (digest != header.final_sha256) {
        return std::unexpected(Error::FinalHashMismatch);
    }
    return digest;
}

Result<Receipt> Installer::emitReceipt(const Header& header,
                                       std::optional<Error> failure,
                                       const Hash& image_hash) {
    Receipt receipt{};
    receipt.body.magic = kReceiptMagic;
    receipt.body.device_serial = policy_.device_serial;
    receipt.body.hw_id = policy_.hardware_id;
    receipt.body.status = statusCode(failure);
    receipt.body.version = header.version_monotonic;
    receipt.body.boot_retries = failure ? 0 : kBootRetries;
    receipt.body.image_sha256 = image_hash;

    const auto signature = crypto_.signReceipt(rawBytes(receipt.body));
    if (!signature) {
        return std::unexpected(Error::Crypto);
    }
    receipt.signature = *signature;

    if (!media_.write(receiptOffset(header), rawBytes(receipt))) {
        return std::unexpected(Error::Io);
    }
    return receipt;
}

Result<Receipt> Installer::install(Mode mode) {
    auto prefix = readPrefix();
    if (!prefix) {
        return std::unexpected(prefix.error());
    }
    if (auto ok = validate(*prefix); !ok) {
        // Пакет чужий або підроблений — квитанції не буде: ми навіть
        // не знаємо, чи ці метадані стосуються нашого парку.
        return std::unexpected(ok.error());
    }
    const Header& header = prefix->header;

    if (auto ok = verifyHashTable(header); !ok) {
        return std::unexpected(ok.error());
    }

    // Пастка "стерли раніше, ніж перевірили". Slot B гине лише тепер,
    // коли підпис випуску і таблиця хешів уже підтверджені: інакше
    // кожен зіпсований файл коштував би платі циклу перезапису.
    if (mode == Mode::Fresh &&
        !flash_.erase(0, header.chunk_count * kChunkSize)) {
        return std::unexpected(Error::FlashErase);
    }

    auto image = streamChunks(header, mode);

    std::optional<Error> failure;
    if (!image) {
        failure = image.error();
    } else {
        // Новій прошивці дається три спроби завантажитися й підтвердити
        // себе; не підтвердить — сторожовий таймер поверне Slot A.
        const BootState state{header.version_monotonic,
                              SlotFlag::PendingVerify, kBootRetries};
        if (!boot_.store(state)) {
            failure = Error::NvsWrite;
        }
    }

    // Квитанцію пишемо і після невдачі: технікові потрібен доказ
    // причини, а не мовчазна відмова пристрою.
    auto receipt = emitReceipt(header, failure, image ? *image : Hash{});
    if (failure) {
        return std::unexpected(*failure);
    }
    return receipt;
}

}  // namespace upkg
