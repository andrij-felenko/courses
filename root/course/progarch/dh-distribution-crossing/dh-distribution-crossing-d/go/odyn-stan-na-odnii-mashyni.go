// Фоновий рефлекс звірки: не гарантія, а наполегливість.
func Reconcile(ctx context.Context, link CloudLink, twin *Twin) error {
	if twin.Reported != twin.Desired {                    // хмара й дім розійшлися
		if _, err := link.Send(ctx, SetState(twin.ID, twin.Desired)); err != nil {
			return err                                    // дошли бажане (ідемпотентно!)
		}
	}
	twin.Reported = link.Read(ctx, twin.ID)               // перечитай справжній стан
	return nil
}
