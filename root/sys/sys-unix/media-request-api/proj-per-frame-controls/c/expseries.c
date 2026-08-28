/* expseries.c — серія кадрів із різними витримками через медіазапити.
 *
 *   cc -O2 -Wall -o expseries expseries.c
 *   ./expseries /dev/media0 /dev/video0 [/dev/v4l-subdev0]
 *
 * Третій аргумент — вузол, якому належить витримка; якщо його немає,
 * керування шукають на самому відеовузлі.
 * Потрібні заголовки ядра 4.20 або новіші.
 */
#include <errno.h>
#include <fcntl.h>
#include <poll.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <unistd.h>

#include <linux/media.h>
#include <linux/videodev2.h>

#define NSLOT   3    /* стільки запитів тримаємо в польоті одночасно */
#define FRAMES 12    /* стільки кадрів знімаємо всього */
#define TYPE   V4L2_BUF_TYPE_VIDEO_CAPTURE

/* витримки в одиницях по 100 мкс: 2 мс, 10 мс, 50 мс */
static const int EXPOSURE[NSLOT] = { 20, 100, 500 };

struct slot {
    int    req_fd;   /* дескриптор запиту */
    void  *start;    /* відображений буфер */
    size_t length;
    int    want;     /* витримка, яку ми поклали в цей запит */
};

static void die(const char *what)
{
    fprintf(stderr, "%s: %s\n", what, strerror(errno));
    exit(EXIT_FAILURE);
}

/* ioctl, який не здається на сигналі */
static int xioctl(int fd, unsigned long cmd, void *arg)
{
    int r;
    do { r = ioctl(fd, cmd, arg); } while (r == -1 && errno == EINTR);
    return r;
}

/* ── три дії над вмістом запиту ───────────────────────────────────────── */

/* Покласти витримку В ЗАПИТ. Без request_fd те саме значення пішло б
   у залізо негайно — тобто не в той кадр. */
static int want_exposure(int ctrl_fd, int req_fd, int value)
{
    struct v4l2_ext_control c = { .id = V4L2_CID_EXPOSURE_ABSOLUTE, .value = value };
    struct v4l2_ext_controls ec = {
        .which      = V4L2_CTRL_WHICH_REQUEST_VAL,
        .request_fd = req_fd,
        .count      = 1,
        .controls   = &c,
    };
    return xioctl(ctrl_fd, VIDIOC_S_EXT_CTRLS, &ec);
}

/* Прочитати з ЗАВЕРШЕНОГО запиту те, що драйвер справді застосував. */
static int applied_exposure(int ctrl_fd, int req_fd, int *value)
{
    struct v4l2_ext_control c = { .id = V4L2_CID_EXPOSURE_ABSOLUTE };
    struct v4l2_ext_controls ec = {
        .which      = V4L2_CTRL_WHICH_REQUEST_VAL,
        .request_fd = req_fd,
        .count      = 1,
        .controls   = &c,
    };
    if (xioctl(ctrl_fd, VIDIOC_G_EXT_CTRLS, &ec) == -1)
        return -1;
    *value = c.value;
    return 0;
}

/* Покласти буфер У ЗАПИТ, а не у вхідну чергу драйвера. Прапорець і поле
   пишемо в одному місці: нарізно про друге забувають. */
static int put_buffer(int video_fd, int req_fd, unsigned index)
{
    struct v4l2_buffer b = {
        .type       = TYPE,
        .memory     = V4L2_MEMORY_MMAP,
        .index      = index,
        .flags      = V4L2_BUF_FLAG_REQUEST_FD,
        .request_fd = req_fd,
    };
    return xioctl(video_fd, VIDIOC_QBUF, &b);
}

