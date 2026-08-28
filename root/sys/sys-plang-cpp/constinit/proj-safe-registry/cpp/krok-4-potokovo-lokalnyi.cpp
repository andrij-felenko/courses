struct ThreadTraceBuffer {
    static constexpr size_t kCapacity = 128;
    uint64_t events[kCapacity];
    size_t write_index;
    uint32_t thread_id;

    constexpr ThreadTraceBuffer() noexcept
        : events{}, write_index(0), thread_id(0) {}

    void record_event(uint64_t event_id) noexcept {
        if (write_index < kCapacity) {
            events[write_index++] = event_id;
        }
    }
};

constinit thread_local ThreadTraceBuffer t_trace_buffer{};
