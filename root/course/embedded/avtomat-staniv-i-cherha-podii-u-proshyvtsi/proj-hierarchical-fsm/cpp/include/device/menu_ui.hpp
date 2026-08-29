// menu_ui.hpp — трирівневе ієрархічне меню портативного калібратора.
//
// Дерево станів:
//   ScreenSaver           екран вимкнено, процесор спить
//   Active                суперстан: підсвітка, аварії, таймаут бездіяльності
//     MainMenu            типовий підстан Active
//     Settings            яскравість і калібрування
//       Calibration       вимірювання зміщення нуля АЦП
//
// Кожен обробник описує ЛИШЕ те, що унікальне для його рівня. Гілка default
// повертає parent(...) — саме вона і є ребром дерева.
#pragma once

#include "device/board.hpp"
#include "hsm/hsm.hpp"

#include <cstdint>

namespace device {

// Сигнали застосунку. Нумерація починається після службових сигналів рушія.
inline constexpr hsm::Signal kBtnUp = hsm::userSignal(0);
inline constexpr hsm::Signal kBtnDown = hsm::userSignal(1);
inline constexpr hsm::Signal kBtnEnter = hsm::userSignal(2);
inline constexpr hsm::Signal kBtnBack = hsm::userSignal(3);
inline constexpr hsm::Signal kTimeoutIdle = hsm::userSignal(4); // хвилина без натискань
inline constexpr hsm::Signal kSensorFault = hsm::userSignal(5); // відмова давача

enum class MenuItem : std::uint8_t { Measure = 0, Settings, About, Count };

template <Board B>
class MenuUi final : public hsm::StateMachine<MenuUi<B>> {
    using Base = hsm::StateMachine<MenuUi<B>>;

public:
    using State = typename Base::State;

    explicit MenuUi(B& board) : Base{&MenuUi::initial}, board_{board} {}

    // Чи спить прилад: головний цикл питає, перш ніж скидати тактування.
    [[nodiscard]] bool isAsleep() { return this->isIn(&MenuUi::screenSaver); }

private:
    static constexpr std::uint8_t kItemCount = static_cast<std::uint8_t>(MenuItem::Count);
    static constexpr std::uint8_t kBrightnessStep = 10;
    static constexpr std::uint8_t kBrightnessMin = 10;
    static constexpr std::uint8_t kBrightnessMax = 100;

    // Дія, прив'язана до самого переходу «Settings -> MainMenu»: рушій
    // виконає її після виходу зі старої гілки і до входу в нову.
    void clearErrors() {
        errorCount_ = 0;
        board_.trace("дія переходу: лічильник відмов давача скинуто");
    }

    // Початковий псевдостан: прилад прокидається із зануреним екраном.
    hsm::Result initial(const hsm::Event&) {
        return this->transition(&MenuUi::screenSaver);
    }

    hsm::Result screenSaver(const hsm::Event& e) {
        switch (e.sig) {
            case hsm::Signal::Entry:
                board_.enterLowPower();
                return this->handled();

            case hsm::Signal::Exit:
                board_.exitLowPower();
                return this->handled();

            case kBtnUp:
            case kBtnDown:
                // Прокрутка на зануреному екрані не будить прилад — але й
                // суперстанові подію не віддаємо: це свідома глухота.
                return this->ignored();

            case kBtnEnter:
            case kBtnBack:
                // Ціль складена: типовий підстан обере Init у active().
                return this->transition(&MenuUi::active);

            case kSensorFault:
                // Уві сні відмову лише рахуємо, екран не піднімаємо.
                countFault();
                return this->handled();

            default:
                return this->parent(Base::topState());
        }
    }

    // Суперстан: усе спільне для всіх екранів приладу.
    hsm::Result active(const hsm::Event& e) {
        switch (e.sig) {
            case hsm::Signal::Entry:
                board_.setBacklight(brightness_);
                return this->handled();

            case hsm::Signal::Exit:
                // Гарантія рушія: підсвітка згасне на БУДЬ-ЯКОМУ шляху
                // назовні, з якої б глибини меню користувач не вийшов.
                board_.setBacklight(0);
                return this->handled();

            case hsm::Signal::Init:
                return this->transition(&MenuUi::mainMenu);

            case kSensorFault:
                // Одна реакція на аварію замість копії в кожному підменю.
                countFault();
                board_.showFault(errorCount_);
                return this->handled();

            case kTimeoutIdle:
                // Глобальний таймаут: із будь-якої глибини — у заставку.
                return this->transition(&MenuUi::screenSaver);

            default:
                return this->parent(Base::topState());
        }
    }

