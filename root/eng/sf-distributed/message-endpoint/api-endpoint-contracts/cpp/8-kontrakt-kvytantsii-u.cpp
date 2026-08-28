class IClaimCheckPayloadStore {
public:
    virtual ~IClaimCheckPayloadStore() = default;

    // Збереження великого бінарного об'єкта в S3/Blob Storage
    // Повертає URI збереженого ресурсу (квитанцію)
    virtual std::future<std::string> uploadPayloadAsync(
        const std::string& payload_bytes,
        std::chrono::milliseconds timeout
    ) = 0;

    // Завантаження бінарного об'єкта за URI квитанції
    virtual std::future<std::string> downloadPayloadAsync(
        const std::string& claim_check_uri,
        std::chrono::milliseconds timeout
    ) = 0;
};
