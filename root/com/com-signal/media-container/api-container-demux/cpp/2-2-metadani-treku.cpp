struct StreamInfo {
    std::uint32_t stream_index{0};
    MediaStreamType type{MediaStreamType::Unknown};
    MediaCodecID codec_id{MediaCodecID::Unknown};
    std::uint32_t time_base_num{1};
    std::uint32_t time_base_den{90000};

    // Параметри відео
    std::uint32_t width{0};
    std::uint32_t height{0};

    // Параметри аудіо
    std::uint32_t sample_rate{0};
    std::uint32_t channels{0};

    // Заголовок ініціалізації кодека
    std::vector<std::uint8_t> extradata;
};
