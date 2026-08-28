#include <xf86drm.h>
#include <xf86drmMode.h>
#include <drm_fourcc.h>

uint32_t fb_id = 0;
uint32_t handles[4] = { (uint32_t)dmabuf_fd, 0, 0, 0 };
uint32_t pitches[4] = { 1920 * 2, 0, 0, 0 };
uint32_t offsets[4] = { 0, 0, 0, 0 };

if (drmModeAddFB2(drm_fd, 1920, 1080, DRM_FORMAT_UYVY,
                  handles, pitches, offsets, &fb_id, 0) == 0) {
    /* Атомарне перемикання площини дисплея (Atomic Commit) */
    drmModePageFlip(drm_fd, crtc_id, fb_id, DRM_MODE_PAGE_FLIP_EVENT, NULL);
}
