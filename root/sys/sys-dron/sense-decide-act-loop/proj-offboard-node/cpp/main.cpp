#include <chrono>
#include <cmath>
#include <memory>
#include <atomic>
#include <rclcpp/rclcpp.hpp>
#include <px4_msgs/msg/offboard_control_mode.hpp>
#include <px4_msgs/msg/trajectory_setpoint.hpp>
#include <px4_msgs/msg/vehicle_command.hpp>
#include <px4_msgs/msg/vehicle_control_mode.hpp>
#include <px4_msgs/msg/vehicle_local_position.hpp>
#include <px4_msgs/msg/vehicle_status.hpp>

using namespace std::chrono_literals;

/**
 * @brief Високопродуктивний вузол Offboard-керування з підтримкою Feed-Forward.
 */
class OffboardControlNode : public rclcpp::Node {
public:
    OffboardControlNode() : Node("offboard_control_node"), state_(NodeState::PREFLIGHT_STREAMING) {
        // QoS для сумісності з Micro-XRCE-DDS (Best Effort, Transient Local)
        rmw_qos_profile_t qos_profile = rmw_qos_profile_sensor_data;
        auto qos = rclcpp::QoS(rclcpp::QoSInitialization(qos_profile.history, 5), qos_profile);

        // Публікатори керування
        offboard_mode_pub_ = this->create_publisher<px4_msgs::msg::OffboardControlMode>(
            "/fmu/in/offboard_control_mode", 10);
        trajectory_setpoint_pub_ = this->create_publisher<px4_msgs::msg::TrajectorySetpoint>(
            "/fmu/in/trajectory_setpoint", 10);
        vehicle_command_pub_ = this->create_publisher<px4_msgs::msg::VehicleCommand>(
            "/fmu/in/vehicle_command", 10);

        // Підписники телеметрії
        local_pos_sub_ = this->create_subscription<px4_msgs::msg::VehicleLocalPosition>(
            "/fmu/out/vehicle_local_position", qos,
            std::bind(&OffboardControlNode::on_local_position, this, std::placeholders::_1));
        
        vehicle_status_sub_ = this->create_subscription<px4_msgs::msg::VehicleStatus>(
            "/fmu/out/vehicle_status", qos,
            std::bind(&OffboardControlNode::on_vehicle_status, this, std::placeholders::_1));

        // Високоточний детермінований таймер контуру керування (50 Гц -> 20 мс)
        timer_ = this->create_wall_timer(20ms, std::bind(&OffboardControlNode::control_loop_step, this));

        start_time_ = this->now();
        RCLCPP_INFO(this->get_logger(), "Offboard Control Node ініціалізовано. Старт попереднього потоку 50 Гц.");
    }

private:
    enum class NodeState {
        PREFLIGHT_STREAMING,
        REQUESTING_OFFBOARD,
        ARMING,
        ACTIVE_FLIGHT,
        HOVER_HOLD
    };

    // Обробник поточної локальної одометрії
    void on_local_position(const px4_msgs::msg::VehicleLocalPosition::SharedPtr msg) {
        current_x_.store(msg->x, std::memory_order_relaxed);
        current_y_.store(msg->y, std::memory_order_relaxed);
        current_z_.store(msg->z, std::memory_order_relaxed);
        last_odom_time_ = this->now();
    }

    // Обробник статусу польотного контролера
    void on_vehicle_status(const px4_msgs::msg::VehicleStatus::SharedPtr msg) {
        nav_state_.store(msg->nav_state, std::memory_order_relaxed);
        arming_state_.store(msg->arming_state, std::memory_order_relaxed);
    }

