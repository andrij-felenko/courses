namespace dataflow {

class FrameHandle {
public:
    FrameHandle() noexcept = default;
    FrameHandle(Engine* engine, FrameId id) noexcept : engine_(engine), id_(id) {}
    ~FrameHandle() {
        if (engine_ && id_ != 0) {
            release();
        }
    }

    FrameHandle(const FrameHandle&) = delete;
    FrameHandle& operator=(const FrameHandle&) = delete;
    FrameHandle(FrameHandle&& other) noexcept : engine_(other.engine_), id_(other.id_) {
        other.engine_ = nullptr;
        other.id_ = 0;
    }

    [[nodiscard]] FrameId id() const noexcept { return id_; }

private:
    void release() noexcept;
    Engine* engine_{nullptr};
    FrameId id_{0};
};

} // namespace dataflow
