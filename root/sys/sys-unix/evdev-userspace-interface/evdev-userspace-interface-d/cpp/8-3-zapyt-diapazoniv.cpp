#include <iostream>
#include <sys/ioctl.h>
#include <linux/input.h>

void print_abs_x_info(int fd) {
    struct input_absinfo abs_x{};
    if (::ioctl(fd, EVIOCGABS(ABS_X), &abs_x) == 0) {
        std::cout << "Axis X: Min = " << abs_x.minimum
                  << ", Max = " << abs_x.maximum
                  << ", Fuzz = " << abs_x.fuzz
                  << ", Resolution = " << abs_x.resolution << " units/mm\n";
    }
}
