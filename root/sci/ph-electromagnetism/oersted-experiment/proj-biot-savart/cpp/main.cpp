#include <array>
#include <vector>
#include <cmath>

using Vec3 = std::array<double, 3>;

// векторний добуток двох 3-векторів
Vec3 cross(const Vec3 &u, const Vec3 &v) {
    return { u[1]*v[2] - u[2]*v[1],
             u[2]*v[0] - u[0]*v[2],
             u[0]*v[1] - u[1]*v[0] };
}

// node[0..N], node[N] == node[0] (замкнено); струм I; точка P
Vec3 biot_savart(const std::vector<Vec3> &node, double I, const Vec3 &P) {
    const double k = 1e-7;             // μ₀ / 4π
    const double r_min = 1e-4;         // захист від ділення на ~0 (див. пастки)
    Vec3 B = {0.0, 0.0, 0.0};
    for (size_t i = 0; i + 1 < node.size(); i++) {
        const Vec3 &a = node[i];
        const Vec3 &b = node[i + 1];
        Vec3 dL  = { b[0]-a[0], b[1]-a[1], b[2]-a[2] };   // вектор відрізка (напрям = напрям струму)
        Vec3 mid = { (a[0]+b[0])/2, (a[1]+b[1])/2, (a[2]+b[2])/2 };  // точка прикладання — середина
        Vec3 r   = { P[0]-mid[0], P[1]-mid[1], P[2]-mid[2] };        // вектор від дроту до P
        double rmag = std::sqrt(r[0]*r[0] + r[1]*r[1] + r[2]*r[2]);  // довжина r
        if (rmag < r_min) continue;    // пропустити відрізок біля дроту
        Vec3 c = cross(dL, r);         // векторний добуток dL × r
        double s = k * I / (rmag*rmag*rmag);   // = k·I/r³,  бо r̂/r² = r/r³
        B[0] += s * c[0];
        B[1] += s * c[1];
        B[2] += s * c[2];
    }
    return B;                          // вектор (Bx, By, Bz) у теслах
}
