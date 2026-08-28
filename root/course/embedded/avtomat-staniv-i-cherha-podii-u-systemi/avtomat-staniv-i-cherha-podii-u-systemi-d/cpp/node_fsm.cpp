// node_fsm.cpp — Реалізація автомата польового вузла на C++
#include "hsm_engine.hpp"
#include <iostream>

enum class NodeSignal : uint16_t {
    TimerTick = static_cast<uint16_t>(Signal::UserStart),
    DataReady,
    NetOk,
    NetTimeout,
    LowBattery,
    ButtonPress
};

class IotNodeController : public HierarchicalStateMachine<IotNodeController> {
public:
    IotNodeController() = default;

    void start() {
        init(&IotNodeController::state_root);
    }

    Result state_root(const Event& e) {
        switch (e.sig) {
            case Signal::Init:
                return transition(&IotNodeController::state_operational);

            default:
                if (static_cast<NodeSignal>(e.sig) == NodeSignal::LowBattery) {
                    std::cout << "[Root] Low battery (" << e.param << " mV)! Emergency.\n";
                    return transition(&IotNodeController::state_fault);
                }
                return super_state(&IotNodeController::top_state);
        }
    }

    Result state_operational(const Event& e) {
        switch (e.sig) {
            case Signal::Entry:
                std::cout << "[Operational] Entry: Enable 3V3 sensor power rail\n";
                return handled();

            case Signal::Exit:
                std::cout << "[Operational] Exit: Disable 3V3 rail, ensure radio OFF\n";
                return handled();

            case Signal::Init:
                return transition(&IotNodeController::state_idle);

            default:
                return super_state(&IotNodeController::state_root);
        }
    }

    Result state_idle(const Event& e) {
        switch (e.sig) {
            case Signal::Entry:
                std::cout << "[Idle] Entry: Arm periodic wakeup timer\n";
                return handled();

            case Signal::Exit:
                std::cout << "[Idle] Exit: Disarm wakeup timer\n";
                return handled();

            default:
                auto sig = static_cast<NodeSignal>(e.sig);
                if (sig == NodeSignal::TimerTick || sig == NodeSignal::ButtonPress) {
                    return transition(&IotNodeController::state_sampling);
                }
                return super_state(&IotNodeController::state_operational);
        }
    }

    Result state_sampling(const Event& e) {
        switch (e.sig) {
            case Signal::Entry:
                std::cout << "[Sampling] Entry: Start ADC conversion over DMA\n";
                return handled();

            case Signal::Exit:
                std::cout << "[Sampling] Exit: Stop ADC DMA\n";
                return handled();

            default:
                if (static_cast<NodeSignal>(e.sig) == NodeSignal::DataReady) {
                    std::cout << "[Sampling] Acquired " << e.param << " samples! Connect.\n";
                    return transition(&IotNodeController::state_modem_connecting);
                }
                return super_state(&IotNodeController::state_operational);
        }
    }

    Result state_communicating(const Event& e) {
        switch (e.sig) {
            case Signal::Entry:
                std::cout << "[Communicating] Entry: Power on cellular modem\n";
                return handled();

            case Signal::Exit:
                std::cout << "[Communicating] Exit: Power down modem\n";
                return handled();

            default:
                if (static_cast<NodeSignal>(e.sig) == NodeSignal::NetTimeout) {
                    std::cout << "[Communicating] Network timeout! Return to idle.\n";
                    return transition(&IotNodeController::state_idle);
                }
                return super_state(&IotNodeController::state_operational);
        }
    }

    Result state_modem_connecting(const Event& e) {
        switch (e.sig) {
            case Signal::Entry:
                std::cout << "[ModemConnecting] Entry: Check network registration\n";
                return handled();

            default:
                if (static_cast<NodeSignal>(e.sig) == NodeSignal::NetOk) {
                    return transition(&IotNodeController::state_data_publishing);
                }
                return super_state(&IotNodeController::state_communicating);
        }
    }

    Result state_data_publishing(const Event& e) {
        switch (e.sig) {
            case Signal::Entry:
                std::cout << "[DataPublishing] Entry: Publish telemetry packet\n";
                return handled();

            default:
                if (static_cast<NodeSignal>(e.sig) == NodeSignal::NetOk) {
                    std::cout << "[DataPublishing] Telemetry ACK received!\n";
                    return transition(&IotNodeController::state_idle);
                }
                return super_state(&IotNodeController::state_communicating);
        }
    }

    Result state_fault(const Event& e) {
        switch (e.sig) {
            case Signal::Entry:
                std::cout << "[Fault] Entry: Disconnect relays, write crashlog.\n";
                return handled();

            default:
                return super_state(&IotNodeController::state_root);
        }
    }
};
