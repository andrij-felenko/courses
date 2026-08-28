enum class DeviceSignal : uint16_t {
    BtnUp = static_cast<uint16_t>(QSignal::User),
    BtnDown,
    BtnEnter,
    BtnBack,
    TimeoutIdle
};

class DeviceUI : public HsmBase {
public:
    DeviceUI() 
        : HsmBase(static_cast<StateHandler>(&DeviceUI::stateInitial)),
          brightness_(80), 
          is_calibrated_(false) {}

private:
    uint8_t brightness_;
    bool is_calibrated_;

    QResult stateInitial(const QEvt&) {
        return tran(static_cast<StateHandler>(&DeviceUI::stateScreenSaver));
    }

    QResult stateScreenSaver(const QEvt& e) {
        if (e.sig == static_cast<QSignal>(DeviceSignal::BtnEnter) ||
            e.sig == static_cast<QSignal>(DeviceSignal::BtnBack)) {
            return tran(static_cast<StateHandler>(&DeviceUI::stateMainMenu));
        }
        return super(&HsmBase::topState);
    }

    QResult stateActive(const QEvt& e) {
        switch (e.sig) {
            case QSignal::Entry:
                // LCD_SetBacklight(100);
                return handled();
            case QSignal::Exit:
                // LCD_SetBacklight(0);
                return handled();
            default:
                if (e.sig == static_cast<QSignal>(DeviceSignal::TimeoutIdle)) {
                    return tran(static_cast<StateHandler>(&DeviceUI::stateScreenSaver));
                }
                return super(&HsmBase::topState);
        }
    }

    QResult stateMainMenu(const QEvt& e) {
        switch (e.sig) {
            case QSignal::Entry:
                // Draw_Icon_Menu();
                return handled();
            default:
                if (e.sig == static_cast<QSignal>(DeviceSignal::BtnEnter)) {
                    return tran(static_cast<StateHandler>(&DeviceUI::stateSettings));
                }
                return super(static_cast<StateHandler>(&DeviceUI::stateActive));
        }
    }

    QResult stateSettings(const QEvt& e) {
        switch (e.sig) {
            case QSignal::Entry:
                // Display_Settings();
                return handled();
            default:
                if (e.sig == static_cast<QSignal>(DeviceSignal::BtnUp)) {
                    if (brightness_ < 100) brightness_ += 10;
                    return handled();
                }
                if (e.sig == static_cast<QSignal>(DeviceSignal::BtnEnter)) {
                    return tran(static_cast<StateHandler>(&DeviceUI::stateCalibration));
                }
                if (e.sig == static_cast<QSignal>(DeviceSignal::BtnBack)) {
                    return tran(static_cast<StateHandler>(&DeviceUI::stateMainMenu));
                }
                return super(static_cast<StateHandler>(&DeviceUI::stateActive));
        }
    }

    QResult stateCalibration(const QEvt& e) {
        switch (e.sig) {
            case QSignal::Entry:
                // Start_Calib();
                return handled();
            case QSignal::Exit:
                // Stop_Calib();
                return handled();
            default:
                if (e.sig == static_cast<QSignal>(DeviceSignal::BtnEnter)) {
                    is_calibrated_ = true;
                    return tran(static_cast<StateHandler>(&DeviceUI::stateSettings));
                }
                if (e.sig == static_cast<QSignal>(DeviceSignal::BtnBack)) {
                    return tran(static_cast<StateHandler>(&DeviceUI::stateSettings));
                }
                return super(static_cast<StateHandler>(&DeviceUI::stateSettings));
        }
    }
};
