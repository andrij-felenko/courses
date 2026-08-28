struct SensorFrame {
    uint64_t timestamp_ns;
    uint32_t device_id;
    std::vector<float> readings;
};

// Спеціалізація структури у просторі імен бібліотеки
template<>
struct trait_design::SerializerTraits<SensorFrame> {
    static void write(BinaryBuffer& buf, const SensorFrame& frame) {
        SerializerTraits<uint64_t>::write(buf, frame.timestamp_ns);
        SerializerTraits<uint32_t>::write(buf, frame.device_id);
        SerializerTraits<std::vector<float>>::write(buf, frame.readings);
    }
};
