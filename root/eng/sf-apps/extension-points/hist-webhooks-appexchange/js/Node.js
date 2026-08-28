// Той самий дзвінок, ідіоматично для Node.js.
const twilio = require("twilio");
const client = twilio(accountSid, authToken);

const call = await client.calls.create({
  to: "+380671234567",       // кому дзвонимо
  from: "+15551234567",      // з якого номера (виданого сервісом)
  url: "https://example.com/say-hello.xml",  // що казати, коли піднімуть
});

console.log(call.sid);        // ідентифікатор дзвінка
