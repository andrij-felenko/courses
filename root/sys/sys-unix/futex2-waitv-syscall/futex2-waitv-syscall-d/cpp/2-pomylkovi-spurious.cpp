int index;
for (;;) {
    try {
        index = Futex2::waitv(waiters, &ts, CLOCK_MONOTONIC);
        break;
    } catch (const std::system_error& e) {
        if (e.code().value() != EINTR)
            throw;              /* усе інше — не наша справа */
    }
}
