package main

import (
    "context"
    "fmt"
    "time"
    "golang.org/x/sync/singleflight"
)

var sf singleflight.Group

func fetchUserData(ctx context.Context, userID string) (string, error) {
    ch := sf.DoChan(userID, func() (any, error) {
        // Важке звернення до бази даних або мікросервісу
        time.Sleep(100 * time.Millisecond)
        return fmt.Sprintf("Data for %s", userID), nil
    })

    select {
    case <-ctx.Done():
        // Клієнтський таймаут: не блокуємо поточного викликача
        return "", ctx.Err()
    case res := <-ch:
        if res.Err != nil {
            return "", res.Err
        }
        return res.Val.(string), nil
    }
}
