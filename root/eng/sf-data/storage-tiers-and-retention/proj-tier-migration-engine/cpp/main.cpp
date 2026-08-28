#include <iostream>
#include <vector>
#include <memory>
#include <shared_mutex>
#include <mutex>
#include <atomic>
#include <chrono>
#include <cmath>
#include <thread>
#include <optional>
#include <algorithm>

enum class StorageTier : uint8_t {
    Hot = 0,
    Warm = 1,
    Cold = 2,
    Archive = 3
};

enum class ChunkState : uint8_t {
    Online,
    Migrating,
    Deleted
};

struct ChunkMetadata {
    const uint64_t id;
    const size_t size_bytes;
    StorageTier current_tier{StorageTier::Hot};
    ChunkState state{ChunkState::Online};
    
    double temperature_score{1.0};
    std::chrono::system_clock::time_point last_access;
    uint64_t access_count{0};
    uint32_t checksum{0};
    
    mutable std::shared_mutex rw_lock;

    ChunkMetadata(uint64_t chunk_id, size_t size)
        : id(chunk_id), size_bytes(size), last_access(std::chrono::system_clock::now()),
          checksum(static_cast<uint32_t>(chunk_id ^ 0xDEADBEEF)) {}
          
    double calculate_decayed_temperature(std::chrono::system_clock::time_point now, double half_life_sec) const {
        auto duration = std::chrono::duration_cast<std::chrono::seconds>(now - last_access).count();
        if (duration <= 0) return temperature_score;
        double decay = std::pow(2.0, -static_cast<double>(duration) / half_life_sec);
        return temperature_score * decay;
    }
};

class TieringMigrationEngine {
public:
    TieringMigrationEngine(size_t hot_capacity_bytes, double high_wm = 0.85, double low_wm = 0.70)
        : hot_tier_capacity_(hot_capacity_bytes),
          high_watermark_(high_wm),
          low_watermark_(low_wm),
          is_running_(true) {}

    ~TieringMigrationEngine() {
        stop();
    }

    void register_chunk(uint64_t id, size_t size_bytes) {
        auto chunk = std::make_unique<ChunkMetadata>(id, size_bytes);
        std::unique_lock lock(catalog_mutex_);
        hot_bytes_used_ += size_bytes;
        chunks_.push_back(std::move(chunk));
    }

    void record_access(uint64_t chunk_id) {
        std::shared_lock lock(catalog_mutex_);
        if (chunk_id >= chunks_.size()) return;
        
        auto& c = *chunks_[chunk_id];
        std::unique_lock chunk_lock(c.rw_lock);
        auto now = std::chrono::system_clock::now();
        double decayed = c.calculate_decayed_temperature(now, 3600.0);
        c.temperature_score = decayed + 1.0;
        c.last_access = now;
        ++c.access_count;
    }

    void start_scheduler() {
        worker_thread_ = std::jthread([this](std::stop_token st) {
            while (!st.stop_requested() && is_running_) {
                evaluate_and_migrate();
                std::this_thread::sleep_for(std::chrono::milliseconds(500));
            }
        });
    }

    void stop() {
        is_running_ = false;
        if (worker_thread_.joinable()) {
            worker_thread_.request_stop();
        }
    }

private:
    const size_t hot_tier_capacity_;
    const double high_watermark_;
    const double low_watermark_;
    
    std::atomic<bool> is_running_{false};
    std::atomic<size_t> hot_bytes_used_{0};
    
    std::vector<std::unique_ptr<ChunkMetadata>> chunks_;
    std::shared_mutex catalog_mutex_;
    std::jthread worker_thread_;

    bool execute_chunk_migration(ChunkMetadata& chunk, StorageTier target_tier) {
        StorageTier old_tier;
        size_t size = chunk.size_bytes;

        {
            std::unique_lock lock(chunk.rw_lock);
            if (chunk.state != ChunkState::Online || chunk.current_tier == target_tier) {
                return false;
            }
            old_tier = chunk.current_tier;
            chunk.state = ChunkState::Migrating;
        }

        // Імітація фонового передавання даних у новий ярус
        std::this_thread::sleep_for(std::chrono::milliseconds(5));
        uint32_t calculated_crc = static_cast<uint32_t>(chunk.id ^ 0xDEADBEEF);

        if (calculated_crc != chunk.checksum) {
            std::unique_lock lock(chunk.rw_lock);
            chunk.state = ChunkState::Online; // Відкат стану
            std::cerr << "[ПОМИЛКА] Невідповідність CRC під час міграції чанка " << chunk.id << "\n";
            return false;
        }

        // Атомарна фіксація нового ярусу
        {
            std::unique_lock lock(chunk.rw_lock);
            chunk.current_tier = target_tier;
            chunk.state = ChunkState::Online;
        }

        // Звільнення ємності гарячого ярусу
        if (old_tier == StorageTier::Hot) {
            hot_bytes_used_.fetch_sub(size);
        }

        std::cout << "[ТИРУВАННЯ] Чанк " << chunk.id << " переведено на ярус " 
                  << static_cast<int>(target_tier) << " (" << size << " байтів)\n";
        return true;
    }

    void evaluate_and_migrate() {
        size_t used = hot_bytes_used_.load();
        double current_ratio = static_cast<double>(used) / static_cast<double>(hot_tier_capacity_);

        if (current_ratio <= high_watermark_) return;

        std::cout << "[УВАГА] Рівень заповнення Hot ярусу: " << (current_ratio * 100.0) 
                  << "% > High Watermark. Запуск витіснення.\n";

        auto now = std::chrono::system_clock::now();

        while (current_ratio > low_watermark_ && is_running_) {
            ChunkMetadata* best_candidate = nullptr;
            double min_score = std::numeric_limits<double>::max();

            {
                std::shared_lock lock(catalog_mutex_);
                for (const auto& chunk : chunks_) {
                    std::shared_lock chunk_lock(chunk->rw_lock);
                    if (chunk->state == ChunkState::Online && chunk->current_tier == StorageTier::Hot) {
                        double score = chunk->calculate_decayed_temperature(now, 3600.0);
                        if (score < min_score) {
                            min_score = score;
                            best_candidate = chunk.get();
                        }
                    }
                }
            }

            if (!best_candidate) break;

            execute_chunk_migration(*best_candidate, StorageTier::Warm);
            
            used = hot_bytes_used_.load();
            current_ratio = static_cast<double>(used) / static_cast<double>(hot_tier_capacity_);
        }
    }
};
