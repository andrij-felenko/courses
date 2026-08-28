type Subscriber struct{ URL, Secret string }

func dispatch(subs []Subscriber, ev MotionEvent) {
    payload, _ := json.Marshal(map[string]any{             // лише свідомо обраний вміст
        "type": "motion.detected", "room": ev.Room, "at": ev.At,
    })
    var wg sync.WaitGroup
    for _, s := range subs {
        wg.Add(1)
        go func(s Subscriber) {                            // кожен одержувач — окрема горутина
            defer wg.Done()
            ctx, cancel := context.WithTimeout(context.Background(), 800*time.Millisecond)
            defer cancel()
            req, _ := http.NewRequestWithContext(ctx, "POST", s.URL, bytes.NewReader(payload))
            req.Header.Set("content-type", "application/json")
            res, err := http.DefaultClient.Do(req)
            if err != nil {                                // таймаут чи мертвий вузол — падає ЛИШЕ цей
                log.Printf("вебхук %s впав: %v", s.URL, err)
                return
            }
            res.Body.Close()
        }(s)
    }
    wg.Wait()                                              // збій одного не чіпає інших
}
