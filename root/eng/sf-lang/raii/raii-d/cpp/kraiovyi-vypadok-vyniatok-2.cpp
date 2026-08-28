class SafeDualDevice {
    UniqueFd fd1_; // Якщо fd2_ впаде, деструктор fd1_
    UniqueFd fd2_; // викличеться автоматично!
public:
    SafeDualDevice() 
        : fd1_(::open("/dev/dev1", O_RDWR)),
          fd2_(::open("/dev/dev2", O_RDWR)) {
        if (!fd1_ || !fd2_) throw std::runtime_error("Device open failed");
    }
};
