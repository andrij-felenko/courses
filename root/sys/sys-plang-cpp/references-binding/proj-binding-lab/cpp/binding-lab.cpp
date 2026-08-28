// binding-lab.cpp — лабораторія зв'язування. C++20, жодних залежностей.
#include <functional>
#include <iostream>
#include <map>
#include <string>
#include <string_view>
#include <thread>
#include <utility>

class Loud {
public:
    explicit Loud(std::string name) : name_(std::move(name)), id_(next_++) {
        say("створено");
    }
    Loud(const Loud& other) : name_(other.name_), id_(next_++) {
        ++copies_;
        say("КОПІЮВАННЯ", other.id_);
    }
    Loud(Loud&& other) noexcept : name_(std::move(other.name_)), id_(next_++) {
        other.name_ = "(вичерпаний)";
        say("переміщення", other.id_);
    }
    Loud& operator=(const Loud&) = delete;
    Loud& operator=(Loud&&)      = delete;
    ~Loud() { say("знищено"); }

    int                id()   const { return id_; }
    const std::string& name() const { return name_; }

    static int  copies()      { return copies_; }
    static void mute(bool on) { mute_ = on; }

private:
    void say(std::string_view what, int from = 0) const {
        if (mute_) return;
        std::cout << "      #" << id_ << "  " << what;
        if (from != 0) std::cout << " з #" << from;
        std::cout << "  «" << name_ << "»\n";
    }

    std::string name_;
    int         id_;

    static inline int  next_   = 1;
    static inline int  copies_ = 0;
    static inline bool mute_   = false;
};

static void head(std::string_view title) {
    std::cout << "\n──  " << title << "  ──\n";
}
