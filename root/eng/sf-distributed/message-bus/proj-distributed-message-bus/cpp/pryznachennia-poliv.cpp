#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <memory>
#include <functional>
#include <unordered_map>
#include <unordered_set>
#include <chrono>
#include <cstdint>
#include <format>
#include <span>

/* Ідіоматичний конверт повідомлення на C++20 */
struct MessageEnvelope {
    std::string message_id;
    std::string topic;
    std::string correlation_id;
    std::string causation_id;
    std::string traceparent;
    uint32_t schema_version{1};
    uint64_t timestamp_us{0};
    
    std::vector<uint8_t> payload;

    static MessageEnvelope create(std::string_view topic, 
                                  std::string_view corr_id = "", 
                                  uint32_t version = 1) {
        static uint64_t id_seq = 1000;
        uint64_t current_id = ++id_seq;
        
        MessageEnvelope env;
        env.message_id = std::format("msg_{}", current_id);
        env.topic = std::string(topic);
        env.correlation_id = corr_id.empty() ? env.message_id : std::string(corr_id);
        env.traceparent = std::format("00-trace{}-span01-01", current_id);
        env.schema_version = version;
        
        auto now = std::chrono::system_clock::now();
        env.timestamp_us = std::chrono::duration_cast<std::chrono::microseconds>(
            now.time_since_epoch()).count();
        return env;
    }
    
    void set_payload(std::span<const uint8_t> data) {
        payload.assign(data.begin(), data.end());
    }
};
