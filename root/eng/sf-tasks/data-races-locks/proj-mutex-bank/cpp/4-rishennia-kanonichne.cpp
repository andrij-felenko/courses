#include <cstdint>
#include <mutex>

bool transfer_money(SafeAccount& from, SafeAccount& to, int64_t amount) {
    if (&from == &to || amount <= 0) {
        return false;
    }

    // std::scoped_lock гарантує одночасне захоплення двох замків без ризику дедлоку
    // і автоматично звільняє їх при будь-якому виході з функції
    std::scoped_lock lock(from.get_mutex(), to.get_mutex());

    if (from.raw_balance() >= amount) {
        from.raw_modify(-amount);
        to.raw_modify(amount);
        return true;
    }

    return false;
}
