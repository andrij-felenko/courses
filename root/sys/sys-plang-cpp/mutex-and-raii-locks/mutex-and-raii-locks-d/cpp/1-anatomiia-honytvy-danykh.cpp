#include <mutex>
#include <stdexcept>

struct BankAccount {
    int balance = 0;
    std::mutex mtx;

    void deposit_naive(int amount) {
        mtx.lock();

        if (amount <= 0) {
            // Забутий unlock перед генерацією винятку або поверненням
            throw std::invalid_argument("Сума повинна бути додатною");
        }

        balance += amount;

        mtx.unlock(); // До цього рядка код може ніколи не дійти!
    }
};
