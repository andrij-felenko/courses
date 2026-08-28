func queryUser(id int) (*User, error) {
    ch := make(chan *User) // Небуферизований канал

    go func() {
        user := fetchFromDatabase(id)
        ch <- user // Якщо викликач вийшов через тайм-аут, горутина заблокується назавжди!
    }()

    select {
    case res := <-ch:
        return res, nil
    case <-time.After(100 * time.Millisecond):
        return nil, errors.New("тайм-аут запиту")
    }
}
