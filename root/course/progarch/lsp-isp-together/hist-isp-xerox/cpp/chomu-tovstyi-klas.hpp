// job.h — один товстий клас, який #include-ять УСІ клієнти
class Job {
public:
    void print();     // треба клієнтові друку
    void staple();    // треба клієнтові степлера
    void fax();       // треба клієнтові факсу
    void scan();
    void cancel();
    // …ще десятки методів усіх підсистем
};
