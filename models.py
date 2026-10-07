from datetime import datetime
from sqlalchemy import String, Float, Integer, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(200))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Health profile
    has_asthma: Mapped[bool] = mapped_column(Boolean, default=False)
    has_cardiovascular: Mapped[bool] = mapped_column(Boolean, default=False)
    has_elderly_child: Mapped[bool] = mapped_column(Boolean, default=False)
    athlete_mode: Mapped[bool] = mapped_column(Boolean, default=False)
    aqi_alert_threshold: Mapped[int] = mapped_column(Integer, default=100)
    aqi_standard: Mapped[str] = mapped_column(String(10), default="NAQI")  # NAQI | AQI | WHO
    temperature_unit: Mapped[str] = mapped_column(String(1), default="C")  # C | F
    notify_push: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_email: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_morning_brief: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_exercise_window: Mapped[bool] = mapped_column(Boolean, default=False)
    notify_rain_alert: Mapped[bool] = mapped_column(Boolean, default=True)

    locations: Mapped[list["SavedLocation"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    plans: Mapped[list["Plan"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class SavedLocation(Base):
    __tablename__ = "saved_locations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    label: Mapped[str] = mapped_column(String(100))           # e.g. "Home", "Office"
    city: Mapped[str] = mapped_column(String(150))
    country: Mapped[str] = mapped_column(String(100), default="IN")
    lat: Mapped[float] = mapped_column(Float)
    lon: Mapped[float] = mapped_column(Float)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    is_indoor: Mapped[bool] = mapped_column(Boolean, default=False)
    sensor_id: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="locations")


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    activity_type: Mapped[str] = mapped_column(String(100))
    location_label: Mapped[str | None] = mapped_column(String(200))
    lat: Mapped[float | None] = mapped_column(Float)
    lon: Mapped[float | None] = mapped_column(Float)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime)
    notes: Mapped[str | None] = mapped_column(Text)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    is_shared: Mapped[bool] = mapped_column(Boolean, default=False)
    share_token: Mapped[str | None] = mapped_column(String(64), unique=True, index=True)
    # Snapshot of forecast at time of planning
    forecast_aqi: Mapped[int | None] = mapped_column(Integer)
    forecast_weather: Mapped[dict | None] = mapped_column(JSON)
    risk_level: Mapped[str | None] = mapped_column(String(20))  # safe | caution | high | extreme
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="plans")


class AQICache(Base):
    """Persisted cache for AQI readings — also used for historical data."""
    __tablename__ = "aqi_cache"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    city: Mapped[str] = mapped_column(String(150), index=True)
    lat: Mapped[float | None] = mapped_column(Float)
    lon: Mapped[float | None] = mapped_column(Float)
    aqi: Mapped[int] = mapped_column(Integer)
    pm25: Mapped[float | None] = mapped_column(Float)
    pm10: Mapped[float | None] = mapped_column(Float)
    no2: Mapped[float | None] = mapped_column(Float)
    o3: Mapped[float | None] = mapped_column(Float)
    so2: Mapped[float | None] = mapped_column(Float)
    co: Mapped[float | None] = mapped_column(Float)
    source: Mapped[str] = mapped_column(String(20), default="waqi")  # waqi | openaq | sensor
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
