void process_transaction() {
    Transaction* tx = new Transaction();
    
    if (!tx->validate()) {
        // Забули написати delete tx! Витік пам'яті при ранньому return
        return; 
    }
    
    tx->execute(); // Якщо тут виникне виняток, рядок delete tx буде пропущено!
    
    delete tx;
}
