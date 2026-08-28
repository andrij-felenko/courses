#define _GNU_SOURCE
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>

int openat(int dirfd, const char *pathname, int flags, ... /* mode_t mode */);
int mkdirat(int dirfd, const char *pathname, mode_t mode);
int unlinkat(int dirfd, const char *pathname, int flags);
int symlinkat(const char *target, int newdirfd, const char *linkpath);
int linkat(int olddirfd, const char *oldpath,
           int newdirfd, const char *newpath, int flags);
int renameat(int olddirfd, const char *oldpath,
             int newdirfd, const char *newpath);
int fstatat(int dirfd, const char *pathname, struct stat *statbuf, int flags);
