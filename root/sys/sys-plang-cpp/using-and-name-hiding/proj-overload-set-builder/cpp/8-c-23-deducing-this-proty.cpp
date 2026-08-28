struct ModernStreamExportable {
    // Явний об'єктний параметр замінює CRTP і static_cast:
    void export_to(this const auto& self, std::ostream& os) {
        self.format_stream(os);
    }
};

struct ModernBinaryExportable {
    void export_to(this const auto& self, std::vector<uint8_t>& buf) {
        self.format_binary(buf);
    }
};

// Цільовий клас у C++23:
struct ModernTelemetryFrame : public ModernStreamExportable,
                              public ModernBinaryExportable {
    // Using-оголошення залишаються НЕОБХІДНИМИ для об'єднання перевантажень!
    using ModernStreamExportable::export_to;
    using ModernBinaryExportable::export_to;

    void format_stream(std::ostream& os) const { os << "C++23 Telemetry"; }
    void format_binary(std::vector<uint8_t>& b) const { b.push_back(0xFF); }
};
