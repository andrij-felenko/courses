#include <string>
#include <chrono>
#include <expected>
#include <cstdint>

struct PurgePolicyConfig {
    std::string table_name;
    std::string time_column;
    std::string primary_key;
    std::chrono::hours retention_window{24 * 30}; // 30 днів
    uint32_t batch_size{5000};
    std::chrono::milliseconds throttle_delay{100};
};

struct PurgeExecutionStats {
    uint64_t rows_scanned{0};
    uint64_t rows_purged{0};
    uint64_t batches_executed{0};
    std::chrono::milliseconds duration{0};
};

enum class PurgeError {
    ConnectionFailed,
    LockTimeout,
    ForeignKeyViolation,
    KmsShreddingFailed
};

class IPurgeEngine {
public:
    virtual ~IPurgeEngine() = default;
    
    [[nodiscard]] virtual std::expected<PurgeExecutionStats, PurgeError> 
    execute_chunked_purge(const PurgePolicyConfig& config) noexcept = 0;
};
