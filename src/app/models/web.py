from __future__ import annotations

from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, relationship

from app.models.base import Base


class Page(Base):
    __tablename__ = "web_page"

    url: Mapped[str] = sa.Column(sa.String, primary_key=True)

    status: Mapped[int] = sa.Column(sa.Integer, default=0, nullable=False)
    content_type: Mapped[str] = sa.Column(sa.String, default="", nullable=False)
    lang: Mapped[str] = sa.Column(sa.String, default="", nullable=False)


class ScreenShot(Base):
    __tablename__ = "web_screenshot"

    url: Mapped[str] = sa.Column(
        sa.String, sa.ForeignKey("web_page.url"), primary_key=True
    )
    timestamp: Mapped[datetime] = sa.Column(
        sa.DateTime, default=datetime.utcnow, nullable=False
    )

    page: relationship[Page] = relationship("Page", back_populates="screenshots")

    screenshot_id: Mapped[str] = sa.Column(sa.String, default="", nullable=False)
