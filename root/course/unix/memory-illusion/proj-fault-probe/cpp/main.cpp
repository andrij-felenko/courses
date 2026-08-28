#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <string_view>
#include <system_error>
#include <memory>
#include <span>
#include <chrono>
#include <cstdint>
#include <cstring>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/resource.h>
#include <sys/wait.h>
#include <sys/types.h>

namespace mem_probe {

struct Snapshot {
    long minflt{0};
    long majflt{0};
    std::size_t resident_pages{0};
    std::size_t total_pages{0};
    std::size_t smaps_rss_kb{0};
    std::size_t smaps_pss_kb{0};
    std::size_t smaps_private_dirty_kb{0};
    std::chrono::steady_clock::time_point timestamp{};
};

class MappedBuffer {
public:
    explicit MappedBuffer(std::size_t size) : size_(size) {
        void* ptr = ::mmap(nullptr, size_, PROT_READ | PROT_WRITE,
                           MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
        if (ptr == MAP_FAILED) {
            throw std::system_error(errno, std::generic_category(), "mmap failed");
        }
        data_ = static_cast<char*>(ptr);
        ::madvise(data_, size_, MADV_NOHUGEPAGE);
    }

    ~MappedBuffer() noexcept {
        if (data_ != nullptr) {
            ::munmap(data_, size_);
        }
    }

    MappedBuffer(const MappedBuffer&) = delete;
    MappedBuffer& operator=(const MappedBuffer&) = delete;

    MappedBuffer(MappedBuffer&& other) noexcept : data_(other.data_), size_(other.size_) {
        other.data_ = nullptr;
        other.size_ = 0;
    }

    MappedBuffer& operator=(MappedBuffer&& other) noexcept {
        if (this != &other) {
            if (data_ != nullptr) {
                ::munmap(data_, size_);
            }
            data_ = other.data_;
            size_ = other.size_;
            other.data_ = nullptr;
            other.size_ = 0;
        }
        return *this;
    }

    [[nodiscard]] volatile char* data() noexcept { return data_; }
    [[nodiscard]] std::size_t size() const noexcept { return size_; }

private:
    char* data_{nullptr};
    std::size_t size_{0};
};

void populate_smaps_metrics(Snapshot& snap) {
    std::ifstream file("/proc/self/smaps_rollup");
    if (!file.is_open()) return;

    std::string key;
    std::size_t value{0};
    std::string unit;

    while (file >> key >> value >> unit) {
        if (key == "Rss:") {
            snap.smaps_rss_kb = value;
        } else if (key == "Pss:") {
            snap.smaps_pss_kb = value;
        } else if (key == "Private_Dirty:") {
            snap.smaps_private_dirty_kb = value;
        }
    }
}

Snapshot take_snapshot(const volatile void* addr, std::size_t length, std::size_t page_size) {
    Snapshot snap;
    snap.timestamp = std::chrono::steady_clock::now();

    struct rusage usage{};
    if (::getrusage(RUSAGE_SELF, &usage) == 0) {
        snap.minflt = usage.ru_minflt;
        snap.majflt = usage.ru_majflt;
    }

    populate_smaps_metrics(snap);

    if (addr != nullptr && length > 0) {
        snap.total_pages = length / page_size;
        std::vector<unsigned char> vec(snap.total_pages, 0);
        // mincore вимагає non-const void* за сигнатурою POSIX
        if (::mincore(const_cast<void*>(static_cast<const void*>(addr)), length, vec.data()) == 0) {
            for (auto byte : vec) {
                if (byte & 1) {
                    snap.resident_pages++;
                }
            }
        }
    }
    return snap;
}

void print_delta(std::string_view stage, const Snapshot& before, const Snapshot& after) {
    long d_minflt = after.minflt - before.minflt;
    long d_majflt = after.majflt - before.majflt;
    long d_res = static_cast<long>(after.resident_pages) - static_cast<long>(before.resident_pages);
    auto dur_us = std::chrono::duration_cast<std::chrono::microseconds>(after.timestamp - before.timestamp).count();

    std::cout << "[" << stage << "] Час: " << dur_us << " мкс | Збої: +"
              << d_minflt << " min, +" << d_majflt
              << " maj | DRAM: " << after.resident_pages
              << "/" << after.total_pages << " стор. (+" << d_res << ")"
              << " | RSS: " << after.smaps_rss_kb << " КіБ, PSS: "
              << after.smaps_pss_kb << " КіБ, PrivDirty: "
              << after.smaps_private_dirty_kb << " КіБ\n";
}

void run_demand_paging(std::size_t page_size) {
    std::cout << "\n=== ТЕСТ 1: Demand Paging (Виділення 100 сторінок = "
              << (100 * page_size) / 1024 << " КіБ) ===\n";
    constexpr std::size_t num_pages = 100;
    const std::size_t total_bytes = num_pages * page_size;

    Snapshot s0 = take_snapshot(nullptr, 0, page_size);
    MappedBuffer buffer(total_bytes);
    Snapshot s1 = take_snapshot(buffer.data(), buffer.size(), page_size);
    print_delta("1. mmap() (чиста обіцянка)", s0, s1);

    volatile char sink = 0;
    for (std::size_t i = 0; i < 15; ++i) {
        sink += buffer.data()[i * page_size];
    }
    (void)sink;

    Snapshot s2 = take_snapshot(buffer.data(), buffer.size(), page_size);
    print_delta("2. Читання 15 сторінок", s1, s2);

    for (std::size_t i = 0; i < 40; ++i) {
        buffer.data()[i * page_size] = static_cast<char>(i + 1);
    }

    Snapshot s3 = take_snapshot(buffer.data(), buffer.size(), page_size);
    print_delta("3. Запис у 40 сторінок", s2, s3);

    for (std::size_t i = 0; i < 40; ++i) {
        buffer.data()[i * page_size] = static_cast<char>(i + 2);
    }

    Snapshot s4 = take_snapshot(buffer.data(), buffer.size(), page_size);
    print_delta("4. Повторний запис у 40 стор.", s3, s4);

    for (std::size_t i = 40; i < num_pages; ++i) {
        buffer.data()[i * page_size] = static_cast<char>(i + 1);
    }

    Snapshot s5 = take_snapshot(buffer.data(), buffer.size(), page_size);
    print_delta("5. Запис у решту 60 стор.", s4, s5);
}

void run_copy_on_write(std::size_t page_size) {
    std::cout << "\n=== ТЕСТ 2: Copy-on-Write (Розгалуження через fork, 50 сторінок) ===\n";
    constexpr std::size_t num_pages = 50;
    const std::size_t total_bytes = num_pages * page_size;

    MappedBuffer buffer(total_bytes);

    for (std::size_t i = 0; i < num_pages; ++i) {
        buffer.data()[i * page_size] = static_cast<char>(0xAA);
    }

    Snapshot s_parent_init = take_snapshot(buffer.data(), buffer.size(), page_size);
    std::cout << "Стан пам'яті батька до fork(): " << s_parent_init.resident_pages
              << "/" << s_parent_init.total_pages << " резидентних сторінок\n";

    pid_t pid = ::fork();
    if (pid < 0) {
        throw std::system_error(errno, std::generic_category(), "fork failed");
    }

    if (pid == 0) {
        Snapshot s_child_start = take_snapshot(buffer.data(), buffer.size(), page_size);

        volatile char sum = 0;
        for (std::size_t i = 0; i < num_pages; ++i) {
            sum += buffer.data()[i * page_size];
        }
        (void)sum;

        Snapshot s_child_read = take_snapshot(buffer.data(), buffer.size(), page_size);
        print_delta("Дитина: читання 50 стор.", s_child_start, s_child_read);

        for (std::size_t i = 0; i < 20; ++i) {
            buffer.data()[i * page_size] = static_cast<char>(0xBB);
        }

        Snapshot s_child_write = take_snapshot(buffer.data(), buffer.size(), page_size);
        print_delta("Дитина: запис у 20 стор. (COW)", s_child_read, s_child_write);

        ::_exit(0);
    } else {
        int status = 0;
        ::waitpid(pid, &status, 0);

        Snapshot s_parent_after_child = take_snapshot(buffer.data(), buffer.size(), page_size);
        std::cout << "\nПроцес-дитина завершився. Батько лишився єдиним власником.\n";

        for (std::size_t i = 0; i < 20; ++i) {
            buffer.data()[i * page_size] = static_cast<char>(0xCC);
        }

        Snapshot s_parent_write_split = take_snapshot(buffer.data(), buffer.size(), page_size);
        print_delta("Батько: запис у 20 відколотих", s_parent_after_child, s_parent_write_split);

        for (std::size_t i = 20; i < num_pages; ++i) {
            buffer.data()[i * page_size] = static_cast<char>(0xDD);
        }

        Snapshot s_parent_write_sole = take_snapshot(buffer.data(), buffer.size(), page_size);
        print_delta("Батько: запис у 30 спільних", s_parent_write_split, s_parent_write_sole);
    }
}

} // namespace mem_probe

int main() {
    long sc_res = ::sysconf(_SC_PAGESIZE);
    if (sc_res <= 0) {
        std::cerr << "Не вдалося визначити розмір сторінки системи\n";
        return 1;
    }
    auto page_size = static_cast<std::size_t>(sc_res);
    std::cout << "Розмір апаратної сторінки системи: " << page_size << " байтів\n";

    try {
        mem_probe::run_demand_paging(page_size);
        mem_probe::run_copy_on_write(page_size);
    } catch (const std::exception& ex) {
        std::cerr << "Помилка виконання: " << ex.what() << '\n';
        return 1;
    }

    return 0;
}
