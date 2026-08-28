// Інвертувати 3×3 (гомографію) через приєднану матрицю — коротко й без циклу Гаусса.
static int invert3x3(const double H[9], double Hi[9]) {
    double det = H[0]*(H[4]*H[8]-H[5]*H[7])
               - H[1]*(H[3]*H[8]-H[5]*H[6])
               + H[2]*(H[3]*H[7]-H[4]*H[6]);
    if (fabs(det) < 1e-12) return 0;
    double id = 1.0 / det;
    Hi[0]=(H[4]*H[8]-H[5]*H[7])*id; Hi[1]=(H[2]*H[7]-H[1]*H[8])*id; Hi[2]=(H[1]*H[5]-H[2]*H[4])*id;
    Hi[3]=(H[5]*H[6]-H[3]*H[8])*id; Hi[4]=(H[0]*H[8]-H[2]*H[6])*id; Hi[5]=(H[2]*H[3]-H[0]*H[5])*id;
    Hi[6]=(H[3]*H[7]-H[4]*H[6])*id; Hi[7]=(H[1]*H[6]-H[0]*H[7])*id; Hi[8]=(H[0]*H[4]-H[1]*H[3])*id;
    return 1;
}

// Яскравість кадру в точці канонічного квадрата (Xc,Yc) — через обернену гомографію.
// Найближчий сусід (INTER_NEAREST, як у OpenCV-aruco); межі кадру перевіряємо.
static int sample_canonical(const uint8_t *img, int W, int H_img,
                            const double Hi[9], double Xc, double Yc) {
    double w = Hi[6]*Xc + Hi[7]*Yc + Hi[8];
    if (fabs(w) < 1e-12) return 0;
    int sx = (int)((Hi[0]*Xc + Hi[1]*Yc + Hi[2]) / w + 0.5);
    int sy = (int)((Hi[3]*Xc + Hi[4]*Yc + Hi[5]) / w + 0.5);
    if (sx < 0 || sx >= W || sy < 0 || sy >= H_img) return -1;   // вилізли за кадр
    return img[sy * W + sx];
}
