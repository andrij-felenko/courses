namespace algorithms {

enum class FilterError {
    EmptyInput,
    NullPointer,
    AllocationFailure,
    PeelingFailedExceededAttempts,
    CorruptedBuffer,
    UnsupportedVersion
};

template <typename FingerprintType = uint8_t>
class XorFilter;

} // namespace algorithms
