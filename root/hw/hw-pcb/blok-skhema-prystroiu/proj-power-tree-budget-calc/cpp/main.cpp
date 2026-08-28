#include <iostream>
#include <vector>
#include <memory>
#include <string>
#include <string_view>
#include <format>
#include <numeric>
#include <algorithm>
#include <cstdint>

namespace hw::powertree {

enum class NodeType : uint8_t {
    RootSource,
    BuckConverter,
    BoostConverter,
    LdoRegulator,
    IsolatedDcDc,
    LeafLoad
};

struct NodeConfig {
    std::string name;
    NodeType type{NodeType::LeafLoad};
    float v_out{3.3f};
    float i_leaf_load{0.0f};
    float i_max_limit{1.0f};
    float efficiency_nominal{0.90f};
    float theta_ja{40.0f};
    float t_j_max{125.0f};
};

struct CalculatedMetrics {
    float i_out{0.0f};
    float p_out{0.0f};
    float efficiency{1.0f};
    float p_in{0.0f};
    float i_in{0.0f};
    float p_loss{0.0f};
    float t_junction{25.0f};
    bool is_overcurrent{false};
    bool is_overheated{false};
};

class PowerNode {
public:
    explicit PowerNode(NodeConfig config)
        : config_{std::move(config)} {}

    void addChild(std::shared_ptr<PowerNode> child) {
        if (child) {
            children_.push_back(child);
            child->parent_ = this;
        }
    }

    void calculateBottomUp(float ambient_temp_c) noexcept {
        float sum_child_current = 0.0f;
        for (const auto& child : children_) {
            child->calculateBottomUp(ambient_temp_c);
            sum_child_current += child->metrics_.i_in;
        }

        if (config_.type == NodeType::LeafLoad) {
            metrics_.i_out = config_.i_leaf_load;
            metrics_.p_out = config_.v_out * metrics_.i_out;
            metrics_.efficiency = 1.0f;
            metrics_.p_in = metrics_.p_out;
            metrics_.i_in = metrics_.i_out;
            metrics_.p_loss = 0.0f;
            metrics_.t_junction = ambient_temp_c;
            metrics_.is_overcurrent = false;
            metrics_.is_overheated = false;
            return;
        }

        metrics_.i_out = sum_child_current;
        metrics_.p_out = config_.v_out * metrics_.i_out;
        metrics_.is_overcurrent = (config_.i_max_limit > 0.0f && metrics_.i_out > config_.i_max_limit);

        if (config_.type == NodeType::RootSource) {
            metrics_.efficiency = 1.0f;
            metrics_.p_in = metrics_.p_out;
            metrics_.i_in = metrics_.i_out;
            metrics_.p_loss = 0.0f;
            metrics_.t_junction = ambient_temp_c;
            metrics_.is_overheated = false;
            return;
        }

        const float v_in = parent_ ? parent_->config_.v_out : config_.v_out;
        metrics_.efficiency = computeEfficiency(metrics_.i_out, v_in);

        if (config_.type == NodeType::LdoRegulator) {
            metrics_.p_loss = (v_in - config_.v_out) * metrics_.i_out;
            metrics_.p_in = metrics_.p_out + metrics_.p_loss;
            metrics_.i_in = metrics_.i_out;
        } else {
            metrics_.p_in = (metrics_.efficiency > 0.01f) 
                            ? (metrics_.p_out / metrics_.efficiency) 
                            : metrics_.p_out;
            metrics_.p_loss = metrics_.p_in - metrics_.p_out;
            metrics_.i_in = (v_in > 0.01f) ? (metrics_.p_in / v_in) : 0.0f;
        }

        metrics_.t_junction = ambient_temp_c + (metrics_.p_loss * config_.theta_ja);
        metrics_.is_overheated = (metrics_.t_junction > config_.t_j_max);
    }

    void printReport(int depth = 0) const {
        std::string indent(static_cast<size_t>(depth * 2), ' ');

        std::string_view type_label = "LOAD";
        switch (config_.type) {
            case NodeType::RootSource:    type_label = "ROOT"; break;
            case NodeType::BuckConverter: type_label = "BUCK"; break;
            case NodeType::BoostConverter:type_label = "BOOST"; break;
            case NodeType::LdoRegulator:  type_label = "LDO"; break;
            case NodeType::IsolatedDcDc:  type_label = "ISO-DC"; break;
            case NodeType::LeafLoad:      type_label = "LOAD"; break;
        }

        std::cout << std::format("{}[{:6}] {:<20} | {:4.1f}V | I_out: {:5.3f}A | P_out: {:5.2f}W | ККД: {:4.1f}% | P_loss: {:5.2f}W | T_j: {:5.1f}°C",
                                 indent, type_label, config_.name, config_.v_out, metrics_.i_out,
                                 metrics_.p_out, metrics_.efficiency * 100.0f,
                                 metrics_.p_loss, metrics_.t_junction);

        if (metrics_.is_overcurrent) std::cout << " -> [УВАГА: СТРУМ > ЛІМІТ!]";
        if (metrics_.is_overheated)  std::cout << " -> [УВАГА: ПЕРЕГРІВ КРИСТАЛА!]";
        std::cout << '\n';

        for (const auto& child : children_) {
            child->printReport(depth + 1);
        }
    }

