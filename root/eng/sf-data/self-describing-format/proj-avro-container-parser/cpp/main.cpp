#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <span>
#include <memory>
#include <optional>
#include <expected>
#include <array>
#include <cstring>
#include <cstdint>

namespace avro {

constexpr size_t SYNC_SIZE = 16;
constexpr size_t MAGIC_SIZE = 4;
constexpr std::array<uint8_t, MAGIC_SIZE> EXPECTED_MAGIC = {'O', 'b', 'j', 0x01};

enum class ParseError {
    UnexpectedEof,
    InvalidMagic,
    CorruptedVarint,
    SyncMismatch,
    InvalidSchema
};

/* Зручний неволодіючий зчитувач двійкового зрізу */
class SpanReader {
public:
    explicit SpanReader(std::span<const uint8_t> buffer) : buffer_(buffer), offset_(0) {}

    [[nodiscard]] bool has_bytes(size_t n) const noexcept {
        return offset_ + n <= buffer_.size();
    }

    [[nodiscard]] size_t remaining() const noexcept {
        return buffer_.size() - offset_;
    }

    [[nodiscard]] size_t offset() const noexcept {
        return offset_;
    }

    std::expected<uint8_t, ParseError> read_u8() noexcept {
        if (!has_bytes(1)) return std::unexpected(ParseError::UnexpectedEof);
        return buffer_[offset_++];
    }

    /* Зчитування 64-бітного цілого Zigzag Varint */
    std::expected<int64_t, ParseError> read_zigzag_long() noexcept {
        uint64_t raw = 0;
        int shift = 0;

        while (has_bytes(1)) {
            uint8_t b = buffer_[offset_++];
            raw |= static_cast<uint64_t>(b & 0x7F) << shift;
            if ((b & 0x80) == 0) {
                int64_t decoded = static_cast<int64_t>((raw >> 1) ^ (-(raw & 1)));
                return decoded;
            }
            shift += 7;
            if (shift >= 64) return std::unexpected(ParseError::CorruptedVarint);
        }
        return std::unexpected(ParseError::UnexpectedEof);
    }

    /* Зчитування рядка UTF-8 */
    std::expected<std::string, ParseError> read_string() {
        auto len_res = read_zigzag_long();
        if (!len_res || *len_res < 0) return std::unexpected(ParseError::CorruptedVarint);

        size_t len = static_cast<size_t>(*len_res);
        if (!has_bytes(len)) return std::unexpected(ParseError::UnexpectedEof);

        std::string s(reinterpret_cast<const char*>(buffer_.data() + offset_), len);
        offset_ += len;
        return s;
    }

    /* Зчитування двійкового блоку байтів */
    std::expected<std::span<const uint8_t>, ParseError> read_bytes() noexcept {
        auto len_res = read_zigzag_long();
        if (!len_res || *len_res < 0) return std::unexpected(ParseError::CorruptedVarint);

        size_t len = static_cast<size_t>(*len_res);
        if (!has_bytes(len)) return std::unexpected(ParseError::UnexpectedEof);

        std::span<const uint8_t> slice(buffer_.data() + offset_, len);
        offset_ += len;
        return slice;
    }

