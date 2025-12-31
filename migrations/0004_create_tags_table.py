"""Auto-generated migration.

Created: 2025-12-30 12:05:56
"""

depends_on = "0003_create_comments_table"


def upgrade(ctx):
    """Apply migration."""
    ctx.create_table(
        "tags",
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
                'name': 'name',
                'python_type': 'str',
                'db_type': None,
                'nullable': False,
                'primary_key': False,
                'unique': True,
                'default': None,
                'auto_increment': False
            },
            {
                'name': 'slug',
                'python_type': 'str',
                'db_type': None,
                'nullable': False,
                'primary_key': False,
                'unique': True,
                'default': None,
                'auto_increment': False
            }
        ],
    )
    ctx.create_table(
        "post_tags",
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
                'name': 'post_id',
                'python_type': 'int',
                'db_type': None,
                'nullable': True,
                'primary_key': False,
                'unique': False,
                'default': None,
                'auto_increment': False
            },
            {
                'name': 'tag_id',
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
                'name': 'fk_post_tags_post_id',
                'columns': [
                    'post_id'
                ],
                'ref_table': 'posts',
                'ref_columns': [
                    'id'
                ],
                'on_delete': 'CASCADE',
                'on_update': 'CASCADE'
            },
            {
                'name': 'fk_post_tags_tag_id',
                'columns': [
                    'tag_id'
                ],
                'ref_table': 'tags',
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
    ctx.drop_table("post_tags")
    ctx.drop_table("tags")
