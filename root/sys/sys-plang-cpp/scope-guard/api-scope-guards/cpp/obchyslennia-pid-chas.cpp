constexpr int compute_compile_time_val() {
    int state = 10;
    {
        std::scope_exit guard = [&state] { state *= 2; };
        state += 5;
    } // guard виконується тут під час компіляції, state стає 30
    return state;
}

static_assert(compute_compile_time_val() == 30);
