/* Файл реалізації engine.cpp */
#include "engine_api.h"
#include <memory>
#include <vector>
#include <string>

class EngineCore {
public:
    explicit EngineCore(std::string name) : name_(std::move(name)) {
        buffer_.reserve(4096);
    }
    void process(const uint8_t* data, size_t len) {
        // Складна внутрішня C++ логіка
    }
private:
    std::string name_;
    std::vector<uint8_t> buffer_;
};

// Повне визначення структури дескриптора
struct engine_t {
    std::unique_ptr<EngineCore> core;
};
