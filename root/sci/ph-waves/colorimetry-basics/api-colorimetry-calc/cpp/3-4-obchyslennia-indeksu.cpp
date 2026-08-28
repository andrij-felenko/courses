/**
 * @brief Розраховує індекси кольоропередачі R_a та R1..R15.
 * 
 * @param spectrum Спектр джерела світла.
 * @param cct_info Дані колірної температури CCT.
 * @return std::expected з CRIResult або ErrorCode.
 */
[[nodiscard]] std::expected<CRIResult, ErrorCode> compute_cri(
    const SpectralData& spectrum,
    const CCTResult&    cct_info
) noexcept;
