// validator.ts — Архітектурний валідатор на TypeScript / Node.js
import * as fs from 'fs';

interface Relationship {
    source: string;
    destination: string;
    description: string;
    technology: string;
}

interface WorkspaceModel {
    relationships: Relationship[];
    containers: { id: string; name: string; tags: string[] }[];
}

export function validateArchitecture(modelJsonPath: string): { passed: boolean; errors: string[] } {
    const raw = fs.readFileSync(modelJsonPath, 'utf-8');
    const model: WorkspaceModel = JSON.parse(raw);
    const errors: string[] = [];

    for (const rel of model.relationships) {
        // Правило 1: Перевірка обов'язковості опису протоколу
        if (!rel.technology || rel.technology.trim().length === 0) {
            errors.push(`[RULE-1] Зв'язок "${rel.source} -> ${rel.destination}" (${rel.description}) не має вказаного протоколу!`);
        }

        // Правило 2: Захист від прямого доступу UI до баз даних
        if (rel.source.includes('webSpa') && rel.destination.includes('Db')) {
            errors.push(`[RULE-2 CRITICAL] Виявлено прямий доступ UI "${rel.source}" до бази даних "${rel.destination}" в обхід API Gateway!`);
        }

        // Правило 3: Принцип Single Writer для бази даних платежів
        if (rel.destination.includes('paymentDb') && !rel.source.includes('paymentService')) {
            errors.push(`[RULE-3] Порушення ізоляції даних: сторонній контейнер "${rel.source}" намагається напряму читати/писати в "${rel.destination}".`);
        }
    }

    return {
        passed: errors.length === 0,
        errors
    };
}

// Точка входу
const result = validateArchitecture('./architecture/output/workspace.json');
if (!result.passed) {
    console.error(`❌ Архітектурний аудит провалено (${result.errors.length} дефектів):`);
    result.errors.forEach(err => console.error(`  - ${err}`));
    process.exit(1);
} else {
    console.log('✅ Архітектурну модель верифіковано: усі інваріанти виконано.');
}
