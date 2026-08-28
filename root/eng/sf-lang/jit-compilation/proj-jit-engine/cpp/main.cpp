#include <iostream>
#include <span>
#include <vector>
#include <cstdint>
#include <cstring>
#include <system_error>

#if defined(_WIN32) || defined(_WIN64)
#include <windows.h>
#else
#include <sys/mman.h>
#include <unistd.h>
#endif

// RAII-клас для суворого контролю стану та прав віртуальної сторінки
class ExecutableMemory {
public:
    enum class State {
        Writable,    // W=1, X=0 (дозволено генерацію коду)
        Executable,  // W=0, X=1 (дозволено виконання, запис заборонено)
        Freed        // Пам'ять повернуто операційній системі
    };

    explicit ExecutableMemory(size_t size = 4096) : size_(size), state_(State::Writable) {
#if defined(_WIN32) || defined(_WIN64)
        ptr_ = static_cast<uint8_t*>(VirtualAlloc(nullptr, size_, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE));
        if (!ptr_) {
            throw std::system_error(static_cast<int>(GetLastError()), std::system_category(), "VirtualAlloc failed");
        }
#else
        void* p = mmap(nullptr, size_, PROT_READ | PROT_WRITE, MAP_ANONYMOUS | MAP_PRIVATE, -1, 0);
        if (p == MAP_FAILED) {
            throw std::system_error(errno, std::generic_category(), "mmap failed");
        }
        ptr_ = static_cast<uint8_t*>(p);
#endif
    }

    ~ExecutableMemory() noexcept {
        release();
    }

    ExecutableMemory(const ExecutableMemory&) = delete;
    ExecutableMemory& operator=(const ExecutableMemory&) = delete;

    ExecutableMemory(ExecutableMemory&& other) noexcept 
        : ptr_(other.ptr_), size_(other.size_), state_(other.state_) {
        other.ptr_ = nullptr;
        other.state_ = State::Freed;
    }

    ExecutableMemory& operator=(ExecutableMemory&& other) noexcept {
        if (this != &other) {
            release();
            ptr_ = other.ptr_;
            size_ = other.size_;
            state_ = other.state_;
            other.ptr_ = nullptr;
            other.state_ = State::Freed;
        }
        return *this;
    }

    void make_executable() {
        if (state_ != State::Writable) {
            throw std::logic_error("Сторінка не перебуває в стані запису");
        }

#if defined(_WIN32) || defined(_WIN64)
        DWORD old_prot;
        if (!VirtualProtect(ptr_, size_, PAGE_EXECUTE_READ, &old_prot)) {
            throw std::system_error(static_cast<int>(GetLastError()), std::system_category(), "VirtualProtect failed");
        }
#else
        if (mprotect(ptr_, size_, PROT_READ | PROT_EXEC) != 0) {
            throw std::system_error(errno, std::generic_category(), "mprotect failed");
        }
        __builtin___clear_cache(reinterpret_cast<char*>(ptr_), reinterpret_cast<char*>(ptr_) + size_);
#endif
        state_ = State::Executable;
    }

    [[nodiscard]] uint8_t* data() {
        if (state_ != State::Writable) {
            throw std::logic_error("Спроба запису у виконувану або звільнену пам'ять");
        }
        return ptr_;
    }

    [[nodiscard]] size_t size() const noexcept { return size_; }
    [[nodiscard]] State state() const noexcept { return state_; }

    template<typename FuncType>
    [[nodiscard]] FuncType as_function() const {
        if (state_ != State::Executable) {
            throw std::logic_error("Спроба виклику коду зі сторінки, яка не має прав PROT_EXEC");
        }
        return reinterpret_cast<FuncType>(reinterpret_cast<uintptr_t>(ptr_));
    }

private:
    void release() noexcept {
        if (!ptr_) return;
#if defined(_WIN32) || defined(_WIN64)
        VirtualFree(ptr_, 0, MEM_RELEASE);
#else
        munmap(ptr_, size_);
#endif
        ptr_ = nullptr;
        state_ = State::Freed;
    }

    uint8_t* ptr_{nullptr};
    size_t size_{0};
    State state_{State::Freed};
};

// Емітер інструкцій x86-64
class SimpleJitEmitter {
public:
    static void emit_mul_add(std::span<uint8_t> buffer, int32_t constant) {
        std::vector<uint8_t> bytes;

#if defined(_WIN32) || defined(_WIN64)
        // imul rcx, rdx
        bytes.insert(bytes.end(), {0x48, 0x0F, 0xAF, 0xCA});
        // add rcx, imm32
        bytes.insert(bytes.end(), {0x48, 0x81, 0xC1});
        append_int32(bytes, constant);
        // mov rax, rcx
        bytes.insert(bytes.end(), {0x48, 0x89, 0xC8});
#else
        // imul rdi, rsi
        bytes.insert(bytes.end(), {0x48, 0x0F, 0xAF, 0xFE});
        // add rdi, imm32
        bytes.insert(bytes.end(), {0x48, 0x81, 0xC7});
        append_int32(bytes, constant);
        // mov rax, rdi
        bytes.insert(bytes.end(), {0x48, 0x89, 0xF8});
#endif
        // ret
        bytes.push_back(0xC3);

        if (bytes.size() > buffer.size()) {
            throw std::runtime_error("JIT-буфер замалий для емітованого коду");
        }
        std::memcpy(buffer.data(), bytes.data(), bytes.size());
    }

private:
    static void append_int32(std::vector<uint8_t>& vec, int32_t val) {
        const auto* raw = reinterpret_cast<const uint8_t*>(&val);
        vec.insert(vec.end(), raw, raw + sizeof(int32_t));
    }
};

int main() {
    try {
        ExecutableMemory mem(4096);

        // Генерація коду для f(a, b) = a * b + 42
        SimpleJitEmitter::emit_mul_add(std::span<uint8_t>(mem.data(), mem.size()), 42);

        // Перемикання в режим виконання (W^X)
        mem.make_executable();

        // Отримання покажчика на функцію
        using JitSignature = int64_t (*)(int64_t, int64_t);
        auto fn = mem.as_function<JitSignature>();

        int64_t a = 7, b = 8;
        int64_t res = fn(a, b);

        std::cout << "JIT f(" << a << ", " << b << ") = " << res
                  << " (очікувано 7 * 8 + 42 = 98)\n";

    } catch (const std::exception& ex) {
        std::cerr << "Помилка JIT: " << ex.what() << '\n';
        return 1;
    }
    return 0;
}
