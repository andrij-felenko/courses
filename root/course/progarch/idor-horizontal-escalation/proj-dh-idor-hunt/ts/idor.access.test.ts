// idor.access.test.ts — той самий перебір, тепер як регресійний вартовий
import { describe, it, expect, beforeAll } from "vitest";
import request from "supertest";
import { app } from "../app";

let cookie4021: string;      // сесія мешканця #4021
const OWN      = 4021;       // дім, що НАЛЕЖИТЬ #4021
const NEIGHBOR = 4022;       // дім сусіда — ІСНУЄ, але чужий
const ABSENT   = 999999;     // дому не існує зовсім
const SHARED   = 4055;       // дім, куди #4021 УПУЩЕНИЙ як член родини

beforeAll(async () => { cookie4021 = await loginAs(4021); });

describe("device-API не пускає горизонтально", () => {
  it("власний дім — 200", async () => {
    const res = await request(app).get(`/api/homes/${OWN}/devices`).set("Cookie", cookie4021);
    expect(res.status).toBe(200);
  });

  it("дім, куди впущений членом родини — 200", async () => {
    const res = await request(app).get(`/api/homes/${SHARED}/devices`).set("Cookie", cookie4021);
    expect(res.status).toBe(200);            // гілку «упущений» не можна зламати латкою
  });

  // НЕСУЧИЙ негатив: сусідський дім ІСНУЄ, та не наш → мусить бути 404, не 200 і не 403
  it("чужий ІСНУЮЧИЙ дім — 404 (не 200 і не 403)", async () => {
    const res = await request(app).get(`/api/homes/${NEIGHBOR}/devices`).set("Cookie", cookie4021);
    expect(res.status).toBe(404);
  });

  it("неіснуючий дім — теж 404 (не відрізнити від чужого)", async () => {
    const res = await request(app).get(`/api/homes/${ABSENT}/devices`).set("Cookie", cookie4021);
    expect(res.status).toBe(404);
  });

  // цілий перебір, як у нападника: жоден чужий id не сміє тектити
  it("перебір сусідів не тече: кожен чужий id → 404", async () => {
    for (let id = OWN + 1; id <= OWN + 30; id++) {
      if (id === SHARED) continue;           // цей нам свідомо відкрито
      const res = await request(app).get(`/api/homes/${id}/devices`).set("Cookie", cookie4021);
      expect(res.status, `home ${id} має бути закритий`).toBe(404);
    }
  });
});
