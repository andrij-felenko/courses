#include <sys/stat.h>

int _close(int fd)              { (void)fd; return -1; }      // нема чого закривати
int _lseek(int fd, int p, int w){ (void)fd;(void)p;(void)w; return 0; }
int _isatty(int fd)             { (void)fd; return 1; }       // консоль = термінал
int _fstat(int fd, struct stat *st) {
    (void)fd;
    st->st_mode = S_IFCHR;      // «символьний пристрій»: stdio вимкне блочну буферизацію
    return 0;
}
void _exit(int code)            { (void)code; while (1) {} }  // на МК нема куди «вийти»
int _kill(int pid, int sig)     { (void)pid;(void)sig; errno = EINVAL; return -1; }
int _getpid(void)               { return 1; }
