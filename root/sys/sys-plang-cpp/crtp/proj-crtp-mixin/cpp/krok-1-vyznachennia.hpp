#include <cstdint>
#include <cstring>
#include <chrono>
#include <iostream>
#include <vector>

template <typename Derived>
class Validatable {
public:
    bool validate() const {
        const auto& self = *static_cast<const Derived*>(this);
        return self.validate_impl();
    }
};
