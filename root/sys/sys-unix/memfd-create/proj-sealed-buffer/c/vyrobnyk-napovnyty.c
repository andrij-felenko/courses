#define WIDTH  640
#define HEIGHT 360
struct frame { uint32_t w, h; uint32_t px[]; };
#define FRAME_BYTES (sizeof(struct frame) + (size_t)WIDTH * HEIGHT * 4)

static void producer(int sock, int with_shrink)
{
    int fd = memfd_create("frame", MFD_CLOEXEC | MFD_ALLOW_SEALING);
    if (fd < 0) die("memfd_create");
    if (ftruncate(fd, FRAME_BYTES) < 0) die("ftruncate");

    struct frame *f = mmap(NULL, FRAME_BYTES, PROT_READ | PROT_WRITE,
                           MAP_SHARED, fd, 0);
    if (f == MAP_FAILED) die("mmap");

    f->w = WIDTH; f->h = HEIGHT;
    for (size_t i = 0; i < (size_t)WIDTH * HEIGHT; i++) {
        uint32_t g = (uint32_t)((i % WIDTH) * 255 / (WIDTH - 1));
        f->px[i] = 0xff000000u | (g << 8);
    }

    /* пастка: пломбуємо, поки живе власне записувальне відображення */
    if (fcntl(fd, F_ADD_SEALS, F_SEAL_WRITE) < 0)
        printf("[виробник] F_SEAL_WRITE до munmap → %s\n", strerror(errno));

    if (munmap(f, FRAME_BYTES) < 0) die("munmap");

    int seals = F_SEAL_GROW | F_SEAL_WRITE | F_SEAL_SEAL;
    if (with_shrink) seals |= F_SEAL_SHRINK;
    if (fcntl(fd, F_ADD_SEALS, seals) < 0) die("F_ADD_SEALS");

    printf("[виробник] пломби 0x%x, %zu байтів → віддаю дескриптор\n",
           fcntl(fd, F_GET_SEALS), FRAME_BYTES);
    if (send_fd(sock, fd) < 0) die("send_fd");

    char ack;
    if (read(sock, &ack, 1) != 1) die("read");     /* сусід уже відобразив */
    if (ftruncate(fd, 0) == 0)
        puts("[виробник] ftruncate(fd, 0) пройшов — файл тепер порожній");
    else
        printf("[виробник] ftruncate(fd, 0) → %s\n", strerror(errno));
    if (write(sock, "T", 1) != 1) die("write");
    close(fd);
}
