type Twin struct{ Dev, Desired, Reported string }

// Рефлекс звірки: не гарантія, а наполегливість. Кликати періодично у фоні.
func (c *NetworkCloud) Reconcile(ctx context.Context, tw *Twin) error {
	if tw.Reported != tw.Desired { // хмара й дім розійшлися — дошли бажане
		key := "set-" + tw.Dev + "-" + tw.Desired // СТАЛИЙ ключ наміру → повтор не задвоїть
		if _, err := c.Send(ctx, Command{Key: key, Kind: "setState", Dev: tw.Dev, Arg: tw.Desired}); err != nil {
			return err // не збіглося цього разу — спробуємо в наступному циклі
		}
	}
	got, err := c.ReadState(ctx, tw.Dev) // перечитай, що хмара тепер чує
	if err != nil {
		return err
	}
	tw.Reported = got
	return nil
}
