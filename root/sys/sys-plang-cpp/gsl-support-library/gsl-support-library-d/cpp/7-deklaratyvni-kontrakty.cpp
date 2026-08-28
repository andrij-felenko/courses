double calculate_sensor_variance(gsl::span<const double> samples, gsl::not_null<double*> mean_out) {
    // Преумови функції (Preconditions)
    Expects(samples.size() >= 2);
    Expects(!samples.empty());

    double sum = 0.0;
    for (double s : samples) sum += s;
    *mean_out = sum / static_cast<double>(samples.size());

    double variance = 0.0;
    for (double s : samples) {
        double diff = s - *mean_out;
        variance += diff * diff;
    }
    variance /= static_cast<double>(samples.size() - 1);

    // Постумова функції (Postconditions)
    Ensures(variance >= 0.0);
    return variance;
}