    // Головний крок детермінованого контуру керування
    void control_loop_step() {
        // Завжди публікуємо прапорці режимів керування
        publish_offboard_control_mode();

        double elapsed_sec = (this->now() - start_time_).seconds();

        // Логіка автомату переходів
        switch (state_) {
            case NodeState::PREFLIGHT_STREAMING:
                // Живимо автопілот нульовими зміщеннями перед входом
                publish_trajectory_setpoint(0.0f, 0.0f, -2.0f, 0.0f, 0.0f, 0.0f, 0.0f);
                if (stream_counter_++ > 30) { // >600 мс стабільного потоку
                    state_ = NodeState::REQUESTING_OFFBOARD;
                }
                break;

            case NodeState::REQUESTING_OFFBOARD:
                publish_trajectory_setpoint(0.0f, 0.0f, -2.0f, 0.0f, 0.0f, 0.0f, 0.0f);
                send_vehicle_command(px4_msgs::msg::VehicleCommand::VEHICLE_CMD_DO_SET_MODE, 1.0f, 6.0f);
                if (nav_state_.load(std::memory_order_relaxed) == px4_msgs::msg::VehicleStatus::NAVIGATION_STATE_OFFBOARD) {
                    RCLCPP_INFO(this->get_logger(), "Режим OFFBOARD активовано автопілотом.");
                    state_ = NodeState::ARMING;
                }
                break;

            case NodeState::ARMING:
                publish_trajectory_setpoint(0.0f, 0.0f, -2.0f, 0.0f, 0.0f, 0.0f, 0.0f);
                send_vehicle_command(px4_msgs::msg::VehicleCommand::VEHICLE_CMD_COMPONENT_ARM_DISARM, 1.0f);
                if (arming_state_.load(std::memory_order_relaxed) == px4_msgs::msg::VehicleStatus::ARMING_STATE_ARMED) {
                    RCLCPP_INFO(this->get_logger(), "Мотори зведено. Старт польотного завдання.");
                    flight_start_time_ = this->now();
                    state_ = NodeState::ACTIVE_FLIGHT;
                }
                break;

            case NodeState::ACTIVE_FLIGHT: {
                // Перевірка свіжості одометрії (Watchdog сенсорів)
                if ((this->now() - last_odom_time_).seconds() > 0.3) {
                    RCLCPP_WARN_THROTTLE(this->get_logger(), *this->get_clock(), 1000, 
                        "Затримка одометрії > 300 мс! Перехід у захисне утримання позиції.");
                    state_ = NodeState::HOVER_HOLD;
                    break;
                }

                // Генерація траєкторії кругового руху радіусом R = 5 м зі швидкістю w = 0.5 рад/с
                double t = (this->now() - flight_start_time_).seconds();
                float radius = 5.0f;
                float omega = 0.5f;

                float x_des = radius * std::cos(omega * t);
                float y_des = radius * std::sin(omega * t);
                float z_des = -3.0f; // Висота 3 метри (Z униз у системі NED)

                // Вектор швидкості прямого зв'язку (Feed-Forward Velocity)
                float vx_ff = -radius * omega * std::sin(omega * t);
                float vy_ff = radius * omega * std::cos(omega * t);
                float vz_ff = 0.0f;

                // Розрахунок курсу по вектору руху
                float yaw_des = std::atan2(vy_ff, vx_ff);

                publish_trajectory_setpoint(x_des, y_des, z_des, vx_ff, vy_ff, vz_ff, yaw_des);
                break;
            }

            case NodeState::HOVER_HOLD:
                // Зависання в поточній зафіксованій точці
                publish_trajectory_setpoint(
                    current_x_.load(std::memory_order_relaxed),
                    current_y_.load(std::memory_order_relaxed),
                    current_z_.load(std::memory_order_relaxed),
                    0.0f, 0.0f, 0.0f, 0.0f);
                break;
        }
    }

    // Публікація прапорців контурів керування
    void publish_offboard_control_mode() {
        px4_msgs::msg::OffboardControlMode msg{};
        msg.timestamp = this->get_clock()->now().nanoseconds() / 1000;
        msg.position = true;
        msg.velocity = true;      // Дозволяємо Feed-Forward по швидкості
        msg.acceleration = false;
        msg.attitude = false;
        msg.body_rate = false;
        offboard_mode_pub_->publish(msg);
    }

    // Публікація структури сетпоінта
    void publish_trajectory_setpoint(float x, float y, float z, float vx, float vy, float vz, float yaw) {
        px4_msgs::msg::TrajectorySetpoint msg{};
        msg.timestamp = this->get_clock()->now().nanoseconds() / 1000;
        msg.position = {x, y, z};
        msg.velocity = {vx, vy, vz};
        msg.acceleration = {NAN, NAN, NAN}; // Ігноруємо прискорення
        msg.yaw = yaw;
        msg.yawspeed = NAN;
        trajectory_setpoint_pub_->publish(msg);
    }

    // Відправка команд на автопілот
    void send_vehicle_command(uint16_t command, float param1 = 0.0f, float param2 = 0.0f) {
        px4_msgs::msg::VehicleCommand msg{};
        msg.timestamp = this->get_clock()->now().nanoseconds() / 1000;
        msg.param1 = param1;
        msg.param2 = param2;
        msg.command = command;
        msg.target_system = 1;
        msg.target_component = 1;
        msg.source_system = 1;
        msg.source_component = 1;
        msg.from_external = true;
        vehicle_command_pub_->publish(msg);
    }

    rclcpp::Publisher<px4_msgs::msg::OffboardControlMode>::SharedPtr offboard_mode_pub_;
    rclcpp::Publisher<px4_msgs::msg::TrajectorySetpoint>::SharedPtr trajectory_setpoint_pub_;
    rclcpp::Publisher<px4_msgs::msg::VehicleCommand>::SharedPtr vehicle_command_pub_;
    rclcpp::Subscription<px4_msgs::msg::VehicleLocalPosition>::SharedPtr local_pos_sub_;
    rclcpp::Subscription<px4_msgs::msg::VehicleStatus>::SharedPtr vehicle_status_sub_;
    rclcpp::TimerBase::SharedPtr timer_;

    NodeState state_;
    rclcpp::Time start_time_;
    rclcpp::Time flight_start_time_;
    rclcpp::Time last_odom_time_{0, 0, RCL_ROS_TIME};

    uint32_t stream_counter_{0};
    std::atomic<float> current_x_{0.0f};
    std::atomic<float> current_y_{0.0f};
    std::atomic<float> current_z_{0.0f};
    std::atomic<uint8_t> nav_state_{0};
    std::atomic<uint8_t> arming_state_{0};
};

int main(int argc, char* argv[]) {
    rclcpp::init(argc, argv);
    auto node = std::make_shared<OffboardControlNode>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}
