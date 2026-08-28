#include <linux/landlock.h>
#include <sys/prctl.h>
#include <sys/syscall.h>
#include <unistd.h>

/* Створення правил Landlock: дозволяємо лише читання вказаного каталогу */
struct landlock_ruleset_attr attr = {
    .handled_access_fs = LANDLOCK_ACCESS_FS_READ_FILE | LANDLOCK_ACCESS_FS_READ_DIR,
};
int ruleset_fd = syscall(__NR_landlock_create_ruleset, &attr, sizeof(attr), 0);

/* Активація самообмеження процесу */
prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0);
syscall(__NR_landlock_restrict_self, ruleset_fd, 0);
close(ruleset_fd);
