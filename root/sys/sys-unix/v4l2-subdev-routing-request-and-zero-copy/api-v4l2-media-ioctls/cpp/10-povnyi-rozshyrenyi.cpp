#include <iostream>
#include <vector>
#include <string>
#include <system_error>
#include <cstdint>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <poll.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <linux/media.h>
#include <linux/v4l2-subdev.h>
#include <linux/videodev2.h>

class ScopedFd {
    int fd_{-1};
public:
    explicit ScopedFd(int fd = -1) : fd_(fd) {}
    ~ScopedFd() { reset(); }

    ScopedFd(const ScopedFd&) = delete;
    ScopedFd& operator=(const ScopedFd&) = delete;

    ScopedFd(ScopedFd&& other) noexcept : fd_(other.fd_) { other.fd_ = -1; }
    ScopedFd& operator=(ScopedFd&& other) noexcept {
        if (this != &other) {
            reset();
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }
};

class MmappedBuffer {
    void* start_{MAP_FAILED};
    size_t length_{0};
    ScopedFd dbuf_fd_;

public:
    MmappedBuffer() = default;
    MmappedBuffer(void* start, size_t length, ScopedFd dbuf_fd)
        : start_(start), length_(length), dbuf_fd_(std::move(dbuf_fd)) {}

    ~MmappedBuffer() {
        if (start_ != MAP_FAILED && start_ != nullptr) {
            ::munmap(start_, length_);
        }
    }

    MmappedBuffer(const MmappedBuffer&) = delete;
    MmappedBuffer& operator=(const MmappedBuffer&) = delete;

    MmappedBuffer(MmappedBuffer&&) noexcept = default;
    MmappedBuffer& operator=(MmappedBuffer&&) noexcept = default;

    [[nodiscard]] void* data() const noexcept { return start_; }
    [[nodiscard]] size_t size() const noexcept { return length_; }
    [[nodiscard]] int dmabuf_fd() const noexcept { return dbuf_fd_.get(); }
};

class MediaIoctlPipeline {
    ScopedFd media_fd_;
    ScopedFd subdev_fd_;
    ScopedFd video_fd_;
    std::vector<MmappedBuffer> buffers_;

    static void check_ioctl(int res, const std::string& msg) {
        if (res < 0) {
            throw std::system_error(errno, std::generic_category(), msg);
        }
    }

public:
    void init(const std::string& media_dev, const std::string& subdev_dev, const std::string& video_dev) {
        media_fd_.reset(::open(media_dev.c_str(), O_RDWR));
        check_ioctl(media_fd_.valid() ? 0 : -1, "Open " + media_dev);

        subdev_fd_.reset(::open(subdev_dev.c_str(), O_RDWR));
        check_ioctl(subdev_fd_.valid() ? 0 : -1, "Open " + subdev_dev);

        video_fd_.reset(::open(video_dev.c_str(), O_RDWR | O_NONBLOCK));
        check_ioctl(video_fd_.valid() ? 0 : -1, "Open " + video_dev);
    }

    void configure_pipeline() {
        v4l2_subdev_format sfmt{};
        sfmt.pad = 0;
        sfmt.which = V4L2_SUBDEV_FORMAT_ACTIVE;
        sfmt.format.width = 1920;
        sfmt.format.height = 1080;
        sfmt.format.code = MEDIA_BUS_FMT_UYVY8_2X8;
        sfmt.format.field = V4L2_FIELD_NONE;
        check_ioctl(::ioctl(subdev_fd_.get(), VIDIOC_SUBDEV_S_FMT, &sfmt), "VIDIOC_SUBDEV_S_FMT");

        v4l2_format vfmt{};
        vfmt.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        vfmt.fmt.pix.width = 1920;
        vfmt.fmt.pix.height = 1080;
        vfmt.fmt.pix.pixelformat = V4L2_PIX_FMT_UYVY;
        vfmt.fmt.pix.field = V4L2_FIELD_NONE;
        check_ioctl(::ioctl(video_fd_.get(), VIDIOC_S_FMT, &vfmt), "VIDIOC_S_FMT");

        v4l2_requestbuffers req{};
        req.count = 4;
        req.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        req.memory = V4L2_MEMORY_MMAP;
        check_ioctl(::ioctl(video_fd_.get(), VIDIOC_REQBUFS, &req), "VIDIOC_REQBUFS");

        buffers_.reserve(req.count);

        for (uint32_t i = 0; i < req.count; ++i) {
            v4l2_buffer buf{};
            buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
            buf.memory = V4L2_MEMORY_MMAP;
            buf.index = i;
            check_ioctl(::ioctl(video_fd_.get(), VIDIOC_QUERYBUF, &buf), "VIDIOC_QUERYBUF");

            void* ptr = ::mmap(nullptr, buf.length, PROT_READ | PROT_WRITE, MAP_SHARED, video_fd_.get(), buf.m.offset);
            if (ptr == MAP_FAILED) {
                throw std::system_error(errno, std::generic_category(), "mmap failed");
            }

            v4l2_exportbuffer expbuf{};
            expbuf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
            expbuf.index = i;
            expbuf.flags = O_CLOEXEC | O_RDWR;
            check_ioctl(::ioctl(video_fd_.get(), VIDIOC_EXPBUF, &expbuf), "VIDIOC_EXPBUF");

            buffers_.emplace_back(ptr, buf.length, ScopedFd(expbuf.fd));
        }
    }

    void stream_one_frame() {
        for (uint32_t i = 0; i < buffers_.size(); ++i) {
            v4l2_buffer buf{};
            buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
            buf.memory = V4L2_MEMORY_MMAP;
            buf.index = i;
            check_ioctl(::ioctl(video_fd_.get(), VIDIOC_QBUF, &buf), "VIDIOC_QBUF");
        }

        v4l2_buf_type stype = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        check_ioctl(::ioctl(video_fd_.get(), VIDIOC_STREAMON, &stype), "VIDIOC_STREAMON");

        pollfd pfd{};
        pfd.fd = video_fd_.get();
        pfd.events = POLLIN;

        int poll_res = ::poll(&pfd, 1, 2000);
        if (poll_res > 0 && (pfd.revents & POLLIN)) {
            v4l2_buffer dqbuf{};
            dqbuf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
            dqbuf.memory = V4L2_MEMORY_MMAP;
            check_ioctl(::ioctl(video_fd_.get(), VIDIOC_DQBUF, &dqbuf), "VIDIOC_DQBUF");

            std::cout << "[C++] Frame sequence: " << dqbuf.sequence << ", payload: " << dqbuf.bytesused << " bytes\n";
        } else {
            std::cerr << "[C++] Timeout waiting for frame\n";
        }

        check_ioctl(::ioctl(video_fd_.get(), VIDIOC_STREAMOFF, &stype), "VIDIOC_STREAMOFF");
    }
};

int main() {
    try {
        MediaIoctlPipeline app;
        app.init("/dev/media0", "/dev/v4l2-subdev0", "/dev/video0");
        app.configure_pipeline();
        app.stream_one_frame();
    } catch (const std::exception& ex) {
        std::cerr << "Pipeline error: " << ex.what() << "\n";
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