int main(int argc, char **argv)
{
    const char *media_path = argc > 1 ? argv[1] : "/dev/media0";
    const char *video_path = argc > 2 ? argv[2] : "/dev/video0";
    const char *ctrl_path  = argc > 3 ? argv[3] : NULL;

    struct slot   slot[NSLOT];
    struct pollfd pfd[NSLOT];
    enum v4l2_buf_type type = TYPE;
    int i, head = 0, done = 0;

    int media_fd = open(media_path, O_RDWR);
    if (media_fd == -1)
        die(media_path);

    /* O_NONBLOCK навмисно: DQBUF ми кличемо лише після завершення запиту,
       тож блокуватися він не має права. Якщо все-таки заблокувався б,
       ми побачимо EAGAIN замість тихого зависання. */
    int video_fd = open(video_path, O_RDWR | O_NONBLOCK);
    if (video_fd == -1)
        die(video_path);

    int ctrl_fd = video_fd;
    if (ctrl_path && (ctrl_fd = open(ctrl_path, O_RDWR)) == -1)
        die(ctrl_path);

    /* Чи має ця черга право приймати буфери в запитах.
       count = 0 — проба без побічних дій. */
    struct v4l2_requestbuffers rb = {
        .count = 0, .type = TYPE, .memory = V4L2_MEMORY_MMAP,
    };
    if (xioctl(video_fd, VIDIOC_REQBUFS, &rb) == -1)
        die("VIDIOC_REQBUFS (проба)");
    if (!(rb.capabilities & V4L2_BUF_CAP_SUPPORTS_REQUESTS)) {
        fprintf(stderr, "%s: черга не вміє запитів — далі йти нема куди\n", video_path);
        return EXIT_FAILURE;
    }

    rb.count = NSLOT;
    if (xioctl(video_fd, VIDIOC_REQBUFS, &rb) == -1)
        die("VIDIOC_REQBUFS");
    if (rb.count < NSLOT) {
        fprintf(stderr, "драйвер дав %u буферів замість %d\n", rb.count, NSLOT);
        return EXIT_FAILURE;
    }

    for (i = 0; i < NSLOT; i++) {
        struct v4l2_buffer b = { .type = TYPE, .memory = V4L2_MEMORY_MMAP, .index = i };

        if (xioctl(video_fd, VIDIOC_QUERYBUF, &b) == -1)
            die("VIDIOC_QUERYBUF");
        slot[i].length = b.length;
        slot[i].start  = mmap(NULL, b.length, PROT_READ | PROT_WRITE,
                              MAP_SHARED, video_fd, b.m.offset);
        if (slot[i].start == MAP_FAILED)
            die("mmap");

        if (xioctl(media_fd, MEDIA_IOC_REQUEST_ALLOC, &slot[i].req_fd) == -1)
            die("MEDIA_IOC_REQUEST_ALLOC");
        pfd[i].fd     = slot[i].req_fd;
        pfd[i].events = POLLPRI;
    }

    /* Режим перемикають один раз і напряму: доки автоекспозиція ввімкнена,
       ручну витримку драйвер має право просто ігнорувати. */
    struct v4l2_control mode = {
        .id = V4L2_CID_EXPOSURE_AUTO, .value = V4L2_EXPOSURE_MANUAL,
    };
    if (xioctl(ctrl_fd, VIDIOC_S_CTRL, &mode) == -1)
        fprintf(stderr, "увага: автоекспозицію вимкнути не вдалося (%s)\n",
                strerror(errno));

    /* Три запити наперед: у кожному своя витримка і свій буфер. */
    for (i = 0; i < NSLOT; i++) {
        slot[i].want = EXPOSURE[i];
        if (want_exposure(ctrl_fd, slot[i].req_fd, slot[i].want) == -1)
            die("VIDIOC_S_EXT_CTRLS у запит");
        if (put_buffer(video_fd, slot[i].req_fd, i) == -1)
            die("VIDIOC_QBUF у запит");
        if (xioctl(slot[i].req_fd, MEDIA_REQUEST_IOC_QUEUE, NULL) == -1)
            die("MEDIA_REQUEST_IOC_QUEUE");
    }

    if (xioctl(video_fd, VIDIOC_STREAMON, &type) == -1)
        die("VIDIOC_STREAMON");

    printf(" кадр слот   заявлено  застосовано  буфер  sequence\n");

    while (done < FRAMES) {
        int n = poll(pfd, NSLOT, 2000);

        if (n == -1) {
            if (errno == EINTR)
                continue;
            die("poll");
        }
        if (n == 0) {
            fprintf(stderr, "за 2 с не завершився жоден запит\n");
            break;
        }

        /* Запити виконуються в порядку черги, а ставимо ми їх по колу —
           отже й завершуються вони по колу. Чекаємо саме на голову. */
        while (pfd[head].revents & POLLPRI) {
            struct v4l2_buffer b = { .type = TYPE, .memory = V4L2_MEMORY_MMAP };
            struct slot *s = &slot[head];
            int got = 0;

            if (applied_exposure(ctrl_fd, s->req_fd, &got) == -1)
                die("VIDIOC_G_EXT_CTRLS із запиту");
            if (xioctl(video_fd, VIDIOC_DQBUF, &b) == -1)
                die("VIDIOC_DQBUF");

            printf("%5d %4d %8.1f мс %9.1f мс %6u %9u\n",
                   done, head, s->want / 10.0, got / 10.0, b.index, b.sequence);

            /* тут була б робота з пікселями: s->start, b.bytesused */

            if (xioctl(s->req_fd, MEDIA_REQUEST_IOC_REINIT, NULL) == -1)
                die("MEDIA_REQUEST_IOC_REINIT");

            /* Наступне значення в справжній програмі дав би регулятор
               яскравості; тут слот просто лишається на своїй витримці. */
            s->want = EXPOSURE[head];
            if (want_exposure(ctrl_fd, s->req_fd, s->want) == -1)
                die("VIDIOC_S_EXT_CTRLS у запит");
            if (put_buffer(video_fd, s->req_fd, b.index) == -1)
                die("VIDIOC_QBUF у запит");
            if (xioctl(s->req_fd, MEDIA_REQUEST_IOC_QUEUE, NULL) == -1)
                die("MEDIA_REQUEST_IOC_QUEUE");

            pfd[head].revents = 0;
            head = (head + 1) % NSLOT;
            if (++done >= FRAMES)
                break;
        }
    }

    if (xioctl(video_fd, VIDIOC_STREAMOFF, &type) == -1)
        die("VIDIOC_STREAMOFF");
    for (i = 0; i < NSLOT; i++) {
        close(slot[i].req_fd);
        munmap(slot[i].start, slot[i].length);
    }
    if (ctrl_fd != video_fd)
        close(ctrl_fd);
    close(video_fd);
    close(media_fd);
    return 0;
}
