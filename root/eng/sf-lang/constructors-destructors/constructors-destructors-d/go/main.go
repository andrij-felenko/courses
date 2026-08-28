func processFile(filename string) error {
    f, err := os.Open(filename)
    if err != nil {
        return err
    }
    defer f.Close() // Гарантоване закриття дескриптора при будь-якому виході з функції

    // Робота з файлом...
    return nil
}