    hsm::Result mainMenu(const hsm::Event& e) {
        switch (e.sig) {
            case hsm::Signal::Entry:
                board_.drawMenu(menuItem_);
                return this->handled();

            case kBtnUp:
                menuItem_ = static_cast<std::uint8_t>((menuItem_ + kItemCount - 1) % kItemCount);
                board_.drawMenu(menuItem_);
                return this->handled();

            case kBtnDown:
                menuItem_ = static_cast<std::uint8_t>((menuItem_ + 1) % kItemCount);
                board_.drawMenu(menuItem_);
                return this->handled();

            case kBtnEnter:
                switch (static_cast<MenuItem>(menuItem_)) {
                    case MenuItem::Settings:
                        return this->transition(&MenuUi::settings);
                    case MenuItem::Measure:
                        board_.showMeasurement(adcOffset_);
                        return this->handled();
                    default:
                        board_.showAbout();
                        return this->handled();
                }

            case kBtnBack:
                // З кореня меню виходити нікуди, будити суперстан не треба.
                return this->ignored();

            default:
                return this->parent(&MenuUi::active);
        }
    }

    hsm::Result settings(const hsm::Event& e) {
        switch (e.sig) {
            case hsm::Signal::Entry:
                board_.drawSettings(brightness_, adcOffset_, calibrated_);
                return this->handled();

            case hsm::Signal::Exit:
                // Запис у Flash трапиться і при звичайному «Назад», і при
                // таймауті з глибини калібрування — рушій не дає шансу
                // цього пропустити.
                board_.saveSettings(brightness_, adcOffset_);
                return this->handled();

            case kBtnUp:
                if (brightness_ <= kBrightnessMax - kBrightnessStep) {
                    brightness_ = static_cast<std::uint8_t>(brightness_ + kBrightnessStep);
                }
                board_.setBacklight(brightness_);
                board_.drawSettings(brightness_, adcOffset_, calibrated_);
                return this->handled();

            case kBtnDown:
                if (brightness_ >= kBrightnessMin + kBrightnessStep) {
                    brightness_ = static_cast<std::uint8_t>(brightness_ - kBrightnessStep);
                }
                board_.setBacklight(brightness_);
                board_.drawSettings(brightness_, adcOffset_, calibrated_);
                return this->handled();

            case kBtnEnter:
                return this->transition(&MenuUi::calibration);

            case kBtnBack:
                return this->transition(&MenuUi::mainMenu, &MenuUi::clearErrors);

            default:
                return this->parent(&MenuUi::active);
        }
    }

    hsm::Result calibration(const hsm::Event& e) {
        switch (e.sig) {
            case hsm::Signal::Entry:
                acceptCalib_ = false;
                board_.startCalibration();
                return this->handled();

            case hsm::Signal::Exit: {
                // Генератор глушиться завжди, а результат приймається лише
                // тоді, коли користувач устиг його підтвердити. Аварійний
                // вихід за таймаутом мовчки викидає недомірене значення.
                const std::int16_t offset = board_.stopCalibration();
                if (acceptCalib_) {
                    adcOffset_ = offset;
                    calibrated_ = true;
                }
                acceptCalib_ = false;
                return this->handled();
            }

            case kBtnEnter:
                acceptCalib_ = true;
                return this->transition(&MenuUi::settings);

            case kBtnBack:
                // Скасування: вихід зі стану сам зупинить генератор.
                return this->transition(&MenuUi::settings);

            case kBtnUp:
            case kBtnDown:
                // Під час вимірювання яскравість не чіпаємо: зміна струму
                // підсвітки зсунула б нуль АЦП просто в ході калібрування.
                return this->ignored();

            default:
                // kTimeoutIdle звідси піде вгору: Settings -> Active,
                // і Active поверне прилад у заставку.
                return this->parent(&MenuUi::settings);
        }
    }

    void countFault() {
        if (errorCount_ < 255) {
            ++errorCount_;
        }
    }

    B& board_;
    std::uint8_t brightness_{80};
    std::uint8_t menuItem_{static_cast<std::uint8_t>(MenuItem::Measure)};
    std::int16_t adcOffset_{0};
    std::uint8_t errorCount_{0};
    bool calibrated_{false};
    bool acceptCalib_{false};
};

} // namespace device
