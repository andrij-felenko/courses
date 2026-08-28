#include <iostream>
#include <string>
#include <memory>

struct UserRecord {
    int id;
    std::string username;
    std::string email;
};

class PersistenceEntry {
public:
    UserRecord current;
    UserRecord snapshot;

    PersistenceEntry(UserRecord record) : current(record), snapshot(record) {}

    void flush() {
        if (current.username != snapshot.username || current.email != snapshot.email) {
            std::cout << "[SQL] UPDATE users SET username='" << current.username 
                      << "', email='" << current.email 
                      << "' WHERE id=" << current.id << ";\n";
            snapshot = current;
        } else {
            std::cout << "[No-Op] Змін для id=" << current.id << " не виявлено.\n";
        }
    }
};
