/* композитор: віддати кадр, який ще малюється */
int out_fence = -1;

drmModeAtomicAddProperty(req, plane_id, prop_in_fence_fd,  client_fence);
drmModeAtomicAddProperty(req, crtc_id,  prop_out_fence_ptr, (uint64_t)(uintptr_t)&out_fence);
drmModeAtomicCommit(fd, req, DRM_MODE_ATOMIC_NONBLOCK, NULL);

/* виклик уже повернувся; out_fence спрацює після реального перемикання кадру */
struct pollfd pfd = { .fd = out_fence, .events = POLLIN };
poll(&pfd, 1, 100);
close(out_fence);
