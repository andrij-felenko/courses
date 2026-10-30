#include <iostream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <memory>
#include <fstream>
#

class VisaDevice {
public:
    explicit VisaDevice(std::string address) : addr_(std::move(address)), connected_(false) {}
    ~VisaDevice() { disconnect(); }

    void connect() {
        connected_ = true;
        std::cout << "Підключено до VISA приладу: " << addr_ << '\n';
    }

    void disconnect() {
        if (connected_) {
            connected_ = false;
            std::cout << "Відключено від VISA приладу.\n";
        }
    }

    bool is_connected() const { return connected_; }

private:
    std::string addr_;
    bool connected_;
};

class ValveAnalyzerCpp {
public:
    struct Dataset {
        std::vector<double> time;
        std::vector<double> pressure;
        std::vector<double> flow;
    };

    Dataset acquire_waveforms() {
        Dataset ds;
        int num_points = 1000;
        ds.time.resize(num_points);
        ds.pressure.resize(num_points);
        ds.flow.resize(num_points);

        double f = 100.0;
        for (int i = 0; i < num_points; ++i) {
            double t = static_cast<double>(i) / 10000.0;
            ds.time[i] = t;
            ds.pressure[i] = 100.0 * std::sin(2 * 3.1415926535 * f * t);
            ds.flow[i] = 50.0 * std::sin(2 * 3.1415926535 * f * t - 0.25);
        }
        return ds;
    }

    double calculate_reverse_flow(const std::vector<double>& flow) {
        auto min_it = std::min_element(flow.begin(), flow.end());
        if (min_it != flow.end() && *min_it < 0.0) {
            return std::abs(*min_it);
        }
        return 0.0;
    }
};

int main() {
    std::cout << "Запуск аналізу пелюсткових клапанів на C++...\n";
    
    auto device = std::make_unique<VisaDevice>("TCPIP0::192.168.1.100::INSTR");
    device->connect();

    ValveAnalyzerCpp analyzer;
    auto data = analyzer.acquire_waveforms();
    double reverse_flow = analyzer.calculate_reverse_flow(data.flow);

    std::cout << "Визначений зворотний потік (C++): " << reverse_flow << " мл/с\n";
    
    return 0;
}
