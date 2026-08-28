// C++ Idiomatic Implementation: RAII, std::string_view, std::expected, DTOs
#include <iostream>
#include <string>
#include <string_view>
#include <expected>
#include <format>
#include <vector>

struct TraceContext {
    std::string trace_id;
    std::string parent_span_id;
    std::string current_span_id;
    bool sampled{false};
};

struct UnlockCommand {
    std::string user_id;
    std::string home_id;
    std::string lock_id;
    TraceContext trace;
};

struct DeviceTwin {
    std::string lock_id;
    std::string desired_state;
    std::string reported_state;
    int version{1};
};

struct OutboxEvent {
    int64_t id;
    std::string aggregate_id;
    std::string event_type;
    std::string payload_json;
    std::string trace_id;
    std::string span_id;
};

enum class PipelineError {
    InvalidTraceparent,
    Unauthorized,
    DatabaseError
};

class TraceparentParser {
public:
    static std::expected<TraceContext, PipelineError> parse(std::string_view header) {
        if (header.size() < 55 || !header.starts_with("00-")) {
            return std::unexpected(PipelineError::InvalidTraceparent);
        }
        if (header[2] != '-' || header[35] != '-' || header[52] != '-') {
            return std::unexpected(PipelineError::InvalidTraceparent);
        }

        TraceContext ctx;
        ctx.trace_id = std::string(header.substr(3, 32));
        ctx.parent_span_id = std::string(header.substr(36, 16));
        ctx.current_span_id = "a1b2c3d4e5f67890"; // Generated Span ID
        ctx.sampled = (header[54] == '1');
        return ctx;
    }
};

class SmartLockRepository {
public:
    std::expected<void, PipelineError> save_transactional(const DeviceTwin& twin, const OutboxEvent& event) {
        std::cout << std::format("[DB TX BEGIN]\n");
        std::cout << std::format("  UPDATE device_twins SET desired_state='{}', version={} WHERE id='{}';\n",
                                  twin.desired_state, twin.version, twin.lock_id);
        std::cout << std::format("  INSERT INTO outbox_messages (aggregate_id, event_type, payload, trace_id, span_id)\n"
                                  "  VALUES ('{}', '{}', '{}', '{}', '{}');\n",
                                  event.aggregate_id, event.event_type, event.payload_json,
                                  event.trace_id, event.span_id);
        std::cout << std::format("[DB TX COMMIT] Success\n");
        return {};
    }
};

class SmartLockService {
    SmartLockRepository repo_;
public:
    std::expected<void, PipelineError> execute_unlock(const UnlockCommand& cmd) {
        std::cout << std::format("[Trace: {}] Executing unlock command for lock {}\n",
                                  cmd.trace.trace_id, cmd.lock_id);

        DeviceTwin twin{
            .lock_id = cmd.lock_id,
            .desired_state = "UNLOCKED",
            .reported_state = "LOCKED",
            .version = 2
        };

        OutboxEvent event{
            .id = 1001,
            .aggregate_id = cmd.lock_id,
            .event_type = "LockUnlockCommanded",
            .payload_json = std::format(R"({{"lock_id":"{}","desired":"UNLOCKED","user_id":"{}"}})", cmd.lock_id, cmd.user_id),
            .trace_id = cmd.trace.trace_id,
            .span_id = cmd.trace.current_span_id
        };

        return repo_.save_transactional(twin, event);
    }
};

int main() {
    std::string_view trace_hdr = "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01";
    auto trace_res = TraceparentParser::parse(trace_hdr);
    if (!trace_res) {
        std::cerr << "Failed to parse traceparent\n";
        return 1;
    }

    UnlockCommand cmd{
        .user_id = "user_alex_123",
        .home_id = "home_h1",
        .lock_id = "lock_front_door",
        .trace = *trace_res
    };

    SmartLockService service;
    auto result = service.execute_unlock(cmd);
    if (!result) {
        std::cerr << "Pipeline failed\n";
        return 1;
    }
    return 0;
}
