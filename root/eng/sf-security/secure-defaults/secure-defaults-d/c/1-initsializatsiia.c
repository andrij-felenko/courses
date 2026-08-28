/* НЕБЕЗПЕЧНО: Оптимістичний дефолт */
bool check_access_insecure(const User* user, const char* ip) {
    bool access_granted = true;
    if (user_is_banned(user)) access_granted = false;
    if (ip_is_blacklisted(ip)) access_granted = false;
    return access_granted;
}

/* БЕЗПЕЧНО: Песимістичний дефолт */
bool check_access_secure(const User* user, const char* resource, const char* ip) {
    bool access_granted = false;
    if (user_is_authenticated(user) && 
        user_has_explicit_permission(user, resource) && 
        ip_in_allowed_subnet(ip)) {
        access_granted = true;
    }
    return access_granted;
}
