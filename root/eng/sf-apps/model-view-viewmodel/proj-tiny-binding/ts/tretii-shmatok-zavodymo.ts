// ── 3. Модель подання й дві прив'язки ──
const vm = observable({ temperature: 22, error: '' });

// «обчислювана» властивість — просто слухач, що пише в сусідню
vm.signals.on('temperature', () => {
  const t = vm.temperature;
  vm.error = (Number.isFinite(t) && t >= 5 && t <= 30) ? '' : 'дозволено 5…30';
});

const stop = [
  bind(document.querySelector('#temp')  as HTMLInputElement, vm, 'temperature', asNumber),
  bind(document.querySelector('#error') as HTMLInputElement, vm, 'error', asText),
];

vm.temperature = 35;        // поле саме показало «35», підказка — «дозволено 5…30»
                            // друк у полі так само сам оновлює vm.temperature

stop.forEach(off => off()); // зв'язки зняті: віджети можна викидати
