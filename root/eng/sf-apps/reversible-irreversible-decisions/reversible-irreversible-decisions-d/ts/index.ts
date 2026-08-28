// TypeScript, ts-morph: обійти імпорти й упасти, якщо драйвер протік повз адаптер
import { Project } from "ts-morph";

const project = new Project({ tsConfigFilePath: "tsconfig.json" });
const leaks = project.getSourceFiles()
    .filter(f => !f.getFilePath().includes("/persistence/adapter/"))
    .filter(f => f.getImportDeclarations()
        .some(d => d.getModuleSpecifierValue().startsWith("pg")));

if (leaks.length > 0) {
    console.error("Драйвер бази протік повз адаптер:", leaks.map(f => f.getFilePath()));
    process.exit(1);           // завалюємо білд — шов порушено
}
