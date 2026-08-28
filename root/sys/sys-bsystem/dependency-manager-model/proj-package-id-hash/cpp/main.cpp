#include <iostream>
#include <string>
#include <string_view>
#include <map>
#include <vector>
#include <sstream>
#include <iomanip>
#include <cstdint>

class PackageIdCalculator {
public:
    void set_setting(std::string key, std::string value) {
        settings_[std::move(key)] = std::move(value);
    }

    void set_option(std::string key, std::string value) {
        options_[std::move(key)] = std::move(value);
    }

    void add_dependency_id(std::string dep_name, std::string dep_package_id) {
        dependencies_[std::move(dep_name)] = std::move(dep_package_id);
    }

    [[nodiscard]] std::string compute_id() const {
        std::ostringstream canonical_stream;

        // Контейнер std::map гарантує суворе лексикографічне сортування за ключами
        for (const auto& [k, v] : settings_) {
            canonical_stream << "s:" << k << '=' << v << '\n';
        }
        for (const auto& [k, v] : options_) {
            canonical_stream << "o:" << k << '=' << v << '\n';
        }
        for (const auto& [k, v] : dependencies_) {
            canonical_stream << "r:" << k << '=' << v << '\n';
        }

        const std::string canonical_str = canonical_stream.str();
        const uint64_t hash_val = compute_fnv1a(canonical_str);

        std::ostringstream id_stream;
        id_stream << "pkg_" << std::hex << std::setw(16) << std::setfill('0') << hash_val;
        return id_stream.str();
    }

private:
    static uint64_t compute_fnv1a(std::string_view data) noexcept {
        uint64_t hash = 14695981039346656037ULL;
        for (const char c : data) {
            hash ^= static_cast<uint8_t>(c);
            hash *= 1099511628211ULL;
        }
        return hash;
    }

    std::map<std::string, std::string> settings_;
    std::map<std::string, std::string> options_;
    std::map<std::string, std::string> dependencies_;
};

int main() {
    PackageIdCalculator calc;

    calc.set_setting("os", "Linux");
    calc.set_setting("arch", "x86_64");
    calc.set_setting("compiler", "gcc");
    calc.set_setting("compiler.version", "13");
    calc.set_setting("compiler.cppstd", "20");
    calc.set_setting("build_type", "Release");

    calc.set_option("shared", "False");
    calc.set_option("fPIC", "True");

    calc.add_dependency_id("zlib", "pkg_e72a084c911b33fa");

    const std::string package_id = calc.compute_id();
    std::cout << "Розрахований Package ID: " << package_id << '\n';

    return 0;
}
