int fd = open("app.apk", O_RDONLY);          /* саме O_RDONLY */

struct fsverity_enable_arg arg = {
        .version        = 1,
        .hash_algorithm = FS_VERITY_HASH_ALG_SHA256,
        .block_size     = 4096,
};                                            /* решта полів — нулі */

if (ioctl(fd, FS_IOC_ENABLE_VERITY, &arg) != 0)
        perror("FS_IOC_ENABLE_VERITY");
