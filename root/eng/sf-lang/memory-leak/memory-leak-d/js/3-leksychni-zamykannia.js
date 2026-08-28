function createButtonHandler() {
    // Величезний масив на 50 мегабайтів
    const hugeDataset = new Uint8Array(50 * 1024 * 1024);
    
    // Повертаємо крихітну функцію
    return function onClick() {
        // Навіть якщо onClick не звертається до hugeDataset безпосередньо,
        // деякі рушії оптимізації можуть зберегти весь спільний фрейм змінних
        console.log("Кнопку натиснуто");
    };
}
