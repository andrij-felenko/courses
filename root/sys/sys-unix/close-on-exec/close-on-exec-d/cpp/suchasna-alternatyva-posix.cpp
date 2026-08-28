#include <spawn.h>
#include <unistd.h>
#include <vector>
#include <system_error>

class SpawnFileActions {
public:
    SpawnFileActions() {
        if (::posix_spawn_file_actions_init(&m_actions) != 0) {
            throw std::system_error(errno, std::generic_category(), "init actions failed");
        }
    }
    
    ~SpawnFileActions() {
        ::posix_spawn_file_actions_destroy(&m_actions);
    }
    
    void add_close(int fd) {
        if (::posix_spawn_file_actions_addclose(&m_actions, fd) != 0) {
            throw std::system_error(errno, std::generic_category(), "addclose failed");
        }
    }
    
    posix_spawn_file_actions_t* get() noexcept { return &m_actions; }

private:
    posix_spawn_file_actions_t m_actions;
};
