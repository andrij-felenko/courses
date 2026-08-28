// Ризикований підхід у C: ручне повернення сокета
PooledConnection *conn = pool_acquire(pool, 5);
if (!conn) return -1;

if (process_transaction(conn->fd) < 0) {
    // ПОМИЛКА: достроковий вихід залишає сокет заблокованим у пулі назавжди!
    return -1; 
}
pool_release(pool, conn, 0);
return 0;
