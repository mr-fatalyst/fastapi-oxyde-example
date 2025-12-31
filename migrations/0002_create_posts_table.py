"""Auto-generated migration.

Created: 2025-12-30 11:49:05
"""

depends_on = "0001_create_users_table"


def upgrade(ctx):
    """Apply migration."""
    ctx.create_table(
        "posts",
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
                'name': 'title',
                'python_type': 'str',
                'db_type': None,
                'nullable': False,
                'primary_key': False,
                'unique': False,
                'default': None,
                'auto_increment': False
            },
            {
                'name': 'content',
                'python_type': 'str',
                'db_type': None,
                'nullable': False,
                'primary_key': False,
                'unique': False,
                'default': None,
                'auto_increment': False
            },
            {
                'name': 'published',
                'python_type': 'bool',
                'db_type': None,
                'nullable': False,
                'primary_key': False,
                'unique': False,
                'default': '0',
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
            },
            {
                'name': 'updated_at',
                'python_type': 'datetime',
                'db_type': None,
                'nullable': True,
                'primary_key': False,
                'unique': False,
                'default': 'CURRENT_TIMESTAMP',
                'auto_increment': False
            },
            {
                'name': 'author_id',
                'python_type': 'int',
                'db_type': None,
                'nullable': True,
                'primary_key': False,
                'unique': False,
                'default': None,
                'auto_increment': False
            }
        ],
        foreign_keys=[
            {
                'name': 'fk_posts_author_id',
                'columns': [
                    'author_id'
                ],
                'ref_table': 'users',
                'ref_columns': [
                    'id'
                ],
                'on_delete': 'CASCADE',
                'on_update': 'CASCADE'
            }
        ],
    )


def downgrade(ctx):
    """Revert migration."""
    ctx.drop_table("posts")
