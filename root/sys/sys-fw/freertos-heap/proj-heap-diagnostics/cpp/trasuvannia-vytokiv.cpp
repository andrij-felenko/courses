#include <array>
#include <concepts>
#include "esp_heap_trace.h"
#include "esp_log.h"

template <size_t RecordCount = 128>
class ScopedHeapLeakTracer {
public:
    ScopedHeapLeakTracer() {
        ESP_ERROR_CHECK(heap_trace_init_standalone(records_.data(), records_.size()));
        ESP_ERROR_CHECK(heap_trace_start(HEAP_TRACE_LEAKS));
    }

    ~ScopedHeapLeakTracer() noexcept {
        heap_trace_stop();
        ESP_LOGI("LEAK_TRACE", "Аналіз невивільнених алокацій у блоці:");
        heap_trace_dump();
    }

    ScopedHeapLeakTracer(const ScopedHeapLeakTracer &) = delete;
    ScopedHeapLeakTracer &operator=(const ScopedHeapLeakTracer &) = delete;

private:
    std::array<heap_trace_record_t, RecordCount> records_{};
};

void profile_subsystem_cpp(void (*workload)())
{
    {
        ScopedHeapLeakTracer<64> tracer;
        workload();
    } // ~ScopedHeapLeakTracer автоматично зупинить трасування та роздрукує звіт
}
