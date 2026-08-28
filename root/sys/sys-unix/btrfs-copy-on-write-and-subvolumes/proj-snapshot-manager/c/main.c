// c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include <linux/btrfs.h>
#include <linux/fs.h>

// Помічник для створення нового порожнього субтому
int create_subvolume(const char *parent_dir, const char *subvol_name) {
    int dir_fd = open(parent_dir, O_RDONLY | O_DIRECTORY);
    if (dir_fd < 0) {
        perror("[ERR] Не вдалося відкрити батьківську директорію");
        return -1;
    }

    struct btrfs_ioctl_vol_args args;
    memset(&args, 0, sizeof(args));
    strncpy(args.name, subvol_name, BTRFS_PATH_NAME_MAX);
    args.name[BTRFS_PATH_NAME_MAX] = '\0';

    if (ioctl(dir_fd, BTRFS_IOC_SUBVOL_CREATE, &args) < 0) {
        perror("[ERR] Помилка ioctl(BTRFS_IOC_SUBVOL_CREATE)");
        close(dir_fd);
        return -1;
    }

    close(dir_fd);
    printf("[+] Субтом '%s' успішно створено в '%s'\n", subvol_name, parent_dir);
    return 0;
}

// Помічник для створення знімка лише для читання (Read-Only Snapshot)
int create_readonly_snapshot(const char *src_subvol, const char *parent_dir, const char *snap_name) {
    int src_fd = open(src_subvol, O_RDONLY | O_DIRECTORY);
    if (src_fd < 0) {
        perror("[ERR] Не вдалося відкрити джерельний субтом");
        return -1;
    }

    int parent_fd = open(parent_dir, O_RDONLY | O_DIRECTORY);
    if (parent_fd < 0) {
        perror("[ERR] Не вдалося відкрити батьківську директорію для знімка");
        close(src_fd);
        return -1;
    }

    struct btrfs_ioctl_vol_args_v2 args2;
    memset(&args2, 0, sizeof(args2));
    args2.fd = src_fd;
    args2.flags = BTRFS_SUBVOL_RDONLY;
    strncpy(args2.name, snap_name, BTRFS_SUBVOL_NAME_MAX);
    args2.name[BTRFS_SUBVOL_NAME_MAX] = '\0';

    if (ioctl(parent_fd, BTRFS_IOC_SNAP_CREATE_V2, &args2) < 0) {
        perror("[ERR] Помилка ioctl(BTRFS_IOC_SNAP_CREATE_V2)");
        close(parent_fd);
        close(src_fd);
        return -1;
    }

    close(parent_fd);
    close(src_fd);
    printf("[+] Read-Only знімок '%s' успішно створено\n", snap_name);
    return 0;
}

// Помічник для клонування файлу через VFS FICLONE (reflink)
int reflink_clone_file(const char *src_path, const char *dst_path) {
    int src_fd = open(src_path, O_RDONLY);
    if (src_fd < 0) {
        perror("[ERR] Не вдалося відкрити джерельний файл");
        return -1;
    }

    int dst_fd = open(dst_path, O_WRONLY | O_CREAT | O_EXCL, 0644);
    if (dst_fd < 0) {
        perror("[ERR] Не вдалося створити цільовий файл");
        close(src_fd);
        return -1;
    }

    if (ioctl(dst_fd, FICLONE, src_fd) < 0) {
        perror("[ERR] Помилка ioctl(FICLONE) — не Btrfs або між пристроями");
        close(src_fd);
        close(dst_fd);
        unlink(dst_path);
        return -1;
    }

    close(src_fd);
    close(dst_fd);
    printf("[+] Файл '%s' успішно клоновано через FICLONE у '%s'\n", src_path, dst_path);
    return 0;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <точка_монтування_btrfs>\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *mnt = argv[1];
    char subvol_path[1024];
    snprintf(subvol_path, sizeof(subvol_path), "%s/subvol_demo", mnt);

    if (create_subvolume(mnt, "subvol_demo") != 0) {
        return EXIT_FAILURE;
    }

    char src_file[1024], dst_file[1024];
    snprintf(src_file, sizeof(src_file), "%s/source.bin", mnt);
    snprintf(dst_file, sizeof(dst_file), "%s/cloned.bin", subvol_path);

    // Запис вихідного тестового файлу
    int tmp_fd = open(src_file, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (tmp_fd >= 0) {
        const char *data = "Btrfs CoW Reflink Payload Data\n";
        write(tmp_fd, data, strlen(data));
        close(tmp_fd);
    }

    reflink_clone_file(src_file, dst_file);
    create_readonly_snapshot(subvol_path, mnt, "subvol_demo_snap");

    return EXIT_SUCCESS;
}
