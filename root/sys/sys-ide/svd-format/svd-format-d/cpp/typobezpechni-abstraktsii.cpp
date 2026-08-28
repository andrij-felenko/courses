#include <cstdint>
#include <concepts>

namespace hal {

// Концепти прав доступу до регістрів
template <typename T>
concept Readable = requires(T reg) {
    { reg.read_raw() } -> std::same_as<uint32_t>;
};

template <typename T>
concept Writable = requires(T reg, uint32_t val) {
    reg.write_raw(val);
};

// Строго типізований перелік для бітового поля довжини слова
enum class UsartWordLength : uint32_t {
    Bits8 = 0,
    Bits9 = 1
};

// Шаблон типізованого бітового поля
template <uint32_t Offset, uint32_t Width, typename ValueType = uint32_t>
struct BitField {
    static constexpr uint32_t pos = Offset;
    static constexpr uint32_t mask = ((1UL << Width) - 1UL) << pos;

    static constexpr uint32_t encode(ValueType value) noexcept {
        return (static_cast<uint32_t>(value) << pos) & mask;
    }

    static constexpr ValueType decode(uint32_t reg_val) noexcept {
        return static_cast<ValueType>((reg_val & mask) >> pos);
    }
};

// Типобезпечний клас регістра
template <uintptr_t Address, typename AccessPolicy>
class HardwareRegister {
public:
    static constexpr uintptr_t address = Address;

    [[nodiscard]] static uint32_t read_raw() noexcept requires Readable<AccessPolicy> {
        return *reinterpret_cast<volatile uint32_t*>(address);
    }

    static void write_raw(uint32_t val) noexcept requires Writable<AccessPolicy> {
        *reinterpret_cast<volatile uint32_t*>(address) = val;
    }

    // Безпечна модифікація через типізовані поля
    template <typename Field, typename ValType>
    static void set_field(ValType value) noexcept requires Writable<AccessPolicy> && Readable<AccessPolicy> {
        uint32_t current = read_raw();
        current &= ~Field::mask;
        current |= Field::encode(value);
        write_raw(current);
    }
};

// Політики доступу
struct ReadWritePolicy {
    static uint32_t read_raw();
    static void write_raw(uint32_t);
};

struct ReadOnlyPolicy {
    static uint32_t read_raw();
};

// Оголошення конкретних полів і регістрів зі зміщеннями
using Usart1Cr1 = HardwareRegister<0x4001380CUL, ReadWritePolicy>;

struct Usart1Fields {
    using Enable = BitField<0, 1, bool>;
    using WordLength = BitField<12, 1, UsartWordLength>;
    using ParityControl = BitField<10, 1, bool>;
};

} // namespace hal

void configure_usart() {
    // Безпечний запис конфігурації
    hal::Usart1Cr1::set_field<hal::Usart1Fields::WordLength>(hal::UsartWordLength::Bits8);
    hal::Usart1Cr1::set_field<hal::Usart1Fields::Enable>(true);

    // Спроба передати невідповідний тип або записати в Read-Only викликає помилку компіляції:
    // hal::Usart1Cr1::set_field<hal::Usart1Fields::WordLength>(42); // ПОМИЛКА: 42 не є UsartWordLength
}
