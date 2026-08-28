// У Rust читання під RCU оформлюється через RCU Guard
let rcu_guard = kernel::sync::rcu::read_lock();

// Пошук у колекції, захищеній RCU
if let Some(dev) = dev_list.iter(&rcu_guard).find(|d| d.ifindex == idx) {
    // Працюємо з dev...
}
// Guard автоматично звільняється при виході з області видимості
drop(rcu_guard);

// Письменник
let mut list = dev_list.lock(); // Захист письменників
let old_node = list.remove(idx);
// Звільнення буде автоматично відкладене завдяки Drop + RCU
