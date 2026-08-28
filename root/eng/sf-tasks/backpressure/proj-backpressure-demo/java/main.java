// Стеля: put() у повну чергу присипляє нитку.
BlockingQueue<Job> jobs = new ArrayBlockingQueue<>(32);

// Двійник: LinkedBlockingQueue без місткості. Її стеля — Integer.MAX_VALUE,
// тобто фактично вся пам'ять процесу.
BlockingQueue<Job> unbounded = new LinkedBlockingQueue<>();

// І найгірше: саме ця необмежена черга сидить усередині стандартної
// фабрики пулів — у документації JDK так і написано, що пул із фіксованим
// числом ниток працює над спільною НЕОБМЕЖЕНОЮ чергою.
ExecutorService pool = Executors.newFixedThreadPool(8);

// Чесний варіант — зібрати пул руками: стеля черги + явне рішення,
// що робити з тим, хто не вліз.
ExecutorService safe = new ThreadPoolExecutor(
        8, 8, 0L, TimeUnit.MILLISECONDS,
        new ArrayBlockingQueue<>(32),                 // стеля
        new ThreadPoolExecutor.CallerRunsPolicy());   // не вліз — виконуй сам, у своїй нитці
