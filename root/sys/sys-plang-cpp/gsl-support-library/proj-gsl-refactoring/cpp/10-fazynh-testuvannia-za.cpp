// Цільова функція фазингу libFuzzer
extern "C" int LLVMFuzzerTestOneInput(const uint8_t* Data, size_t Size) {
    class NullLogger final : public ILogger {
    public:
        void log_info(std::string_view) override {}
        void log_error(std::string_view) override {}
    };

    NullLogger null_logger;
    gsl::not_null<ILogger*> logger_ptr = &null_logger;

    // Створюємо gsl::span над випадковим байтовим потоком від фазера
    auto fuzzer_span = gsl::as_bytes(gsl::span<const uint8_t>(Data, Size));

    // Виклик декодера: не повинен падати з SIGSEGV за жодних умов
    (void)SafeTelemetryDecoder::decode_packet(fuzzer_span, logger_ptr);

    return 0;
}
