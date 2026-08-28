// C++ Idiomatic Wrapper Header: spectral_analysis_api.hpp
#ifndef SPECTRAL_ANALYSIS_API_HPP
#define SPECTRAL_ANALYSIS_API_HPP

#include <span>
#include <vector>
#include <system_error>
#include "spectral_analysis_api.h"

namespace spectral {

enum class Window : int {
    Rectangular = WINDOW_RECTANGULAR,
    Hann        = WINDOW_HANN,
    Hamming     = WINDOW_HAMMING,
    Blackman    = WINDOW_BLACKMAN,
    FlatTop     = WINDOW_FLAT_TOP
};

struct SpectralResult {
    std::vector<double> frequencies;
    std::vector<double> psd;
    double enbw_hz;
    int segments_averaged;
};

class Analyzer {
public:
    Analyzer(double sample_rate_hz, int fft_size, Window win = Window::Hann) {
        cfg_.sample_rate_hz = sample_rate_hz;
        cfg_.fft_size = fft_size;
        cfg_.overlap_samples = fft_size / 2;
        cfg_.window_type = static_cast<WindowType>(win);
        
        if (int err = psd_analyzer_init(&cfg_); err != PSD_SUCCESS) {
            throw std::system_error(err, std::generic_category(), "PSD Init Failed");
        }
    }

    SpectralResult process(std::span<const double> signal) const {
        PsdResult c_res{};
        int status = psd_compute_welch(signal.data(), static_cast<int>(signal.size()), &cfg_, &c_res);
        if (status != PSD_SUCCESS) {
            throw std::system_error(status, std::generic_category(), "PSD Compute Failed");
        }

        SpectralResult cpp_res;
        cpp_res.frequencies.assign(c_res.freq_bins, c_res.freq_bins + c_res.num_bins);
        cpp_res.psd.assign(c_res.psd_density, c_res.psd_density + c_res.num_bins);
        cpp_res.enbw_hz = c_res.enbw_hz;
        cpp_res.segments_averaged = c_res.segments_averaged;

        psd_result_free(&c_res);
        return cpp_res;
    }

private:
    PsdConfig cfg_{};
};

} // namespace spectral

#endif // SPECTRAL_ANALYSIS_API_HPP
