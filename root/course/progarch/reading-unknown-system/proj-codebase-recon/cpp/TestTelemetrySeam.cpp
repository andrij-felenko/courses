// Characterization Test у C++: TestTelemetrySeam.cpp
#include <cassert>
#include <vector>

class MockNotificationSink : public INotificationSink {
public:
    int last_device = -1;
    std::string last_message;

    void send(int device_id, std::string_view message) override {
        last_device = device_id;
        last_message = std::string(message);
    }
};

void run_cpp_characterization_tests() {
    auto mock_sink = std::make_shared<MockNotificationSink>();
    TelemetryProcessor processor(mock_sink);

    TelemetryPacket pkt1{201, 90.0f, 0x01};
    int res1 = processor.process(pkt1);
    assert(res1 == 2);
    assert(mock_sink->last_device == 201);
    assert(mock_sink->last_message == "CRITICAL_OVERHEAT");

    // Зафіксований несподіваний інваріант: без прапора status_flags=0x01 перегрів ігнорується
    TelemetryPacket pkt2{202, 90.0f, 0x00};
    int res2 = processor.process(pkt2);
    assert(res2 == 0);

    std::cout << "C++ характеристичні тести успішно зафіксували стабільність шову!\n";
}
