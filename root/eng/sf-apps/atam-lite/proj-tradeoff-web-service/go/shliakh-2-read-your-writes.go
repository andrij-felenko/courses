// Шлях 2: read-your-writes. Після запису «пришпилюємо» читання цього
// користувача до основної на вікно W — доки репліка гарантовано наздожене.
const writeWindow = time.Second // W = 1 с: стеля лага з запасом

type ProfileStore struct {
	primary  *pgxpool.Pool
	replicas []*pgxpool.Pool
	recent   RecentWrites // спільний на ВСІ вузли (напр. Redis із TTL)
}

func (s *ProfileStore) Save(ctx context.Context, userID string, patch []byte) error {
	if _, err := s.primary.Exec(ctx,
		"UPDATE profiles SET data = $2, updated_at = now() WHERE id = $1",
		userID, patch); err != nil {
		return err
	}
	return s.recent.Mark(ctx, userID, writeWindow) // «гарячий» на W
}

func (s *ProfileStore) Get(ctx context.Context, userID string) ([]byte, error) {
	var src *pgxpool.Pool
	if hot, _ := s.recent.IsHot(ctx, userID); hot {
		src = s.primary // свіжо писав → з основної
	} else {
		src = s.replicas[rand.Intn(len(s.replicas))]
	}
	var data []byte
	err := src.QueryRow(ctx,
		"SELECT data FROM profiles WHERE id = $1", userID).Scan(&data)
	return data, err // гаряче читання ЗАВЖДИ бачить власний запис
}
