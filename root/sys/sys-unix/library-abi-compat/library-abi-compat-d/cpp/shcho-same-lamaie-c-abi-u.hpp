// C++ версія: ідіоматичний підхід з прихованням даних за допомогою Pimpl
#include <string_view>
#include <cstdint>
#include <memory>

class UserRecord {
public:
    UserRecord(uint32_t id, std::string_view name);
    ~UserRecord();

    [[nodiscard]] uint32_t id() const noexcept;
    [[nodiscard]] std::string_view name() const noexcept;

private:
    struct Impl;
    std::unique_ptr<Impl> impl_; // Фіксований розмір 8 B — ABI повністю захищено
};
