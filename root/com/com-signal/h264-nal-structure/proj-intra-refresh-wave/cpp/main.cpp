// refresh.hpp — планувальник хвилі intra refresh.
// Стан між кадрами — чотири числа; уся арифметика цілочислова.

#include <algorithm>

class IntraRefresh {
public:
    struct Plan {
        int  firstCol{0};      // [firstCol, lastCol) — форсувати intra
        int  lastCol{0};
        int  recoveryCnt{-1};  // поле SEI recovery_point, -1 — не треба
    };

    IntraRefresh(int widthPx, int heightPx, int periodFrames)
        : mbW_{(widthPx + 15) / 16},
          mbH_{(heightPx + 15) / 16},
          stripe_{std::max(1, (mbW_ + periodFrames - 1) / periodFrames)} {}

    // Відкотити хвилю на початок: відповідь на PLI від приймача.
    void restart() noexcept { wave_ = 0; clean_ = 0; }

    Plan beginFrame() noexcept {
        const int cycle = (mbW_ + stripe_ - 1) / stripe_;
        clean_ = wave_;                  // опора чиста рівно доти, куди дійшла хвиля
        return Plan{wave_,
                    std::min(wave_ + stripe_, mbW_),
                    wave_ == 0 ? cycle - 1 : -1};
    }

    void endFrame() noexcept {
        wave_ += stripe_;
        if (wave_ >= mbW_) wave_ = 0;    // цикл безперервний
    }

    // Чи взагалі обмежувати рух цього блока. Брудній зоні все одно.
    [[nodiscard]] bool mvConstrained(int mbX) const noexcept { return mbX < clean_; }

    // Стеля горизонтальної складової вектора, у чвертьпікселях.
    // Нуль виходить лише в останній чистій колонці — там блок
    // не має права дивитися праворуч навіть на піксель.
    [[nodiscard]] int mvXLimit(int mbX) const noexcept {
        const int limit = clean_ * 16 - (mbX + 1) * 16 - kMvGuardPx;
        return limit < 0 ? 0 : limit * 4;
    }

    [[nodiscard]] int mbHeight() const noexcept { return mbH_; }

private:
    static constexpr int kMvGuardPx = 8;  // 3 px фільтр + 3 px згладжування, із запасом

    int mbW_;
    int mbH_;
    int stripe_;
    int wave_{0};
    int clean_{0};
};
