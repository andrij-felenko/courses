// database_safe.hpp
#pragma once
#include <string>

class Database {
public:
    Database() : conn_str_("postgres://localhost:5432") {}
    [[nodiscard]] const std::string& connection() const noexcept { return conn_str_; }
private:
    std::string conn_str_;
};

// Construct-On-First-Use:
inline Database& get_database() {
    // Гарантія C++11: ініціалізація локального static є строго потокобезпечною
    // та відбувається рівно один раз під час першого проходження через цей рядок.
    static Database instance;
    return instance;
}