    [[nodiscard]] const CalculatedMetrics& metrics() const noexcept { return metrics_; }
    [[nodiscard]] const NodeConfig& config() const noexcept { return config_; }

private:
    [[nodiscard]] float computeEfficiency(float i_out, float v_in) const noexcept {
        if (config_.type == NodeType::LdoRegulator) {
            return (v_in > 0.01f) ? (config_.v_out / v_in) : 0.5f;
        }

        if (i_out <= 0.001f) return 0.20f;
        float load_ratio = i_out / (config_.i_max_limit > 0.01f ? config_.i_max_limit : 1.0f);
        load_ratio = std::clamp(load_ratio, 0.0f, 1.0f);

        float eff = config_.efficiency_nominal * (1.0f - 0.15f * (1.0f - load_ratio) * (1.0f - load_ratio));
        return std::max(eff, 0.10f);
    }

    NodeConfig config_;
    CalculatedMetrics metrics_;
    PowerNode* parent_{nullptr};
    std::vector<std::shared_ptr<PowerNode>> children_;
};

} // namespace hw::powertree

int main() {
    using namespace hw::powertree;

    constexpr float ambient_temp = 60.0f;

    auto root = std::make_shared<PowerNode>(NodeConfig{"Primary 24V DC", NodeType::RootSource, 24.0f, 0.0f, 5.0f, 1.0f, 0.0f, 125.0f});
    auto buck_5v = std::make_shared<PowerNode>(NodeConfig{"Buck 24V->5V", NodeType::BuckConverter, 5.0f, 0.0f, 2.5f, 0.91f, 35.0f, 125.0f});

    auto buck_3v3 = std::make_shared<PowerNode>(NodeConfig{"Buck 5V->3.3V", NodeType::BuckConverter, 3.3f, 0.0f, 1.5f, 0.94f, 45.0f, 125.0f});
    auto buck_1v2 = std::make_shared<PowerNode>(NodeConfig{"Buck 5V->1.2V Core", NodeType::BuckConverter, 1.2f, 0.0f, 1.2f, 0.88f, 50.0f, 125.0f});
    auto ldo_3v3a = std::make_shared<PowerNode>(NodeConfig{"LDO 5V->3.3V_ANA", NodeType::LdoRegulator, 3.3f, 0.0f, 0.2f, 0.66f, 62.0f, 125.0f});
    auto iso_5v   = std::make_shared<PowerNode>(NodeConfig{"ISO DC-DC 5V->5V", NodeType::IsolatedDcDc, 5.0f, 0.0f, 0.3f, 0.78f, 70.0f, 125.0f});

    root->addChild(buck_5v);
    buck_5v->addChild(buck_3v3);
    buck_5v->addChild(buck_1v2);
    buck_5v->addChild(ldo_3v3a);
    buck_5v->addChild(iso_5v);

    buck_3v3->addChild(std::make_shared<PowerNode>(NodeConfig{"MCU I/O & Periph", NodeType::LeafLoad, 3.3f, 0.120f}));
    buck_3v3->addChild(std::make_shared<PowerNode>(NodeConfig{"QSPI Flash 32MB",  NodeType::LeafLoad, 3.3f, 0.045f}));
    buck_3v3->addChild(std::make_shared<PowerNode>(NodeConfig{"Ethernet PHY",     NodeType::LeafLoad, 3.3f, 0.180f}));

    buck_1v2->addChild(std::make_shared<PowerNode>(NodeConfig{"MCU Cortex-M7 Core", NodeType::LeafLoad, 1.2f, 0.850f}));

    ldo_3v3a->addChild(std::make_shared<PowerNode>(NodeConfig{"24-bit Delta-Sigma ADC", NodeType::LeafLoad, 3.3f, 0.015f}));
    ldo_3v3a->addChild(std::make_shared<PowerNode>(NodeConfig{"Input Buffer Op-Amps",   NodeType::LeafLoad, 3.3f, 0.025f}));
    ldo_3v3a->addChild(std::make_shared<PowerNode>(NodeConfig{"Precision 2.5V VREF",    NodeType::LeafLoad, 3.3f, 0.005f}));

    iso_5v->addChild(std::make_shared<PowerNode>(NodeConfig{"CAN-FD Transceiver", NodeType::LeafLoad, 5.0f, 0.060f}));
    iso_5v->addChild(std::make_shared<PowerNode>(NodeConfig{"RS-485 Modbus Node", NodeType::LeafLoad, 5.0f, 0.080f}));

    root->calculateBottomUp(ambient_temp);

    std::cout << "========================================================================================\n";
    std::cout << "        ІНЖЕНЕРНИЙ ЗВІТ РОЗРАХУНКУ ДЕРЕВА ЖИВЛЕННЯ ТА ТЕПЛОВОГО БАЛАНСУ (C++20)         \n";
    std::cout << std::format("        Температура середовища T_amb = {:.1f} °C                                         \n", ambient_temp);
    std::cout << "========================================================================================\n";
    root->printReport();
    std::cout << "========================================================================================\n";
    std::cout << std::format("Підсумок: Вхідна потужність = {:.2f} Вт | Вхідний струм від 24V = {:.3f} А\n",
                             root->metrics().p_in, root->metrics().i_in);
    std::cout << "========================================================================================\n";

    return 0;
}
