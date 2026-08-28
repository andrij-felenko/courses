namespace mavlink {

// Маска прапорця наявності підпису у полі incompat_flags
inline constexpr uint8_t kFlagSigned = 0x01;

// Фіксована довжина блоку підпису у фізичному кадрі (байти)
inline constexpr size_t kSignatureBlockLen = 13;

// Прапорці конфігурації підписування
inline constexpr uint8_t kSigningFlagSignOutgoing = 0x01;

// Коди статусу кадрування
enum class FramingStatus : uint8_t {
    Incomplete   = 0,
    Ok           = 1,
    BadCrc       = 2,
    BadSignature = 3
};

// Максимальна кількість незалежних потоків підпису в таблиці сесій
inline constexpr size_t kMaxSigningStreams = 16;

} // namespace mavlink
