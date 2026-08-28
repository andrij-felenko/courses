#include <iostream>
#include <gsl/gsl>

struct TransformConfig {
    int id;
    double scale;
};

// Контракт виражено в системі типів: p не може бути nullptr
void apply_transform_cpp(gsl::not_null<const TransformConfig*> cfg, 
                         gsl::not_null<double*> value) noexcept {
    // Жодних перевірок у тілі: гарантовано валідні адреси на рівні компілятора
    *value = (*value) * cfg->scale;
}
