#include <iostream>
#include <vector>
#include <map>
#include <span>
#include <memory>
#include <optional>
#include <string_view>
#include <array>

namespace quic {

struct QpackEntry {
    std::string_view name;
    std::string_view value;
};

// Статична таблиця QPACK (RFC 9204)
constexpr std::array<QpackEntry, 100> QPACK_STATIC_TABLE = []{
    std::array<QpackEntry, 100> table{};
    table[0]  = {":authority", ""};
    table[1]  = {":path", "/"};
    table[15] = {":method", "GET"};
    table[17] = {":method", "POST"};
    table[25] = {":status", "200"};
    table[28] = {":status", "404"};
    table[29] = {":status", "500"};
    table[31] = {"accept-encoding", "gzip, deflate, br"};
    table[45] = {"content-type", "application/json"};
    table[95] = {"user-agent", "quic-client/1.0"};
    return table;
}();

class QuicStreamReassembler {
public:
    QuicStreamReassembler(uint64_t stream_id, uint64_t max_stream_data)
        : stream_id_(stream_id), max_stream_data_(max_stream_data) {}

    bool insert_frame(uint64_t offset, std::span<const uint8_t> data, bool is_fin) {
        if (offset + data.size() > max_stream_data_) {
            std::cerr << "[FLOW_CONTROL_ERROR] Exceeded max_stream_data: " 
                      << offset + data.size() << " > " << max_stream_data_ << "\n";
            return false;
        }

        if (is_fin) {
            if (fin_received_ && final_size_ != offset + data.size()) {
                std::cerr << "[FINAL_SIZE_ERROR] Conflicting final size for stream " << stream_id_ << "\n";
                return false;
            }
            fin_received_ = true;
            final_size_ = offset + data.size();
        }

        if (offset + data.size() <= read_offset_) {
            return true; // Вже прочитано
        }

        // Обрізання вже прочитаного фрагмента
        size_t skip = 0;
        if (offset < read_offset_) {
            skip = static_cast<size_t>(read_offset_ - offset);
            offset = read_offset_;
        }

        // Вставка у впорядковане дерево за зсувом
        pending_chunks_[offset] = std::vector<uint8_t>(data.begin() + skip, data.end());
        return true;
    }

    std::vector<uint8_t> read_contiguous() {
        std::vector<uint8_t> result;

        auto it = pending_chunks_.begin();
        while (it != pending_chunks_.end() && it->first <= read_offset_) {
            uint64_t chunk_offset = it->first;
            const auto& chunk_data = it->second;

            if (chunk_offset + chunk_data.size() > read_offset_) {
                size_t skip = static_cast<size_t>(read_offset_ - chunk_offset);
                size_t take = chunk_data.size() - skip;

                result.insert(result.end(), chunk_data.begin() + skip, chunk_data.end());
                read_offset_ += take;
            }

            it = pending_chunks_.erase(it);
        }

        return result;
    }

    [[nodiscard]] bool is_complete() const noexcept {
        return fin_received_ && (read_offset_ >= final_size_);
    }

    [[nodiscard]] uint64_t stream_id() const noexcept { return stream_id_; }

    static void decode_qpack_indexed(uint8_t index) {
        if (index < QPACK_STATIC_TABLE.size() && !QPACK_STATIC_TABLE[index].name.empty()) {
            std::cout << "  [QPACK Header] " << QPACK_STATIC_TABLE[index].name 
                      << ": " << QPACK_STATIC_TABLE[index].value << "\n";
        } else {
            std::cout << "  [QPACK Header] Unknown static index " << static_cast<int>(index) << "\n";
        }
    }

private:
    uint64_t stream_id_;
    uint64_t read_offset_{0};
    uint64_t max_stream_data_;
    bool fin_received_{false};
    uint64_t final_size_{0};
    std::map<uint64_t, std::vector<uint8_t>> pending_chunks_;
};

} // namespace quic
