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
#include <linux/dma-buf.h>

// RAII обгортка для файлового дескриптора пристрою
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

// RAII обгортка для відображеного в пам'ять V4L2 буфера
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

class V4L2ZeroCopyPipeline {
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
    void open_devices(const std::string& media_dev,
                      const std::string& subdev_dev,
                      const std::string& video_dev) {
        media_fd_.reset(::open(media_dev.c_str(), O_RDWR));
        check_ioctl(media_fd_.valid() ? 0 : -1, "Відкриття " + media_dev);

        subdev_fd_.reset(::open(subdev_dev.c_str(), O_RDWR));
        check_ioctl(subdev_fd_.valid() ? 0 : -1, "Відкриття " + subdev_dev);

        video_fd_.reset(::open(video_dev.c_str(), O_RDWR | O_NONBLOCK));
        check_ioctl(video_fd_.valid() ? 0 : -1, "Відкриття " + video_dev);
    }

    void configure_subdev_format(uint32_t pad, uint32_t width, uint32_t height, uint32_t mbus_code) {
        struct v4l2_subdev_format fmt{};
        fmt.pad = pad;
        fmt.which = V4L2_SUBDEV_FORMAT_ACTIVE;
        fmt.format.width = width;
        fmt.format.height = height;
        fmt.format.code = mbus_code;
        fmt.format.field = V4L2_FIELD_NONE;

        check_ioctl(::ioctl(subdev_fd_.get(), VIDIOC_SUBDEV_S_FMT, &fmt), "VIDIOC_SUBDEV_S_FMT");
        std::cout << "[V4L2 C++] Subdev pad format: " << fmt.format.width << "x" << fmt.format.height << "\n";
    }

    void setup_buffers_and_export(size_t buffer_count) {
        struct v4l2_format vfmt{};
        vfmt.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        vfmt.fmt.pix.width = 1920;
        vfmt.fmt.pix.height = 1080;
        vfmt.fmt.pix.pixelformat = V4L2_PIX_FMT_UYVY;
        vfmt.fmt.pix.field = V4L2_FIELD_NONE;

        check_ioctl(::ioctl(video_fd_.get(), VIDIOC_S_FMT, &vfmt), "VIDIOC_S_FMT");

        struct v4l2_requestbuffers req{};
        req.count = static_cast<uint32_t>(buffer_count);
        req.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        req.memory = V4L2_MEMORY_MMAP;

        check_ioctl(::ioctl(video_fd_.get(), VIDIOC_REQBUFS, &req), "VIDIOC_REQBUFS");
        buffers_.reserve(req.count);

        for (uint32_t i = 0; i < req.count; ++i) {
            struct v4l2_buffer buf{};
            buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
            buf.memory = V4L2_MEMORY_MMAP;
            buf.index = i;

            check_ioctl(::ioctl(video_fd_.get(), VIDIOC_QUERYBUF, &buf), "VIDIOC_QUERYBUF");

            void* ptr = ::mmap(nullptr, buf.length, PROT_READ | PROT_WRITE, MAP_SHARED, video_fd_.get(), buf.m.offset);
            if (ptr == MAP_FAILED) {
                throw std::system_error(errno, std::generic_category(), "mmap бувера");
            }

            struct v4l2_exportbuffer expbuf{};
            expbuf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
            expbuf.index = i;
            expbuf.flags = O_CLOEXEC | O_RDWR;

            check_ioctl(::ioctl(video_fd_.get(), VIDIOC_EXPBUF, &expbuf), "VIDIOC_EXPBUF");

            buffers_.emplace_back(ptr, buf.length, ScopedFd(expbuf.fd));
            std::cout << "[V4L2 C++] Буфер " << i << " mmapped (" << buf.length
                      << " байт), DMABUF FD: " << expbuf.fd << "\n";
        }
    }

    void capture_frame() {
        for (uint32_t i = 0; i < buffers_.size(); ++i) {
            struct v4l2_buffer buf{};
            buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
            buf.memory = V4L2_MEMORY_MMAP;
            buf.index = i;
            check_ioctl(::ioctl(video_fd_.get(), VIDIOC_QBUF, &buf), "VIDIOC_QBUF");
        }

        enum v4l2_buf_type type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        check_ioctl(::ioctl(video_fd_.get(), VIDIOC_STREAMON, &type), "VIDIOC_STREAMON");

        pollfd pfd{};
        pfd.fd = video_fd_.get();
        pfd.events = POLLIN;

        int poll_res = ::poll(&pfd, 1, 2000);
        if (poll_res > 0 && (pfd.revents & POLLIN)) {
            struct v4l2_buffer dqbuf{};
            dqbuf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
            dqbuf.memory = V4L2_MEMORY_MMAP;
            check_ioctl(::ioctl(video_fd_.get(), VIDIOC_DQBUF, &dqbuf), "VIDIOC_DQBUF");

            std::cout << "[V4L2 C++] Захоплено кадр " << dqbuf.sequence
                      << " розміром " << dqbuf.bytesused << " байт\n";

            dma_buf_sync dsync{};
            dsync.flags = DMA_BUF_SYNC_START | DMA_BUF_SYNC_READ;
            check_ioctl(::ioctl(buffers_[dqbuf.index].dmabuf_fd(), DMABUF_IOCTL_SYNC, &dsync), "DMABUF_SYNC START");

            std::cout << "[V4L2 C++] CPU Sync OK\n";

            dsync.flags = DMA_BUF_SYNC_END | DMA_BUF_SYNC_READ;
            check_ioctl(::ioctl(buffers_[dqbuf.index].dmabuf_fd(), DMABUF_IOCTL_SYNC, &dsync), "DMABUF_SYNC END");
        } else {
            std::cerr << "[V4L2 C++] Таймаут очікування кадру\n";
        }

        check_ioctl(::ioctl(video_fd_.get(), VIDIOC_STREAMOFF, &type), "VIDIOC_STREAMOFF");
    }
};

int main() {
    try {
        V4L2ZeroCopyPipeline pipeline;
        pipeline.open_devices("/dev/media0", "/dev/v4l2-subdev0", "/dev/video0");
        pipeline.configure_subdev_format(0, 1920, 1080, MEDIA_BUS_FMT_UYVY8_2X8);
        pipeline.setup_buffers_and_export(4);
        pipeline.capture_frame();
    } catch (const std::exception& ex) {
        std::cerr << "Помилка конвеєра: " << ex.what() << "\n";
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
