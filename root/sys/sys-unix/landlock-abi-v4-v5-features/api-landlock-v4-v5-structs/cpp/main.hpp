#include <linux/landlock.h>
#include <sys/syscall.h>
#include <unistd.h>

extern "C" {
    int landlock_create_ruleset(
        const struct landlock_ruleset_attr *attr,
        std::size_t size,
        std::uint32_t flags
    );

    int landlock_add_rule(
        int ruleset_fd,
        enum landlock_rule_type rule_type,
        const void *rule_attr,
        std::uint32_t flags
    );

    int landlock_restrict_self(
        int ruleset_fd,
        std::uint32_t flags
    );
}
