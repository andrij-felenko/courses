namespace libesimage {
enum class BoundaryType { Plane, Sphere, CornerReflector90, DielectricInterface };

struct SolverConfig {
    BoundaryType boundary_type{BoundaryType::Plane};
    double plane_z_coord{0.0};
    Vector3D sphere_center{0.0, 0.0, 0.0};
    double sphere_radius{1.0};
    double eps1{1.0};
    double eps2{1.0};
    double singularity_cutoff{1e-12};
};
}
