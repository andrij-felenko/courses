// scripts/check-team-boundaries.ts — Робочий TypeScript інспектор меж топології
import * as fs from 'fs';
import * as yaml from 'js-yaml';

interface TeamSpec {
  id: string;
  name: string;
  type: string;
  domain_contexts?: string[];
  max_cognitive_capacity_services?: number;
}

interface TopologyConfig {
  teams: TeamSpec[];
}

interface GraphEdge {
  source_context: string;
  target_context: string;
  type: 'api' | 'db_direct' | 'event';
  interaction_mode?: 'x-as-a-service' | 'facilitating' | 'collaboration';
  collaboration_duration_days?: number;
}

interface ArchitectureGraph {
  edges: GraphEdge[];
}

export function runSociotechnicalAudit(topologyPath: string, graphPath: string): void {
  const config = yaml.load(fs.readFileSync(topologyPath, 'utf8')) as TopologyConfig;
  const graph = JSON.parse(fs.readFileSync(graphPath, 'utf8')) as ArchitectureGraph;

  const contextToTeam = new Map<string, string>();
  const teamLimits = new Map<string, number>();
  const teamCounts = new Map<string, number>();

  for (const team of config.teams) {
    const limit = team.max_cognitive_capacity_services ?? 3;
    teamLimits.set(team.id, limit);
    teamCounts.set(team.id, 0);

    for (const ctx of team.domain_contexts || []) {
      contextToTeam.set(ctx, team.id);
      teamCounts.set(team.id, (teamCounts.get(team.id) || 0) + 1);
    }
  }

  const errors: string[] = [];
  const warnings: string[] = [];

  // Перевірка когнітивного ліміту
  teamCounts.forEach((count, teamId) => {
    const limit = teamLimits.get(teamId) || 3;
    if (count > limit) {
      errors.push(`КОГНІТИВНЕ ПЕРЕВАНТАЖЕННЯ: Команда '${teamId}' володіє ${count} контекстами (ліміт: ${limit})`);
    }
  });

  // Перевірка графа залежностей
  for (const edge of graph.edges) {
    const sourceTeam = contextToTeam.get(edge.source_context) || 'UNKNOWN';
    const targetTeam = contextToTeam.get(edge.target_context) || 'UNKNOWN';

    if (sourceTeam !== targetTeam && edge.type === 'db_direct') {
      errors.push(`КРИТИЧНА ЕРОЗІЯ: Прямий доступ до БД між ${sourceTeam} -> ${targetTeam} у контексті '${edge.target_context}'!`);
    }

    if (edge.interaction_mode === 'collaboration' && (edge.collaboration_duration_days || 0) > 21) {
      warnings.push(`ТРИВАЛИЙ COLLABORATION: ${sourceTeam} та ${targetTeam} співпрацюють ${edge.collaboration_duration_days} днів (ліміт 21)`);
    }
  }

  console.log('=' .repeat(60));
  console.log('РЕЗУЛЬТАТИ АУДИТУ СОЦІОТЕХНІЧНОЇ ТОПОЛОГІЇ');
  console.log('=' .repeat(60));

  if (warnings.length > 0) {
    console.log('\n⚠️ ПОПЕРЕДЖЕННЯ:');
    warnings.forEach((w) => console.log(`  - ${w}`));
  }

  if (errors.length > 0) {
    console.error('\n❌ ПОРУШЕННЯ ТА ЕРОЗІЯ:');
    errors.forEach((e) => console.error(`  - ${e}`));
    process.exit(1);
  }

  console.log('\n✅ Соціотехнічні межі дотримано успішно!');
}
