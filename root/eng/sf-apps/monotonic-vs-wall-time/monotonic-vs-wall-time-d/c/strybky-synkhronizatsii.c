// ПОМИЛКА: використання настінного часу для дедлайну
struct timeval start, now;
gettimeofday(&start, NULL);
double timeout_sec = 30.0;

while (!resource_ready()) {
    gettimeofday(&now, NULL);
    double elapsed = (now.tv_sec - start.tv_sec) + 
                     (now.tv_usec - start.tv_usec) / 1000000.0;
    
    if (elapsed >= timeout_sec) {
        handle_timeout_failure();
        break;
    }
    usleep(10000); // 10 мс
}
