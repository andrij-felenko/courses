// Ідіоматична RAII-обгортка для буфера та MR у C++20
#include <infiniband/verbs.h>
#include <memory>
#include <span>
#include <vector>
#include <stdexcept>

class RegisteredBuffer {
public:
    RegisteredBuffer(ibv_pd* pd, size_t size, int access_flags)
        : data_(size) {
        mr_ = ibv_reg_mr(pd, data_.data(), data_.size(), access_flags);
        if (!mr_) throw std::runtime_error("Помилка реєстрації пам'яті ibv_reg_mr");
    }

    ~RegisteredBuffer() noexcept {
        if (mr_) ibv_dereg_mr(mr_);
    }

    RegisteredBuffer(const RegisteredBuffer&) = delete;
    RegisteredBuffer& operator=(const RegisteredBuffer&) = delete;

    RegisteredBuffer(RegisteredBuffer&& o) noexcept
        : data_(std::move(o.data_)), mr_(o.mr_) {
        o.mr_ = nullptr;
    }

    [[nodiscard]] uint32_t lkey() const noexcept { return mr_->lkey; }
    [[nodiscard]] uint32_t rkey() const noexcept { return mr_->rkey; }
    [[nodiscard]] uint64_t remote_ptr() const noexcept {
        return reinterpret_cast<uint64_t>(data_.data());
    }
    [[nodiscard]] std::span<std::byte> bytes() noexcept {
        return std::span(reinterpret_cast<std::byte*>(data_.data()), data_.size());
    }

private:
    std::vector<char> data_;
    ibv_mr* mr_{nullptr};
};
