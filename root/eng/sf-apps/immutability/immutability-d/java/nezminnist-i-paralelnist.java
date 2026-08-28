final AtomicReference<Config> ref = new AtomicReference<>(Config.initial());

// ЧИТАЧ: миттєвий незмінний знімок, жодного замка
Config now = ref.get();
apply(now.timeout(), now.retries());     // цілісний, застиглий світ — не попливе під руками

// ПИСАР: підготуй нову версію й підміни атомарно; при збігу — повтори
Config prev, next;
do {
    prev = ref.get();
    next = prev.withTimeout(0);          // нова НЕЗМІННА версія, стара ціла
} while (!ref.compareAndSet(prev, next));
