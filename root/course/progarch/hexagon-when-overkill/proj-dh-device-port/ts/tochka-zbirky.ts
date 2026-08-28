const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

async function tick(device: Device, heating: boolean): Promise<boolean> {
  const t = await device.temperature();   // read
  heating = shouldHeat(t, heating);        // decide — чисте правило
  await device.heat(heating);              // act
  return heating;
}

async function run(device: Device): Promise<void> {  // прод: вічний цикл, як серце v0
  let heating = false;
  while (true) {
    heating = await tick(device, heating);
    await sleep(30_000);
  }
}

function buildDevice(): Device {          // ТОЧКА ЗБІРКИ — одне місце, що знає, хто за портом
  if (process.env.DH_ENV === "prod")
    return new RealDevice("28-0119a1b2c3d4", "http://192.168.1.50");
  return new FakeDevice();                // усюди, крім проду, — дім у пам'яті
}

run(buildDevice());                       // у проді сюди стане RealDevice — і код вище не здригнеться
