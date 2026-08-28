struct DeviceNode {
    virtual ~DeviceNode() = default;
    int32_t node_id{1};
};

struct AudioInput : public DeviceNode {
    int32_t sample_rate{48000};
};

struct AudioOutput : public DeviceNode {
    float volume{1.0f};
};

struct AudioDuplexDevice : public AudioInput, public AudioOutput {
    int64_t device_id{100};
};
