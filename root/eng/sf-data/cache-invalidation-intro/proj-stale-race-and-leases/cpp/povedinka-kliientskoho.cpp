std::string fetchUserData(LeaseCache& cache, std::string_view key) {
    int retries = 5;
    while (retries-- > 0) {
        auto res = cache.get(key);

        if (res.status == CacheGetStatus::Hit) {
            return res.value;
        }

        if (res.status == CacheGetStatus::MissLeaseGranted) {
            std::string db_val = "Alice";
            auto set_res = cache.set(key, db_val, res.token);
            if (set_res == CacheSetStatus::StaleTokenRejected) {
                std::cerr << "Попередження: токен застарів, запис відхилено кешем.\n";
            }
            return db_val;
        }

        if (res.status == CacheGetStatus::MissLeaseBusy) {
            std::this_thread::sleep_for(std::chrono::milliseconds(20 + (std::rand() % 10)));
        }
    }

    return "Alice";
}
