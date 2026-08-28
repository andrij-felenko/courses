#include <iostream>
#include <vector>
#include <span>
#include <system_error>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <poll.h>
#include <linux/videodev2.h>

class M2MScalerDevice {
public:
    explicit M2MScalerDevice(const std::string &dev_path) {
        fd_ = ::open(dev_path.c_str(), O_RDWR | O_NONBLOCK);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити пристрій M2M");
        }
    }

    ~M2MScalerDevice() {
        stop_streaming();
        unmap_buffers();
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    // Заборона копіювання для збереження коректності володіння дескриптором
    M2MScalerDevice(const M2MScalerDevice &) = delete;
    M2MScalerDevice &operator=(const M2MScalerDevice &) = delete;

    void configure_formats(uint32_t src_w, uint32_t src_h, uint32_t dst_w, uint32_t dst_h) {
        v4l2_format fmt_out{};
        fmt_out.type = V4L2_BUF_TYPE_VIDEO_OUTPUT;
        fmt_out.fmt.pix.width = src_w;
        fmt_out.fmt.pix.height = src_h;
        fmt_out.fmt.pix.pixelformat = V4L2_PIX_FMT_YUYV;
        fmt_out.fmt.pix.field = V4L2_FIELD_NONE;
        send_ioctl(VIDIOC_S_FMT, &fmt_out, "Помилка встановлення формату OUTPUT");

        v4l2_format fmt_cap{};
        fmt_cap.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        fmt_cap.fmt.pix.width = dst_w;
        fmt_cap.fmt.pix.height = dst_h;
        fmt_cap.fmt.pix.pixelformat = V4L2_PIX_FMT_NV12;
        fmt_cap.fmt.pix.field = V4L2_FIELD_NONE;
        send_ioctl(VIDIOC_S_FMT, &fmt_cap, "Помилка встановлення формату CAPTURE");
    }

    void allocate_and_mmap() {
        // Виділення та відображення вхідного буфера OUTPUT
        v4l2_requestbuffers req_out{};
        req_out.count = 1;
        req_out.type = V4L2_BUF_TYPE_VIDEO_OUTPUT;
        req_out.memory = V4L2_MEMORY_MMAP;
        send_ioctl(VIDIOC_REQBUFS, &req_out, "Помилка REQBUFS OUTPUT");

        v4l2_buffer buf_out{};
        buf_out.type = V4L2_BUF_TYPE_VIDEO_OUTPUT;
        buf_out.memory = V4L2_MEMORY_MMAP;
        buf_out.index = 0;
        send_ioctl(VIDIOC_QUERYBUF, &buf_out, "Помилка QUERYBUF OUTPUT");

        out_len_ = buf_out.length;
        out_ptr_ = ::mmap(nullptr, out_len_, PROT_READ | PROT_WRITE, MAP_SHARED, fd_, buf_out.m.offset);
        if (out_ptr_ == MAP_FAILED) {
            throw std::system_error(errno, std::generic_category(), "Помилка mmap OUTPUT");
        }

        // Виділення та відображення вихідного буфера CAPTURE
        v4l2_requestbuffers req_cap{};
        req_cap.count = 1;
        req_cap.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        req_cap.memory = V4L2_MEMORY_MMAP;
        send_ioctl(VIDIOC_REQBUFS, &req_cap, "Помилка REQBUFS CAPTURE");

        v4l2_buffer buf_cap{};
        buf_cap.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        buf_cap.memory = V4L2_MEMORY_MMAP;
        buf_cap.index = 0;
        send_ioctl(VIDIOC_QUERYBUF, &buf_cap, "Помилка QUERYBUF CAPTURE");

        cap_len_ = buf_cap.length;
        cap_ptr_ = ::mmap(nullptr, cap_len_, PROT_READ | PROT_WRITE, MAP_SHARED, fd_, buf_cap.m.offset);
        if (cap_ptr_ == MAP_FAILED) {
            throw std::system_error(errno, std::generic_category(), "Помилка mmap CAPTURE");
        }
    }

    void process_single_frame() {
        // Заповнення вхідного буфера тестовими даними
        std::memset(out_ptr_, 0x7F, out_len_);

        v4l2_buffer buf_out{};
        buf_out.type = V4L2_BUF_TYPE_VIDEO_OUTPUT;
        buf_out.memory = V4L2_MEMORY_MMAP;
        buf_out.index = 0;
        buf_out.bytesused = out_len_;
        send_ioctl(VIDIOC_QBUF, &buf_out, "Помилка QBUF OUTPUT");

        v4l2_buffer buf_cap{};
        buf_cap.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        buf_cap.memory = V4L2_MEMORY_MMAP;
        buf_cap.index = 0;
        send_ioctl(VIDIOC_QBUF, &buf_cap, "Помилка QBUF CAPTURE");

        v4l2_buf_type type_out = V4L2_BUF_TYPE_VIDEO_OUTPUT;
        v4l2_buf_type type_cap = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        send_ioctl(VIDIOC_STREAMON, &type_out, "Помилка STREAMON OUTPUT");
        send_ioctl(VIDIOC_STREAMON, &type_cap, "Помилка STREAMON CAPTURE");
        streaming_ = true;

        pollfd pfd{fd_, POLLIN, 0};
        int ret = ::poll(&pfd, 1, 2000);
        if (ret <= 0) {
            throw std::runtime_error("Апаратний блок не відповів за відведений тайм-аут");
        }

        send_ioctl(VIDIOC_DQBUF, &buf_cap, "Помилка DQBUF CAPTURE");
        std::cout << "C++: Кадр масштабовано! Отримано " << buf_cap.bytesused << " байтів NV12.\n";

        send_ioctl(VIDIOC_DQBUF, &buf_out, "Помилка DQBUF OUTPUT");
    }

private:
    void send_ioctl(unsigned long request, void *arg, const char *err_msg) {
        int r;
        do {
            r = ::ioctl(fd_, request, arg);
        } while (r == -1 && errno == EINTR);

        if (r < 0) {
            throw std::system_error(errno, std::generic_category(), err_msg);
        }
    }

    void stop_streaming() noexcept {
        if (streaming_ && fd_ >= 0) {
            v4l2_buf_type type_out = V4L2_BUF_TYPE_VIDEO_OUTPUT;
            v4l2_buf_type type_cap = V4L2_BUF_TYPE_VIDEO_CAPTURE;
            ::ioctl(fd_, VIDIOC_STREAMOFF, &type_out);
            ::ioctl(fd_, VIDIOC_STREAMOFF, &type_cap);
            streaming_ = false;
        }
    }

    void unmap_buffers() noexcept {
        if (out_ptr_ && out_ptr_ != MAP_FAILED) {
            ::munmap(out_ptr_, out_len_);
            out_ptr_ = nullptr;
        }
        if (cap_ptr_ && cap_ptr_ != MAP_FAILED) {
            ::munmap(cap_ptr_, cap_len_);
            cap_ptr_ = nullptr;
        }
    }

    int fd_{-1};
    void *out_ptr_{nullptr};
    size_t out_len_{0};
    void *cap_ptr_{nullptr};
    size_t cap_len_{0};
    bool streaming_{false};
};

int main(int argc, char **argv) {
    try {
        const std::string dev = (argc > 1) ? argv[1] : "/dev/video10";
        M2MScalerDevice scaler(dev);
        scaler.configure_formats(1920, 1080, 640, 480);
        scaler.allocate_and_mmap();
        scaler.process_single_frame();
    } catch (const std::exception &ex) {
        std::cerr << "Помилка: " << ex.what() << '\n';
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
