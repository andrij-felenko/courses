// ❌ БАГ: бюджет на настінному часі
type WallBudget struct {
	now      func() time.Time // настінний годинник; впорскуємо, щоб відтворити стрибок
	deadline time.Time
}

func NewWallBudget(now func() time.Time, total time.Duration) WallBudget {
	return WallBudget{now: now, deadline: now().Add(total)} // дедлайн = настінне «тепер» + 30с
}

func (b WallBudget) Remaining() time.Duration {
	return b.deadline.Sub(b.now()) // настінне − настінне: беззахисне перед стрибком
}
