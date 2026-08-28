#include <iostream>
#include <vector>
#include <memory>
#include <span>
#include <stdexcept>
#include <string>
#include <format>
#include <cuda_runtime.h>

/* Безпечна обгортка перевірки помилок CUDA через винятки */
inline void check_cuda(cudaError_t result, const char *msg) {
    if (result != cudaSuccess) {
        throw std::runtime_error(std::string(msg) + ": " + cudaGetErrorString(result));
    }
}

/* RAII-керування потоком CUDA */
class CudaStream {
public:
    CudaStream() {
        check_cuda(cudaStreamCreateWithFlags(&stream_, cudaStreamNonBlocking),
                   "Не вдалося створити cudaStream");
    }
    ~CudaStream() noexcept {
        if (stream_) {
            cudaStreamDestroy(stream_);
        }
    }
    CudaStream(const CudaStream&) = delete;
    CudaStream& operator=(const CudaStream&) = delete;
    CudaStream(CudaStream&& other) noexcept : stream_(other.stream_) {
        other.stream_ = nullptr;
    }
    CudaStream& operator=(CudaStream&& other) noexcept {
        if (this != &other) {
            if (stream_) cudaStreamDestroy(stream_);
            stream_ = other.stream_;
            other.stream_ = nullptr;
        }
        return *this;
    }

    [[nodiscard]] cudaStream_t get() const noexcept { return stream_; }
    void synchronize() const {
        check_cuda(cudaStreamSynchronize(stream_), "Помилка синхронізації потоку");
    }

private:
    cudaStream_t stream_{nullptr};
};

/* RAII-буфер зафіксованої пам'яті хоста (Pinned Host Memory) */
template <typename T>
class PinnedBuffer {
public:
    explicit PinnedBuffer(size_t count) : count_(count) {
        check_cuda(cudaHostAlloc(reinterpret_cast<void**>(&ptr_),
                                 count_ * sizeof(T),
                                 cudaHostAllocDefault),
                   "Помилка виділення Pinned пам'яті");
    }
    ~PinnedBuffer() noexcept {
        if (ptr_) {
            cudaFreeHost(ptr_);
        }
    }
    PinnedBuffer(const PinnedBuffer&) = delete;
    PinnedBuffer& operator=(const PinnedBuffer&) = delete;
    PinnedBuffer(PinnedBuffer&& other) noexcept : ptr_(other.ptr_), count_(other.count_) {
        other.ptr_ = nullptr;
        other.count_ = 0;
    }
    PinnedBuffer& operator=(PinnedBuffer&& other) noexcept {
        if (this != &other) {
            if (ptr_) cudaFreeHost(ptr_);
            ptr_ = other.ptr_;
            count_ = other.count_;
            other.ptr_ = nullptr;
            other.count_ = 0;
        }
        return *this;
    }

    [[nodiscard]] T* data() noexcept { return ptr_; }
    [[nodiscard]] const T* data() const noexcept { return ptr_; }
    [[nodiscard]] size_t size() const noexcept { return count_; }
    [[nodiscard]] size_t bytes() const noexcept { return count_ * sizeof(T); }
    [[nodiscard]] std::span<T> span() noexcept { return std::span<T>(ptr_, count_); }

private:
    T* ptr_{nullptr};
    size_t count_{0};
};

/* RAII-буфер пам'яті пристрою (Device VRAM) */
template <typename T>
class DeviceBuffer {
public:
    explicit DeviceBuffer(size_t count) : count_(count) {
        check_cuda(cudaMalloc(reinterpret_cast<void**>(&ptr_), count_ * sizeof(T)),
                   "Помилка виділення VRAM пам'яті");
    }
    ~DeviceBuffer() noexcept {
        if (ptr_) {
            cudaFree(ptr_);
        }
    }
    DeviceBuffer(const DeviceBuffer&) = delete;
    DeviceBuffer& operator=(const DeviceBuffer&) = delete;
    DeviceBuffer(DeviceBuffer&& other) noexcept : ptr_(other.ptr_), count_(other.count_) {
        other.ptr_ = nullptr;
        other.count_ = 0;
    }
    DeviceBuffer& operator=(DeviceBuffer&& other) noexcept {
        if (this != &other) {
            if (ptr_) cudaFree(ptr_);
            ptr_ = other.ptr_;
            count_ = other.count_;
            other.ptr_ = nullptr;
            other.count_ = 0;
        }
        return *this;
    }

    [[nodiscard]] T* data() noexcept { return ptr_; }
    [[nodiscard]] const T* data() const noexcept { return ptr_; }
    [[nodiscard]] size_t size() const noexcept { return count_; }
    [[nodiscard]] size_t bytes() const noexcept { return count_ * sizeof(T); }

private:
    T* ptr_{nullptr};
    size_t count_{0};
};

/* Ядро CUDA */
__global__ void process_kernel_cpp(const float *in, float *out, float scale, int n) {
    int idx = blockDim.x * blockIdx.x + threadIdx.x;
    if (idx < n) {
        float val = in[idx];
        #pragma unroll
        for (int i = 0; i < 64; ++i) {
            val = val * scale + 0.001f;
        }
        out[idx] = val;
    }
}

int main() {
    try {
        constexpr size_t chunk_size = 1024 * 1024;
        constexpr size_t num_chunks = 8;
        constexpr size_t num_streams = 2;
        constexpr size_t total_elements = chunk_size * num_chunks;

        /* Виділення фіксованих буферів хоста з автоматичним вивільненням */
        PinnedBuffer<float> host_in(total_elements);
        PinnedBuffer<float> host_out(total_elements);

        auto in_span = host_in.span();
        for (size_t i = 0; i < in_span.size(); ++i) {
            in_span[i] = static_cast<float>(i % 100) * 0.01f;
        }

        /* Створення масиву подвійних буферів та потоків */
        std::vector<DeviceBuffer<float>> dev_in;
        std::vector<DeviceBuffer<float>> dev_out;
        std::vector<CudaStream> streams;

        dev_in.reserve(num_streams);
        dev_out.reserve(num_streams);
        streams.reserve(num_streams);

        for (size_t s = 0; s < num_streams; ++s) {
            dev_in.emplace_back(chunk_size);
            dev_out.emplace_back(chunk_size);
            streams.emplace_back();
        }

        dim3 block(256);
        dim3 grid((chunk_size + block.x - 1) / block.x);

        /* Конвеєрний запуск */
        for (size_t i = 0; i < num_chunks; ++i) {
            size_t s = i % num_streams;
            size_t offset = i * chunk_size;

            check_cuda(cudaMemcpyAsync(dev_in[s].data(),
                                       host_in.data() + offset,
                                       chunk_size * sizeof(float),
                                       cudaMemcpyHostToDevice,
                                       streams[s].get()),
                       "H2D копіювання зазнало невдачі");

            process_kernel_cpp<<<grid, block, 0, streams[s].get()>>>(
                dev_in[s].data(), dev_out[s].data(), 1.002f, static_cast<int>(chunk_size)
            );

            check_cuda(cudaMemcpyAsync(host_out.data() + offset,
                                       dev_out[s].data(),
                                       chunk_size * sizeof(float),
                                       cudaMemcpyDeviceToHost,
                                       streams[s].get()),
                       "D2H копіювання зазнало невдачі");
        }

        /* Синхронізація потоків */
        for (auto &stream : streams) {
            stream.synchronize();
        }

        std::cout << "C++ RAII конвеєрна обробка успішно завершена.\n";

    } catch (const std::exception &ex) {
        std::cerr << "Критична помилка: " << ex.what() << '\n';
        return 1;
    }

    return 0;
}
