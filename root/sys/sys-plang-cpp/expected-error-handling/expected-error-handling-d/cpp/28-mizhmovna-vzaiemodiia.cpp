// C-FFI сумісна структура для експорту в C# або Rust
struct C_ResultHandle {
    void* ptr;
    int error_code;
    bool is_success;
};

extern "C" C_ResultHandle c_api_fetch_user(uint64_t id) {
    auto res = fetch_user(id);
    if (res) {
        return C_ResultHandle{.ptr = new UserData(std::move(*res)), .error_code = 0, .is_success = true};
    }
    return C_ResultHandle{.ptr = nullptr, .error_code = static_cast<int>(res.error()), .is_success = false};
}
