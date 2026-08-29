// Стенд контролера безпеки.
// Тут живе реалізація Hal поверх моделі проводки: тестові виходи, контакти
// грибка, місця замикань, котушки контакторів із їхньою механічною затримкою
// та дзеркальні NC-контакти петлі EDM. Модель потрібна, щоб дефекти, заради
// яких написано діагностику, можна було внести навмисно — на живому верстаті
// міжканальне замикання не влаштовують.

#include <array>
#include <format>
#include <iostream>
#include <string_view>

#include "supervisor.hpp"

namespace {

using namespace safety;

constexpr Millis kContactorDelay{15};   // час відпускання якоря контактора

class Bench final : public Hal {
public:
    // Стан проводки, яким крутять сценарії.
    std::array<bool, 2> contactClosed{true, true};    // контакти грибка
    std::array<bool, 2> shortToSupply{false, false};  // лінія на +24 В
    bool crossCircuit{false};                         // лінії зрощені між собою
    bool contactorWelded{false};                      // силовий контакт K1 приварився

    EnablingContacts enabling{.circuitA = false, .circuitB = false, .panicClosed = true};
    bool resetButton{};
    bool ackButton{};
    bool operatorBusy{};

    bool lamp{};
    bool buzzer{};

    void tick()
    {
        clock_ += Millis{1};
        // Дзеркальні контакти йдуть слідом за котушкою, але не миттєво.
        // Приварений силовий контакт тримає свій NC розімкненим назавжди.
        if (now() - coilSince_ >= kContactorDelay) {
            mirrorClosed_ = !coilOn_ && !contactorWelded;
        }
    }

    void setTestOutput(Channel ch, bool high) override { testOut_[index(ch)] = high; }

    bool readEstopInput(Channel ch) const override
    {
        Drive drive = lineDrive(ch);

        if (crossCircuit) {
            // Зрощені лінії — один вузол. Двотактний вихід, що тягне вниз,
            // перемагає: саме тому чужий імпульс видно на обох входах.
            const Drive neighbour = lineDrive(other(ch));
            if (neighbour == Drive::Low) {
                drive = Drive::Low;
            } else if (neighbour == Drive::High && drive == Drive::None) {
                drive = Drive::High;
            }
            if (shortToSupply[index(other(ch))]) {
                return true;
            }
        }

        if (shortToSupply[index(ch)]) {
            return true;   // стороннє живлення дужче за тестовий вихід
        }
        return drive == Drive::High;
    }

    bool readEdmLoop() const override { return mirrorClosed_; }

    void setContactors(bool energize) override
    {
        if (coilOn_ != energize) {
            coilOn_ = energize;
            coilSince_ = now();
        }
    }

    EnablingContacts readEnablingContacts() const override { return enabling; }
    bool readResetButton() const override { return resetButton; }
    bool readAckButton() const override { return ackButton; }
    bool operatorActive() const override { return operatorBusy; }

    void setLamp(bool on) override { lamp = on; }
    void setBuzzer(bool on) override { buzzer = on; }

    // Тестовий імпульс з'їдає справжній час циклу.
    void busyWait(Micros duration) override { clock_ += duration; }

    Millis now() const override { return std::chrono::duration_cast<Millis>(clock_); }

private:
    // Чим лінія керується просто зараз. Розімкнений контакт лишає вхід
    // висіти на підтяжці вниз, замкнений — під двотактним тестовим виходом.
    enum class Drive { None, Low, High };

    Drive lineDrive(Channel ch) const
    {
        if (!contactClosed[index(ch)]) {
            return Drive::None;
        }
        return testOut_[index(ch)] ? Drive::High : Drive::Low;
    }

    std::array<bool, 2> testOut_{true, true};
    Micros clock_{0};
    Millis coilSince_{0};
    bool   coilOn_{};
    bool   mirrorClosed_{true};
};

// Один прогін сценарію: свіжий стенд, свіжий наглядач, друк подій.
class Rig {
public:
    explicit Rig(std::string_view title)
    {
        std::cout << std::format("\n=== {} ===\n", title);
        report(true);
    }

    void step(Millis span)
    {
        for (Millis i{0}; i < span; i += Millis{1}) {
            bench_.tick();
            sup_.poll();
            report(false);
        }
    }

    void gripEnable()  { bench_.enabling = {.circuitA = true,  .circuitB = true,  .panicClosed = true}; }
    void gripRelease() { bench_.enabling = {.circuitA = false, .circuitB = false, .panicClosed = true}; }
    void gripPanic()   { bench_.enabling = {.circuitA = false, .circuitB = false, .panicClosed = false}; }

    void pressReset()
    {
        bench_.resetButton = true;
        step(Millis{10});
        bench_.resetButton = false;
        step(Millis{10});
    }

    void hitMushroom()     { bench_.contactClosed = {false, false}; }
    void releaseMushroom() { bench_.contactClosed = {true, true}; }

