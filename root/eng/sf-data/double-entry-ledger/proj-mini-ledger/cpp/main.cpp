#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <unordered_map>
#include <optional>
#include <cstdint>
#include <numeric>
#include <stdexcept>

enum class AccountType {
    Asset,
    Liability,
    Equity,
    Revenue,
    Expense
};

struct Account {
    uint32_t id;
    std::string name;
    AccountType type;
};

struct Posting {
    uint32_t account_id;
    int64_t amount; // Знакове: додатне — дебет, від'ємне — кредит
    uint64_t sequence{0};
};

struct Transaction {
    uint32_t id;
    std::string idempotency_key;
    std::string description;
    std::vector<Posting> postings;
};

struct BalanceSnapshot {
    uint64_t at_sequence{0};
    int64_t balance{0};
};

class LedgerEngine {
public:
    void add_account(uint32_t id, std::string_view name, AccountType type) {
        if (accounts_.find(id) != accounts_.end()) {
            throw std::runtime_error("Рахунок із таким ID уже існує");
        }
        accounts_[id] = Account{id, std::string(name), type};
    }

    enum class PostResult {
        Success,
        IdempotentDuplicate,
        UnbalancedTransaction,
        AccountNotFound
    };

    PostResult post_transaction(std::string_view idempotency_key,
                                std::string_view description,
                                const std::vector<Posting>& entries) {
        if (entries.size() < 2) {
            return PostResult::UnbalancedTransaction;
        }

        // 1. Перевірка ідемпотентності
        if (!idempotency_key.empty()) {
            auto it = transactions_by_key_.find(std::string(idempotency_key));
            if (it != transactions_by_key_.end()) {
                return PostResult::IdempotentDuplicate;
            }
        }

        // 2. Перевірка інваріанта нульової суми: сума всіх amount повинна дорівнювати 0
        int64_t total_sum = std::accumulate(entries.begin(), entries.end(), int64_t{0},
            [](int64_t acc, const Posting& p) { return acc + p.amount; });

        if (total_sum != 0) {
            return PostResult::UnbalancedTransaction;
        }

        // 3. Валідація існування всіх задіяних рахунків
        for (const auto& entry : entries) {
            if (accounts_.find(entry.account_id) == accounts_.end()) {
                return PostResult::AccountNotFound;
            }
        }

        // 4. Атомарна фіксація транзакції та запис проводок у незмінний журнал
        uint32_t tx_id = static_cast<uint32_t>(transactions_.size() + 1);
        Transaction tx{tx_id, std::string(idempotency_key), std::string(description), {}};

        for (auto entry : entries) {
            entry.sequence = ++global_sequence_;
            postings_log_.push_back(entry);
            tx.postings.push_back(entry);
        }

        transactions_.push_back(tx);
        if (!idempotency_key.empty()) {
            transactions_by_key_[std::string(idempotency_key)] = tx_id;
        }

        return PostResult::Success;
    }

    void create_snapshot(uint32_t account_id) {
        int64_t balance = 0;
        uint64_t max_seq = 0;

        for (const auto& p : postings_log_) {
            if (p.account_id == account_id) {
                balance += p.amount;
                if (p.sequence > max_seq) {
                    max_seq = p.sequence;
                }
            }
        }

        snapshots_[account_id] = BalanceSnapshot{max_seq, balance};
    }

    [[nodiscard]] int64_t get_balance(uint32_t account_id) const {
        int64_t base_balance = 0;
        uint64_t after_sequence = 0;

        auto snap_it = snapshots_.find(account_id);
        if (snap_it != snapshots_.end()) {
            base_balance = snap_it->second.balance;
            after_sequence = snap_it->second.at_sequence;
        }

        // Інкрементальний підрахунок залишку тільки за новими проводками
        int64_t delta = 0;
        for (const auto& p : postings_log_) {
            if (p.account_id == account_id && p.sequence > after_sequence) {
                delta += p.amount;
            }
        }

        return base_balance + delta;
    }

    // Сторнування (реверс) раніше зафіксованої транзакції
    PostResult reverse_transaction(uint32_t original_tx_id, std::string_view new_key) {
        if (original_tx_id == 0 || original_tx_id > transactions_.size()) {
            return PostResult::AccountNotFound;
        }

        const auto& original = transactions_[original_tx_id - 1];
        std::vector<Posting> reversal_entries;
        reversal_entries.reserve(original.postings.size());

        for (const auto& p : original.postings) {
            reversal_entries.push_back(Posting{p.account_id, -p.amount, 0});
        }

        std::string desc = "Сторнування транзакції #" + std::to_string(original_tx_id) + ": " + original.description;
        return post_transaction(new_key, desc, reversal_entries);
    }

private:
    std::unordered_map<uint32_t, Account> accounts_;
    std::vector<Posting> postings_log_;
    std::vector<Transaction> transactions_;
    std::unordered_map<std::string, uint32_t> transactions_by_key_;
    std::unordered_map<uint32_t, BalanceSnapshot> snapshots_;
    uint64_t global_sequence_{0};
};

int main() {
    LedgerEngine ledger;

    ledger.add_account(101, "Bank_Account_UAH", AccountType::Asset);
    ledger.add_account(201, "Customer_Deposits", AccountType::Liability);
    ledger.add_account(401, "Processing_Fee_Income", AccountType::Revenue);

    // 1. Поповнення балансу на 1500.00 грн (150000 копійок)
    auto res1 = ledger.post_transaction("DEP-100", "Поповнення рахунку", {
        {101, 150000},
        {201, -150000}
    });
    std::cout << "Tx 1 проведено: " << (res1 == LedgerEngine::PostResult::Success) << "\n";

    // Створюємо знімок стану
    ledger.create_snapshot(101);

    // 2. Списання комісії 30.00 грн
    ledger.post_transaction("FEE-100", "Комісія", {
        {201, 3000},
        {401, -3000}
    });

    std::cout << "Баланс банку: " << ledger.get_balance(101) << " коп.\n";
    std::cout << "Баланс зобов'язань клієнта: " << ledger.get_balance(201) << " коп.\n";
    std::cout << "Баланс доходів: " << ledger.get_balance(401) << " коп.\n";

    // 3. Сторнування помилкової комісії
    ledger.reverse_transaction(2, "REV-FEE-100");
    std::cout << "Після сторнування комісії, зобов'язання клієнта: " 
              << ledger.get_balance(201) << " коп.\n";

    return 0;
}
