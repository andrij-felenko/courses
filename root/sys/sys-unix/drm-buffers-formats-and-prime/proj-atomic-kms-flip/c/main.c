/* C Implementation: Atomic KMS Double Buffer Page Flip */
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <poll.h>
#include <unistd.h>
#include <xf86drm.h>
#include <xf86drmMode.h>

struct buffer_t {
    uint32_t width;
    uint32_t height;
    uint32_t pitch;
    uint32_t handle;
    uint32_t size;
    uint32_t fb_id;
    uint32_t *vaddr;
};

struct kms_context {
    int fd;
    uint32_t conn_id;
    uint32_t crtc_id;
    uint32_t plane_id;
    uint32_t crtc_index;
    drmModeModeInfo mode;
    
    uint32_t prop_fb_id;
    uint32_t prop_crtc_id;
    uint32_t prop_crtc_w;
    uint32_t prop_crtc_h;
    uint32_t prop_src_w;
    uint32_t prop_src_h;
    
    struct buffer_t buffers[2];
    int current_buf;
    int waiting_for_flip;
};

static uint32_t get_property_id(int fd, uint32_t obj_id, uint32_t obj_type, const char *name) {
    drmModeObjectPropertiesPtr props = drmModeObjectGetProperties(fd, obj_id, obj_type);
    if (!props) return 0;
    
    uint32_t prop_id = 0;
    for (uint32_t i = 0; i < props->count_props; i++) {
        drmModePropertyPtr prop = drmModeGetProperty(fd, props->props[i]);
        if (prop) {
            if (strcmp(prop->name, name) == 0) {
                prop_id = prop->prop_id;
                drmModeFreeProperty(prop);
                break;
            }
            drmModeFreeProperty(prop);
        }
    }
    drmModeFreeObjectProperties(props);
    return prop_id;
}

static int create_dumb_buffer(int fd, struct buffer_t *buf, uint32_t width, uint32_t height) {
    struct drm_mode_create_dumb creq = {
        .width = width,
        .height = height,
        .bpp = 32
    };
    if (drmIoctl(fd, DRM_IOCTL_MODE_CREATE_DUMB, &creq) < 0) return -1;

    buf->width = width;
    buf->height = height;
    buf->pitch = creq.pitch;
    buf->handle = creq.handle;
    buf->size = creq.size;

    if (drmModeAddFB(fd, width, height, 24, 32, buf->pitch, buf->handle, &buf->fb_id) < 0) return -1;

    struct drm_mode_map_dumb mreq = { .handle = buf->handle };
    if (drmIoctl(fd, DRM_IOCTL_MODE_MAP_DUMB, &mreq) < 0) return -1;

    buf->vaddr = mmap(NULL, buf->size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, mreq.offset);
    if (buf->vaddr == MAP_FAILED) return -1;

    return 0;
}

static void page_flip_cb(int fd, unsigned int seq, unsigned int tv_sec, unsigned int tv_usec, unsigned int crtc_id, void *data) {
    struct kms_context *ctx = (struct kms_context *)data;
    ctx->waiting_for_flip = 0;
}

