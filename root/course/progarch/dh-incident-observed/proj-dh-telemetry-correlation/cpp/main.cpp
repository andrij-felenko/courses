// C++20 / OpenTelemetry C++ SDK / Prometheus-cpp
#include <iostream>
#include <string>
#include <memory>
#include <thread>
#include <optional>
#include <random>
#include <sstream>
#include <iomanip>
#include <chrono>

// Структура W3C Trace Context
struct TraceContext {
    std::string trace_id;
    std::string span_id;
    bool sampled{true};

    static std::string generate_hex(size_t bytes) {
        thread_local std::mt19937 generator{std::random_device{}()};
        std::uniform_int_distribution<uint32_t> dist(0, 255);
        std::stringstream ss;
        for (size_t i = 0; i < bytes; ++i) {
            ss << std::hex << std::setw(2) << std::setfill('0') << dist(generator);
        }
        return ss.str();
    }

    static TraceContext parse_or_create(const std::string& traceparent_header) {
        // Формат W3C: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
        if (traceparent_header.size() >= 55 && traceparent_header.substr(0, 2) == "00") {
            TraceContext ctx;
            ctx.trace_id = traceparent_header.substr(3, 32);
            ctx.span_id = traceparent_header.substr(36, 16);
            ctx.sampled = (traceparent_header.substr(53, 2) == "01");
            return ctx;
        }
        // Генерація нового TraceID, якщо заголовок відсутній або пошкоджений
        return TraceContext{generate_hex(16), generate_hex(8), true};
    }

    std::string to_traceparent() const {
        return "00-" + trace_id + "-" + span_id + "-" + (sampled ? "01" : "00");
    }
};

// Thread-local зберігання контексту для поточного потоку обробки
thread_local std::optional<TraceContext> g_current_trace_context;

// RAII обгортка для безпечного керування часом життя контексту в потоці
class TraceScope {
public:
    explicit TraceScope(TraceContext ctx) : prev_ctx_(g_current_trace_context) {
        g_current_trace_context = std::move(ctx);
    }
    ~TraceScope() {
        g_current_trace_context = prev_ctx_;
    }
    TraceScope(const TraceScope&) = delete;
    TraceScope& operator=(const TraceScope&) = delete;

private:
    std::optional<TraceContext> prev_ctx_;
};

// Структурований JSON-логер із автоматичним прокиданням TraceID
class CorrelatedLogger {
public:
    static void log_info(const std::string& service, const std::string& msg) {
        emit_log("INFO", service, msg);
    }
    static void log_error(const std::string& service, const std::string& msg, const std::string& err_detail) {
        emit_log("ERROR", service, msg, err_detail);
    }

private:
    static void emit_log(const std::string& level, const std::string& service, 
                         const std::string& msg, const std::string& err = "") {
        auto now = std::chrono::system_clock::now().time_since_epoch();
        auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(now).count();

        std::string tid = g_current_trace_context ? g_current_trace_context->trace_id : "none";
        std::string sid = g_current_trace_context ? g_current_trace_context->span_id : "none";

        std::cout << "{"
                  << "\"timestamp_ms\":" << ms << ","
                  << "\"level\":\"" << level << "\","
                  << "\"service\":\"" << service << "\","
                  << "\"trace_id\":\"" << tid << "\","
                  << "\"span_id\":\"" << sid << "\","
                  << "\"message\":\"" << msg << "\"";
        if (!err.empty()) {
            std::cout << ",\"error\":\"" << err << "\"";
        }
        std::cout << "}\n";
    }
};

// Приклад сервісу обробки телеметрії
class DeviceTelemetryService {
public:
    void handle_request(const std::string& raw_traceparent) {
        TraceContext ctx = TraceContext::parse_or_create(raw_traceparent);
        TraceScope scope(ctx); // Записує контекст у thread_local

        CorrelatedLogger::log_info("device-telemetry-svc", "Прийнято запит телеметрії давача");

        // Симуляція виклику бази даних із розширеним спаном
        execute_db_query();
    }

private:
    void execute_db_query() {
        // У реальному коді тут створюється Child Span і передається Exemplar у Prometheus
        CorrelatedLogger::log_info("device-telemetry-svc", "Виконання SQL запиту до PostgreSQL");
    }
};
