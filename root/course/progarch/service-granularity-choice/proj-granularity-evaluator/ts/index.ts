interface ServiceNode {
  name: string;
  internalComputeMs: number;
  p50NetMs: number;
  p99NetMs: number;
  failureRate: number;
}

interface TeamTopology {
  numEngineers: number;
  numServices: number;
  numRepositories: number;
  numTechStacks: number;
}

interface GranularityMetrics {
  totalP50Ms: number;
  totalP99Ms: number;
  tailImpactProbability: number;
  systemAvailability: number;
  cognitiveLoadIndex: number;
  isNanoServiceDanger: boolean;
}

function evaluateGranularity(chain: ServiceNode[], team: TeamTopology): GranularityMetrics {
  let sumCompute = 0;
  let sumNetP50 = 0;
  let sumNetP99Sq = 0;
  let availProd = 1.0;
  const K = chain.length;

  for (const node of chain) {
    sumCompute += node.internalComputeMs;
    sumNetP50 += node.p50NetMs;
    const netDeltaP99 = node.p99NetMs - node.p50NetMs;
    sumNetP99Sq += netDeltaP99 * netDeltaP99;
    availProd *= (1.0 - node.failureRate);
  }

  const totalP50Ms = sumCompute + sumNetP50;
  const totalP99Ms = totalP50Ms + Math.sqrt(sumNetP99Sq);
  const tailImpactProbability = 1.0 - Math.pow(0.99, K);
  
  const alphaRepo = 1.5;
  const betaPipe = 2.0;
  const gammaStack = 3.5;
  const capacityFactor = 5.0;

  const rawLoad = (team.numServices * alphaRepo) + 
                  (team.numRepositories * betaPipe) + 
                  (team.numTechStacks * gammaStack);

  const cognitiveLoadIndex = rawLoad / (team.numEngineers * capacityFactor);
  const netRatio = totalP50Ms > 0 ? (sumNetP50 / totalP50Ms) : 0;

  return {
    totalP50Ms,
    totalP99Ms,
    tailImpactProbability,
    systemAvailability: availProd,
    cognitiveLoadIndex,
    isNanoServiceDanger: netRatio > 0.60 || cognitiveLoadIndex > 1.2 || K > 10
  };
}
