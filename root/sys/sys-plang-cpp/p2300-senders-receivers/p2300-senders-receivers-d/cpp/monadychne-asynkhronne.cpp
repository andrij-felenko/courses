auto fetch_user(int id) { /* повертає Sender<User> */ }
auto fetch_orders(User u) { /* повертає Sender<Orders> */ }

auto pipeline = std::execution::just(42)
              | std::execution::let_value([](int id) {
                    return fetch_user(id);
                })
              | std::execution::let_value([](User user) {
                    return fetch_orders(user);
                });
