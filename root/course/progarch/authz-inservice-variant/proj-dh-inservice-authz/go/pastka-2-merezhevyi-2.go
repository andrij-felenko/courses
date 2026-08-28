func (a *InServiceAuthorizer) Can(ctx context.Context, u User, action Action, r Resource) (bool, error) {
	role, err := a.memberships.RoleIn(ctx, u.ID, r.HomeID)
	if err != nil {
		return false, err // збій членства → DENY (fail-closed); помилку — в лог і метрику
	}
	if role == "" {
		return false, nil // не член цього дому → deny (IDOR закрито)
	}
	return actionsByRole[role][action], nil // відмова за замовчуванням: нема запису → false
}
