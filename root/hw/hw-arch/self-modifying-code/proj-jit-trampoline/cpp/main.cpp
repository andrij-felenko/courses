#include <iostream>
#include <vector>
#include <span>
#include <memory>
#include <expected>
#include <string>
#include <cstdint>
#include <cstring>
#include <sys/mman.h>
#include <unistd.h>

#if defined(__x86_64__) || defined(_M_X64)
#define ARCH_X86_64 1
#elif defined(__aarch64__) || defined(_M_ARM64)
#define ARCH_AARCH64 1
#else
#error "Непідтримувана процесорна архітектура для прямої генерації коду"
#endif

// RAII обгортка для керування пам'яттю JIT-блоків
class JitMemoryBlock {
public:
    enum class Protection {
        ReadWrite,
        ReadExecute
    };

    static std::expected<JitMemoryBlock, std::string> allocate(size_t min_size) {
        long page_size = sysconf(_SC_PAGESIZE);
        if (page_size <= 0) page_size = 4096;

        size_t alloc_size = (min_size + page_size - 1) & ~(page_size - 1);
        void* ptr = mmap(nullptr, alloc_size, PROT_READ | PROT_WRITE,
                         MAP_ANONYMOUS | MAP_PRIVATE, -1, 0);

        if (ptr == MAP_FAILED) {
            return std::unexpected("Не вдалося виділити пам'ять через mmap");
        }

        return JitMemoryBlock(static_cast<uint8_t*>(ptr), alloc_size);
    }

    ~JitMemoryBlock() noexcept {
        if (buffer_ && size_ > 0) {
            munmap(buffer_, size_);
        }
    }

    // Заборона копіювання об'єкта для запобігання подвійному звільненню
    JitMemoryBlock(const JitMemoryBlock&) = delete;
    JitMemoryBlock& operator=(const JitMemoryBlock&) = delete;

    // Підтримка семантики переміщення (Move Constructor / Move Assignment)
    JitMemoryBlock(JitMemoryBlock&& other) noexcept
        : buffer_(other.buffer_), size_(other.size_), code_len_(other.code_len_) {
        other.buffer_ = nullptr;
        other.size_ = 0;
        other.code_len_ = 0;
    }

    JitMemoryBlock& operator=(JitMemoryBlock&& other) noexcept {
        if (this != &other) {
            if (buffer_ && size_ > 0) munmap(buffer_, size_);
            buffer_ = other.buffer_;
            size_ = other.size_;
            code_len_ = other.code_len_;
            other.buffer_ = nullptr;
            other.size_ = 0;
            other.code_len_ = 0;
        }
        return *this;
    }

    std::expected<void, std::string> set_protection(Protection prot) noexcept {
        int flags = (prot == Protection::ReadWrite)
                    ? (PROT_READ | PROT_WRITE)
                    : (PROT_READ | PROT_EXEC);

        if (mprotect(buffer_, size_, flags) != 0) {
            return std::unexpected("Помилка зміни прав доступу сторінки mprotect");
        }
        return {};
    }

    void sync_cache() noexcept {
        __builtin___clear_cache(reinterpret_cast<char*>(buffer_),
                                reinterpret_cast<char*>(buffer_ + code_len_));
    }

    std::span<uint8_t> as_writable_span() noexcept {
        return std::span<uint8_t>(buffer_, size_);
    }

    template <typename FuncSignature>
    FuncSignature get_entry_point() const noexcept {
        return reinterpret_cast<FuncSignature>(buffer_);
    }

    void set_code_length(size_t len) noexcept { code_len_ = len; }
    size_t size() const noexcept { return size_; }
    size_t code_length() const noexcept { return code_len_; }

private:
    explicit JitMemoryBlock(uint8_t* buf, size_t sz) noexcept
        : buffer_(buf), size_(sz), code_len_(0) {}

    uint8_t* buffer_{nullptr};
    size_t size_{0};
    size_t code_len_{0};
};

// Типобезпечний клас генератора коду лінійних виразів
class LinearJitCompiler {
public:
    using FuncType = int32_t (*)(int32_t);

