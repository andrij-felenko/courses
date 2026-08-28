namespace embedded::lvgl {

struct DisplayConfiguration {
    int16_t horizontalResolution{320};
    int16_t verticalResolution{240};
    int16_t physicalWidth{320};
    int16_t physicalHeight{240};
    int16_t offsetX{0};
    int16_t offsetY{0};
    bool directMode{false};
    bool fullRefresh{false};
    void* userData{nullptr};
};

} // namespace embedded::lvgl
