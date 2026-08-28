#include <string>
#include <chrono>
#include <cstdint>
#include <string_view>

struct ActivityMetadata {
    std::string step_id;
    std::string activity_name;
    std::string queue_name;
    std::chrono::seconds timeout{30};
    std::chrono::seconds heartbeat_timeout{5};
    uint32_t max_retries{5};
    double backoff_coefficient{2.0};
    bool is_compensation{false};
};

struct ActivityTaskContext {
    std::string execution_id;
    std::string workflow_id;
    uint32_t attempt_number{1};
    std::string_view payload_json;
};
