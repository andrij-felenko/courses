namespace geometry {
    class Vector3D {
    public:
        void scale(double factor);
        double length() const;
        void normalize() &;
        Vector3D normalized() &&;
        explicit operator bool() const;
    };
}
