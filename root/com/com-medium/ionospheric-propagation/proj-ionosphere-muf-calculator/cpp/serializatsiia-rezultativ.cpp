std::string to_json(const PathParams& p, const PathMetrics& m) {
    std::ostringstream ss;
    ss << "{\"fc_mhz\":" << m.critical_freq_mhz
       << ",\"muf_mhz\":" << m.muf_mhz
       << ",\"owf_mhz\":" << m.owf_mhz
       << ",\"reflected\":" << (m.skip_distance_km.has_value() ? "true" : "false");
    if (m.skip_distance_km) {
        ss << ",\"skip_km\":" << *m.skip_distance_km;
    }
    ss << "}";
    return ss.str();
}
