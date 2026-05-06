from sqlglot.dialects.tsql import TSQL
from sqlglot.generators.synapse import SynapseGenerator
from sqlglot.parsers.synapse import SynapseParser


class Synapse(TSQL):
    """Azure Synapse Analytics SQL dialect (TSQL sub-dialect)."""

    Parser = SynapseParser
    Generator = SynapseGenerator
