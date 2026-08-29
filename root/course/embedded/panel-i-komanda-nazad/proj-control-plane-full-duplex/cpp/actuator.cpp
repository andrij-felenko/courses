#include "actuator.hpp"

#include <algorithm>
#include <cstdlib>
#include <utility>

namespace cp {
namespace {

/* У прошивці ця структура лежить у RTC-пам'яті (RTC_NOINIT_ATTR): вона
   переживає скидання по живленню, а звичайні об'єкти — ні. Тут вона так само
   переживає знищення Actuator, і саме це робить сценарій brownout чесним. */
struct Persist {
    bool        inFlight{false};
    std::string cmdId;
    int         targetPct{0};
};

Persist g_persist;

}  // namespace

Actuator::Actuator(Valve& valve, DedupRing& dedup) : valve_{valve}, dedup_{dedup}
{
    valve_.stop();
    const int pos = position();
    if (g_persist.inFlight) {
        /* Вал лишився посеред ходу. Кінцевики кажуть, де він насправді,
           і сервер мусить дізнатися про незакриту транзакцію. */
        publishStatus(g_persist.cmdId, "FAILED", 0, pos, ErrCode::HardwareFault);
        dedup_.update(g_persist.cmdId, Outcome{"FAILED", 0, pos, ErrCode::HardwareFault});
        g_persist.inFlight = false;
    }
}

bool Actuator::submit(Job job)
{
    const std::scoped_lock lock{inboxMutex_};
    if (inbox_.size() >= InboxLimit) {
        return false;
    }
    inbox_.push_back(std::move(job));
    return true;
}

bool Actuator::busy() const
{
    const std::scoped_lock lock{inboxMutex_};
    return moving_ || !inbox_.empty();
}

std::optional<Actuator::Job> Actuator::takeJob()
{
    const std::scoped_lock lock{inboxMutex_};
    if (inbox_.empty()) {
        return std::nullopt;
    }
    Job job = std::move(inbox_.front());
    inbox_.pop_front();
    return job;
}

/* Кінцевики точніші за датчик: у крайніх положеннях віримо їм. */
int Actuator::position() const
{
    if (valve_.limitClosed()) {
        return 0;
    }
    if (valve_.limitOpen()) {
        return 100;
    }
    return valve_.position();
}

bool Actuator::reached(int pos) const
{
    if (targetPct_ <= 0) {
        return valve_.limitClosed() || pos <= TolerancePct;
    }
    if (targetPct_ >= 100) {
        return valve_.limitOpen() || pos >= 100 - TolerancePct;
    }
    return std::abs(pos - targetPct_) <= TolerancePct;
}

int Actuator::progressPct(int pos) const
{
    const int span = std::abs(targetPct_ - startPct_);
    if (span == 0) {
        return 100;
    }
    const int moved = std::abs(pos - startPct_);
    return std::min(99, (moved * 100) / span);  // сто ставить лише завершення
}

void Actuator::report(std::string_view state, int progress, int value, ErrCode err)
{
    publishStatus(cmdId_, state, progress, value, err);
    dedup_.update(cmdId_, Outcome{std::string{state}, progress, value, err});
}

void Actuator::finish(std::string_view state, int progress, int pos, ErrCode err)
{
    valve_.stop();
    g_persist.inFlight = false;
    moving_ = false;
    report(state, progress, pos, err);
}

void Actuator::begin(Job job, Millis now)
{
    cmdId_ = std::move(job.cmdId);
    targetPct_ = job.targetPct;
    startPct_ = position();
    startedAt_ = now;
    lastReport_ = now;
    moving_ = true;

    g_persist.cmdId = cmdId_;
    g_persist.targetPct = targetPct_;
    g_persist.inFlight = true;

    valve_.drive(targetPct_);
    report("STARTED", 0, startPct_, ErrCode::None);
}

void Actuator::poll(Millis now)
{
    if (!moving_) {
        if (auto job = takeJob()) {
            begin(std::move(*job), now);
        }
        return;
    }

    const int pos = position();
    if (reached(pos)) {
        finish("COMPLETED", 100, pos, ErrCode::None);
        return;
    }
    if (now - startedAt_ >= MoveTimeout) {
        /* Вал не дійшов за відведений час: заклинило, зрив муфти, обрив драйвера. */
        finish("FAILED", progressPct(pos), pos, ErrCode::HardwareFault);
        return;
    }
    if (now - lastReport_ >= ProgressPeriod) {
        lastReport_ = now;
        report("IN_PROGRESS", progressPct(pos), pos, ErrCode::None);
    }
}

}  // namespace cp
