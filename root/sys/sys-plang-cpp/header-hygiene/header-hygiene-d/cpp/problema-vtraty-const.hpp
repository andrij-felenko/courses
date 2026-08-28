// UserSession.h
#pragma once
#include <memory>

class UserSession {
public:
    UserSession();
    ~UserSession();

    void inspect() const; // Має бути чистою операцією читання!

private:
    struct Impl;
    std::unique_ptr<Impl> m_impl;
};
