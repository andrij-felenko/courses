// Один градусний файл: N вузлів по стороні (3601 або 1201),
// рядки з півночі на південь, значення із заходу на схід, big-endian.
static constexpr int16_t VOID = -32768;

class DegreeTile {
public:
    // lat, lon — у градусах; повертає false, якщо будь-який із чотирьох
    // вузлів комірки є прогалиною: інтерполювати прогалину не можна.
    bool sample(double lat, double lon, double& out) const {
        const double gx = (lon - lon0_) * (N_ - 1);      // у вузлах, від заходу
        const double gy = (lat0_ + 1.0 - lat) * (N_ - 1); // у вузлах, від півночі
        const int i = static_cast<int>(std::floor(gx));
        const int j = static_cast<int>(std::floor(gy));
        if (i < 0 || j < 0 || i >= N_ - 1 || j >= N_ - 1) return false;

        const double u = gx - i, v = gy - j;
        const int16_t h00 = at(i,     j    ), h10 = at(i + 1, j    );
        const int16_t h01 = at(i,     j + 1), h11 = at(i + 1, j + 1);
        if (h00 == VOID || h10 == VOID || h01 == VOID || h11 == VOID) return false;

        const double a = h00 + u * (h10 - h00);
        const double b = h01 + u * (h11 - h01);
        out = a + v * (b - a);
        return true;
    }

private:
    int16_t at(int i, int j) const {                     // рядок j, стовпець i
        const uint8_t* p = raw_ + 2 * (static_cast<size_t>(j) * N_ + i);
        return static_cast<int16_t>((p[0] << 8) | p[1]); // старший байт перший
    }
    const uint8_t* raw_;   // відображений у пам'ять файл
    int   N_;              // 3601 або 1201
    double lat0_, lon0_;   // південно-західний кут квадрата, цілі градуси
};
