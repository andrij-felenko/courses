type Twin = { dev: string; desired: string; reported: string };

// Рефлекс звірки: не гарантія, а наполегливість. Кликати періодично у фоні.
async function reconcile(cloud: NetworkCloud, tw: Twin): Promise<void> {
  if (tw.reported !== tw.desired) {                 // хмара й дім розійшлися
    const key = `set-${tw.dev}-${tw.desired}`;      // сталий ключ наміру → повтор не задвоїть
    await cloud.send({ key, kind: "setState", dev: tw.dev, arg: tw.desired });
  }
  tw.reported = await cloud.readState(tw.dev);      // перечитай, що хмара тепер чує
}
