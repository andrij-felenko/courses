#include <cstdint>

class FdoChannel {
public:
    enum class Status {
        Ok,
        HighSideShortCircuit,
        LowSideShortCircuit
    };

    FdoChannel(volatile uint32_t* hsCtrl, volatile uint32_t* lsCtrl,
               volatile uint32_t* vFbHs, volatile uint32_t* vFbLs,
               uint32_t hsMask, uint32_t lsMask)
        : hsCtrlReg_(hsCtrl), lsCtrlReg_(lsCtrl),
          vFbHsReg_(vFbHs), vFbLsReg_(vFbLs),
          hsMask_(hsMask), lsMask_(lsMask) {}

    Status verifyOffState() const {
        // Гарантуємо вимкнений стан керуючих регістрів
        *hsCtrlReg_ &= ~hsMask_;
        *lsCtrlReg_ &= ~lsMask_;

        const bool hsVoltagePresent = (*vFbHsReg_ & hsMask_) != 0;
        const bool lsVoltagePresent = (*vFbLsReg_ & lsMask_) != 0;

        if (hsVoltagePresent) {
            return Status::HighSideShortCircuit;
        }
        if (lsVoltagePresent) {
            return Status::LowSideShortCircuit;
        }

        return Status::Ok;
    }

private:
    volatile uint32_t* hsCtrlReg_;
    volatile uint32_t* lsCtrlReg_;
    volatile uint32_t* vFbHsReg_;
    volatile uint32_t* vFbLsReg_;
    uint32_t hsMask_;
    uint32_t lsMask_;
};
