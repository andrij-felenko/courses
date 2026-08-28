#include <iostream>
#include <vector>
#include <array>
#include <memory>
#include <fstream>
#include <stdexcept>
#include <system_error>
#include <cerrno>
#include <cstdint>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <asm/sgx.h>

constexpr std::size_t kPageSize = 4096;
constexpr std::size_t kSigstructSize = 1808;

/* RAII обгортка для файлового дескриптора SGX */
class SgxDevice {
public:
    explicit SgxDevice(const char* device_path = "/dev/sgx_enclave") {
        fd_ = ::open(device_path, O_RDWR);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити SGX пристрій");
        }
    }

    ~SgxDevice() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    SgxDevice(const SgxDevice&) = delete;
    SgxDevice& operator=(const SgxDevice&) = delete;

    [[nodiscard]] int get() const noexcept { return fd_; }

private:
    int fd_{-1};
};

/* RAII обгортка для відображення пам'яті mmap */
class EnclaveMemory {
public:
    EnclaveMemory(int sgx_fd, std::size_t size) : size_(size) {
        addr_ = ::mmap(nullptr, size_, PROT_READ | PROT_WRITE | PROT_EXEC,
                        MAP_SHARED, sgx_fd, 0);
        if (addr_ == MAP_FAILED) {
            throw std::system_error(errno, std::generic_category(), "Помилка mmap пам'яті енклава");
        }
    }

    ~EnclaveMemory() {
        if (addr_ != MAP_FAILED) {
            ::munmap(addr_, size_);
        }
    }

    EnclaveMemory(const EnclaveMemory&) = delete;
    EnclaveMemory& operator=(const EnclaveMemory&) = delete;

    [[nodiscard]] void* data() const noexcept { return addr_; }
    [[nodiscard]] std::size_t size() const noexcept { return size_; }

private:
    void* addr_{MAP_FAILED};
    std::size_t size_{0};
};

/* Клас завантажувача енклавів */
class EnclaveLoader {
public:
    static void load(const std::string& sigstruct_path, std::size_t enclave_size) {
        SgxDevice device;

        // 1. Читання бінарної структури SIGSTRUCT
        std::array<std::uint8_t, kSigstructSize> sigstruct_buf{};
        std::ifstream sig_file(sigstruct_path, std::ios::binary);
        if (!sig_file.read(reinterpret_cast<char*>(sigstruct_buf.data()), kSigstructSize)) {
            throw std::runtime_error("Помилка читання файлу SIGSTRUCT");
        }

        // 2. Створення SECS та виклик SGX_IOC_ENCLAVE_CREATE
        alignas(kPageSize) std::array<std::uint8_t, kPageSize> secs_buf{};
        *reinterpret_cast<std::uint64_t*>(secs_buf.data() + 8) = enclave_size;

        sgx_enclave_create create_req{};
        create_req.src = reinterpret_cast<std::uint64_t>(secs_buf.data());

        if (::ioctl(device.get(), SGX_IOC_ENCLAVE_CREATE, &create_req) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка ioctl SGX_IOC_ENCLAVE_CREATE");
        }

        // 3. Резервування віртуальної пам'яті через mmap RAII
        EnclaveMemory enclave_mem(device.get(), enclave_size);

        // 4. Додавання початкової сторінки
        alignas(kPageSize) std::array<std::uint8_t, kPageSize> code_page{};
        code_page.fill(0x90); // Заповнення NOP інструкціями

        sgx_secinfo secinfo{};
        secinfo.flags = SGX_SECINFO_REG | SGX_SECINFO_R | SGX_SECINFO_W | SGX_SECINFO_X;

        sgx_enclave_add_pages add_req{};
        add_req.src = reinterpret_cast<std::uint64_t>(code_page.data());
        add_req.offset = 0;
        add_req.length = kPageSize;
        add_req.secinfo = reinterpret_cast<std::uint64_t>(&secinfo);
        add_req.flags = SGX_PAGE_MEASURE;

        if (::ioctl(device.get(), SGX_IOC_ENCLAVE_ADD_PAGES, &add_req) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка ioctl SGX_IOC_ENCLAVE_ADD_PAGES");
        }

        // 5. Ініціалізація енклава
        sgx_enclave_init init_req{};
        init_req.sigstruct = reinterpret_cast<std::uint64_t>(sigstruct_buf.data());

        if (::ioctl(device.get(), SGX_IOC_ENCLAVE_INIT, &init_req) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка ioctl SGX_IOC_ENCLAVE_INIT");
        }

        std::cout << "Енклав C++ успішно завантажено за адресою: " << enclave_mem.data() << std::endl;
    }
};
