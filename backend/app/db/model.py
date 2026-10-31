import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    crm_customer_id: Mapped[str | None] = mapped_column(
        String(100),
        unique=True,
        nullable=True,
    )

    zoho_customer_id: Mapped[str | None] = mapped_column(
        String(100),
        unique=True,
        nullable=True,
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(50))
    currency: Mapped[str] = mapped_column(
        String(10),
        default="AED",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    deals: Mapped[list["Deal"]] = relationship(
        back_populates="customer"
    )


class Deal(Base):
    __tablename__ = "deals"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    crm_deal_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    customer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("customers.id"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    stage: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        String(10),
        default="AED",
        nullable=False,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
    )

    tax_rate: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=Decimal("5.00"),
        nullable=False,
    )

    closed_won_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    customer: Mapped["Customer"] = relationship(
        back_populates="deals"
    )

    sales_order: Mapped["SalesOrder | None"] = relationship(
        back_populates="deal",
        uselist=False,
    )


class SalesOrder(Base):
    __tablename__ = "sales_orders"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    deal_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("deals.id"),
        unique=True,
        nullable=False,
    )

    zoho_sales_order_id: Mapped[str | None] = mapped_column(
        String(100),
        unique=True,
    )

    order_number: Mapped[str | None] = mapped_column(
        String(100)
    )

    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
    )

    tax_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
    )

    total: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        String(10),
        default="AED",
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="created",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    deal: Mapped["Deal"] = relationship(
        back_populates="sales_order"
    )

    invoices: Mapped[list["Invoice"]] = relationship(
        back_populates="sales_order"
    )


class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    sales_order_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sales_orders.id"),
        nullable=False,
    )

    zoho_invoice_id: Mapped[str | None] = mapped_column(
        String(100),
        unique=True,
    )

    invoice_number: Mapped[str | None] = mapped_column(
        String(100)
    )

    milestone_percentage: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
    )

    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
    )

    tax_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
    )

    total: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
    )

    amount_paid: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        default=Decimal("0.00"),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="draft",
        nullable=False,
    )

    due_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    sales_order: Mapped["SalesOrder"] = relationship(
        back_populates="invoices"
    )

    payments: Mapped[list["Payment"]] = relationship(
        back_populates="invoice"
    )


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    zoho_payment_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    invoice_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("invoices.id"),
        nullable=False,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        String(10),
        default="AED",
        nullable=False,
    )

    payment_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    invoice: Mapped["Invoice"] = relationship(
        back_populates="payments"
    )


class IntegrationEvent(Base):
    __tablename__ = "integration_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    event_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    external_object_id: Mapped[str | None] = mapped_column(
        String(100)
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="received",
        nullable=False,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )


class IntegrationLog(Base):
    __tablename__ = "integration_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    deal_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("deals.id"),
        nullable=True,
    )

    event_id: Mapped[str | None] = mapped_column(
        String(255)
    )

    system: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    operation: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    method: Mapped[str | None] = mapped_column(
        String(10)
    )

    endpoint: Mapped[str | None] = mapped_column(
        String(500)
    )

    status_code: Mapped[int | None] = mapped_column(
        Integer
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    request_summary: Mapped[str | None] = mapped_column(
        Text
    )

    response_summary: Mapped[str | None] = mapped_column(
        Text
    )

    error_message: Mapped[str | None] = mapped_column(
        Text
    )

    duration_ms: Mapped[int | None] = mapped_column(
        Integer
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


class SyncState(Base):
    __tablename__ = "sync_states"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    resource_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    resource_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    last_synced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

    last_external_updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        nullable=False,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text
    )

    __table_args__ = (
        UniqueConstraint(
            "resource_type",
            "resource_id",
            "source",
            name="uq_sync_resource_source",
        ),
    )