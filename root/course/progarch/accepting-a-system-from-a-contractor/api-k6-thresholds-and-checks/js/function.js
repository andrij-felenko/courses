export const options = {
  scenarios: {
    contractor_acceptance_gate: {
      executor: 'ramping-arrival-rate',
      startRate: 50,
      timeUnit: '1s',
      preAllocatedVUs: 100,
      maxVUs: 500,
      stages: [
        { target: 200, duration: '2m' },   // Розгін до 200 RPS
        { target: 200, duration: '10m' },  // Стабільне робоче плато за контрактом
        { target: 350, duration: '3m' },   // Стресове навантаження вище норми
        { target: 0, duration: '1m' },     // Плавне завершення та охолодження
      ],
    },
  },
};

export default function () {
  // Виконання тестових HTTP-запитів до цільового API
}
