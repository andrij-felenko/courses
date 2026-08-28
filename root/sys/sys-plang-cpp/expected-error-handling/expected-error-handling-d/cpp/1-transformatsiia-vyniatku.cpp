template <typename F>
auto make_expected_from_call(F&& func) noexcept 
    -> std::expected<std::invoke_result_t<F>, std::string> 
{
    try {
        if constexpr (std::is_void_v<std::invoke_result_t<F>>) {
            func();
            return {};
        } else {
            return func();
        }
    } catch (const std::exception& ex) {
        return std::unexpected(ex.what());
    } catch (...) {
        return std::unexpected("Невідомий системний виняток");
    }
}
