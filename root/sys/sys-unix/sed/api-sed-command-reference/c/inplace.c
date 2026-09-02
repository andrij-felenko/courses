#include "inplace.h"

#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

#if defined(__linux__)
#include <sys/xattr.h>
#endif
#if defined(SED_WITH_SELINUX)
#include <selinux/selinux.h>
#endif

/* Шаблон тимчасового файла ЗАВЖДИ в каталозі цілі: у /tmp (окремий tmpfs)
   rename() упав би з EXDEV — Invalid cross-device link. */
static char *make_template(const char *target) {
    const char *slash = strrchr(target, '/');
    size_t dir_len = slash ? (size_t)(slash - target) + 1 : 0;
    char *tmpl = malloc(dir_len + sizeof "sedXXXXXX");
    if (!tmpl) return NULL;
    memcpy(tmpl, target, dir_len);
    memcpy(tmpl + dir_len, "sedXXXXXX", sizeof "sedXXXXXX");
    return tmpl;
}

static int write_all(int fd, const char *data, size_t len) {
    while (len > 0) {
        ssize_t n = write(fd, data, len);
        if (n < 0) {
            if (errno == EINTR) continue;
            return -1;
        }
        data += n;
        len -= (size_t)n;
    }
    return 0;
}

#if defined(__linux__)
/* Розширені атрибути (user.* і POSIX ACL) на новому inode треба відтворити руками. */
static void copy_xattrs(int src_fd, int dst_fd) {
    ssize_t names_len = flistxattr(src_fd, NULL, 0);
    if (names_len <= 0) return;
    char *names = malloc((size_t)names_len);
    if (!names) return;
    if (flistxattr(src_fd, names, (size_t)names_len) != names_len) {
        free(names);
        return;
    }
    for (char *n = names; n < names + names_len; n += strlen(n) + 1) {
        ssize_t vlen = fgetxattr(src_fd, n, NULL, 0);
        if (vlen < 0) continue;
        char *value = malloc((size_t)vlen ? (size_t)vlen : 1u);
        if (!value) continue;
        if (fgetxattr(src_fd, n, value, (size_t)vlen) == vlen)
            (void)fsetxattr(dst_fd, n, value, (size_t)vlen, 0);
        free(value);
    }
    free(names);
}
#endif

static void copy_metadata(int src_fd, int dst_fd, const struct stat *st) {
    /* mkstemp створює файл із 0600 — без fchmod результат втратив би права. */
    (void)fchmod(dst_fd, st->st_mode & 07777);
    /* Власника відтворюємо «за можливості»: без CAP_CHOWN буде EPERM,
       і тоді власником зміненого файла стане той, хто запустив sed. */
    (void)fchown(dst_fd, st->st_uid, st->st_gid);
#if defined(__linux__)
    copy_xattrs(src_fd, dst_fd);
#else
    (void)src_fd;
#endif
#if defined(SED_WITH_SELINUX)
    /* Новий файл дістав би тип за правилом переходу каталогу (etc_t замість
       shadow_t) — мітку переносимо явно, до rename(). */
    char *ctx = NULL;
    if (fgetfilecon(src_fd, &ctx) >= 0) {
        (void)fsetfilecon(dst_fd, ctx);
        freecon(ctx);
    }
#endif
}

static int make_backup(const char *target, const char *suffix) {
    size_t n = strlen(target) + strlen(suffix) + 1;
    char *bak = malloc(n);
    if (!bak) {
        errno = ENOMEM;
        return -1;
    }
    snprintf(bak, n, "%s%s", target, suffix);
    unlink(bak);
    /* Жорстке посилання лишає старий inode на місці; де посилання неможливе
       (інша ФС, каталог без прав) — падаємо на перейменування, як BSD sed. */
    int rc = (link(target, bak) == 0 || rename(target, bak) == 0) ? 0 : -1;
    int saved = errno;
    free(bak);
    errno = saved;
    return rc;
}

int sed_inplace_commit(const char *target, const char *content, size_t len,
                       const SedInplaceOpts *opts) {
    char *resolved = NULL;
    char *tmpl = NULL;
    int src_fd = -1, tmp_fd = -1, rc = -1, saved;
    struct stat st;

    if (opts->follow_symlinks) {
        resolved = realpath(target, NULL);   /* саме посилання лишається цілим */
        if (resolved) target = resolved;
    }

    tmpl = make_template(target);
    if (!tmpl) {
        errno = ENOMEM;
        goto out;
    }
    src_fd = open(target, O_RDONLY);
    if (src_fd < 0) goto out;
    if (fstat(src_fd, &st) != 0) goto out;
    if (!S_ISREG(st.st_mode)) {
        errno = EINVAL;                      /* на місці правимо лише звичайні файли */
        goto out;
    }

    tmp_fd = mkstemp(tmpl);
    if (tmp_fd < 0) goto out;
    copy_metadata(src_fd, tmp_fd, &st);

    if (write_all(tmp_fd, content, len) != 0) goto out;
    if (fsync(tmp_fd) != 0) goto out;        /* дані на носії ДО підміни імені */
    if (close(tmp_fd) != 0) {
        tmp_fd = -1;
        goto out;
    }
    tmp_fd = -1;

    if (opts->backup_suffix && make_backup(target, opts->backup_suffix) != 0) goto out;

    /* Атомарна підміна dentry. Старий inode живий, поки його тримають чужі
       дескриптори: саме тому tail -f після sed -i більше нічого не бачить. */
    if (rename(tmpl, target) != 0) goto out;
    rc = 0;

out:
    saved = errno;
    if (tmp_fd >= 0) close(tmp_fd);
    if (src_fd >= 0) close(src_fd);
    if (rc != 0 && tmpl) unlink(tmpl);
    free(tmpl);
    free(resolved);
    errno = saved;
    return rc;
}
