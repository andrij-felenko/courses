#include <dirent.h>

DIR           *opendir(const char *name);
DIR           *fdopendir(int fd);
struct dirent *readdir(DIR *dirp);
int            closedir(DIR *dirp);
void           rewinddir(DIR *dirp);
long           telldir(DIR *dirp);
void           seekdir(DIR *dirp, long loc);
int            dirfd(DIR *dirp);