    static std::expected<void, std::string> compile(JitMemoryBlock& mem,
                                                   int32_t multiplier,
                                                   int32_t addend) {
        auto span = mem.as_writable_span();

#if defined(ARCH_X86_64)
        const uint8_t code[] = {
            0x69, 0xFF,
            static_cast<uint8_t>(multiplier & 0xFF),
            static_cast<uint8_t>((multiplier >> 8) & 0xFF),
            static_cast<uint8_t>((multiplier >> 16) & 0xFF),
            static_cast<uint8_t>((multiplier >> 24) & 0xFF),
            0x81, 0xC7,
            static_cast<uint8_t>(addend & 0xFF),
            static_cast<uint8_t>((addend >> 8) & 0xFF),
            static_cast<uint8_t>((addend >> 16) & 0xFF),
            static_cast<uint8_t>((addend >> 24) & 0xFF),
            0x89, 0xF8,
            0xC3
        };
        size_t len = sizeof(code);
#elif defined(ARCH_AARCH64)
        const uint32_t imm_mul = static_cast<uint32_t>(multiplier) & 0xFFFF;
        const uint32_t imm_add = static_cast<uint32_t>(addend) & 0xFFFF;

        const uint32_t code[] = {
            0x52800000 | (imm_mul << 5) | 1,
            0x1B017C00,
            0x52800000 | (imm_add << 5) | 1,
            0x0B010000,
            0xD65F03C0
        };
        size_t len = sizeof(code);
#endif

        if (len > span.size()) {
            return std::unexpected("Розмір виділеного буфера менший за довжину коду");
        }

        std::memcpy(span.data(), code, len);
        mem.set_code_length(len);

        auto prot_res = mem.set_protection(JitMemoryBlock::Protection::ReadExecute);
        if (!prot_res) return prot_res;

        mem.sync_cache();
        return {};
    }

    static std::expected<void, std::string> patch_multiplier(JitMemoryBlock& mem,
                                                            int32_t new_multiplier) {
        auto prot_rw = mem.set_protection(JitMemoryBlock::Protection::ReadWrite);
        if (!prot_rw) return prot_rw;

        auto span = mem.as_writable_span();
#if defined(ARCH_X86_64)
        span[2] = static_cast<uint8_t>(new_multiplier & 0xFF);
        span[3] = static_cast<uint8_t>((new_multiplier >> 8) & 0xFF);
        span[4] = static_cast<uint8_t>((new_multiplier >> 16) & 0xFF);
        span[5] = static_cast<uint8_t>((new_multiplier >> 24) & 0xFF);
#elif defined(ARCH_AARCH64)
        uint32_t* patch_ptr = reinterpret_cast<uint32_t*>(span.data());
        uint32_t imm = static_cast<uint32_t>(new_multiplier) & 0xFFFF;
        patch_ptr[0] = 0x52800000 | (imm << 5) | 1;
#endif

        auto prot_rx = mem.set_protection(JitMemoryBlock::Protection::ReadExecute);
        if (!prot_rx) return prot_rx;

        mem.sync_cache();
        return {};
    }
};

int main() {
    auto mem_alloc = JitMemoryBlock::allocate(4096);
    if (!mem_alloc) {
        std::cerr << "Помилка виділення пам'яті: " << mem_alloc.error() << '\n';
        return EXIT_FAILURE;
    }

    auto& jit_mem = *mem_alloc;

    std::cout << "1. C++ JIT: компіляція лінійної функції f(x) = x * 10 + 7\n";
    auto comp_res = LinearJitCompiler::compile(jit_mem, 10, 7);
    if (!comp_res) {
        std::cerr << "Помилка компіляції коду: " << comp_res.error() << '\n';
        return EXIT_FAILURE;
    }

    auto func = jit_mem.get_entry_point<LinearJitCompiler::FuncType>();
    int32_t x = 5;
    int32_t res1 = func(x);
    std::cout << "   Результат f(" << x << ") = " << res1 << " (очікувано: 57)\n";

    std::cout << "2. C++ JIT: гаряче латання коефіцієнта f(x) = x * 100 + 7\n";
    auto patch_res = LinearJitCompiler::patch_multiplier(jit_mem, 100);
    if (!patch_res) {
        std::cerr << "Помилка модифікації інструкцій: " << patch_res.error() << '\n';
        return EXIT_FAILURE;
    }

    int32_t res2 = func(x);
    std::cout << "   Результат f(" << x << ") після оновлення = " << res2 << " (очікувано: 507)\n";

    std::cout << "3. Пам'ять гарантовано звільняється автоматичним деструктором RAII.\n";
    return EXIT_SUCCESS;
}
