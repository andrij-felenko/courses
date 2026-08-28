/* C++ RAII-обгортка для реєстрації існуючих контейнерів (std::vector) */
#include <cuda_runtime.h>
#include <span>
#include <stdexcept>

template <typename T>
class RegisteredHostSpan {
public:
    explicit RegisteredHostSpan(std::span<T> data_span, unsigned int flags = cudaHostRegisterDefault)
        : span_(data_span) {
        cudaError_t err = cudaHostRegister(span_.data(), span_.size_bytes(), flags);
        if (err != cudaSuccess) {
            throw std::runtime_error("cudaHostRegister failed");
        }
    }
    ~RegisteredHostSpan() noexcept {
        cudaHostUnregister(span_.data());
    }
    RegisteredHostSpan(const RegisteredHostSpan&) = delete;
    RegisteredHostSpan& operator=(const RegisteredHostSpan&) = delete;

    [[nodiscard]] std::span<T> span() const noexcept { return span_; }

private:
    std::span<T> span_;
};
