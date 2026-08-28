class IMessageTranslator {
public:
    virtual ~IMessageTranslator() = default;
    
    // Трансформація корисного навантаження у цільову схему даних
    virtual std::expected<NormalizedMessage, TranslationError> translate(
        const NormalizedMessage& source_message,
        std::string_view target_schema_id
    ) const = 0;
};
