drm_mode_fb_cmd2 fb_cmd{};
fb_cmd.width = 1920;
fb_cmd.height = 1080;
fb_cmd.pixel_format = DRM_FORMAT_NV12; // FourCC NV12
fb_cmd.handles[0] = gem_handle_y;       // Диспетчер GEM для площини Y
fb_cmd.pitches[0] = 1920;              // Stride площини Y
fb_cmd.offsets[0] = 0;

fb_cmd.handles[1] = gem_handle_uv;      // Диспетчер GEM для площини UV
fb_cmd.pitches[1] = 1920;              // Stride площини UV
fb_cmd.offsets[1] = 1920 * 1080;       // Зсув до площини UV
