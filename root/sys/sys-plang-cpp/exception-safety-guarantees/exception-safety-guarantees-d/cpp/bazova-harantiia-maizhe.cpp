class Widget {
    std::unique_ptr<Impl>    impl_;
    std::vector<std::string> log_;
    bool                     ready_ = false;
public:
    void reset(const std::string& name) {
        auto fresh = std::make_unique<Impl>(name);  // може кинути
        log_.push_back(name);                       // може кинути
        impl_ = std::move(fresh);                   // кинути нема чому
        ready_ = true;                              // кинути нема чому
    }
};
