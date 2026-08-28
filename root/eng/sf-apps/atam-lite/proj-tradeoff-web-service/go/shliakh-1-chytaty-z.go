// Шлях 1: читання завжди з пулу реплік. Швидко й дешево —
// але репліка може ще НЕ мати щойно записаного (застаріле читання).
type ProfileStore struct {
	primary  *pgxpool.Pool   // єдина основна — приймає записи
	replicas []*pgxpool.Pool // пул реплік — розносять читання
}

func (s *ProfileStore) Save(ctx context.Context, userID string, patch []byte) error {
	_, err := s.primary.Exec(ctx,
		"UPDATE profiles SET data = $2, updated_at = now() WHERE id = $1",
		userID, patch)
	return err
}

func (s *ProfileStore) Get(ctx context.Context, userID string) ([]byte, error) {
	r := s.replicas[rand.Intn(len(s.replicas))] // випадкова репліка
	var data []byte
	err := r.QueryRow(ctx,
		"SELECT data FROM profiles WHERE id = $1", userID).Scan(&data)
	return data, err // може бути версія ДО Save(), якщо репліка відстала
}
