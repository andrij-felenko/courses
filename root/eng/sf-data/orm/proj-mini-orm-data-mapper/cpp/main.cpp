#include <iostream>
#include <vector>
#include <string>
#include <memory>
#include <unordered_map>
#include <stdexcept>

namespace mini_orm {

// 1. Чиста доменна модель (POCO)
class User {
public:
    uint32_t id;
    std::string name;
    std::string email;

    User(uint32_t id, std::string name, std::string email)
        : id(id), name(std::move(name)), email(std::move(email)) {}
};

enum class EntityState { Clean, New, Dirty, Deleted };

struct TrackedEntity {
    std::shared_ptr<User> entity;
    User snapshot; // Знімок стану для Dirty Checking
    EntityState state{EntityState::Clean};
};

// 2. Unit of Work та Identity Map
class UnitOfWork {
public:
    std::shared_ptr<User> find_by_id(uint32_t id) {
        auto it = identity_map_.find(id);
        if (it != identity_map_.end()) {
            std::cout << "[IdentityMap] Сутність id=" << id << " знайдена в L1 кеші\n";
            return it->second.entity;
        }

        // Імітація вибірки з бази даних (SQL SELECT)
        std::cout << "[DB Query] SELECT * FROM users WHERE id = " << id << ";\n";
        auto user = std::make_shared<User>(id, "Олександр", "alex@example.com");
        
        TrackedEntity tracked{user, *user, EntityState::Clean};
        identity_map_[id] = tracked;
        return user;
    }

    void register_new(std::shared_ptr<User> user) {
        identity_map_[user->id] = {user, *user, EntityState::New};
    }

    void register_deleted(uint32_t id) {
        auto it = identity_map_.find(id);
        if (it != identity_map_.end()) {
            it->second.state = EntityState::Deleted;
        }
    }

    void commit() {
        std::cout << "\n=== Unit of Work: Генерація пакетного COMMIT ===\n";
        for (auto& [id, tracked] : identity_map_) {
            if (tracked.state == EntityState::New) {
                std::cout << "[SQL INSERT] INTO users (id, name, email) VALUES ("
                          << tracked.entity->id << ", '" << tracked.entity->name 
                          << "', '" << tracked.entity->email << "');\n";
                tracked.snapshot = *tracked.entity;
                tracked.state = EntityState::Clean;
            } else if (tracked.state == EntityState::Clean) {
                // Автоматичний Dirty Checking
                if (tracked.entity->name != tracked.snapshot.name || 
                    tracked.entity->email != tracked.snapshot.email) {
                    std::cout << "[SQL UPDATE] users SET name = '" << tracked.entity->name
                              << "', email = '" << tracked.entity->email 
                              << "' WHERE id = " << tracked.entity->id << ";\n";
                    tracked.snapshot = *tracked.entity;
                }
            } else if (tracked.state == EntityState::Deleted) {
                std::cout << "[SQL DELETE] FROM users WHERE id = " << id << ";\n";
            }
        }
        std::cout << "=== Усі зміни зафіксовано успішно ===\n\n";
    }

private:
    std::unordered_map<uint32_t, TrackedEntity> identity_map_;
};

} // namespace mini_orm
