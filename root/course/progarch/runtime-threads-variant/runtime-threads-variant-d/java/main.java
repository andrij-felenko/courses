// Приймальний сервер DH: тримає живі з'єднання від хабів
ExecutorService pool = Executors.newFixedThreadPool(200);   // обмежений пул (з попереднього розділу)
ServerSocket server = new ServerSocket(8443);

while (true) {
    Socket conn = server.accept();          // блокуємось, поки прийде новий хаб
    pool.submit(() -> handle(conn));        // потік із пулу бере це з'єднання собі
}

void handle(Socket conn) throws IOException {
    var in = new DataInputStream(conn.getInputStream());
    while (true) {                          // поки хаб на зв'язку
        Frame f = readFrame(in);            // БЛОКУЄМОСЬ, поки прийде кадр
        registry.update(f.deviceId(), f.state());   // спільний стан — за замком (нижче)
        reply(conn, ackFor(f));             // відповіли — і знову чекаємо
    }                                       // розрив → виняток → потік вивільняється в пул
}
