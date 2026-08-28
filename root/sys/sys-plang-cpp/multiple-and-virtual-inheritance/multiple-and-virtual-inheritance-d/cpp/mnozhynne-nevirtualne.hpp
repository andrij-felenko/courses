struct AudioInput {
    virtual ~AudioInput() = default;
    virtual void read_samples();
    int32_t sample_rate{48000};
};

struct AudioOutput {
    virtual ~AudioOutput() = default;
    virtual void write_samples();
    float volume{1.0f};
};

struct AudioDuplexDevice : public AudioInput, public AudioOutput {
    void read_samples() override;
    void write_samples() override;
    int64_t device_id{42};
};
