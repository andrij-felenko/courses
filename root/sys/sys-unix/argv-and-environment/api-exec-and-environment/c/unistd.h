/* POSIX Сигнатури C */
#include <unistd.h>

int execve(const char *pathname, char *const argv[], char *const envp[]);
int execv(const char *pathname, char *const argv[]);
int execvp(const char *file, char *const argv[]);
int execvpe(const char *file, char *const argv[], char *const envp[]);
int execl(const char *pathname, const char *arg0, ... /*, (char *)0 */);
int execlp(const char *file, const char *arg0, ... /*, (char *)0 */);
int execle(const char *pathname, const char *arg0, ... /*, (char *)0, char *const envp[] */);
int fexecve(int fd, char *const argv[], char *const envp[]);
