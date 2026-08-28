#include <sys/wait.h>

pid_t wait(int *_Nullable wstatus);
pid_t waitpid(pid_t pid, int *_Nullable wstatus, int options);
int   waitid(idtype_t idtype, id_t id, siginfo_t *infop, int options);

/* для wait3/wait4 у glibc потрібен _DEFAULT_SOURCE
   (до glibc 2.19 — _BSD_SOURCE), і додатковий заголовок */
#include <sys/resource.h>

pid_t wait3(int *_Nullable wstatus, int options,
            struct rusage *_Nullable rusage);
pid_t wait4(pid_t pid, int *_Nullable wstatus, int options,
            struct rusage *_Nullable rusage);
