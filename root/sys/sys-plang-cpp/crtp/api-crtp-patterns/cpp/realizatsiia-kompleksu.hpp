#include <iostream>
#include <string>

template <typename Derived>
class Formattable {
public:
    void print() const {
        const auto& self = *static_cast<const Derived*>(this);
        std::cout << self.to_string() << "\n";
    }
};

template <typename Derived>
class Sizable {
public:
    size_t byte_size() const noexcept {
        return sizeof(Derived);
    }
};

class UserPayload : public Formattable<UserPayload>, public Sizable<UserPayload> {
public:
    uint64_t user_id{0};
    uint32_t flags{0};

    std::string to_string() const {
        return "UserPayload[id=" + std::to_string(user_id) + "]";
    }
};
