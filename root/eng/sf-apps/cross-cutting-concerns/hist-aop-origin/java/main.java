// Аспект: усе логування системи — в одному місці, як окремий модуль
aspect Logging {
    // ЗРІЗ ТОЧОК: добираємо всі виклики методів, назва яких — на "set"
    pointcut setters(): execution(* set*(..));

    // ПОРАДА: що зробити ДО кожної дібраної точки сполучення
    before(): setters() {
        System.out.println("викликано сетер: "
                           + thisJoinPoint.getSignature());
    }
}
