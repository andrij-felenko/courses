#!/usr/bin/env node
// Перевірка карти контекстів як код. Падає (exit 1) на забороненій стрілці.
import { readFileSync, readdirSync, statSync } from "node:fs";
import { join, relative, sep } from "node:path";

// 1. ОГОЛОШЕНА карта: контекст -> корінь + дозволені низові з ТИПОМ зв'язку.
const CONTEXTS = {
  sales:   { root: "src/sales",   allow: { billing: "acl" } },
  stock:   { root: "src/stock",   allow: { sales: "customer-supplier" } },
  billing: { root: "src/billing", allow: {} },
  shared:  { root: "src/shared",  allow: {}, sharedKernel: true },
};

const norm = (p) => p.split(sep).join("/");

function ownerOf(path) {                       // власник — за найдовшим збігом кореня
  let best = null, bestLen = -1;
  const p = norm(path);
  for (const [name, meta] of Object.entries(CONTEXTS)) {
    const r = meta.root;
    if ((p === r || p.startsWith(r + "/")) && r.length > bestLen) {
      best = name; bestLen = r.length;
    }
  }
  return best;
}

function* walk(dir) {
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry);
    if (statSync(full).isDirectory()) yield* walk(full);
    else if (/\.(m?[jt]sx?)$/.test(entry)) yield full;
  }
}

// цілі з import ... from "X", import("X"), require("X"), export ... from "X"
const SPEC = /(?:import[\s\S]*?from|import|export[\s\S]*?from|require)\s*\(?\s*["']([^"']+)["']/g;

function resolveToCtx(spec, fromRel) {
  if (!spec.startsWith(".")) return null;      // пакет із node_modules — не межа
  const dir = fromRel.split("/").slice(0, -1).join("/");
  const stack = [];
  for (const seg of (dir + "/" + spec).split("/")) {
    if (seg === "." || seg === "") continue;
    if (seg === "..") stack.pop();
    else stack.push(seg);                       // грубий resolve відносного шляху
  }
  return ownerOf(stack.join("/"));
}

function discoveredEdges(srcRoot) {
  const edges = new Set();
  for (const file of walk(srcRoot)) {
    const rel = "src/" + norm(relative(srcRoot, file));
    const frm = ownerOf(rel);
    if (!frm) continue;
    for (const m of readFileSync(file, "utf8").matchAll(SPEC)) {
      const to = resolveToCtx(m[1], rel);
      if (to && to !== frm) edges.add(`${frm} ${to}`);
    }
  }
  return [...edges].map((e) => e.split(" "));
}

const allowed = (frm, to) =>
  CONTEXTS[to]?.sharedKernel === true || to in CONTEXTS[frm].allow;

function main(src) {
  const edges = discoveredEdges(src);
  const violations = edges.filter(([f, t]) => !allowed(f, t)).sort();
  if (violations.length === 0) {
    console.log(`карта тримається: ${edges.length} стрілок, усі оголошені`);
    return 0;
  }
  console.error("ЗАБОРОНЕНІ стрілки через межу (нема на карті):");
  for (const [f, t] of violations)
    console.error(`  ${f} -> ${t}   (дозволено з ${f}: ${Object.keys(CONTEXTS[f].allow).join(", ") || "—"})`);
  return 1;
}

process.exit(main(process.argv[2] ?? "src"));
