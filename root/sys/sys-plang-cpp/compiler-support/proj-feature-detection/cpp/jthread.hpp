// compat/jthread.hpp
#pragma once

#include "version_check.hpp"

#if defined(__cpp_lib_jthread) && (__cpp_lib_jthread >= 201911L)

    #include <thread>

    namespace compat {
        using jthread = std::jthread;
        using stop_token = std::stop_token;
        using stop_source = std::stop_source;
    }

#else

    #include <thread>
    #include <atomic>
    #include <memory>
    #include <utility>

    namespace compat {

        class stop_source;

        class stop_token {
        public:
            stop_token() noexcept : flag_(nullptr) {}
            explicit stop_token(const std::atomic<bool>* flag) noexcept : flag_(flag) {}

            bool stop_requested() const noexcept {
                return flag_ && flag_->load(std::memory_order_relaxed);
            }

        private:
            const std::atomic<bool>* flag_;
        };

        class stop_source {
        public:
            stop_source() : flag_(false) {}

            stop_token get_token() const noexcept {
                return stop_token(&flag_);
            }

            bool request_stop() noexcept {
                return !flag_.exchange(true, std::memory_order_relaxed);
            }

        private:
            std::atomic<bool> flag_;
        };

        class jthread {
        public:
            jthread() noexcept = default;

            template <typename Function, typename... Args>
            explicit jthread(Function&& f, Args&&... args) {
                stop_source_ = std::make_unique<stop_source>();
                thread_ = std::thread(std::forward<Function>(f), stop_source_->get_token(), std::forward<Args>(args)...);
            }

            ~jthread() {
                if (joinable()) {
                    request_stop();
                    join();
                }
            }

            jthread(jthread&&) noexcept = default;
            jthread& operator=(jthread&&) noexcept = default;

            bool joinable() const noexcept { return thread_.joinable(); }
            void join() { thread_.join(); }
            void detach() { thread_.detach(); }

            bool request_stop() noexcept {
                return stop_source_ ? stop_source_->request_stop() : false;
            }

            stop_token get_stop_token() const noexcept {
                return stop_source_ ? stop_source_->get_token() : stop_token();
            }

        private:
            std::unique_ptr<stop_source> stop_source_;
            std::thread thread_;
        };

    } // namespace compat

#endif
