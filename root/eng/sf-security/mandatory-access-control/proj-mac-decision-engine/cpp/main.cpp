#include <iostream>
#include <vector>
#include <unordered_map>
#include <cstdint>
#include <string_view>
#include <format>

enum class Permission : uint32_t {
    None    = 0,
    Read    = 1U << 0,
    Write   = 1U << 1,
    Execute = 1U << 2,
    Append  = 1U << 3,
};

constexpr Permission operator|(Permission a, Permission b) noexcept {
    return static_cast<Permission>(static_cast<uint32_t>(a) | static_cast<uint32_t>(b));
}

constexpr Permission operator&(Permission a, Permission b) noexcept {
    return static_cast<Permission>(static_cast<uint32_t>(a) & static_cast<uint32_t>(b));
}

enum class SecurityClass : uint16_t {
    File   = 1,
    Socket = 2,
    Dir    = 3,
};

struct SecurityContext {
    uint16_t type_id{0};
    uint8_t mls_sensitivity{0};
    uint64_t mls_categories{0};

    [[nodiscard]] constexpr bool dominates(const SecurityContext& other) const noexcept {
        if (mls_sensitivity < other.mls_sensitivity) return false;
        return (mls_categories & other.mls_categories) == other.mls_categories;
    }
};

struct CacheKey {
    uint16_t src_type;
    uint16_t target_type;
    SecurityClass target_class;

    bool operator==(const CacheKey& o) const noexcept {
        return src_type == o.src_type && target_type == o.target_type && target_class == o.target_class;
    }
};

struct CacheKeyHash {
    std::size_t operator()(const CacheKey& k) const noexcept {
        const std::size_t h1 = std::hash<uint16_t>{}(k.src_type);
        const std::size_t h2 = std::hash<uint16_t>{}(k.target_type);
        const std::size_t h3 = std::hash<uint16_t>{}(static_cast<uint16_t>(k.target_class));
        return h1 ^ (h2 << 8) ^ (h3 << 16);
    }
};

struct PolicyRule {
    uint16_t src_type;
    uint16_t target_type;
    SecurityClass target_class;
    Permission allowed_permissions;
};

class SecurityEngine {
public:
    void add_rule(uint16_t src, uint16_t target, SecurityClass cl, Permission perms) {
        rules_.push_back({src, target, cl, perms});
        avc_cache_.clear(); // скидання кешу при зміні політики
    }

    [[nodiscard]] bool check_permission(const SecurityContext& subj,
                                        const SecurityContext& obj,
                                        SecurityClass target_class,
                                        Permission requested) {
        // 1. MLS-фільтрація
        const bool is_read = static_cast<bool>(requested & (Permission::Read | Permission::Execute));
        const bool is_write = static_cast<bool>(requested & (Permission::Write | Permission::Append));

        if (is_read && !subj.dominates(obj)) return false;
        if (is_write && !obj.dominates(subj)) return false;

        // 2. Швидкий пошук у хеш-таблиці AVC
        const CacheKey key{subj.type_id, obj.type_id, target_class};
        if (auto it = avc_cache_.find(key); it != avc_cache_.end()) {
            ++cache_hits_;
            return (it->second & requested) == requested;
        }

        // 3. Cache Miss: обчислення повного вектора дозволів у Security Server
        ++cache_misses_;
        const Permission allowed = compute_access_vector(subj.type_id, obj.type_id, target_class);
        avc_cache_[key] = allowed;

        return (allowed & requested) == requested;
    }

    [[nodiscard]] std::size_t hits() const noexcept { return cache_hits_; }
    [[nodiscard]] std::size_t misses() const noexcept { return cache_misses_; }

private:
    [[nodiscard]] Permission compute_access_vector(uint16_t src, uint16_t target, SecurityClass cl) const noexcept {
        auto result = Permission::None;
        for (const auto& rule : rules_) {
            if (rule.src_type == src && rule.target_type == target && rule.target_class == cl) {
                result = result | rule.allowed_permissions;
            }
        }
        return result;
    }

    std::vector<PolicyRule> rules_;
    std::unordered_map<CacheKey, Permission, CacheKeyHash> avc_cache_;
    std::size_t cache_hits_{0};
    std::size_t cache_misses_{0};
};

int main() {
    SecurityEngine engine;

    constexpr uint16_t TYPE_HTTPD_T         = 10;
    constexpr uint16_t TYPE_HTTPD_CONTENT_T = 20;
    constexpr uint16_t TYPE_SHADOW_T        = 30;

    engine.add_rule(TYPE_HTTPD_T, TYPE_HTTPD_CONTENT_T, SecurityClass::File, Permission::Read);

    const SecurityContext proc_ctx{.type_id = TYPE_HTTPD_T, .mls_sensitivity = 0, .mls_categories = 0};
    const SecurityContext html_ctx{.type_id = TYPE_HTTPD_CONTENT_T, .mls_sensitivity = 0, .mls_categories = 0};
    const SecurityContext shadow_ctx{.type_id = TYPE_SHADOW_T, .mls_sensitivity = 0, .mls_categories = 0};

    // 1. Cache Miss -> Дозволено
    const bool ok1 = engine.check_permission(proc_ctx, html_ctx, SecurityClass::File, Permission::Read);
    std::cout << "1. httpd_t -> httpd_sys_content_t (читання): " << (ok1 ? "ДОЗВОЛЕНО" : "ЗАБОРОНЕНО") << "\n";

    // 2. Cache Hit -> Дозволено
    const bool ok2 = engine.check_permission(proc_ctx, html_ctx, SecurityClass::File, Permission::Read);
    std::cout << "2. httpd_t -> httpd_sys_content_t (повторне читання): " << (ok2 ? "ДОЗВОЛЕНО" : "ЗАБОРОНЕНО") << "\n";

    // 3. Cache Miss -> Заборонено
    const bool ok3 = engine.check_permission(proc_ctx, shadow_ctx, SecurityClass::File, Permission::Read);
    std::cout << "3. httpd_t -> shadow_t (читання паролів): " << (ok3 ? "ДОЗВОЛЕНО" : "ЗАБОРОНЕНО") << "\n";

    std::cout << "Статистика AVC: Влучань = " << engine.hits() << ", Промахів = " << engine.misses() << "\n";

    return 0;
}
