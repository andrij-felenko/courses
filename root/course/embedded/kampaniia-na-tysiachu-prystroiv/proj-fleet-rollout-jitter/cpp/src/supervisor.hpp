// Дві сторони випробувального терміну.
//
// TrialSupervisor працює в застосунку: він вирішує, чи новий образ довів
// життєздатність. BootSelector працює в завантажувачі: він рахує аварійні
// старти й повертає покажчик на перевірений банк. Обидва спираються на той
// самий запис у незалежній пам'яті — тому й лежать поруч.
#pragma once

#include "storage.hpp"

#include <chrono>
#include <cstdint>
#include <expected>
#include <optional>

namespace fleet {

class TrialSupervisor {
public:
    using Seconds = std::chrono::seconds;

    enum class Outcome {
        Running,      // випробування триває
        Committed,    // образ прийнято остаточно
        RolledBack    // стан переставлено на старий банк, потрібне перезавантаження
    };

    // nullopt — перевірка ще триває; false — зафіксовано дефект.
    struct Health {
        std::optional<bool> self_test;
        std::optional<bool> backend;
    };

    TrialSupervisor(StateStore& store, Seconds window);

    // Образ у неактивному банку записано й перевірено: переставляємо покажчик
    // завантаження й піднімаємо прапорець випробування.
    static std::expected<void, StorageError> arm(StateStore& store, Bank target,
                                                 std::uint32_t campaign_id,
                                                 std::uint32_t image_len,
                                                 std::uint32_t image_crc);

    [[nodiscard]] bool on_trial() const noexcept { return state_.trial_pending; }
    [[nodiscard]] Bank active() const noexcept { return state_.active; }
    [[nodiscard]] std::uint8_t failures() const noexcept { return state_.boot_failures; }
    [[nodiscard]] Seconds elapsed() const noexcept { return elapsed_; }

    // Крок випробування з головного циклу застосунку.
    std::expected<Outcome, StorageError> tick(Seconds dt, Health health);

private:
    std::expected<Outcome, StorageError> commit();
    std::expected<Outcome, StorageError> rollback();

    StateStore& store_;
    RolloutState state_;
    Seconds window_;
    Seconds elapsed_{0};
    bool self_test_passed_{false};
    bool backend_confirmed_{false};
};

class BootSelector {
public:
    enum class Verdict {
        Run,          // стартуємо з вибраного банку
        RolledBack,   // лічильник збоїв вичерпано, повернулись на старий банк
        NoImage       // жоден банк не цілий: лишаємось у завантажувачі
    };

    struct Decision {
        Verdict verdict;
        Bank bank;
        std::uint32_t entry;      // база банку = початок його таблиці векторів
        std::uint8_t failures;
    };

    explicit BootSelector(StateStore& store) : store_(store) {}

    [[nodiscard]] Decision select();

    // VTOR на таблицю векторів банку, MSP з неї ж, стрибок на Reset_Handler.
    static void jump(std::uint32_t entry);

private:
    StateStore& store_;
};

} // namespace fleet
