// order_test.go ── ТЕСТ — це драйвер. Збирає ядро з підробленим сховищем.
package order_test

import (
    "strconv"
    "testing"

    "example/adapters"
    "example/order"
)

func TestОформленняЗберігаєІРахує(t *testing.T) {
    // збірка «під тест»: пам'ять + детермінований id
    n := 0
    сховище := adapters.НовеПамятьСховище()
    сервіс := &order.ЗамовленняСервіс{
        Сховище: сховище,
        НID:     func() string { n++; return strconv.Itoa(n) },
    }

    з, err := сервіс.Оформити("a@b.com", []order.Позиція{{Товар: "книга", Ціна: 200, Кількість: 2}})
    if err != nil {
        t.Fatal(err)
    }
    if з.ID != "1" {
        t.Errorf("id = %q, хотіли \"1\"", з.ID) // джерело підроблене
    }
    if з.Сума() != 400 {
        t.Errorf("сума = %d, хотіли 400", з.Сума()) // правило суми
    }
    if збережене, _ := сховище.Узяти("1"); збережене == nil {
        t.Error("адаптер не зберіг замовлення")
    }
}

func TestПорожнєВідхиляється(t *testing.T) {
    сервіс := &order.ЗамовленняСервіс{Сховище: adapters.НовеПамятьСховище(), НID: func() string { return "x" }}
    if _, err := сервіс.Оформити("a@b.com", nil); err == nil {
        t.Error("порожнє замовлення мало впасти")
    }
}
