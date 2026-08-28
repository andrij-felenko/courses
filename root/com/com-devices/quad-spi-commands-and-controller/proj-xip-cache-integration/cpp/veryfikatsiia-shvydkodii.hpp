/* Замір часу виконання циклу обчислень безпосередньо з QSPI Flash (C++) */
uint32_t benchmark_qspi_execution() noexcept {
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;

    using compute_fn_t = uint32_t (*)(const uint32_t*, size_t);
    auto run_from_qspi = reinterpret_cast<compute_fn_t>(0x90001001U);

    static constexpr auto test_array = std::array<uint32_t, 256>{};

    const uint32_t t_start = DWT->CYCCNT;
    const uint32_t sum = run_from_qspi(test_array.data(), test_array.size());
    const uint32_t t_elapsed = DWT->CYCCNT - t_start;

    (void)sum;
    return t_elapsed;
}
