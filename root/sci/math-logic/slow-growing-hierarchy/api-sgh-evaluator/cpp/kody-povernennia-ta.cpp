namespace sgh {
enum class Status : uint32_t {
    Ok = 0,
    NullPtr = 1,
    Overflow = 2,
    InvalidOrdinal = 3,
    OutOfMemory = 4,
    ParseSyntax = 5,
    NotALimit = 6
};
}
