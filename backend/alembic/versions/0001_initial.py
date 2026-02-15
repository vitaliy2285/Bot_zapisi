"""initial

Revision ID: 0001_initial
Revises:
Create Date: 2026-02-15
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


booking_status = sa.Enum("pending", "confirmed", "paid", "no_show", "completed", name="bookingstatus")
booking_source = sa.Enum("telegram", "direct", name="bookingsource")
schedule_type = sa.Enum("work", "day_off", "break", name="scheduletype")
transaction_type = sa.Enum("payment", "refund", name="transactiontype")
payment_method = sa.Enum("yookassa", "cash", name="paymentmethod")


def upgrade() -> None:
    op.create_table(
        "businesses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("timezone", sa.String(length=64), nullable=False),
        sa.Column("currency", sa.String(length=8), nullable=False),
        sa.Column("settings_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "staff",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("business_id", sa.Integer(), sa.ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=100), nullable=False),
        sa.Column("avatar_url", sa.String(length=1024), nullable=True),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )
    op.create_index("ix_staff_business_id", "staff", ["business_id"])

    op.create_table(
        "services",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("business_id", sa.Integer(), sa.ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )
    op.create_index("ix_services_business_id", "services", ["business_id"])

    op.create_table(
        "clients",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("business_id", sa.Integer(), sa.ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("phone", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("telegram_id", sa.BigInteger(), nullable=True),
        sa.Column("loyalty_points", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_spent", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("business_id", "phone", name="uq_client_business_phone"),
    )
    op.create_index("ix_clients_business_id", "clients", ["business_id"])
    op.create_index("ix_clients_telegram_id", "clients", ["telegram_id"])

    op.create_table(
        "schedules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("staff_id", sa.Integer(), sa.ForeignKey("staff.id", ondelete="CASCADE"), nullable=False),
        sa.Column("schedule_type", schedule_type, nullable=False),
        sa.Column("day", sa.Date(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.CheckConstraint("end_time > start_time", name="ck_schedule_time_order"),
    )
    op.create_index("ix_schedules_staff_id", "schedules", ["staff_id"])
    op.create_index("ix_schedules_day", "schedules", ["day"])

    op.create_table(
        "bookings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("business_id", sa.Integer(), sa.ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("service_id", sa.Integer(), sa.ForeignKey("services.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("staff_id", sa.Integer(), sa.ForeignKey("staff.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("client_id", sa.Integer(), sa.ForeignKey("clients.id", ondelete="SET NULL"), nullable=True),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", booking_status, nullable=False),
        sa.Column("source", booking_source, nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("total_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_bookings_business_id", "bookings", ["business_id"])
    op.create_index("ix_bookings_service_id", "bookings", ["service_id"])
    op.create_index("ix_bookings_staff_id", "bookings", ["staff_id"])
    op.create_index("ix_bookings_client_id", "bookings", ["client_id"])
    op.create_index("ix_bookings_start_at", "bookings", ["start_at"])
    op.create_index("ix_bookings_end_at", "bookings", ["end_at"])

    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("booking_id", sa.Integer(), sa.ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("transaction_type", transaction_type, nullable=False),
        sa.Column("payment_method", payment_method, nullable=False),
        sa.Column("external_payment_id", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_transactions_booking_id", "transactions", ["booking_id"])
    op.create_index("ix_transactions_external_payment_id", "transactions", ["external_payment_id"])


def downgrade() -> None:
    op.drop_index("ix_transactions_external_payment_id", table_name="transactions")
    op.drop_index("ix_transactions_booking_id", table_name="transactions")
    op.drop_table("transactions")

    op.drop_index("ix_bookings_end_at", table_name="bookings")
    op.drop_index("ix_bookings_start_at", table_name="bookings")
    op.drop_index("ix_bookings_client_id", table_name="bookings")
    op.drop_index("ix_bookings_staff_id", table_name="bookings")
    op.drop_index("ix_bookings_service_id", table_name="bookings")
    op.drop_index("ix_bookings_business_id", table_name="bookings")
    op.drop_table("bookings")

    op.drop_index("ix_schedules_day", table_name="schedules")
    op.drop_index("ix_schedules_staff_id", table_name="schedules")
    op.drop_table("schedules")

    op.drop_index("ix_clients_telegram_id", table_name="clients")
    op.drop_index("ix_clients_business_id", table_name="clients")
    op.drop_table("clients")

    op.drop_index("ix_services_business_id", table_name="services")
    op.drop_table("services")

    op.drop_index("ix_staff_business_id", table_name="staff")
    op.drop_table("staff")

    op.drop_table("businesses")

    payment_method.drop(op.get_bind(), checkfirst=True)
    transaction_type.drop(op.get_bind(), checkfirst=True)
    booking_source.drop(op.get_bind(), checkfirst=True)
    booking_status.drop(op.get_bind(), checkfirst=True)
    schedule_type.drop(op.get_bind(), checkfirst=True)
