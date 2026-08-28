void worker_main(parser_ctx* ctx, job_queue& q, std::stop_token stop) noexcept {
    while (auto job = q.pop(stop)) {
        try {
            (*job)();
        } catch (...) {
            std::lock_guard lk{ctx->async_mtx};      // слот спільний між потоками
            ctx->failure = std::current_exception();
            set_message(ctx, "async failure");
        }
    }
}
