#include <string>
#include <memory>
#include <stdexcept>

// Outbound port: абстрактний інтерфейс сховища
class SensorRepository {
public:
    virtual ~SensorRepository() = default;
    virtual bool save_calibration(const std::string& sensor_id, double offset) = 0;
};

// Inbound port: сценарій використання з передачею залежності в конструктор
class CalibrateSensorUseCase {
public:
    explicit CalibrateSensorUseCase(std::shared_ptr<SensorRepository> repo)
        : repo_(std::move(repo)) {
        if (!repo_) throw std::invalid_argument("Repository is required");
    }

    bool execute(const std::string& sensor_id, double offset) const {
        if (offset < -10.0 || offset > 10.0) return false;
        return repo_->save_calibration(sensor_id, offset);
    }
private:
    std::shared_ptr<SensorRepository> repo_;
};
