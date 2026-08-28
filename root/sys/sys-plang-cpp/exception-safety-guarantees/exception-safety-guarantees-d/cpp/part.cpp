class Widget {
    Impl*                    impl_  = nullptr;
    std::vector<std::string> log_;
    bool                     ready_ = false;
public:
    void reset(const std::string& name) {
        delete impl_;
        impl_ = nullptr;
        impl_ = new Impl(name);
        log_.push_back(name);
        ready_ = true;
    }
};
