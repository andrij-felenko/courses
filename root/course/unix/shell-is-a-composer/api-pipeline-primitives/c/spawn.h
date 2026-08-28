#include <spawn.h>

int posix_spawn_file_actions_init(posix_spawn_file_actions_t *file_actions);
int posix_spawn_file_actions_destroy(posix_spawn_file_actions_t *file_actions);

int posix_spawn_file_actions_adddup2(posix_spawn_file_actions_t *file_actions,
                                     int oldfd, int newfd);
int posix_spawn_file_actions_addclose(posix_spawn_file_actions_t *file_actions,
                                      int fd);

int posix_spawnattr_setpgroup(posix_spawnattr_t *attr, pid_t pgroup);
int posix_spawnattr_setflags(posix_spawnattr_t *attr, short flags);
