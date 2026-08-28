#include <iostream>
#include <memory>

// Інтерфейс (контракт)
class OutputDevice {
public:
    virtual ~OutputDevice() = default;
    virtual void write(const std::string& msg) = 0;
};

class ConsoleOutput : public OutputDevice {
public:
    void write(const std::string& msg) override {
        std::cout << "[Консоль]: " << msg << "\n";
    }
};

class FileOutput : public OutputDevice {
public:
    void write(const std::string& msg) override {
        std::cout << "[Файл]: " << msg << "\n";
    }
};

// Замість спадкування від конкретного виводу — володіння через інтерфейс (HAS-A)
class ApplicationLogger {
private:
    std::unique_ptr<OutputDevice> device_;

public:
    explicit ApplicationLogger(std::unique_ptr<OutputDevice> dev) : device_(std::move(dev)) {}

    void setDevice(std::unique_ptr<OutputDevice> dev) {
        device_ = std::move(dev);
    }

    void log(const std::string& text) {
        if (device_) {
            device_->write(text);
        }
    }
};

int main() {
    ApplicationLogger app_logger(std::make_unique<ConsoleOutput>());
    app_logger.log("Старт системи");

    // Заміна стратегії під час виконання без зміни коду логера
    app_logger.setDevice(std::make_unique<FileOutput>());
    app_logger.log("Дані збережено у звіт");
    return 0;
}
