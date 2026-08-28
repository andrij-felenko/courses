#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <linux/fb.h>
#include <stdint.h>

int main() {
    int fbfd = open("/dev/fb0", O_RDWR);
    if (fbfd == -1) {
        perror("Error: cannot open framebuffer device");
        return 1;
    }

    struct fb_var_screeninfo vinfo;
    struct fb_fix_screeninfo finfo;

    // Отримання фіксованої та змінної інформації
    if (ioctl(fbfd, FBIOGET_FSCREENINFO, &finfo) == -1 || 
        ioctl(fbfd, FBIOGET_VSCREENINFO, &vinfo) == -1) {
        perror("Error reading variable information");
        close(fbfd);
        return 1;
    }

    long screensize = vinfo.yres_virtual * finfo.line_length;
    uint8_t *fbp = (uint8_t *)mmap(0, screensize, PROT_READ | PROT_WRITE, MAP_SHARED, fbfd, 0);
    
    if (fbp == MAP_FAILED) {
        perror("Error: failed to map framebuffer device to memory");
        close(fbfd);
        return 1;
    }

    // Малюємо білий квадрат 200 × 200 (x, y від 100 до 299), обрізаний межами екрана
    unsigned int y_max = vinfo.yres < 300 ? vinfo.yres : 300;
    unsigned int x_max = vinfo.xres < 300 ? vinfo.xres : 300;

    for (unsigned int y = 100; y < y_max; y++) {
        for (unsigned int x = 100; x < x_max; x++) {
            long location = (x + vinfo.xoffset) * (vinfo.bits_per_pixel / 8) + 
                            (y + vinfo.yoffset) * finfo.line_length;
            
            if (vinfo.bits_per_pixel == 32) {
                *(fbp + location) = 255;        // Blue
                *(fbp + location + 1) = 255;    // Green
                *(fbp + location + 2) = 255;    // Red
                *(fbp + location + 3) = 255;    // альфа (ARGB) або невживаний X-байт (XRGB)
            }
        }
    }

    munmap(fbp, screensize);
    close(fbfd);
    return 0;
}
