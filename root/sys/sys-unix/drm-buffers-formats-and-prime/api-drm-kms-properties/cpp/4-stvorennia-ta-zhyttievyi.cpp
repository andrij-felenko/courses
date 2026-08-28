// C++: RAII обгортка для двійкового блоку пам'яті ядра
template <typename T>
class PropertyBlob {
    int fd_;
    uint32_t id_{0};
public:
    PropertyBlob(int fd, const T& data) : fd_(fd) {
        if (::drmModeCreatePropertyBlob(fd_, &data, sizeof(T), &id_) != 0) {
            throw std::runtime_error("Не вдалося створити DRM Property Blob у ядрі");
        }
    }
    ~PropertyBlob() {
        if (id_) ::drmModeDestroyPropertyBlob(fd_, id_);
    }
    [[nodiscard]] uint32_t id() const noexcept { return id_; }
};
