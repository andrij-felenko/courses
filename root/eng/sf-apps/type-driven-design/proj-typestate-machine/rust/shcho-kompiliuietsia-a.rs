let closed = Conn::<Closed>::new("device.local:6000");

// closed.request("x");    // E0599: у Conn<Closed> немає методу request
let open = closed.open();  // Closed → Open; closed ПЕРЕМІЩЕНО в open

// closed.open();          // E0382: use of moved value `closed`
// open.request("x");      // E0599: у Conn<Open> ще немає request (не автентифіковані)

let mut authed = open.authenticate("s3cr3t").ok().unwrap();  // Open → Authed; open спожито

// open.close();           // E0382: use of moved value `open`
let _r1 = authed.request("GET /telemetry");   // ✓ лише тут request живе
let _r2 = authed.request("GET /status");      // ✓ &mut self — скільки завгодно разів

let _back = authed.close();  // Authed → Closed; authed спожито
// authed.request("x");     // E0382: use of moved value `authed` — стале після close()
