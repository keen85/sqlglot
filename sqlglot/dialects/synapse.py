from sqlglot import exp
from sqlglot.dialects.tsql import TSQL
from sqlglot.expressions.synapse import (
    ClusteredColumnstoreIndexProperty,
    ClusteredIndexProperty,
    DistributionProperty,
    HashDistribution,
    HeapProperty,
    ReplicateDistribution,
    RoundRobinDistribution,
    SynapsePartitionProperty,
)
from sqlglot.generators.synapse import SynapseGenerator
from sqlglot.parsers.synapse import SynapseParser
from sqlglot.tokens import TokenType


# ── Dialect Definition ─────────────────────────────────────────────────────


class Synapse(TSQL):
    """Azure Synapse Analytics SQL dialect (TSQL sub-dialect)."""

    Parser = SynapseParser
    Generator = SynapseGenerator