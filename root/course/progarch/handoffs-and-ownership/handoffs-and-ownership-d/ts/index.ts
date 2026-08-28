// TypeScript: CI Pull Request Ownership & Contract Gate
import { readFileSync } from 'fs';

interface PullRequestFile {
  filename: string;
  status: 'added' | 'modified' | 'deleted';
}

enum OwnershipMode {
  STRONG = 'STRONG',
  INNER_SOURCE = 'INNER_SOURCE'
}

interface Rule {
  prefix: string;
  ownerGroup: string;
  mode: OwnershipMode;
}

const RULES: Rule[] = [
  { prefix: 'src/core/security/', ownerGroup: 'sec-team', mode: OwnershipMode.STRONG },
  { prefix: 'src/services/telemetry/', ownerGroup: 'platform-team', mode: OwnershipMode.INNER_SOURCE },
  { prefix: 'api/contracts/', ownerGroup: 'arch-board', mode: OwnershipMode.STRONG }
];

export function validatePullRequest(
  changedFiles: PullRequestFile[],
  authorTeams: string[],
  isContractValidated: boolean
): { approved: boolean; reason: string } {
  for (const file of changedFiles) {
    const matchingRule = RULES.find(r => file.filename.startsWith(r.prefix));
    if (!matchingRule) continue;

    const isAuthorOwner = authorTeams.includes(matchingRule.ownerGroup);

    if (!isAuthorOwner) {
      if (matchingRule.mode === OwnershipMode.STRONG) {
        return {
          approved: false,
          reason: `Файл ${file.filename} захищено режимом STRONG. Потрібне обов'язкове ревю від ${matchingRule.ownerGroup}.`
        };
      }

      if (matchingRule.mode === OwnershipMode.INNER_SOURCE && !isContractValidated) {
        return {
          approved: false,
          reason: `Файл ${file.filename} змінено сторонньою командою, але автоматичні контрактні тести не пройдено.`
        };
      }
    }
  }

  return { approved: true, reason: 'Зміни схвалено автоматично або відповідні ревю присутні.' };
}
