#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/sysmacros.h>
#include <sys/xattr.h>
#include <linux/fs.h>

#define COPY_BUF_SIZE 65536

static int copy_sparse_data(int src_fd, int dst_fd, off_t total_size) {
    off_t offset = 0;
    char buffer[COPY_BUF_SIZE];

    while (offset < total_size) {
        off_t data_start = lseek(src_fd, offset, SEEK_DATA);
        if (data_start == -1) {
            if (errno == ENXIO) {
                /* Більше даних немає, решта файлу є діркою */
                break;
            }
            return -1;
        }

        off_t hole_start = lseek(src_fd, data_start, SEEK_HOLE);
        if (hole_start == -1) {
            hole_start = total_size;
        }

        if (lseek(dst_fd, data_start, SEEK_SET) == -1) {
            return -1;
        }

        off_t remaining = hole_start - data_start;
        lseek(src_fd, data_start, SEEK_SET);

        while (remaining > 0) {
            size_t to_read = (remaining < COPY_BUF_SIZE) ? (size_t)remaining : COPY_BUF_SIZE;
            ssize_t n_read = read(src_fd, buffer, to_read);
            if (n_read <= 0) {
                if (n_read < 0 && errno == EINTR) continue;
                return -1;
            }

            ssize_t written = 0;
            while (written < n_read) {
                ssize_t n_write = write(dst_fd, buffer + written, n_read - written);
                if (n_write <= 0) {
                    if (n_write < 0 && errno == EINTR) continue;
                    return -1;
                }
                written += n_write;
            }
            remaining -= n_read;
        }
        offset = hole_start;
    }

    if (ftruncate(dst_fd, total_size) == -1) {
        return -1;
    }
    return 0;
}

static int copy_xattrs(const char *src_path, const char *dst_path) {
    ssize_t list_len = llistxattr(src_path, NULL, 0);
    if (list_len <= 0) {
        return (list_len == 0 || errno == ENOTSUP || errno == ENODATA) ? 0 : -1;
    }

    char *list = malloc(list_len);
    if (!list) return -1;

    list_len = llistxattr(src_path, list, list_len);
    if (list_len < 0) {
        free(list);
        return -1;
    }

    const char *attr_name = list;
    while (attr_name < list + list_len) {
        ssize_t val_len = lgetxattr(src_path, attr_name, NULL, 0);
        if (val_len > 0) {
            void *val = malloc(val_len);
            if (val) {
                if (lgetxattr(src_path, attr_name, val, val_len) == val_len) {
                    lsetxattr(dst_path, attr_name, val, val_len, 0);
                }
                free(val);
            }
        } else if (val_len == 0) {
            lsetxattr(dst_path, attr_name, "", 0, 0);
        }
        attr_name += strlen(attr_name) + 1;
    }

    free(list);
    return 0;
}

int clone_vfs_node(const char *src_path, const char *dst_path) {
    struct statx stx;
    unsigned int mask = STATX_TYPE | STATX_MODE | STATX_UID | STATX_GID |
                        STATX_ATIME | STATX_MTIME | STATX_SIZE;

    if (statx(AT_FDCWD, src_path, AT_SYMLINK_NOFOLLOW, mask, &stx) != 0) {
        perror("statx");
        return -1;
    }

    mode_t type = stx.stx_mode & S_IFMT;

    if (S_ISREG(type)) {
        int src_fd = open(src_path, O_RDONLY | O_NOFOLLOW);
        if (src_fd < 0) return -1;

        int dst_fd = open(dst_path, O_WRONLY | O_CREAT | O_TRUNC, 0600);
        if (dst_fd < 0) {
            close(src_fd);
            return -1;
        }

        /* Спроба скопіювати через CoW copy_file_range */
        loff_t in_off = 0, out_off = 0;
        ssize_t reflink_res = copy_file_range(src_fd, &in_off, dst_fd, &out_off, stx.stx_size, 0);
        if (reflink_res < 0 || (size_t)reflink_res < stx.stx_size) {
            /* Повернення на початок та звичайне розріджене копіювання */
            lseek(src_fd, 0, SEEK_SET);
            lseek(dst_fd, 0, SEEK_SET);
            if (copy_sparse_data(src_fd, dst_fd, stx.stx_size) != 0) {
                close(src_fd);
                close(dst_fd);
                return -1;
            }
        }

        close(src_fd);
        close(dst_fd);
    } else if (S_ISDIR(type)) {
        if (mkdir(dst_path, 0700) != 0 && errno != EEXIST) {
            return -1;
        }
    } else if (S_ISLNK(type)) {
        char link_target[PATH_MAX];
        ssize_t len = readlink(src_path, link_target, sizeof(link_target) - 1);
        if (len < 0) return -1;
        link_target[len] = '\0';

        if (symlink(link_target, dst_path) != 0) return -1;
    } else if (S_ISFIFO(type)) {
        if (mkfifo(dst_path, 0600) != 0) return -1;
    } else if (S_ISCHR(type) || S_ISBLK(type)) {
        dev_t dev = makedev(stx.stx_rdev_major, stx.stx_rdev_minor);
        if (mknod(dst_path, type | 0600, dev) != 0) return -1;
    }

    /* Відновлення розширених атрибутів (xattr, ACL, SELinux) */
    copy_xattrs(src_path, dst_path);

    /* Відновлення власника та групи (потрібні права root / CAP_CHOWN) */
    fchownat(AT_FDCWD, dst_path, stx.stx_uid, stx.stx_gid, AT_SYMLINK_NOFOLLOW);

    /* Відновлення прав доступу mode (після fchownat, щоб не скинулись SUID/SGID) */
    if (!S_ISLNK(type)) {
        fchmodat(AT_FDCWD, dst_path, stx.stx_mode & 07777, 0);
    }

    /* Відновлення міток часу (atime та mtime) */
    struct timespec times[2];
    times[0].tv_sec = stx.stx_atime.tv_sec;
    times[0].tv_nsec = stx.stx_atime.tv_nsec;
    times[1].tv_sec = stx.stx_mtime.tv_sec;
    times[1].tv_nsec = stx.stx_mtime.tv_nsec;

    utimensat(AT_FDCWD, dst_path, times, AT_SYMLINK_NOFOLLOW);

    return 0;
}
