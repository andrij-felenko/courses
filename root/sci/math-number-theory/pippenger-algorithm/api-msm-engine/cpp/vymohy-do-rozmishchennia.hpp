namespace msm {

struct CudaConfig {
    int32_t device_id{0};
    void* cuda_stream{nullptr};
    bool enable_p2p_access{false};
};

class CudaContext {
public:
    explicit CudaContext(CudaConfig config, CurveId curve = CurveId::BN254);
    ~CudaContext();

    CudaContext(const CudaContext&) = delete;
    CudaContext& operator=(const CudaContext&) = delete;

    [[nodiscard]] Status synchronize() noexcept;
};

} // namespace msm
