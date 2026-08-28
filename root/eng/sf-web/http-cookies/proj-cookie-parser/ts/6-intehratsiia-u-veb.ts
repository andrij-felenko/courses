import Fastify from "fastify";
import { parseCookies, serializeSetCookie, CookieOptions } from "./cookie_engine";

const app = Fastify();

// Реєстрація декораторів запиту та відповіді
app.decorateRequest("cookies", null);
app.addHook("onRequest", async (req, reply) => {
  // Лінивий парсинг при першому виклику
  let cachedCookies: Map<string, string> | null = null;
  req.getCookie = (name: string): string | undefined => {
    if (!cachedCookies) {
      cachedCookies = parseCookies(req.headers.cookie);
    }
    return cachedCookies.get(name);
  };
});

app.decorateReply("setCookie", function(name: string, value: string, options?: CookieOptions) {
  const cookieStr = serializeSetCookie(name, value, options);
  this.header("Set-Cookie", cookieStr);
});
