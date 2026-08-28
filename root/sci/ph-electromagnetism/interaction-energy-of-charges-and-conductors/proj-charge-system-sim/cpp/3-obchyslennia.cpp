// Приклад накопичення векторів сил C++
for (size_t i = 0; i < n; ++i) {
    for (size_t j = i + 1; j < n; ++j) {
        double dx = pos[i].x - pos[j].x;
        double dy = pos[i].y - pos[j].y;
        double dz = pos[i].z - pos[j].z;

        double r2 = dx * dx + dy * dy + dz * dz + r_soft_sq;
        double r3 = r2 * std::sqrt(r2);
        double f_mag = kCoulombK * (charges[i] * charges[j]) / r3;

        forces[i].x += f_mag * dx;
        forces[i].y += f_mag * dy;
        forces[i].z += f_mag * dz;

        forces[j].x -= f_mag * dx;
        forces[j].y -= f_mag * dy;
        forces[j].z -= f_mag * dz;
    }
}
