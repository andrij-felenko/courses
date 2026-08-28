#include <unistd.h>

int execl (const char *pathname, const char *arg, ... /*, (char *) NULL */);
int execlp(const char *file,     const char *arg, ... /*, (char *) NULL */);
int execle(const char *pathname, const char *arg, ...
                                 /*, (char *) NULL, char *const envp[] */);

int execv (const char *pathname, char *const argv[]);
int execvp(const char *file,     char *const argv[]);
int execve(const char *pathname, char *const argv[], char *const envp[]);
