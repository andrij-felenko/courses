// Адаптер членства ПО МЕРЕЖІ: тепер roleIn — мережевий стрибок на гарячому шляху unlock.
type RemoteMemberships struct {
	base   string
	client *http.Client
}

func (m *RemoteMemberships) RoleIn(ctx context.Context, userID, homeID string) (Role, error) {
	ctx, cancel := context.WithTimeout(ctx, 200*time.Millisecond) // жорсткий дедлайн — не висіти
	defer cancel()

	url := fmt.Sprintf("%s/memberships?user=%s&home=%s", m.base, userID, homeID)
	req, _ := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	resp, err := m.client.Do(req)
	if err != nil {
		return "", err // мережа/таймаут → помилка нагору (авторизатор оберне її на deny)
	}
	defer resp.Body.Close()

	switch resp.StatusCode {
	case http.StatusNotFound:
		return "", nil // не член цього дому — це «нема ролі», а НЕ збій
	case http.StatusOK:
		var out struct {
			Role Role `json:"role"`
		}
		if err := json.NewDecoder(resp.Body).Decode(&out); err != nil {
			return "", err
		}
		return out.Role, nil
	default:
		return "", fmt.Errorf("membership svc: %s", resp.Status)
	}
}
