struct DeviceNode {
    virtual ~DeviceNode() = default;
    int32_t node_id{1};
};

// Обидва проміжні класи вказують virtual public
struct AudioInput : virtual public DeviceNode {
    int32_t sample_rate{48000};
};

struct AudioOutput : virtual public DeviceNode {
    float volume{1.0f};
};

struct AudioDuplexDevice : public AudioInput, public AudioOutput {
    int64_t device_id{100};
};
