struct DeviceNode {
    virtual void reset() {
        std::cout << "DeviceNode::reset\n";
    }
    virtual ~DeviceNode() = default;
};

struct AudioInput : virtual public DeviceNode {
    void reset() override {
        std::cout << "AudioInput::reset\n";
    }
};

struct AudioOutput : virtual public DeviceNode {
    // Метод reset() НЕ перевизначено в AudioOutput
};

struct AudioDuplexDevice : public AudioInput, public AudioOutput {
    // reset() не перевизначено явно в AudioDuplexDevice
};
