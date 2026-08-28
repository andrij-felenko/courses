// C++ API: Інкапсуляція у клас із патерном Pimpl та розумним покажчиком
#include <memory>

namespace compression {
    class CompressionContext {
    public:
        CompressionContext();
        ~CompressionContext();
        CompressionContext(CompressionContext&&) noexcept;
        CompressionContext& operator=(CompressionContext&&) noexcept;
    private:
        struct Impl;
        std::unique_ptr<Impl> impl_;
    };
}
