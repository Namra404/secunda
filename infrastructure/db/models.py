import uuid
from typing import Optional


from sqlalchemy import (
    String, ForeignKey, UniqueConstraint,
    Table, Column, Index,
)

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase


class Base(DeclarativeBase):
    ...


organization_activities = Table(
    "organization_activities",
    Base.metadata,
    Column("organization_id", UUID(as_uuid=True),
           ForeignKey("organizations.id", ondelete="CASCADE"), primary_key=True),
    Column("activity_id", UUID(as_uuid=True),
           ForeignKey("activities.id", ondelete="CASCADE"), primary_key=True),
)

class BuildingModel(Base):
    __tablename__ = "buildings"
    __table_args__ = (
        Index("idx_buildings_latitude_longitude", "latitude", "longitude"),
    )
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    latitude: Mapped[float] = mapped_column(nullable=False)
    longitude: Mapped[float] = mapped_column(nullable=False)

    organizations: Mapped[list["OrganizationModel"]] = relationship(back_populates="building")



class OrganizationModel(Base):
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True, unique=True)

    building_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("buildings.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    building: Mapped["BuildingModel"] = relationship(back_populates="organizations")


    phones: Mapped[list["OrganizationPhoneModel"]] = relationship(
        back_populates="organization",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


    activities: Mapped[list["ActivityModel"]] = relationship(
        secondary=organization_activities,
        back_populates="organizations",
        lazy="selectin",
    )


class OrganizationPhoneModel(Base):
    __tablename__ = "organization_phones"
    __table_args__ = (
        UniqueConstraint("organization_id", "phone", name="uq_org_phone_unique"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        index=True,
    )

    phone: Mapped[str] = mapped_column(String(32), nullable=False, index=True)

    organization: Mapped["OrganizationModel"] = relationship(back_populates="phones")


class ActivityModel(Base):
    __tablename__ = "activities"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("activities.id", ondelete="RESTRICT"),
        nullable=True,
    )

    parent: Mapped[Optional["ActivityModel"]] = relationship(
        remote_side="ActivityModel.id",

    )

    organizations: Mapped[list["OrganizationModel"]] = relationship(
        secondary=organization_activities,
        back_populates="activities",
        lazy="selectin",
    )