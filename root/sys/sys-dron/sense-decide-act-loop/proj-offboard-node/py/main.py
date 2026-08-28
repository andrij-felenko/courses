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
