__u64 flags = 0;

// Отримання поточних прапорців
if (ioctl(subvol_fd, BTRFS_IOC_SUBVOL_GETFLAGS, &flags) < 0) {
    perror("BTRFS_IOC_SUBVOL_GETFLAGS failed");
}

// Встановлення прапора Read-Only
flags |= BTRFS_SUBVOL_RDONLY;
if (ioctl(subvol_fd, BTRFS_IOC_SUBVOL_SETFLAGS, &flags) < 0) {
    perror("BTRFS_IOC_SUBVOL_SETFLAGS failed");
}
