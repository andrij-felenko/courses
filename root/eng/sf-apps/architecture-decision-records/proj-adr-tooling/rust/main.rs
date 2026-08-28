// Гроші тримаємо в Decimal (не i64, не f64).
// Причини, відкинуті варіанти й ціна: doc/adr/0011-money-as-decimal.md
// (це рішення замінило ADR-0007 «i64 у копійках» — див. посилання там).
//
// Коротко: i64-копійки не вмістили валют із трьома знаками й податкових
// правил зі складним округленням; f64 заборонений через похибку на дробах.

use rust_decimal::Decimal; // де-факто десятковий тип для Rust

#[derive(Clone, Copy)]
struct Money {
    amount: Decimal, // десятковий тип, точний на дробах
}

// Decimal реалізує трейти Add і Mul, тож оператори + і * працюють:
impl std::ops::Add for Money {
    type Output = Money;
    fn add(self, o: Money) -> Money {
        Money { amount: self.amount + o.amount }
    }
}

impl std::ops::Mul<i64> for Money {
    type Output = Money;
    fn mul(self, scale: i64) -> Money {
        Money { amount: self.amount * Decimal::from(scale) }
    }
}

// Наступний, хто захоче «повернути на i64 для швидкості», спершу
// прочитає ADR-0011 і побачить, ЧОМУ від i64 свідомо пішли — і не
// повторить уже пройдену помилку.
