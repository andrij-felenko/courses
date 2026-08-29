#pragma once

// Журнал незавершеної транзакції в незалежній пам'яті (FRAM).
//
// Кільце ідемпотентності живе в SRAM і гине разом із живленням, тому факт
// «токен пішов у залізо» лягає у FRAM ДО подачі струму. Відкритий запис при
// старті означає, що операцію обірвало посеред руху.
//
// Закриття запису — RAII: транзакція знімається деструктором на будь-якому
// виході з виконання, включно з винятком. Об'єкт Nvm створюється зовні й
// переживає перестворення пристрою — саме так, як FRAM переживає скидання.

#include <array>
#include <cstddef>
#include <cstdint>
#include <optional>
#include <span>

#include "wire.hpp"

namespace cmdctl {

class Nvm {
public:
    [[nodiscard]] std::span<std::byte> cells() noexcept { return cells_; }
    [[nodiscard]] std::span<const std::byte> cells() const noexcept { return cells_; }

private:
    std::array<std::byte, 32> cells_{};
};

struct JournalEntry {
    std::uint64_t token{0};
    Type          type{Type::Noop};
};

class Journal {
public:
    explicit Journal(Nvm& nvm) noexcept : nvm_{nvm} {}

    [[nodiscard]] std::optional<JournalEntry> open_entry() const;
    void clear();

    // Відкрита транзакція: живе, поки триває фізична дія.
    class Transaction {
    public:
        Transaction(Journal& owner, std::uint64_t token, Type type);
        ~Transaction();

        Transaction(const Transaction&) = delete;
        Transaction& operator=(const Transaction&) = delete;
        Transaction(Transaction&& other) noexcept;
        Transaction& operator=(Transaction&& other) noexcept;

        // Від'єднати запис, НЕ закриваючи його. Саме так поводиться зникнення
        // живлення: деструктори не виконуються, і відкритий запис лишається у
        // FRAM для процедури відновлення при наступному старті.
        void release() noexcept { owner_ = nullptr; }

    private:
        void close() noexcept;
        Journal* owner_{nullptr};
    };

private:
    void write(std::uint64_t token, Type type, bool open);

    Nvm& nvm_;
};

}  // namespace cmdctl
