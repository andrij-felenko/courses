void save_vtk(const std::string& filename) const {
    std::ofstream out(filename);
    out << "# vtk DataFile Version 3.0\n"
        << "Cahn-Hilliard Phase Field\nASCII\n"
        << "DATASET STRUCTURED_POINTS\n"
        << "DIMENSIONS " << N << " " << N << " 1\n"
        << "SPACING " << h << " " << h << " 1.0\n"
        << "POINT_DATA " << N * N << "\n"
        << "SCALARS composition double 1\nLOOKUP_TABLE default\n";
    for (double val : c_) {
        out << val << "\n";
    }
}
