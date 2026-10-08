class RtdCalibrator {
public:
    static bool calibrateSpan(float r_meas1, float r_ref1, 
                              float r_meas2, float r_ref2, 
                              float& out_zero_offset, float& out_span_gain) {
        float delta_meas = r_meas2 - r_meas1;
        float delta_ref  = r_ref2 - r_ref1;

        if (std::abs(delta_meas) < 1e-6f || std::abs(delta_ref) < 1e-6f) {
            return false;
        }

        out_span_gain = delta_ref / delta_meas;
        out_zero_offset = r_meas1 - (r_ref1 / out_span_gain);
        return true;
    }
};