    Bench& io() noexcept { return bench_; }

private:
    void report(bool force)
    {
        const State st = sup_.state();
        const bool out = sup_.outputsOn();

        if (!force && st == lastState_ && out == lastOut_
            && bench_.lamp == lastLamp_ && bench_.buzzer == lastBuzzer_) {
            return;
        }

        std::cout << std::format("  {:6} мс   K1/K2 {}   {}{}{}\n",
                                 bench_.now().count(),
                                 out ? "ON " : "off",
                                 describe(st),
                                 bench_.lamp ? "   [лампа]" : "",
                                 bench_.buzzer ? "   [зумер]" : "");

        lastState_ = st;
        lastOut_ = out;
        lastLamp_ = bench_.lamp;
        lastBuzzer_ = bench_.buzzer;
    }

    Bench      bench_{};
    Supervisor sup_{bench_};
    State      lastState_{State::Idle};
    bool       lastOut_{};
    bool       lastLamp_{};
    bool       lastBuzzer_{};
};

void scenarioNormalCycle()
{
    Rig rig{"Штатний пуск, удар по грибку, повторний пуск"};
    rig.gripEnable();
    rig.step(Millis{30});
    rig.pressReset();               // контур цілий, петля EDM замкнена → пуск
    rig.step(Millis{100});

    rig.hitMushroom();              // Категорія 0
    rig.step(Millis{150});

    rig.releaseMushroom();
    rig.step(Millis{30});
    rig.pressReset();
    rig.step(Millis{100});
}

void scenarioDiscordance()
{
    Rig rig{"Розбіжність каналів: перекіс контактного блока"};
    rig.gripEnable();
    rig.step(Millis{30});
    rig.pressReset();
    rig.step(Millis{100});

    rig.io().contactClosed[index(Channel::A)] = false;   // розімкнувся лише канал A
    rig.step(Millis{300});
}

void scenarioShortToSupply()
{
    Rig rig{"Замикання лінії каналу A на шину +24 В"};
    rig.gripEnable();
    rig.step(Millis{30});
    rig.pressReset();
    rig.step(Millis{50});

    rig.io().shortToSupply[index(Channel::A)] = true;    // перетерта ізоляція
    rig.step(Millis{100});
}

void scenarioCrossCircuit()
{
    Rig rig{"Міжканальне замикання лінії A на лінію B"};
    rig.gripEnable();
    rig.step(Millis{30});
    rig.pressReset();
    rig.step(Millis{50});

    rig.io().crossCircuit = true;
    rig.step(Millis{100});
}

void scenarioWeldedContactor()
{
    Rig rig{"Зварений силовий контакт K1: петля EDM не замикається"};
    rig.gripEnable();
    rig.step(Millis{30});
    rig.pressReset();
    rig.step(Millis{50});

    rig.io().contactorWelded = true;   // дуга зварила контакт під навантаженням
    rig.hitMushroom();
    rig.step(Millis{400});             // K2 розірвав живлення, EDM зафіксував K1

    rig.releaseMushroom();
    rig.step(Millis{30});
    rig.pressReset();                  // повторний пуск заблоковано
    rig.step(Millis{50});
}

void scenarioPanicRelease()
{
    Rig rig{"Панічне стискання і зворотний хід крізь Позицію 2"};
    rig.gripEnable();
    rig.step(Millis{30});
    rig.pressReset();
    rig.step(Millis{50});

    rig.gripPanic();      // Позиція 3: судомне стискання
    rig.step(Millis{50});

    rig.gripEnable();     // рука розтискається, кнопка проходить Позицію 2
    rig.step(Millis{30});
    rig.pressReset();     // вмикання заборонено: блокування ще зведене
    rig.step(Millis{50});

    rig.gripRelease();    // повне повернення в Позицію 1 знімає блокування
    rig.step(Millis{30});
    rig.gripEnable();
    rig.step(Millis{30});
    rig.pressReset();
    rig.step(Millis{50});
}

void scenarioVigilance()
{
    Rig rig{"Циклічний контроль пильності: лампа → зумер → зупинка"};
    rig.gripEnable();
    rig.step(Millis{30});
    rig.pressReset();
    rig.step(Millis{50});

    rig.io().operatorBusy = true;    // оператор працює джойстиком
    rig.step(Millis{20000});
    rig.io().operatorBusy = false;   // і завмер
    rig.step(Millis{51000});         // 45 с спокою + 2.5 с + 2.5 с

    rig.gripRelease();               // лише повне відпускання знімає блокування
    rig.step(Millis{30});
    rig.gripEnable();
    rig.step(Millis{30});
    rig.pressReset();
    rig.step(Millis{50});
}

}  // namespace

int main()
{
    scenarioNormalCycle();
    scenarioDiscordance();
    scenarioShortToSupply();
    scenarioCrossCircuit();
    scenarioWeldedContactor();
    scenarioPanicRelease();
    scenarioVigilance();
    return 0;
}
