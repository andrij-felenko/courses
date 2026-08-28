#include <iostream>
#include <iomanip>

int main() {
    using Kinematics3D = ManipulatorKinematics<3>;

    Kinematics3D::JointArray joints{{
        {.a = 0.35f, .q_min = -3.14f, .q_max = 3.14f},
        {.a = 0.30f, .q_min = -2.50f, .q_max = 2.50f},
        {.a = 0.15f, .q_min = -2.50f, .q_max = 2.50f}
    }};

    Kinematics3D arm(joints);

    const Kinematics3D::Vec3 target{0.45f, 0.25f, 0.0f};
    const Kinematics3D::JointAngles q_init{0.1f, 0.1f, 0.1f};

    if (auto sol = arm.inverse_kinematics_dls(target, q_init, 100, 1e-4f, 0.05f)) {
        const auto t_verify = arm.forward_kinematics(*sol);
        const auto p = t_verify.translation();

        std::cout << std::fixed << std::setprecision(4);
        std::cout << "IK зійшлася: q = [" << (*sol)[0] << ", " << (*sol)[1] << ", " << (*sol)[2] << "] рад\n";
        std::cout << "Кінцева позиція: [" << p.x << ", " << p.y << ", " << p.z << "] м\n";
    } else {
        std::cout << "IK не зійшлася (поза робочим простором)\n";
    }
    return 0;
}
