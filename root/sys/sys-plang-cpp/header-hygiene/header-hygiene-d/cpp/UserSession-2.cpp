// UserSession.cpp
#include "UserSession.h"
#include "Database.h"

struct UserSession::Impl {
    uint64_t access_count = 0;
    Database db;
};

void UserSession::inspect() const {
    // КОМПІЛЮЄТЬСЯ БЕЗ ПОМИЛОК, але порушує логічну константність!
    m_impl->access_count++; 
}
