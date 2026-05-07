from sqlglot import exp, parse_one
from sqlglot.errors import ParseError, UnsupportedError
from tests.dialects.test_dialect import Validator


class TestSynapse(Validator):
    dialect = "synapse"

    def test_synapse(self):
        # Synapse-specific: DISTRIBUTION properties
        self.validate_identity(
            "CREATE TABLE t (a INTEGER, b VARCHAR(100)) WITH (DISTRIBUTION = HASH(a))"
        )
        self.validate_identity(
            "CREATE TABLE t (a INTEGER, b VARCHAR(100)) WITH (DISTRIBUTION = ROUND_ROBIN)"
        )
        self.validate_identity(
            "CREATE TABLE t (a INTEGER, b VARCHAR(100)) WITH (DISTRIBUTION = REPLICATE)"
        )

        # Synapse-specific: CLUSTERED COLUMNSTORE INDEX
        self.validate_identity(
            "CREATE TABLE t (a INTEGER, b VARCHAR(100)) WITH (CLUSTERED COLUMNSTORE INDEX)"
        )
        self.validate_identity(
            "CREATE TABLE t (a INTEGER, b VARCHAR(100)) WITH (CLUSTERED COLUMNSTORE INDEX ORDER (a))"
        )

        # Synapse-specific: HEAP
        self.validate_identity("CREATE TABLE t (a INTEGER, b VARCHAR(100)) WITH (HEAP)")

        # Synapse-specific: CLUSTERED INDEX
        self.validate_identity(
            "CREATE TABLE t (a INTEGER, b VARCHAR(100)) WITH (CLUSTERED INDEX (a))"
        )
        self.validate_identity(
            "CREATE TABLE t (a INTEGER, b VARCHAR(100)) WITH (CLUSTERED INDEX (a ASC, b DESC))"
        )

        # Synapse-specific: PARTITION property
        self.validate_identity(
            "CREATE TABLE t (a INTEGER, b VARCHAR(100)) WITH (PARTITION (a RANGE LEFT FOR VALUES (1, 2, 3)))"
        )
        self.validate_identity(
            "CREATE TABLE t (a INTEGER, b VARCHAR(100)) WITH (PARTITION (a RANGE RIGHT FOR VALUES (1, 2, 3)))"
        )

        # Synapse-specific: LOCATION property
        self.validate_identity(
            "CREATE TABLE t (a INTEGER, b VARCHAR(100)) WITH (LOCATION = '/data/path')"
        )

        # Combined Synapse table options
        self.validate_identity(
            "CREATE TABLE t (a INTEGER, b VARCHAR(100)) WITH (DISTRIBUTION = HASH(a), CLUSTERED COLUMNSTORE INDEX)"
        )
        self.validate_identity(
            "CREATE TABLE t (a INTEGER, b VARCHAR(100)) WITH (DISTRIBUTION = ROUND_ROBIN, HEAP)"
        )