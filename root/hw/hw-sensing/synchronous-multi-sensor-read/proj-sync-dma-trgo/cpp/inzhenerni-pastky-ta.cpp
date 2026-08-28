namespace memory {

struct CacheManager {
    static void invalidate_buffer(const void* address, std::size_t size_bytes) noexcept {
        SCB_InvalidateDCache_by_Addr(reinterpret_cast<uint32_t*>(const_cast<void*>(address)),
                                     static_cast<std::int32_t>(size_bytes));
    }
};

} // namespace memory