int main(void) {
    struct kms_context ctx = {0};
    ctx.fd = open("/dev/dri/card0", O_RDWR | O_CLOEXEC);
    if (ctx.fd < 0) {
        perror("Не вдалося відкрити /dev/dri/card0");
        return 1;
    }

    /* Обов'язкове включення Atomic та Universal Planes capabilities */
    if (drmSetClientCap(ctx.fd, DRM_CLIENT_CAP_ATOMIC, 1) != 0 ||
        drmSetClientCap(ctx.fd, DRM_CLIENT_CAP_UNIVERSAL_PLANES, 1) != 0) {
        fprintf(stderr, "Atomic KMS не підтримується ядерним драйвером\n");
        close(ctx.fd);
        return 1;
    }

    drmModeResPtr res = drmModeGetResources(ctx.fd);
    drmModeConnectorPtr conn = NULL;
    for (int i = 0; i < res->count_connectors; i++) {
        conn = drmModeGetConnector(ctx.fd, res->connectors[i]);
        if (conn && conn->connection == DRM_MODE_CONNECTED && conn->count_modes > 0) {
            ctx.conn_id = conn->connector_id;
            ctx.mode = conn->modes[0]; // Обираємо перший відданий монітором режим
            break;
        }
        if (conn) drmModeFreeConnector(conn);
    }

    if (!ctx.conn_id) {
        fprintf(stderr, "Підключених моніторів не знайдено\n");
        return 1;
    }

    ctx.crtc_id = res->crtcs[0];
    ctx.crtc_index = 0;
    drmModeFreeResources(res);

    drmModePlaneResPtr planes = drmModeGetPlaneResources(ctx.fd);
    for (uint32_t i = 0; i < planes->count_planes; i++) {
        drmModePlanePtr plane = drmModeGetPlane(ctx.fd, planes->planes[i]);
        if (plane && (plane->possible_crtcs & (1 << ctx.crtc_index))) {
            ctx.plane_id = plane->plane_id;
            drmModeFreePlane(plane);
            break;
        }
        if (plane) drmModeFreePlane(plane);
    }
    drmModeFreePlaneResources(planes);

    /* Зчитування ID властивостей для об'єкта Plane */
    ctx.prop_fb_id   = get_property_id(ctx.fd, ctx.plane_id, DRM_MODE_OBJECT_PLANE, "FB_ID");
    ctx.prop_crtc_id = get_property_id(ctx.fd, ctx.plane_id, DRM_MODE_OBJECT_PLANE, "CRTC_ID");
    ctx.prop_crtc_w  = get_property_id(ctx.fd, ctx.plane_id, DRM_MODE_OBJECT_PLANE, "CRTC_W");
    ctx.prop_crtc_h  = get_property_id(ctx.fd, ctx.plane_id, DRM_MODE_OBJECT_PLANE, "CRTC_H");
    ctx.prop_src_w   = get_property_id(ctx.fd, ctx.plane_id, DRM_MODE_OBJECT_PLANE, "SRC_W");
    ctx.prop_src_h   = get_property_id(ctx.fd, ctx.plane_id, DRM_MODE_OBJECT_PLANE, "SRC_H");

    /* Створення двох Dumb-буферів під розмір відеорежиму */
    create_dumb_buffer(ctx.fd, &ctx.buffers[0], ctx.mode.hdisplay, ctx.mode.vdisplay);
    create_dumb_buffer(ctx.fd, &ctx.buffers[1], ctx.mode.hdisplay, ctx.mode.vdisplay);

    /* Заповнення буферів тестовими кольорами */
    memset(ctx.buffers[0].vaddr, 0xFF, ctx.buffers[0].size); // Білий кадр
    memset(ctx.buffers[1].vaddr, 0x7F, ctx.buffers[1].size); // Сірий кадр

    drmEventContext evctx = {
        .version = DRM_EVENT_CONTEXT_VERSION,
        .page_flip_handler2 = page_flip_cb
    };

    /* Основний асинхронний цикл перемикання кадрів (300 кадрів) */
    for (int frame = 0; frame < 300; frame++) {
        ctx.current_buf ^= 1;
        struct buffer_t *buf = &ctx.buffers[ctx.current_buf];

        drmModeAtomicReqPtr req = drmModeAtomicAlloc();
        drmModeAtomicAddProperty(req, ctx.plane_id, ctx.prop_fb_id, buf->fb_id);
        drmModeAtomicAddProperty(req, ctx.plane_id, ctx.prop_crtc_id, ctx.crtc_id);
        drmModeAtomicAddProperty(req, ctx.plane_id, ctx.prop_crtc_w, buf->width);
        drmModeAtomicAddProperty(req, ctx.plane_id, ctx.prop_crtc_h, buf->height);
        drmModeAtomicAddProperty(req, ctx.plane_id, ctx.prop_src_w, buf->width << 16);
        drmModeAtomicAddProperty(req, ctx.plane_id, ctx.prop_src_h, buf->height << 16);

        ctx.waiting_for_flip = 1;
        uint32_t flags = DRM_MODE_ATOMIC_NONBLOCK | DRM_MODE_PAGE_FLIP_EVENT;
        int ret = drmModeAtomicCommit(ctx.fd, req, flags, &ctx);
        drmModeAtomicFree(req);

        if (ret < 0) {
            perror("Помилка виконання drmModeAtomicCommit");
            break;
        }

        /* Очікування сигналу VBlank від ядра через poll() */
        while (ctx.waiting_for_flip) {
            struct pollfd pfd = { .fd = ctx.fd, .events = POLLIN };
            if (poll(&pfd, 1, -1) > 0) {
                drmHandleEvent(ctx.fd, &evctx);
            }
        }
    }

    close(ctx.fd);
    return 0;
}
