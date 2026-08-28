# ⚙️ Реалізація високопродуктивного Offboard-вузла

У реальних умовах автономного польоту бортовий комп'ютер (Companion Computer) одночасно виконує ресурсомісткі задачі комп'ютерного зору (Visual Inertial Odometry, нейромережеву детекцію об'єктів, побудову тривимірної карти зайнятості простору) та підтримує високочастотний контур керування автопілотом. Якщо генерацію керівних сетпоінтів прив'язати до частоти кадрів камери або циклу SLAM, будь-яка затримка обробки (наприклад, скидання буфера GPU, збірка сміття чи складний патерн сцени, що потребує 150 мс замість звичних 30 мс) спричинить просідання частоти передачі пакетів і негайне аварійне спрацьовування захисту автопілота `Offboard Loss Failsafe`.

Для надійної роботи застосовується двопотокова архітектура:
1. **Асинхронний потік планування (Planning/Perception Thread)**: опрацьовує сенсорні дані з плаваючою частотою 10–30 Гц, генерує параметри гладкої просторової траєкторії (кубічний або квінтичний сплайн) та атомарно записує коефіцієнти у спільний буфер.
2. **Детермінований потік відправки команд (Real-Time Publisher Thread)**: працює на фіксованій частоті 50 Гц (період 20 мс) під керуванням високоточного таймера. Потік обчислює миттєву точку сплайна (позицію, швидкість і прискорення) для поточного монотонного часу `t_now` та транслює комбінований сетпоінт на польотний контролер. Навіть при тимчасовому зависанні зорового потоку відправник продовжує живити автопілот неперервною екстраполяцією.

## 1. Архітектура та послідовність станів (State Machine)

Вузол керування реалізує скінченний автомат з чотирма основними станами:

```
[INIT / DISARMED]
       │
       ▼ (Старт відправки сетпоінтів: 50 Гц, лічильник > 20 пакетів)
[PREFLIGHT_STREAMING]
       │
       ▼ (Отримано підтвердження потоку + надіслано команду OFFBOARD)
[ARMING_AND_TAKEOFF]
       │
       ▼ (Досягнуто робочої висоти + nav_state == OFFBOARD)
[ACTIVE_TRAJECTORY_TRACKING]
       │
       ▼ (Виявлено затримку одометрії або отримано сигнал аварії)
[SAFE_HOLD / RECOVERY]
```

### Протокол входу в режим Offboard (Handshake)

Процес ініціалізації та активації зовнішнього керування підпорядковується суворим часовим правилам захисного автомата польотного контролера:

1. **Попереднє живлення контуру (Pre-flight Streaming)**: автопілот відхиляє будь-яку команду переходу в `OFFBOARD`, якщо не бачить стабільного вхідного потоку команд. Вузол зобов'язаний публікувати повідомлення `OffboardControlMode` та `TrajectorySetpoint` щонайменше 500–1000 мс до запиту режиму.
2. **Запит перемикання режиму (Mode Switch Request)**: після успішної передачі понад 20 пакетів вузол надсилає команду `MAV_CMD_DO_SET_MODE` (PX4 custom mode `OFFBOARD`).
3. **Зведення силової установки (Arming)**: надсилання команди `MAV_CMD_COMPONENT_ARM_DISARM`.
4. **Контроль підтвердження (Feedback Validation)**: перевірка зміни стану `vehicle_status.nav_state` на `NAVIGATION_STATE_OFFBOARD` або аналіз квитанції `COMMAND_ACK`.

---

## 2. Налаштування операційної системи та транспортного моста

Для мінімізації часового джиттера в Linux бортовий комп'ютер налаштовується наступним чином:

### Запуск Micro-XRCE-DDS Agent

Міст Micro-XRCE-DDS є шлюзом між uORB-шиною польотного контролера та DDS-доменом ROS 2. На бортовому комп'ютері агент запускається як системний сервіс systemd з підвищеним пріоритетом:

```bash
# Для послідовного з'єднання через UART (наприклад, порт /dev/ttyTHS1 на швидкості 921600 бод)
MicroXRCEAgent serial --dev /dev/ttyTHS1 -b 921600

# Для підключення через бортову мережу Ethernet / IP (UDP порт 8888)
MicroXRCEAgent udp4 -p 8888
```

### Налаштування планувальника реального часу (POSIX RT)

Щоб запобігти витісненню керуючого потоку фоновими процесами операційної системи, процес прив'язується до виділеного ядра процесора (`taskset` або `pthread_setaffinity_np`), пам'ять блокується від скидання у swap через `mlockall(MCL_CURRENT | MCL_FUTURE)`, а потік таймера переводиться у клас планування `SCHED_FIFO` з пріоритетом 80–90.

---

## 3. Повна реалізація вузла Offboard на C++ та Python

Нижче наведено повнофункціональні реалізації високопродуктивного вузла Offboard для стека ROS 2 (PX4 Micro-XRCE-DDS) з використанням прямого зв'язку Feed-Forward (позиція + лінійна швидкість) та захистом від часового джиттера.

:::tabs
```cpp
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
```
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy

from px4_msgs.msg import (
    OffboardControlMode,
    TrajectorySetpoint,
    VehicleCommand,
    VehicleLocalPosition,
    VehicleStatus,
)


class OffboardControlNode(Node):
    """
    Високопродуктивний Offboard-вузол на Python з Feed-Forward екстраполяцією.
    """

    def __init__(self) -> None:
        super().__init__('offboard_control_node')

        # QoS профіль для датчиків PX4 (Best Effort)
        sensor_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
            history=HistoryPolicy.KEEP_LAST,
            depth=5,
        )

        # Публікатори
        self.offboard_mode_pub = self.create_publisher(
            OffboardControlMode, '/fmu/in/offboard_control_mode', 10
        )
        self.trajectory_setpoint_pub = self.create_publisher(
            TrajectorySetpoint, '/fmu/in/trajectory_setpoint', 10
        )
        self.vehicle_command_pub = self.create_publisher(
            VehicleCommand, '/fmu/in/vehicle_command', 10
        )

        # Підписники
        self.local_pos_sub = self.create_subscription(
            VehicleLocalPosition,
            '/fmu/out/vehicle_local_position',
            self.on_local_position,
            sensor_qos,
        )
        self.vehicle_status_sub = self.create_subscription(
            VehicleStatus,
            '/fmu/out/vehicle_status',
            self.on_vehicle_status,
            sensor_qos,
        )

        # Стан автомату
        self.state = 'PREFLIGHT_STREAMING'
        self.stream_counter = 0

        # Локальна телеметрія
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_z = 0.0
        self.nav_state = 0
        self.arming_state = 0
        self.last_odom_time = self.get_clock().now()

        self.start_time = self.get_clock().now()
        self.flight_start_time = None

        # Високоточний таймер 50 Гц (dt = 0.02 с)
        self.timer = self.create_timer(0.02, self.control_loop_step)
        self.get_logger().info('Offboard Python Node запущено на частоті 50 Гц.')

    def on_local_position(self, msg: VehicleLocalPosition) -> None:
        self.current_x = msg.x
        self.current_y = msg.y
        self.current_z = msg.z
        self.last_odom_time = self.get_clock().now()

    def on_vehicle_status(self, msg: VehicleStatus) -> None:
        self.nav_state = msg.nav_state
        self.arming_state = msg.arming_state

    def control_loop_step(self) -> None:
        # Завжди транслюємо прапорці активності контурів
        self.publish_offboard_control_mode()

        now = self.get_clock().now()

        if self.state == 'PREFLIGHT_STREAMING':
            # Відправка початкової точки утримання
            self.publish_trajectory_setpoint(0.0, 0.0, -2.0, 0.0, 0.0, 0.0, 0.0)
            self.stream_counter += 1
            if self.stream_counter > 30:  # > 600 мс стабільного потоку
                self.state = 'REQUESTING_OFFBOARD'

        elif self.state == 'REQUESTING_OFFBOARD':
            self.publish_trajectory_setpoint(0.0, 0.0, -2.0, 0.0, 0.0, 0.0, 0.0)
            # Команда перемикання режиму (param1=1, param2=6 для PX4 Offboard)
            self.send_vehicle_command(
                VehicleCommand.VEHICLE_CMD_DO_SET_MODE, param1=1.0, param2=6.0
            )
            # Перевірка підтвердження переходу
            if self.nav_state == VehicleStatus.NAVIGATION_STATE_OFFBOARD:
                self.get_logger().info('Автопілот перейшов у режим OFFBOARD.')
                self.state = 'ARMING'

        elif self.state == 'ARMING':
            self.publish_trajectory_setpoint(0.0, 0.0, -2.0, 0.0, 0.0, 0.0, 0.0)
            self.send_vehicle_command(
                VehicleCommand.VEHICLE_CMD_COMPONENT_ARM_DISARM, param1=1.0
            )
            if self.arming_state == VehicleStatus.ARMING_STATE_ARMED:
                self.get_logger().info('Мотори зведено. Старт виконання траєкторії.')
                self.flight_start_time = self.get_clock().now()
                self.state = 'ACTIVE_FLIGHT'

        elif self.state == 'ACTIVE_FLIGHT':
            # Перевірка таймауту одометрії
            odom_age = (now - self.last_odom_time).nanoseconds / 1e9
            if odom_age > 0.3:
                self.get_logger().warn('Втрата одометрії > 300 мс! Перехід у HOVER_HOLD.')
                self.state = 'HOVER_HOLD'
                return

            t = (now - self.flight_start_time).nanoseconds / 1e9
            radius = 5.0
            omega = 0.5

            # Розрахунок позиції (коло радіусом 5 м на висоті 3 м)
            x_des = radius * math.cos(omega * t)
            y_des = radius * math.sin(omega * t)
            z_des = -3.0

            # Розрахунок швидкості Feed-Forward
            vx_ff = -radius * omega * math.sin(omega * t)
            vy_ff = radius * omega * math.cos(omega * t)
            vz_ff = 0.0

            yaw_des = math.atan2(vy_ff, vx_ff)

            self.publish_trajectory_setpoint(
                x_des, y_des, z_des, vx_ff, vy_ff, vz_ff, yaw_des
            )

        elif self.state == 'HOVER_HOLD':
            # Зависання в поточній точці
            self.publish_trajectory_setpoint(
                self.current_x, self.current_y, self.current_z, 0.0, 0.0, 0.0, 0.0
            )

    def publish_offboard_control_mode(self) -> None:
        msg = OffboardControlMode()
        msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        msg.position = True
        msg.velocity = True
        msg.acceleration = False
        msg.attitude = False
        msg.body_rate = False
        self.offboard_mode_pub.publish(msg)

    def publish_trajectory_setpoint(
        self,
        x: float,
        y: float,
        z: float,
        vx: float,
        vy: float,
        vz: float,
        yaw: float,
    ) -> None:
        msg = TrajectorySetpoint()
        msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        msg.position = [float(x), float(y), float(z)]
        msg.velocity = [float(vx), float(vy), float(vz)]
        msg.acceleration = [float('nan'), float('nan'), float('nan')]
        msg.yaw = float(yaw)
        msg.yawspeed = float('nan')
        self.trajectory_setpoint_pub.publish(msg)

    def send_vehicle_command(
        self, command: int, param1: float = 0.0, param2: float = 0.0
    ) -> None:
        msg = VehicleCommand()
        msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        msg.param1 = float(param1)
        msg.param2 = float(param2)
        msg.command = int(command)
        msg.target_system = 1
        msg.target_component = 1
        msg.source_system = 1
        msg.source_component = 1
        msg.from_external = True
        self.vehicle_command_pub.publish(msg)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = OffboardControlNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```
:::

---

## 4. Діагностика та перевірка контуру через інструменти ROS 2

Для контролю роботи вузла та налагодження часових інтервалів на бортовому комп'ютері використовуються стандартні інструменти командного рядка ROS 2:

### Перевірка стабільності частоти публікації (Rate & Jitter Monitor)

Команда `ros2 topic hz` дозволяє оцінити середню частоту та максимальне відхилення між сусідніми повідомленнями:

```bash
ros2 topic hz /fmu/in/trajectory_setpoint
```

Очікуваний вивід для надійного контуру: середня частота `average rate: 50.000`, стандартне відхилення `std dev: 0.0004s`, максимальний інтервал не повинен перевищувати 25–30 мс (запас до ліміту таймауту 500 мс становить понад 16 разів).

### Відстеження поточного стану автопілота

```bash
ros2 topic echo /fmu/out/vehicle_status --field nav_state
```

Значення `nav_state = 14` відповідає активному режиму `NAVIGATION_STATE_OFFBOARD`. Якщо значення раптово змінюється на `4` (`HOLD`) або `5` (`RTL`), це сигналізує про виникнення таймауту або збій у вхідному потоці команд.

---

## 5. Критичні підводні камені реалізації (Pitfalls & Traps)

1. **Блокування основного циклу (Spin Thread Starvation)**: Якщо в callback-функції одометрії або таймера виконується важка операція (наприклад, синхронний I/O, логування на повільний накопичувач або обчислення траєкторії на CPU > 15 мс), таймер 50 Гц почне пропускати такти. Для важких обчислень завжди використовуйте окремий `std::thread` або `rclcpp::CallbackGroup` з типом `Reentrant` та багатопотоковий виконавець `rclcpp::executors::MultiThreadedExecutor`.
2. **Синхронізація часу при старті (Timestamp Zero)**: Якщо `msg.timestamp` надсилається з нульовим значенням або з локальним системним часом Unix замість монотонного часу автопілота, фільтр валідації PX4 відкине пакет як застарілий або невалідний.
3. **Плутанина між фреймами координат ENU та NED**: Екосистема ROS 2 за замовчуванням оперує системою ENU (East-North-Up), де вісь Z спрямована вертикально вгору. Прошивка польотного контролера PX4 та повідомлення `px4_msgs::msg::TrajectorySetpoint` очікують авіаційну систему NED (North-East-Down), де висота є від'ємною координатою Z (`z = -3.0` для польоту на висоті 3 метри). Помилка у знаку координати Z або її швидкості `vz` призведе до того, що апарат спробує виконати удар об землю на максимальному газі.
4. **Асинхронне відновлення після збою (Failsafe Re-engagement)**: Якщо під час польоту відбулося спрацьовування Failsafe (наприклад, через короткочасний сплеск завантаження процесора), повторне переведення в режим Offboard можливе лише після стабілізації частоти та повторення фази попереднього живлення контуру (Pre-flight streaming), інакше автопілот знову відхилить команду переходу.
5. **Санітизація числових значень (NaN / Inf Sanitizer)**: При обчисленні тригонометричних функцій або діленні на малу швидкість у генераторі траєкторії можлива поява значень `Inf` або невалідних чисел. Польотний контролер миттєво відхиляє весь пакет при виявленні некоректних чисел у полях `position` чи `velocity`. Перед публікацією кожна змінна повинна перевірятися через `std::isfinite()`.
