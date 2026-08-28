// У Rust читання під RCU оформлюється через RCU Guard.
// Межі RCU (lock/unlock) прив'язані до часу життя Guard.
let rcu_guard = kernel::sync::rcu::read_lock();

// Пошук у колекції, захищеній RCU. Без Guard компілятор не дасть доступ до елементів.
if let Some(dev) = dev_list.iter(&rcu_guard).find(|d| d.ifindex == idx) {
    // Працюємо з dev...
}
// Guard автоматично звільняється при виході з області видимості, викликаючи rcu_read_unlock() під капотом.
drop(rcu_guard);

// Письменник
let mut list = dev_list.lock(); // Захист письменників (аналог mutex_lock)
let old_node = list.remove(idx); // Вилучення
// Звільнення буде автоматично відкладене завдяки Drop + RCU, або можна явно викликати call_rcu
