#include <iostream>
#include <vector>
#include <string>
#include <memory>
#include <functional>
#include <exception>

// Числові стани автомата корутини
enum class State {
    Start = 0,
    AfterProfile = 1,
    AfterBalance = 2,
    Completed = 3
};

struct Profile {
    std::vector<std::string> accountIds;
};

// Сигнатури асинхронних неблокуючих сервісів
void asyncFetchProfile(const std::string& userId, 
                       std::function<void(const Profile&)> onSuccess,
                       std::function<void(std::exception_ptr)> onError);

void asyncFetchAccountBalance(const std::string& accId, 
                              std::function<void(double)> onSuccess,
                              std::function<void(std::exception_ptr)> onError);

// Кадр корутини у динамічній пам'яті (Heap Frame)
class CalculateTotalBalanceFrame : public std::enable_shared_from_this<CalculateTotalBalanceFrame> {
public:
    State state = State::Start;
    std::string userId;
    Profile profile;
    double total = 0.0;
    size_t loopIndex = 0;

    std::function<void(double)> onComplete;
    std::function<void(std::exception_ptr)> onFailure;

    explicit CalculateTotalBalanceFrame(std::string id,
                                        std::function<void(double)> onComp,
                                        std::function<void(std::exception_ptr)> onFail)
        : userId(std::move(id)), onComplete(std::move(onComp)), onFailure(std::move(onFail)) {}

    void resumeSuccessProfile(const Profile& p) {
        profile = p;
        state = State::AfterProfile;
        step();
    }

    void resumeSuccessBalance(double balance) {
        total += balance;
        loopIndex++;
        state = State::AfterBalance;
        step();
    }

    void resumeError(std::exception_ptr ex) {
        // Імітація обробника catch
        std::cerr << "Помилка розрахунку балансу (перехоплено в автоматі)\n";
        state = State::Completed;
        if (onComplete) {
            onComplete(0.0); // Повернення безпечного значення за замовчуванням
        }
    }

    void step() {
        try {
            switch (state) {
                case State::Start: {
                    auto self = shared_from_this();
                    asyncFetchProfile(userId,
                        [self](const Profile& p) { self->resumeSuccessProfile(p); },
                        [self](std::exception_ptr ex) { self->resumeError(ex); }
                    );
                    return; // Призупинення, вихід з поточного виклику
                }

                case State::AfterProfile:
                case State::AfterBalance: {
                    if (loopIndex < profile.accountIds.size()) {
                        const std::string& accId = profile.accountIds[loopIndex];
                        auto self = shared_from_this();
                        asyncFetchAccountBalance(accId,
                            [self](double bal) { self->resumeSuccessBalance(bal); },
                            [self](std::exception_ptr ex) { self->resumeError(ex); }
                        );
                        return; // Призупинення до відповіді на наступний рахунок
                    }

                    // Усі рахунки успішно опрацьовано
                    state = State::Completed;
                    if (onComplete) {
                        onComplete(total);
                    }
                    return;
                }

                case State::Completed:
                    return;
            }
        } catch (...) {
            resumeError(std::current_exception());
        }
    }
};

void runDesugaredBalanceCalculation(const std::string& userId,
                                   std::function<void(double)> callback) {
    auto frame = std::make_shared<CalculateTotalBalanceFrame>(
        userId, std::move(callback), nullptr
    );
    frame->step();
}
