type Handler = (req: Request) => Response;
type Link    = (next: Handler) => Handler;

// Конвеєрний підпис (req, next) — це та сама Link, лише з аргументами разом
type Middleware = (req: Request, next: Handler) => Response;
const flip = (mw: Middleware): Link => (next) => (req) => mw(req, next);

function build(links: Link[], base: Handler): Handler {
  return links.reduceRight((rest, link) => link(rest), base);
}
