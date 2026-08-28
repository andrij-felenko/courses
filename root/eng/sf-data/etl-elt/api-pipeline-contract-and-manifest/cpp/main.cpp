#include <string>
#include <string_view>
#include <vector>
#include <memory>
#include <span>
#include <expected>
#include <chrono>

// Метадані виконання фази конвеєра (Lineage & Audit)
struct ExecutionAudit {
    std::string pipeline_id;
    std::string stage_name;
    uint64_t records_read{0};
    uint64_t records_written{0};
    uint64_t bytes_transferred{0};
    std::chrono::milliseconds duration_ms{0};
    std::string target_commit_id;
};

// Абстрактний інтерфейс стадії конвеєра
class IPipelineStage {
public:
    virtual ~IPipelineStage() = default;
    virtual std::string_view stage_name() const noexcept = 0;
};

// Стадія видобування (Extract)
class IExtractor : public IPipelineStage {
public:
    // Повертає список сирих рядків або код помилки
    virtual std::expected<std::vector<std::string>, int> extract_batch(
        std::string_view watermark_start, 
        std::string_view watermark_end, 
        size_t limit) = 0;
};

// Стадія сирого або цільового завантаження (Load)
class ILoader : public IPipelineStage {
public:
    // Завантажує сирі дані у шар Bronze або цільову таблицю
    virtual std::expected<ExecutionAudit, int> load_raw_staging(
        std::string_view destination_table,
        std::span<const std::string> raw_json_records) = 0;
};

// Стадія декларативної або імперативної трансформації (Transform)
class ITransformer : public IPipelineStage {
public:
    // Виконує SQL-трансформацію всередині рушія сховища
    virtual std::expected<ExecutionAudit, int> execute_transformation(
        std::string_view sql_query,
        std::string_view target_partition) = 0;
};
