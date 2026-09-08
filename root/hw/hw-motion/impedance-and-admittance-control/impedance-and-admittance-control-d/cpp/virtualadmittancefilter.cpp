class VirtualAdmittanceFilter {
public:
    VirtualAdmittanceFilter(double M_d, double D_d, double K_d, double Ts) {
        // Коефіцієнти білінійного перетворення Тастіна
        double Ts2 = Ts * Ts;
        double a0 = 4.0 * M_d + 2.0 * D_d * Ts + K_d * Ts2;
        
        b0_ = Ts2 / a0;
        b1_ = 2.0 * Ts2 / a0;
        b2_ = Ts2 / a0;
        
        a1_ = (-8.0 * M_d + 2.0 * K_d * Ts2) / a0;
        a2_ = (4.0 * M_d - 2.0 * D_d * Ts + K_d * Ts2) / a0;
        
        x_prev1_ = x_prev2_ = 0.0;
        f_prev1_ = f_prev2_ = 0.0;
    }

    double update(double f_ext) {
        // Різницеве рівняння прямої форми II
        double x_admit = b0_ * f_ext + b1_ * f_prev1_ + b2_ * f_prev2_ 
                         - a1_ * x_prev1_ - a2_ * x_prev2_;
        
        // Зсув історії станів
        f_prev2_ = f_prev1_;
        f_prev1_ = f_ext;
        x_prev2_ = x_prev1_;
        x_prev1_ = x_admit;
        
        return x_admit;
    }

private:
    double b0_, b1_, b2_, a1_, a2_;
    double x_prev1_, x_prev2_, f_prev1_, f_prev2_;
};
