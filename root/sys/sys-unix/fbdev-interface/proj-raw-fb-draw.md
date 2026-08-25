# ⚙️ Малювання у кадровому буфері (C)

Ця програма демонструє, як відкрити `/dev/fb0`, дізнатися його параметри, відобразити пам'ять і намалювати білий квадрат 200 × 200 пікселів.

```c
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
```

Під час малювання ми використовуємо `finfo.line_length` для переміщення по осі Y та розмір пікселя у байтах для осі X. Це гарантує правильне розташування незалежно від апаратного вирівнювання рядків.

Порядок каналів усередині пікселя `bits_per_pixel` не задає — його оголошують поля `red`, `green`, `blue` і `transp` структури `fb_var_screeninfo` (`include/uapi/linux/fb.h`: `struct fb_bitfield` з `offset` і `length`). Розкладка «синій, зелений, червоний, четвертий байт» у прикладі — це `XRGB8888`/`ARGB8888` на little-endian машині; трапляється й дзеркальна `x8b8g8r8` (див. таблицю `SIMPLEFB_FORMATS` в `include/linux/platform_data/simplefb.h`), тож серйозна програма читає зміщення з `vinfo`, а не жорстко кодує індекси.

Четвертий байт — саме той, що найчастіше плутають. У типового 32-бітного fbdev формат — `XRGB8888`: `bits_per_pixel` дорівнює 32, а `transp.length` дорівнює 0, тобто байт не використовується взагалі. Це видно з емуляції fbdev у DRM: хелпер, що заповнює `fb_var_screeninfo` за форматом DRM (`drivers/gpu/drm/drm_fb_helper.c`; ім'я й сигнатура цієї функції мінялися між версіями ядра), розрізняє формати за глибиною — для `XRGB8888` (глибина 24 при 32 бітах на піксель) ставить `transp.length = 0`, а вісімку в `transp` дає лише справжньому `ARGB8888` з глибиною 32; той самий поділ — у рядках `x8r8g8b8` (`transp {0, 0}`) і `a8r8g8b8` (`transp {24, 8}`) таблиці `SIMPLEFB_FORMATS`. Тому запис 255 безпечний в обох випадках: у `XRGB8888` його просто проігнорують, а в `ARGB8888` він дасть повністю непрозорий білий. Нуль же на пристрої з дійсною альфою зробив би «білий квадрат» цілком прозорим — тобто невидимим.
