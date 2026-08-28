#include <iostream>
#include <chrono>
#include <thread>
#include <vector>
#include <span>
#include <optional>

struct Point3D {
    double x{0.0}, y{0.0}, z{0.0};
};

struct TrajectoryPlan {
    std::vector<Point3D> waypoints;
    double cost{99999.0};
    uint32_t iteration{0};
    bool is_valid{false};
};

class RealTimePlanner {
public:
    static constexpr auto kPlanningBudget = std::chrono::microseconds(40000); // 40 мс
    static constexpr auto kSafetyMargin   = std::chrono::microseconds(4000);  // 4 мс

    [[nodiscard]] TrajectoryPlan execute_cycle(const std::optional<TrajectoryPlan>& fallback_plan) const {
        using Clock = std::chrono::steady_clock;
        const auto start_time = Clock::now();
        const auto deadline = start_time + (kPlanningBudget - kSafetyMargin);

        TrajectoryPlan best_plan = fallback_plan.value_or(TrajectoryPlan{
            .waypoints = {Point3D{0, 0, 0}},
            .cost = 99999.0,
            .iteration = 0,
            .is_valid = false
        });

        uint32_t step = 1;
        while (Clock::now() < deadline) {
            TrajectoryPlan candidate = best_plan;
            if (!optimize_step(candidate, step, deadline)) {
                break; // Дедлайн вичерпано
            }
            best_plan = candidate;
            step++;
        }

        const auto elapsed = std::chrono::duration_cast<std::chrono::microseconds>(Clock::now() - start_time);
        std::cout << "[Anytime C++] Цикл завершено за " << elapsed.count()
                  << " мкс (Ітерацій: " << best_plan.iteration
                  << ", Вартість: " << best_plan.cost << ")\n";

        return best_plan;
    }

private:
    [[nodiscard]] bool optimize_step(TrajectoryPlan& plan, uint32_t step,
                                     std::chrono::steady_clock::time_point deadline) const {
        using Clock = std::chrono::steady_clock;
        if (Clock::now() >= deadline) {
            return false;
        }

        plan.iteration = step;
        plan.cost *= 0.85;
        plan.is_valid = true;

        // Симуляція обчислювального навантаження
        std::this_thread::sleep_for(std::chrono::microseconds(1500));
        return true;
    }
};
