// Повністю динамічний фрагмент (поступова міграція)
function legacy_calculate(data: any) {
    return data.price * data.count; // Типи не перевіряються
}

// Статично типізований контракт
interface OrderItem {
    readonly price: number;
    readonly count: number;
}

function safe_calculate(item: OrderItem): number {
    return item.price * item.count; // Перевіряється на етапі збірки
}
