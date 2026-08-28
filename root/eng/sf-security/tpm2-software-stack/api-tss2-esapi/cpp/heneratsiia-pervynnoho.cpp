// У C++20 аргументи огортаються у RAII-обгортки для тимчасових handles
class ScopedEsysHandle {
public:
    ScopedEsysHandle(ESYS_CONTEXT* ctx, ESYS_TR handle = ESYS_TR_NONE) noexcept
        : m_ctx(ctx), m_handle(handle) {}
    ~ScopedEsysHandle() { if (m_ctx && m_handle != ESYS_TR_NONE) Esys_FlushContext(m_ctx, m_handle); }
    [[nodiscard]] ESYS_TR get() const noexcept { return m_handle; }
    [[nodiscard]] ESYS_TR* ptr() noexcept { return &m_handle; }
private:
    ESYS_CONTEXT* m_ctx;
    ESYS_TR m_handle;
};
