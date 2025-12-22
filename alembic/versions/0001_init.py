"""init

Revision ID: 0001_init
Revises:
Create Date: 2025-12-22
"""

from alembic import op
import sqlalchemy as sa

revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        "organizations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False),
    )
    op.create_index("ix_organizations_name", "organizations", ["name"], unique=True)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("org_id", sa.Integer(), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False, server_default="viewer"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_org_id", "users", ["org_id"])

    op.create_table(
        "tags",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("org_id", sa.Integer(), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.UniqueConstraint("org_id", "name", name="uq_tags_org_name"),
    )
    op.create_index("ix_tags_org_id", "tags", ["org_id"])
    op.create_index("ix_tags_name", "tags", ["name"])

    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("org_id", sa.Integer(), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("github_url", sa.String(length=500), nullable=True),
        sa.Column("is_public", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_projects_org_id", "projects", ["org_id"])
    op.create_index("ix_projects_owner_id", "projects", ["owner_id"])
    op.create_index("ix_projects_title", "projects", ["title"])

    op.create_table(
        "project_tags",
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id"), primary_key=True),
        sa.Column("tag_id", sa.Integer(), sa.ForeignKey("tags.id"), primary_key=True),
    )

    op.create_table(
        "activity_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("org_id", sa.Integer(), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("actor_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("entity", sa.String(length=50), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_activity_logs_org_id", "activity_logs", ["org_id"])
    op.create_index("ix_activity_logs_actor_user_id", "activity_logs", ["actor_user_id"])
    op.create_index("ix_activity_logs_entity_id", "activity_logs", ["entity_id"])

def downgrade() -> None:
    op.drop_index("ix_activity_logs_entity_id", table_name="activity_logs")
    op.drop_index("ix_activity_logs_actor_user_id", table_name="activity_logs")
    op.drop_index("ix_activity_logs_org_id", table_name="activity_logs")
    op.drop_table("activity_logs")

    op.drop_table("project_tags")

    op.drop_index("ix_projects_title", table_name="projects")
    op.drop_index("ix_projects_owner_id", table_name="projects")
    op.drop_index("ix_projects_org_id", table_name="projects")
    op.drop_table("projects")

    op.drop_index("ix_tags_name", table_name="tags")
    op.drop_index("ix_tags_org_id", table_name="tags")
    op.drop_table("tags")

    op.drop_index("ix_users_org_id", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

    op.drop_index("ix_organizations_name", table_name="organizations")
    op.drop_table("organizations")
