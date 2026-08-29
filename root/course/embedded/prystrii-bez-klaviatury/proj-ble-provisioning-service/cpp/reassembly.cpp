#include "reassembly.hpp"

#include "crypto.hpp"

namespace prov {

std::uint16_t negotiate_mtu(std::uint16_t client_mtu) noexcept
{
    // Менше за базовий MTU клієнт запропонувати не може — такий запит
    // некоректний, і специфікація велить триматися базового значення.
    if (client_mtu < AttMtuDefault) {
        client_mtu = AttMtuDefault;
    }
    return client_mtu < AttMtuMax ? client_mtu : AttMtuMax;
}

void AttReassembler::cancel() noexcept
{
    // Фрагменти могли нести зашифрований пароль — затираємо, а не просто clear().
    secure_wipe(buffer_);
    buffer_.clear();
    char_uuid_ = 0;
    active_ = false;
}

std::expected<void, AttError> AttReassembler::prepare(std::uint16_t char_uuid,
                                                      std::uint16_t offset,
                                                      std::span<const std::uint8_t> value)
{
    if (!active_) {
        active_ = true;
        char_uuid_ = char_uuid;
        buffer_.clear();
        buffer_.reserve(AttReassemblyCapacity);
    }

    // Черга підготовлених записів одна на зʼєднання: мішати дві характеристики
    // в ній ми не даємо, щоб пів-пакета сесії не приїхало в конфігурацію.
    if (char_uuid_ != char_uuid) {
        return std::unexpected(AttError::Unlikely);
    }

    // Клієнт нумерує фрагменти зміщенням. Приймаємо лише суцільний потік:
    // дірка або перекриття означають загублений чи повторений кадр.
    if (offset != buffer_.size()) {
        return std::unexpected(AttError::InvalidOffset);
    }

    if (value.size() > AttReassemblyCapacity - buffer_.size()) {
        return std::unexpected(AttError::PrepareQueueFull);
    }

    buffer_.insert(buffer_.end(), value.begin(), value.end());
    return {};
}

std::expected<AttReassembler::Assembled, AttError> AttReassembler::execute(bool commit)
{
    if (!commit) {
        cancel();
        return Assembled{};   // скасування — законна дія, не помилка
    }

    if (!active_) {
        return Assembled{};   // порожня черга: виконувати нічого
    }

    if (buffer_.empty()) {
        cancel();
        return std::unexpected(AttError::InvalidAttributeLength);
    }

    active_ = false;          // значення віддали; буфер затре cancel() або наступний prepare
    return Assembled{char_uuid_, std::span<const std::uint8_t>(buffer_)};
}

}  // namespace prov
