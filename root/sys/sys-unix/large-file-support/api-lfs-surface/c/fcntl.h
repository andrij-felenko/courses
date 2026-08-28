/* <fcntl.h> */
int      open64(const char *path, int flags, ... /* mode_t mode */);
int      openat64(int dirfd, const char *path, int flags, ... /* mode_t mode */);
int      creat64(const char *path, mode_t mode);
int      fcntl64(int fd, int cmd, ...);
int      posix_fadvise64(int fd, off64_t offset, off64_t len, int advice);
int      posix_fallocate64(int fd, off64_t offset, off64_t len);

/* <unistd.h> */
off64_t  lseek64(int fd, off64_t offset, int whence);
ssize_t  pread64(int fd, void *buf, size_t n, off64_t offset);
ssize_t  pwrite64(int fd, const void *buf, size_t n, off64_t offset);
int      truncate64(const char *path, off64_t length);
int      ftruncate64(int fd, off64_t length);
int      lockf64(int fd, int cmd, off64_t len);

/* <sys/stat.h> */
int      stat64(const char *path, struct stat64 *buf);
int      fstat64(int fd, struct stat64 *buf);
int      lstat64(const char *path, struct stat64 *buf);
int      fstatat64(int dirfd, const char *path, struct stat64 *buf, int flags);

/* <stdio.h> */
FILE    *fopen64(const char *path, const char *mode);
FILE    *freopen64(const char *path, const char *mode, FILE *stream);
FILE    *tmpfile64(void);
int      fseeko64(FILE *stream, off64_t off, int whence);
off64_t  ftello64(FILE *stream);
int      fgetpos64(FILE *stream, fpos64_t *pos);
int      fsetpos64(FILE *stream, const fpos64_t *pos);

/* <dirent.h> */
struct dirent64 *readdir64(DIR *dirp);
int      scandir64(const char *dir, struct dirent64 ***namelist,
                   int (*sel)(const struct dirent64 *),
                   int (*cmp)(const struct dirent64 **, const struct dirent64 **));
int      scandirat64(int dfd, const char *dir, struct dirent64 ***namelist,
                     int (*sel)(const struct dirent64 *),
                     int (*cmp)(const struct dirent64 **, const struct dirent64 **));
int      alphasort64(const struct dirent64 **a, const struct dirent64 **b);
int      versionsort64(const struct dirent64 **a, const struct dirent64 **b);
ssize_t  getdirentries64(int fd, char *buf, size_t nbytes, off64_t *basep);
