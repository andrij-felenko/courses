#include <iostream>
#include <vector>
#include <string_view>
#include <memory>
#include <expected>
#include <system_error>
#include <dlfcn.h>
#include <link.h>
#include <sys/auxv.h>

namespace loader_inspector {

struct SearchPath {
    std::string name;
    unsigned int flags;
};

/* RAII-обгортка для автоматичного закриття дескриптора dlopen */
class DynamicHandle {
public:
    explicit DynamicHandle(void* handle) : handle_(handle) {}
    ~DynamicHandle() {
        if (handle_) {
            ::dlclose(handle_);
        }
    }

    DynamicHandle(const DynamicHandle&) = delete;
    DynamicHandle& operator=(const DynamicHandle&) = delete;

    DynamicHandle(DynamicHandle&& other) noexcept : handle_(other.handle_) {
        other.handle_ = nullptr;
    }

    DynamicHandle& operator=(DynamicHandle&& other) noexcept {
        if (this != &other) {
            if (handle_) ::dlclose(handle_);
            handle_ = other.handle_;
            other.handle_ = nullptr;
        }
        return *this;
    }

    [[nodiscard]] void* get() const noexcept { return handle_; }

private:
    void* handle_{nullptr};
};

struct SerinfoDeleter {
    void operator()(Dl_serinfo* ptr) const noexcept {
        std::free(ptr);
    }
};

using SerinfoPtr = std::unique_ptr<Dl_serinfo, SerinfoDeleter>;

[[nodiscard]] bool is_secure_mode() noexcept {
    return getauxval(AT_SECURE) != 0;
}

[[nodiscard]] std::expected<DynamicHandle, std::string> open_self() {
    void* handle = ::dlopen(nullptr, RTLD_NOW);
    if (!handle) {
        const char* err = ::dlerror();
        return std::unexpected(err ? err : "Невідома помилка dlopen");
    }
    return DynamicHandle(handle);
}

[[nodiscard]] std::expected<std::vector<SearchPath>, std::string> 
fetch_search_paths(const DynamicHandle& handle) {
    Dl_serinfo size_info{};
    if (::dlinfo(handle.get(), RTLD_DI_SERINFOSIZE, &size_info) != 0) {
        const char* err = ::dlerror();
        return std::unexpected(err ? err : "Помилка RTLD_DI_SERINFOSIZE");
    }

    SerinfoPtr info(static_cast<Dl_serinfo*>(std::malloc(size_info.dls_size)));
    if (!info) {
        return std::unexpected("Помилка виділення пам'яті під Dl_serinfo");
    }

    info->dls_size = size_info.dls_size;
    info->dls_cnt = size_info.dls_cnt;

    if (::dlinfo(handle.get(), RTLD_DI_SERINFO, info.get()) != 0) {
        const char* err = ::dlerror();
        return std::unexpected(err ? err : "Помилка RTLD_DI_SERINFO");
    }

    std::vector<SearchPath> paths;
    paths.reserve(info->dls_cnt);

    for (unsigned int i = 0; i < info->dls_cnt; ++i) {
        paths.push_back(SearchPath{
            .name = info->dls_serpath[i].dls_name,
            .flags = info->dls_serpath[i].dls_flags
        });
    }

    return paths;
}

} // namespace loader_inspector

int main() {
    std::cout << "=== C++ Інспектор динамічного завантажувача ===\n";
    std::cout << "Режим безпеки AT_SECURE: " 
              << (loader_inspector::is_secure_mode() 
                  ? "АКТИВНИЙ (SUID/SGID захист)" 
                  : "Вимкнено") 
              << "\n\n";

    std::cout << "Перелік завантажених модулів у пам'яті:\n";
    ::dl_iterate_phdr([](struct dl_phdr_info* info, size_t, void*) -> int {
        std::string_view name = (info->dlpi_name && info->dlpi_name[0] != '\0') 
                                ? info->dlpi_name 
                                : "[Main Executable]";
        std::cout << "  - [0x" << std::hex << info->dlpi_addr << std::dec << "] " 
                  << name << "\n";
        return 0;
    }, nullptr);

    auto handle_result = loader_inspector::open_self();
    if (!handle_result) {
        std::cerr << "Помилка: " << handle_result.error() << "\n";
        return 1;
    }

    auto paths_result = loader_inspector::fetch_search_paths(*handle_result);
    if (!paths_result) {
        std::cerr << "Помилка аналізу шляхів: " << paths_result.error() << "\n";
        return 1;
    }

    std::cout << "\nАктивні шляхи пошуку ld.so (усього: " << paths_result->size() << "):\n";
    std::size_t index = 1;
    for (const auto& path : *paths_result) {
        std::cout << "  [" << index++ << "] " << path.name << "\n";
    }

    return 0;
}
