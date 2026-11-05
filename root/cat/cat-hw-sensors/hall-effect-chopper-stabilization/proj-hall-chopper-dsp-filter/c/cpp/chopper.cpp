#include "chopper.hpp"

namespace {
    constexpr std::array<int32_t, 4> kFirCoeffs = {102, 410, 410, 102};
}

ChopperProcessor::ChopperProcessor() : fir_(kFirCoeffs) {}

int32_t ChopperProcessor::process(int32_t phase0_val, int32_t phase1_val) {
    int32_t v_hall_raw = (phase0_val - phase1_val) / 2;
    int32_t ma_out = ma_.process(v_hall_raw);
    return fir_.process(ma_out);
}
