#include <mutex>

std::mutex account_a_mtx;
std::mutex account_b_mtx;

void transfer_money() {
    // Атомарне і безпечне захоплення обох м'ютексів без ризику дедлоку:
    std::scoped_lock lock(account_a_mtx, account_b_mtx);
    // Безпечна транзакція
}
