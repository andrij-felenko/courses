package main

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"time"

	"golang.org/x/sync/errgroup"
)

// ── Пул з'єднань: ОДИН клієнт на весь процес → спільний keep-alive ──
var httpClient = &http.Client{
	Transport: &http.Transport{
		MaxIdleConns:        256,
		MaxIdleConnsPerHost: 64, // за замовчуванням лише 2 — задушить фанаут!
		IdleConnTimeout:     90 * time.Second,
	},
}

const overall = 400 * time.Millisecond // бюджет на весь запит

// Один крок фанауту: GET-JSON у наданому контексті (з нього ж і дедлайн).
func getJSON[T any](ctx context.Context, url string) (T, error) {
	var out T
	req, _ := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	req.Header.Set("Accept", "application/json")
	resp, err := httpClient.Do(req)
	if err != nil {
		return out, err
	}
	defer resp.Body.Close()
	if resp.StatusCode/100 != 2 {
		return out, fmt.Errorf("%s → %d", url, resp.StatusCode)
	}
	return out, json.NewDecoder(resp.Body).Decode(&out)
}

func homeHandler(w http.ResponseWriter, r *http.Request) {
	uid := userID(r)

	// спільний бюджет на весь запит; cancel звільняє ресурси при виході
	ctx, cancel := context.WithTimeout(r.Context(), overall)
	defer cancel()

	// кожна горутина пише у СВОЮ змінну (різні комірки → без гонитви),
	// читаємо їх ПІСЛЯ g.Wait() — він дає бар'єр «сталося-до»
	var (
		profile            Profile
		orders             []Order
		tips               []Tip
		ordersErr, tipsErr error
	)

	g, gctx := errgroup.WithContext(ctx)

	// КРИТИЧНИЙ виклик: його помилка йде В ГРУПУ → скасує решту й дасть 503
	g.Go(func() error {
		cctx, c := context.WithTimeout(gctx, 300*time.Millisecond) // min(бюджет, 300)
		defer c()
		p, err := getJSON[Profile](cctx, profileURL(uid))
		profile = p
		return err
	})

	// НЕОБОВ'ЯЗКОВІ: помилку КОВТАЄМО (return nil), щоб не скасувати братів
	g.Go(func() error {
		cctx, c := context.WithTimeout(gctx, 300*time.Millisecond)
		defer c()
		orders, ordersErr = getJSON[[]Order](cctx, ordersURL(uid, 3))
		return nil
	})
	g.Go(func() error {
		cctx, c := context.WithTimeout(gctx, 250*time.Millisecond)
		defer c()
		tips, tipsErr = getJSON[[]Tip](cctx, tipsURL(uid))
		return nil
	})

	// Wait поверне лише помилку КРИТИЧНОГО виклику (або nil)
	if err := g.Wait(); err != nil {
		http.Error(w, `{"error":"home_unavailable"}`, http.StatusServiceUnavailable)
		return
	}

	writeJSON(w, shapeHome(profile, orders, ordersErr, tips, tipsErr))
}

// ── Скроювання: будуємо РІВНО форму екрана ──
func shapeHome(p Profile, orders []Order, oErr error, tips []Tip, tErr error) Home {
	h := Home{Greeting: p.DisplayName, AvatarURL: p.Avatar.Small}
	if oErr == nil {
		for _, o := range orders { // впав — стрічка лишиться порожньою
			h.Orders = append(h.Orders, Card{ID: o.ID, Title: o.Title, Thumb: o.Image})
		}
	}
	if tErr == nil {
		h.Tips = &[]TipView{} // непорожній вказівник → секція є навіть без порад
		for _, t := range tips {
			*h.Tips = append(*h.Tips, TipView{ID: t.ID, Text: t.Text})
		}
	} // tErr != nil → h.Tips лишається nil → клієнт ховає секцію
	h.Degraded = oErr != nil || tErr != nil
	return h
}
