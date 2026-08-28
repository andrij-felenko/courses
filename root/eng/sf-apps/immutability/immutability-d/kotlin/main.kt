data class Money(val amount: Long, val currency: String) {   // data class = рівність за вмістом
    fun add(o: Money): Money {
        require(o.currency == currency) { "різні валюти" }
        return copy(amount = amount + o.amount)               // copy() — «зміна» як новий об'єкт
    }
}

val a = Money(100, "UAH")
val b = Money(100, "UAH")
a === b      // false — різні примірники (ідентичність)
a == b       // true  — рівні за значенням