    std::expected<void, ParseError> skip(size_t n) noexcept {
        if (!has_bytes(n)) return std::unexpected(ParseError::UnexpectedEof);
        offset_ += n;
        return {};
    }

private:
    std::span<const uint8_t> buffer_;
    size_t offset_{0};
};

/* Метадані та схема контейнера */
struct ContainerHeader {
    std::string schema_json;
    std::string codec{"null"};
    std::array<uint8_t, SYNC_SIZE> sync_marker{};
};

/* Розбір заголовка Avro OCF */
std::expected<ContainerHeader, ParseError> parse_header(SpanReader& reader) {
    ContainerHeader header;

    // 1. Перевірка магічних байтів
    if (!reader.has_bytes(MAGIC_SIZE)) return std::unexpected(ParseError::UnexpectedEof);
    for (size_t i = 0; i < MAGIC_SIZE; ++i) {
        if (reader.read_u8().value() != EXPECTED_MAGIC[i]) {
            return std::unexpected(ParseError::InvalidMagic);
        }
    }

    // 2. Розбір карти метаданих
    while (true) {
        auto count_res = reader.read_zigzag_long();
        if (!count_res) return std::unexpected(count_res.error());

        int64_t count = *count_res;
        if (count == 0) break; // Кінець метаданих

        if (count < 0) {
            count = -count;
            auto byte_size_res = reader.read_zigzag_long();
            if (!byte_size_res) return std::unexpected(byte_size_res.error());
        }

        for (int64_t i = 0; i < count; ++i) {
            auto key_res = reader.read_string();
            if (!key_res) return std::unexpected(key_res.error());

            auto val_res = reader.read_bytes();
            if (!val_res) return std::unexpected(val_res.error());

            if (*key_res == "avro.schema") {
                header.schema_json = std::string(
                    reinterpret_cast<const char*>(val_res->data()), val_res->size()
                );
            } else if (*key_res == "avro.codec") {
                header.codec = std::string(
                    reinterpret_cast<const char*>(val_res->data()), val_res->size()
                );
            }
        }
    }

    // 3. Зчитування синхромаркера
    if (!reader.has_bytes(SYNC_SIZE)) return std::unexpected(ParseError::UnexpectedEof);
    for (size_t i = 0; i < SYNC_SIZE; ++i) {
        header.sync_marker[i] = reader.read_u8().value();
    }

    return header;
}

/* Прикладний об'єкт після узгодження схем */
struct ResolvedUserRecord {
    int64_t id;
    std::string name;
    std::string email;
};

/* Зчитування запису із застосуванням правил еволюції схеми */
std::expected<ResolvedUserRecord, ParseError> decode_and_resolve_record(SpanReader& block_reader) {
    // Writer Schema містила: id (int), name (string), legacy_score (int)
    // Reader Schema очікує: id (long), name (string), email (string, default="none@domain")

    auto id_res = block_reader.read_zigzag_long();
    if (!id_res) return std::unexpected(id_res.error());

    auto name_res = block_reader.read_string();
    if (!name_res) return std::unexpected(name_res.error());

    // Пропуск застарілого поля записувача
    auto legacy_res = block_reader.read_zigzag_long();
    if (!legacy_res) return std::unexpected(legacy_res.error());

    return ResolvedUserRecord{
        .id = *id_res,                               // Безпечне розширення int -> long
        .name = std::move(*name_res),
        .email = "none@domain"                       // Значення за замовчуванням
    };
}

/* Ітератор по блоках контейнера */
void process_avro_container(std::span<const uint8_t> file_bytes) {
    SpanReader reader(file_bytes);
    auto header_res = parse_header(reader);
    if (!header_res) {
        std::cerr << "Помилка розбору заголовка Avro\n";
        return;
    }

    const auto& header = *header_res;
    std::cout << "Вбудована JSON-схема файлу:\n" << header.schema_json << "\n";
    std::cout << "Кодек стиснення: " << header.codec << "\n\n";

    size_t block_num = 0;
    while (reader.has_bytes(1)) {
        auto record_count = reader.read_zigzag_long();
        auto block_bytes_size = reader.read_zigzag_long();
        if (!record_count || !block_bytes_size) break;

        std::cout << "Блок #" << ++block_num << ": " << *record_count << " записів, "
                  << *block_bytes_size << " байтів\n";

        if (!reader.has_bytes(static_cast<size_t>(*block_bytes_size))) {
            std::cerr << "Помилка: неповний блок даних\n";
            return;
        }

        auto block_span = file_bytes.subspan(reader.offset(), static_cast<size_t>(*block_bytes_size));
        reader.skip(static_cast<size_t>(*block_bytes_size)).value();

        SpanReader block_reader(block_span);
        for (int64_t i = 0; i < *record_count; ++i) {
            auto rec = decode_and_resolve_record(block_reader);
            if (rec) {
                std::cout << "  [User] id=" << rec->id << ", name='" << rec->name
                          << "', email='" << rec->email << "'\n";
            }
        }

        // Перевірка маркера синхронізації
        if (!reader.has_bytes(SYNC_SIZE)) {
            std::cerr << "Помилка: відсутній маркер синхронізації\n";
            return;
        }

        for (size_t i = 0; i < SYNC_SIZE; ++i) {
            if (reader.read_u8().value() != header.sync_marker[i]) {
                std::cerr << "Критична помилка: маркер синхронізації пошкоджено!\n";
                return;
            }
        }
        std::cout << "  -> Синхромаркер перевірено успішно.\n";
    }
}

} // namespace avro
