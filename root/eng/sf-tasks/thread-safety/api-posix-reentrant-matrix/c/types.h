#include <sys/types.h>
#include <pwd.h>
#include <grp.h>

/* ЗАСТАРІЛІ ОДНОПОТОКОВІ ФУНКЦІЇ */
struct passwd *getpwnam(const char *name);
struct passwd *getpwuid(uid_t uid);
struct group  *getgrnam(const char *name);
struct group  *getgrgid(gid_t gid);

/* РЕЕНТРАБЕЛЬНІ АНАЛОГИ POSIX */
int getpwnam_r(const char *name, struct passwd *pwd,
               char *buf, size_t buflen, struct passwd **result);
int getpwuid_r(uid_t uid, struct passwd *pwd,
               char *buf, size_t buflen, struct passwd **result);
int getgrnam_r(const char *name, struct group *grp,
               char *buf, size_t buflen, struct group **result);
int getgrgid_r(gid_t gid, struct group *grp,
               char *buf, size_t buflen, struct group **result);
