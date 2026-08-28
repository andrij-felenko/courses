// UserSession.h
#pragma once
#include <string>
#include <vector>
#include <memory>
#include <map>
#include "Database.h"

class UserSession {
public:
    UserSession(const std::string& name);
    bool authenticate();

private:
    std::string m_username;
    std::vector<uint64_t> m_permissions;
    std::unique_ptr<Database> m_db;
    std::map<std::string, std::string> m_attributes;
};
