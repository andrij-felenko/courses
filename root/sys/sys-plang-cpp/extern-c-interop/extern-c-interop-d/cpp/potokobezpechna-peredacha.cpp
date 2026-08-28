/* Потоколокальний буфер останньої помилки */
thread_local std::string g_last_error_buffer;

static void set_thread_local_error(const std::string& msg) noexcept {
    g_last_error_buffer = msg;
}

extern "C" const char* engine_get_last_error(void) {
    return g_last_error_buffer.c_str();
}
