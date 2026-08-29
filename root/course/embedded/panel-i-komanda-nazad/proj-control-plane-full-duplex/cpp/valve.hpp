#pragma once

#include <chrono>
#include <mutex>

namespace cp {

/* Стенд: засувка з приводом, датчиком положення і двома кінцевиками.
   На платі замість цього класу — ШІМ, АЦП і два входи GPIO. Механіку крутить
   потік воркера, а заклинювання вмикає потік сценарію, звідси замок. */
class Valve {
public:
    void drive(int targetPct)
    {
        const std::scoped_lock lock{mutex_};
        target_ = targetPct;
    }

    void stop()
    {
        const std::scoped_lock lock{mutex_};
        target_ = -1;                       // привід знеструмлений
        carry_ = std::chrono::milliseconds{0};
    }

    void setJammed(bool jammed)
    {
        const std::scoped_lock lock{mutex_};
        jammed_ = jammed;
    }

    [[nodiscard]] int position() const
    {
        const std::scoped_lock lock{mutex_};
        return position_;
    }

    [[nodiscard]] bool limitClosed() const
    {
        const std::scoped_lock lock{mutex_};
        return position_ <= 0;
    }

    [[nodiscard]] bool limitOpen() const
    {
        const std::scoped_lock lock{mutex_};
        return position_ >= 100;
    }

    void tick(std::chrono::milliseconds dt)
    {
        const std::scoped_lock lock{mutex_};
        if (target_ < 0 || jammed_) {
            return;
        }
        carry_ += dt;
        while (carry_ >= StepPeriod) {
            carry_ -= StepPeriod;
            if (position_ < target_) {
                ++position_;
            } else if (position_ > target_) {
                --position_;
            } else {
                break;
            }
        }
    }

private:
    static constexpr std::chrono::milliseconds StepPeriod{20};  // 1 % ходу за 20 мс

    mutable std::mutex        mutex_;
    int                       position_{0};
    int                       target_{-1};
    bool                      jammed_{false};
    std::chrono::milliseconds carry_{0};
};

}  // namespace cp
