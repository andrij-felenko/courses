#include <xf86drm.h>
#include <xf86drmMode.h>
#include <drm_fourcc.h>
#include <system_error>
#include <array>

uint32_t fb_id = 0;
std::array<uint32_t, 4> handles{ static_cast<uint32_t>(dmabuf_fd), 0, 0, 0 };
std::array<uint32_t, 4> pitches{ 1920 * 2, 0, 0, 0 };
std::array<uint32_t, 4> offsets{ 0, 0, 0, 0 };

if (::drmModeAddFB2(drm_fd, 1920, 1080, DRM_FORMAT_UYVY,
                    handles.data(), pitches.data(), offsets.data(), &fb_id, 0) < 0) {
    throw std::system_error(errno, std::generic_category(), "drmModeAddFB2 failed");
}
::drmModePageFlip(drm_fd, crtc_id, fb_id, DRM_MODE_PAGE_FLIP_EVENT, nullptr);
