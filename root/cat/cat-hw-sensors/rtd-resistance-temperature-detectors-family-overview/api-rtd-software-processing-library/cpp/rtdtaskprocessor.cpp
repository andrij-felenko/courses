class RtdTaskProcessor {
public:
    explicit RtdTaskProcessor(RtdPipeline& pipeline) : pipeline_(pipeline) {}

    RtdStatus process(float raw_r_meas, float& out_temperature) {
        if (!pipeline_.isInitialized()) {
            return RtdStatus::InvalidArg;
        }

        const auto& cfg = pipeline_.config();
        uint8_t diag = RtdDiagnostics::evaluateStatus(raw_r_meas, cfg.r_min, cfg.r_max);
        if (diag != static_cast<uint8_t>(RtdStatus::Ok)) {
            out_temperature = -999.0f;
            return static_cast<RtdStatus>(diag);
        }

        out_temperature = RtdCalculator::calcCvdPositive(raw_r_meas, cfg.r0, cfg.cvd_a, cfg.cvd_b);
        return RtdStatus::Ok;
    }

private:
    RtdPipeline& pipeline_;
};
