/* growprobe.c — перевірка при open() є знімком, а не гарантією.
   cc -m32 growprobe.c -o growprobe        (навмисно ВУЗЬКА збірка) */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>

int main(int argc, char **argv)
{
    if (argc != 2) { fprintf(stderr, "growprobe <файл>\n"); return 2; }

    int fd = open(argv[1], O_RDONLY);
    if (fd < 0) { perror("open"); return 1; }
    printf("відкрито; кінець файлу на %jd\n", (intmax_t)lseek(fd, 0, SEEK_END));

    printf("тепер розширте файл ЗЗОВНІ (truncate -s 3G %s) і тисніть Enter…\n",
           argv[1]);
    (void)getchar();

    off_t end = lseek(fd, 0, SEEK_END);
    if (end == (off_t)-1)
        printf("lseek(SEEK_END) → -1, %s\n", strerror(errno));
    else
        printf("lseek(SEEK_END) → %jd\n", (intmax_t)end);
    return 0;
}
