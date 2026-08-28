#include <stdio.h>
#include <sys/ioctl.h>
#include <linux/input.h>

void print_abs_x_info(int fd) {
    struct input_absinfo abs_x;
    if (ioctl(fd, EVIOCGABS(ABS_X), &abs_x) == 0) {
        printf("Вісь X: Мін = %d, Макс = %d, Похибка = %d, Роздільна здатність = %d units/mm\n",
               abs_x.minimum, abs_x.maximum, abs_x.fuzz, abs_x.resolution);
    }
}
