#include <memory_resource>
#include <memory>

class PmrWidget {
    struct Impl;
    
    // Власний видалювач, що повертає пам'ять у PMR-ресурс
    struct PmrDeleter {
        std::pmr::memory_resource* mr_;
        void operator()(Impl* ptr) const noexcept;
    };

    std::unique_ptr<Impl, PmrDeleter> pImpl_;

public:
    explicit PmrWidget(std::pmr::memory_resource* mr);
    ~PmrWidget();
};
