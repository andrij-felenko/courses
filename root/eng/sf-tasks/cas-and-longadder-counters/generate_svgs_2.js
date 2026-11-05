const fs = require('fs');
const path = require('path');

const files = {
'cas-loop-contention-storm.svg': ['CAS Loop Contention Storm', 'Cache line storm during concurrent CAS increments by multiple CPU cores.', '<rect x="400" y="350" width="160" height="60" fill="#f4f6f8" stroke="#d0d7de" stroke-width="2" rx="4"/><text x="480" y="385" font-size="14" text-anchor="middle">Target Variable</text><path d="M480 300 L480 340" fill="none" stroke="#c0392b" stroke-width="2" marker-end="url(#arr)"/><rect x="400" y="150" width="160" height="150" fill="#fdecea" stroke="#c0392b" stroke-width="2" rx="4"/><text x="480" y="200" font-size="14" text-anchor="middle" fill="#c0392b">Bus Storm</text><text x="480" y="230" font-size="12" text-anchor="middle">Contention Traffic</text>'],
'longadder-striped-cells-architecture.svg': ['LongAdder Striped Cells Architecture', 'Architecture of LongAdder with split base and aligned Cell memory locations.', '<rect x="400" y="150" width="160" height="60" fill="#eaf0fd" stroke="#2457d6" stroke-width="2" rx="4"/><text x="480" y="185" font-size="14" text-anchor="middle">Base Value</text><rect x="250" y="280" width="460" height="80" fill="#f4f6f8" stroke="#d0d7de" stroke-width="2" rx="4"/><text x="480" y="310" font-size="14" text-anchor="middle">Cell Array</text><rect x="270" y="320" width="100" height="30" fill="#fff" stroke="#2457d6"/><text x="320" y="340" font-size="12" text-anchor="middle">Cell 0</text><rect x="390" y="320" width="100" height="30" fill="#fff" stroke="#2457d6"/><text x="440" y="340" font-size="12" text-anchor="middle">Cell 1</text><rect x="590" y="320" width="100" height="30" fill="#fff" stroke="#2457d6"/><text x="640" y="340" font-size="12" text-anchor="middle">Cell N</text>'],
'arm-exclusive-monitor-ll-sc.svg': ['ARM Exclusive Monitor LL/SC', 'Functioning of the hardware exclusive monitor in a microcontroller during read/modify operations.', '<rect x="300" y="200" width="360" height="120" fill="#f4f6f8" stroke="#d0d7de" stroke-width="2" rx="4"/><text x="480" y="240" font-size="16" text-anchor="middle">Exclusive Monitor</text><path d="M200 150 L300 200" fill="none" stroke="#2457d6" stroke-width="2" marker-end="url(#arr)"/><text x="200" y="140" font-size="14">Load-Link</text><path d="M480 120 L480 190" fill="none" stroke="#c0392b" stroke-width="2" marker-end="url(#arr)"/><text x="480" y="110" font-size="14" text-anchor="middle" fill="#c0392b">Store-Conditional</text>'],
'rtos-isr-lockfree-counter.svg': ['RTOS ISR Lock-Free Counter', 'Safe accumulation of statistical metrics in microcontrollers from high-priority ISRs and RTOS tasks without blocking primitives.', '<rect x="350" y="150" width="260" height="160" fill="#e9f7ef" stroke="#27ae60" stroke-width="2" rx="8"/><text x="480" y="190" font-size="16" text-anchor="middle">Lock-Free Counter</text><text x="480" y="230" font-size="14" text-anchor="middle">ISR Safe Accumulation</text>']
};

for (const [name, [header, subheader, body]] of Object.entries(files)) {
  const svg = `<svg viewBox="0 0 960 480" width="960" height="480" font-family="Segoe UI, Roboto, Helvetica, Arial, sans-serif" xmlns="http://www.w3.org/2000/svg">
<rect width="960" height="480" fill="white"/>
<defs>
<marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto">
<path d="M 0 0 L 10 5 L 0 10 z" fill="currentColor"/>
</marker>
</defs>
<text x="480" y="40" font-size="18" font-weight="bold" fill="#1a1a1a" text-anchor="middle">${header}</text>
<text x="480" y="65" font-size="13" fill="#6b7280" text-anchor="middle">${subheader}</text>
${body}
</svg>`;
  fs.writeFileSync(path.join('E:/develop/courses/root/eng/sf-tasks/cas-and-longadder-counters/img', name), svg, 'utf-8');
}
console.log('Done additional');
