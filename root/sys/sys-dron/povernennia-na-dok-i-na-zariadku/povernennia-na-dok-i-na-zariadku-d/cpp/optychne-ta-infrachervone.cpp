#include <mavlink/v2.0/common/mavlink_msg_landing_target.hpp>
#include <array>

mavlink::common::msg::LANDING_TARGET target_msg{};
target_msg.time_usec = time_boot_us;
target_msg.target_num = target_num;
target_msg.frame = MAV_FRAME_BODY_NED;
target_msg.angle_x = angle_x_rad;
target_msg.angle_y = angle_y_rad;
target_msg.distance = distance_m;
target_msg.size_x = size_x_rad;
target_msg.size_y = size_y_rad;
target_msg.x = pos_x_m;
target_msg.y = pos_y_m;
target_msg.z = pos_z_m;
target_msg.q = std::array<float, 4>{q_target[0], q_target[1], q_target[2], q_target[3]};
target_msg.type = LANDING_TARGET_TYPE_VISION_FIDUCIAL;
target_msg.position_valid = position_valid_flag;
