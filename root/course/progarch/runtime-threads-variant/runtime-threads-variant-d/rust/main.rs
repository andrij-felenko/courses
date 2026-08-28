use std::sync::{Arc, Mutex};

// Стан, до якого лізуть УСІ потоки-з'єднання
let registry = Arc::new(Mutex::new(Registry::new()));

// у кожному потоці:
{
    let mut r = registry.lock().unwrap();   // взяв замок — аж тепер видно дані
    r.update(dev, state);                   // чіпати реєстр можна лише тут
}                                           // вийшов із блоку — замок віддано
