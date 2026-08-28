// Гроші тримаємо в Decimal (не int64, не float64).
// Причини, відкинуті варіанти й ціна: doc/adr/0011-money-as-decimal.md
// (це рішення замінило ADR-0007 «int64 у копійках» — див. посилання там).
//
// Коротко: int64-копійки не вмістили валют із трьома знаками й податкових
// правил зі складним округленням; float64 заборонений через похибку на дробах.

import "github.com/shopspring/decimal" // де-факто десятковий тип для Go

type Money struct {
	Amount decimal.Decimal // десятковий тип, точний на дробах
}

// У Go немає перевантаження операторів, а decimal.Decimal рахує
// методами Add/Mul — тож обгортаємо їх у методи Money:
func (m Money) Add(o Money) Money {
	return Money{m.Amount.Add(o.Amount)}
}

func (m Money) Mul(scale int) Money {
	return Money{m.Amount.Mul(decimal.NewFromInt(int64(scale)))}
}

// Наступний, хто захоче «повернути на int64 для швидкості», спершу
// прочитає ADR-0011 і побачить, ЧОМУ від int64 свідомо пішли — і не
// повторить уже пройдену помилку.
