extern "C" int engine_process(engine_t* engine, const uint8_t* in, size_t len) noexcept {
    if (!engine || !engine->core || !in) {
        set_thread_local_error("Недійсний нульовий покажчик аргументу");
        return -1; // INVALID_ARGUMENT
    }

    try {
        engine->core->process(in, len);
        return 0; // SUCCESS
    } catch (const std::invalid_argument& e) {
        set_thread_local_error(e.what());
        return -1; // INVALID_ARGUMENT
    } catch (const std::bad_alloc& e) {
        set_thread_local_error(e.what());
        return -2; // OUT_OF_MEMORY
    } catch (const std::exception& e) {
        set_thread_local_error(e.what());
        return -3; // RUNTIME_ERROR
    } catch (...) {
        set_thread_local_error("Невідомий критичний системний виняток C++");
        return -4; // UNKNOWN_ERROR
    }
}
