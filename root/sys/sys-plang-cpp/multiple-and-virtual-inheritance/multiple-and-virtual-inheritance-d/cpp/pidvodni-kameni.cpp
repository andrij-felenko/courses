struct DeviceNode {
    int32_t node_id;
    DeviceNode& operator=(const DeviceNode& other) {
        std::cout << "Copying DeviceNode\n";
        node_id = other.node_id;
        return *this;
    }
};

struct AudioInput : virtual public DeviceNode {
    int32_t sample_rate;
    AudioInput& operator=(const AudioInput& other) {
        DeviceNode::operator=(other); // Присвоєння віртуальної бази
        sample_rate = other.sample_rate;
        return *this;
    }
};

struct AudioOutput : virtual public DeviceNode {
    float volume;
    AudioOutput& operator=(const AudioOutput& other) {
        DeviceNode::operator=(other); // Ще одне присвоєння тієї самої віртуальної бази!
        volume = other.volume;
        return *this;
    }
};

struct AudioDuplexDevice : public AudioInput, public AudioOutput {
    AudioDuplexDevice& operator=(const AudioDuplexDevice& other) {
        AudioInput::operator=(other);  // Викличе DeviceNode::operator= перший раз
        AudioOutput::operator=(other); // Викличе DeviceNode::operator= ДРУГИЙ раз!
        return *this;
    }
};
