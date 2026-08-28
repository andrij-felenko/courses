// Уся прив'язка до постачальника A замкнена ТУТ.
// Жоден інший файл не бачить vendora::*.
class VendorAQueue : public MessageQueue {
    vendora::Client cli_;                 // тип вендора — лише всередині
public:
    explicit VendorAQueue(const std::string& url) : cli_(url) {}

    bool publish(const std::string& topic,
                const std::string& payload) override {
        vendora::Message m;               // деталь вендора не витікає назовні
        m.set_channel(topic);
        m.set_body(payload);
        return cli_.send(m) == vendora::OK;
    }

    bool consume(std::string& out, int timeout_ms) override {
        vendora::Message m;
        if (cli_.poll(m, timeout_ms) != vendora::OK) return false;
        out = m.body();
        return true;
    }
};
