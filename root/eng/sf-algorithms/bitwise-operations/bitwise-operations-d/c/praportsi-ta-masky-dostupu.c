#include <stdio.h>
#include <stdbool.h>

#define PERM_READ    (1U << 2) // 0b100 = 4
#define PERM_WRITE   (1U << 1) // 0b010 = 2
#define PERM_EXEC    (1U << 0) // 0b001 = 1

bool check_access(uint8_t user_perms, uint8_t required_mask) {
    // Користувач повинен мати ВСІ біти, вказані в required_mask
    return (user_perms & required_mask) == required_mask;
}
