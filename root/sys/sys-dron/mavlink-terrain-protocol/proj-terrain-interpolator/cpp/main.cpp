#include <cstdint>
#include <array>
#include <span>
#include <optional>
#include <cmath>
#include <algorithm>
#include <numbers>

class TerrainManager {
public:
    static constexpr uint16_t GRID_SPACING = 100;
    static constexpr size_t   BLOCK_NODES  = 4;
    static constexpr size_t   CLUSTER_SIZE = 8;
    static constexpr size_t   CACHE_SIZE   = 32;
    static constexpr int16_t  NO_DATA      = -32768;

    struct Block {
        int32_t lat_sw{0};
        int32_t lon_sw{0};
        uint32_t last_access{0};
        std::array<int16_t, 16> data{};
        bool valid{false};
    };

    TerrainManager() = default;

    // Збереження блоку з LRU витісненням
    void insert_block(int32_t lat_sw, int32_t lon_sw, std::span<const int16_t, 16> heights) noexcept {
        Block* target = find_block(lat_sw, lon_sw);
        
        if (!target) {
            auto it = std::min_element(cache_.begin(), cache_.end(),
                [](const Block& a, const Block& b) {
                    if (!a.valid) return true;
                    if (!b.valid) return false;
                    return a.last_access < b.last_access;
                });
            
            target = &(*it);
            if (!target->valid) {
                loaded_count_++;
            }
            target->lat_sw = lat_sw;
            target->lon_sw = lon_sw;
            target->valid = true;
        }

        std::copy(heights.begin(), heights.end(), target->data.begin());
        target->last_access = ++access_counter_;
    }

    // Генерація 64-бітної маски запиту TERRAIN_REQUEST
    [[nodiscard]] uint64_t build_request_mask(int32_t center_lat, int32_t center_lon) const noexcept {
        const int32_t d_lat = get_lat_step_1e7(GRID_SPACING);
        const int32_t d_lon = get_lon_step_1e7(GRID_SPACING, center_lat);
        
        const int32_t block_span_lat = (BLOCK_NODES - 1) * d_lat;
        const int32_t block_span_lon = (BLOCK_NODES - 1) * d_lon;

        const int32_t cluster_sw_lat = center_lat - 4 * block_span_lat;
        const int32_t cluster_sw_lon = center_lon - 4 * block_span_lon;

        uint64_t mask = 0;

        for (size_t r = 0; r < CLUSTER_SIZE; ++r) {
            for (size_t c = 0; c < CLUSTER_SIZE; ++c) {
                const int32_t b_lat = cluster_sw_lat + static_cast<int32_t>(r) * block_span_lat;
                const int32_t b_lon = cluster_sw_lon + static_cast<int32_t>(c) * block_span_lon;

                if (!find_block(b_lat, b_lon)) {
                    mask |= (1ULL << (r * 8 + c));
                }
            }
        }
        return mask;
    }

    // Інтерполяція висоти у заданій точці (lat, lon)
    [[nodiscard]] std::optional<float> get_height(int32_t lat, int32_t lon) noexcept {
        const int32_t d_lat = get_lat_step_1e7(GRID_SPACING);
        const int32_t d_lon = get_lon_step_1e7(GRID_SPACING, lat);
        const int32_t block_span_lat = (BLOCK_NODES - 1) * d_lat;
        const int32_t block_span_lon = (BLOCK_NODES - 1) * d_lon;

        int32_t lat_sw = lat - (lat % block_span_lat);
        int32_t lon_sw = lon - (lon % block_span_lon);
        if (lat < 0 && (lat % block_span_lat != 0)) lat_sw -= block_span_lat;
        if (lon < 0 && (lon % block_span_lon != 0)) lon_sw -= block_span_lon;

        Block* block = find_block(lat_sw, lon_sw);
        if (!block) {
            return std::nullopt;
        }

        const int32_t rel_lat = lat - lat_sw;
        const int32_t rel_lon = lon - lon_sw;

        size_t cell_row = std::min<size_t>(rel_lat / d_lat, 2);
        size_t cell_col = std::min<size_t>(rel_lon / d_lon, 2);

        const int16_t h00 = block->data[cell_row * 4 + cell_col];
        const int16_t h10 = block->data[cell_row * 4 + (cell_col + 1)];
        const int16_t h01 = block->data[(cell_row + 1) * 4 + cell_col];
        const int16_t h11 = block->data[(cell_row + 1) * 4 + (cell_col + 1)];

        if (h00 == NO_DATA || h10 == NO_DATA || h01 == NO_DATA || h11 == NO_DATA) {
            return std::nullopt;
        }

        const float u = static_cast<float>(rel_lon - cell_col * d_lon) / static_cast<float>(d_lon);
        const float v = static_cast<float>(rel_lat - cell_row * d_lat) / static_cast<float>(d_lat);

        return (1.0f - u) * (1.0f - v) * static_cast<float>(h00) +
               u * (1.0f - v) * static_cast<float>(h10) +
               (1.0f - u) * v * static_cast<float>(h01) +
               u * v * static_cast<float>(h11);
    }

    [[nodiscard]] uint16_t loaded_count() const noexcept { return loaded_count_; }

private:
    std::array<Block, CACHE_SIZE> cache_{};
    uint32_t access_counter_{0};
    uint16_t loaded_count_{0};

    [[nodiscard]] Block* find_block(int32_t lat_sw, int32_t lon_sw) noexcept {
        for (auto& block : cache_) {
            if (block.valid && block.lat_sw == lat_sw && block.lon_sw == lon_sw) {
                block.last_access = ++access_counter_;
                return &block;
            }
        }
        return nullptr;
    }

    [[nodiscard]] const Block* find_block(int32_t lat_sw, int32_t lon_sw) const noexcept {
        for (const auto& block : cache_) {
            if (block.valid && block.lat_sw == lat_sw && block.lon_sw == lon_sw) {
                return &block;
            }
        }
        return nullptr;
    }

    [[nodiscard]] static constexpr int32_t get_lat_step_1e7(uint16_t spacing) noexcept {
        return static_cast<int32_t>((static_cast<double>(spacing) / 111319.5) * 1e7);
    }

    [[nodiscard]] static int32_t get_lon_step_1e7(uint16_t spacing, int32_t lat_1e7) noexcept {
        const double lat_rad = (static_cast<double>(lat_1e7) * 1e-7) * (std::numbers::pi / 180.0);
        double cos_lat = std::cos(lat_rad);
        if (cos_lat < 0.01) cos_lat = 0.01;
        return static_cast<int32_t>((static_cast<double>(spacing) / (111319.5 * cos_lat)) * 1e7);
    }
};
