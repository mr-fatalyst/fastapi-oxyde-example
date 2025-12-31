"""Auto-generated migration.

Created: 2025-12-30 11:45:41
"""

depends_on = None


def upgrade(ctx):
    """Apply migration."""
    ctx.create_table(
        "users",
        fields=[
            {
                'name': 'id',
                'python_type': 'int',
                'db_type': None,
                'nullable': True,
                'primary_key': True,
                'unique': False,
                'default': None,
                'auto_increment': False
            },
            {
                'name': 'username',
                'python_type': 'str',
                'db_type': None,
                'nullable': False,
                'primary_key': False,
                'unique': True,
                'default': None,
                'auto_increment': False
            },
            {
                'name': 'email',
                'python_type': 'str',
                'db_type': None,
                'nullable': False,
                'primary_key': False,
                'unique': True,
                'default': None,
                'auto_increment': False
            },
            {
                'name': 'created_at',
                'python_type': 'datetime',
                'db_type': None,
                'nullable': True,
                'primary_key': False,
                'unique': False,
                'default': 'CURRENT_TIMESTAMP',
                'auto_increment': False
            }
        ],
    )


def downgrade(ctx):
    """Revert migration."""
    ctx.drop_table("users")
