#include <unistd.h>
int link(const char *oldpath, const char *newpath);
int unlink(const char *pathname);
int symlink(const char *target, const char *linkpath);
int rmdir(const char *pathname);

#include <sys/stat.h>
int mkdir(const char *pathname, mode_t mode);

#include <stdio.h>
int rename(const char *oldpath, const char *newpath);
