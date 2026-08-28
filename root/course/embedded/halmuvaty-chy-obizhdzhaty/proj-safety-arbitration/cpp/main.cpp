#include <cstdint>
#include <cmath>
#include <algorithm>
#include <optional>

namespace navigation::safety {

enum class Zone : uint8_t {
    Observation = 0,
    Warning,
    EmergencyStop
};

struct Vector2D {
    float x{0.0f};
    float y{0.0f};

    [[nodiscard]] constexpr Vector2D operator+(const Vector2D& o) const noexcept {
        return { x + o.x, y + o.y };
    }

    [[nodiscard]] constexpr Vector2D operator*(float s) const noexcept {
        return { x * s, y * s };
    }

    [[nodiscard]] float length() const noexcept {
        return std::sqrt(x * x + y * y);
    }

    [[nodiscard]] Vector2D normalized() const noexcept {
        const float len = length();
        return (len > 1e-4f) ? Vector2D{ x / len, y / len } : Vector2D{ 0.0f, 0.0f };
    }
};

struct Config {
    float maxDeceleration{2.5f};     // Максимальне сповільнення, м/с²
    float reactionTime{0.05f};       // Затримка реакції приводу, с
    float plannerPeriod{0.20f};      // Очікуваний період планувальника, с
    float stopMargin{0.40f};         // Запас зупинки, м
    float warnBuffer{0.80f};         // Додатковий буфер зони застереження, м
    float hystDistance{0.30f};       // Просторовий гістерезис деескалації, м
    uint32_t holdTicks{20};          // Кількість тактів утримання перед деескалацією
    uint32_t watchdogTimeoutTicks{50}; // Таймаут зв'язку (500 мс при такті 10 мс)
};

class Arbiter {
public:
    explicit constexpr Arbiter(const Config& config = {}) noexcept
        : cfg_(config), currentZone_(Zone::Observation),
          holdCounter_(0), watchdogCounter_(0),
          plannerTimedOut_(false), lastCommand_{} {}

    struct UpdateResult {
        Vector2D velocityCommand;
        Zone activeZone;
        bool isEmergencyOverride;
        bool isPlannerTimedOut;
    };

    void feedPlannerHeartbeat() noexcept {
        watchdogCounter_ = 0;
        plannerTimedOut_ = false;
    }

    [[nodiscard]] UpdateResult update(Vector2D planVel,
                                      const Vector2D& reactVel,
                                      float minObstacleDist,
                                      float currentSpeed) noexcept {
        // 0. Перевірка таймауту каналу зв'язку
        ++watchdogCounter_;
        if (watchdogCounter_ > cfg_.watchdogTimeoutTicks) {
            plannerTimedOut_ = true;
            planVel = { 0.0f, 0.0f };
        }

        // 1. Кінематичний розрахунок динамічних радіусів зон
        const float safeSpeed = std::max(0.0f, currentSpeed);
        const float dBrake = (safeSpeed * safeSpeed) / (2.0f * cfg_.maxDeceleration);
        const float rStop  = dBrake + (safeSpeed * cfg_.reactionTime) + cfg_.stopMargin;
        const float rWarn  = rStop + (safeSpeed * cfg_.plannerPeriod) + cfg_.warnBuffer;

        // 2. Оцінка миттєвої зони
        const Zone instantZone = evaluateZone(minObstacleDist, rStop, rWarn);

        // 3. Автомат переходів із фільтрацією перемикань
        manageZoneTransitions(instantZone, minObstacleDist, rStop, rWarn);

        // 4. Генерація та масштабування вихідного вектора
        Vector2D outVelocity{ 0.0f, 0.0f };
        bool overrideActive = false;

        switch (currentZone_) {
            case Zone::EmergencyStop:
                overrideActive = true;
                outVelocity = { 0.0f, 0.0f };
                break;

            case Zone::Warning: {
                overrideActive = false;
                const float span = rWarn - rStop;
                const float alpha = (span > 1e-3f)
                    ? std::clamp((rWarn - minObstacleDist) / span, 0.0f, 1.0f)
                    : 1.0f;

                outVelocity = (planVel * (1.0f - alpha)) + (reactVel * alpha);

                // Обмеження швидкості за безпечним гальмівним профілем
                const float distToStop = minObstacleDist - rStop;
                if (distToStop > 0.0f) {
                    const float vSafe = std::sqrt(2.0f * cfg_.maxDeceleration * distToStop);
                    const float len = outVelocity.length();
                    if (len > vSafe && len > 1e-4f) {
                        outVelocity = outVelocity * (vSafe / len);
                    }
                } else {
                    outVelocity = { 0.0f, 0.0f };
                }
                break;
            }

            case Zone::Observation:
            default:
                overrideActive = false;
                outVelocity = planVel;
                break;
        }

        lastCommand_ = outVelocity;
        return { outVelocity, currentZone_, overrideActive, plannerTimedOut_ };
    }

    [[nodiscard]] Zone getZone() const noexcept { return currentZone_; }
    [[nodiscard]] Vector2D getLastCommand() const noexcept { return lastCommand_; }
    [[nodiscard]] bool isPlannerTimedOut() const noexcept { return plannerTimedOut_; }

private:
    [[nodiscard]] static constexpr Zone evaluateZone(float dist, float rStop, float rWarn) noexcept {
        if (dist <= rStop) return Zone::EmergencyStop;
        if (dist <= rWarn) return Zone::Warning;
        return Zone::Observation;
    }

    void manageZoneTransitions(Zone instantZone, float dist, float rStop, float rWarn) noexcept {
        if (instantZone > currentZone_) {
            currentZone_ = instantZone;
            holdCounter_ = cfg_.holdTicks;
        } else if (instantZone < currentZone_) {
            bool hysteresisPassed = false;
            if (currentZone_ == Zone::EmergencyStop) {
                hysteresisPassed = (dist > (rStop + cfg_.hystDistance));
            } else if (currentZone_ == Zone::Warning) {
                hysteresisPassed = (dist > (rWarn + cfg_.hystDistance));
            }

            if (hysteresisPassed) {
                if (holdCounter_ > 0) {
                    --holdCounter_;
                } else {
                    currentZone_ = instantZone;
                    holdCounter_ = cfg_.holdTicks;
                }
            } else {
                holdCounter_ = cfg_.holdTicks;
            }
        } else {
            holdCounter_ = cfg_.holdTicks;
        }
    }

    Config cfg_;
    Zone currentZone_;
    uint32_t holdCounter_;
    uint32_t watchdogCounter_;
    bool plannerTimedOut_;
    Vector2D lastCommand_;
};

} // namespace navigation::safety
