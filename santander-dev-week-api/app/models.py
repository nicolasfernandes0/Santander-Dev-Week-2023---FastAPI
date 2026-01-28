from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import datetime

from app.database import Base

# ========== MODELOS DO BANCO (SQLAlchemy) ==========

class UserDB(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=True)
    created_at = Column(String, default=datetime.now().isoformat())
    
    account = relationship("AccountDB", back_populates="user", cascade="all, delete-orphan", uselist=False)
    card = relationship("CardDB", back_populates="user", cascade="all, delete-orphan", uselist=False)
    features = relationship("FeatureDB", back_populates="user", cascade="all, delete-orphan")
    news = relationship("NewsDB", back_populates="user", cascade="all, delete-orphan")

class AccountDB(Base):
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    number = Column(String(50), nullable=False)
    agency = Column(String(20), nullable=False)
    balance = Column(Float, default=0.0)
    limit = Column(Float, default=1000.0)
    
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    user = relationship("UserDB", back_populates="account")

class CardDB(Base):
    __tablename__ = "cards"
    
    id = Column(Integer, primary_key=True, index=True)
    number = Column(String(50), nullable=False)
    limit = Column(Float, default=2000.0)
    
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    user = relationship("UserDB", back_populates="card")

class FeatureDB(Base):
    __tablename__ = "features"
    
    id = Column(Integer, primary_key=True, index=True)
    icon = Column(String(10), nullable=False)
    description = Column(String(200), nullable=False)
    
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("UserDB", back_populates="features")

class NewsDB(Base):
    __tablename__ = "news"
    
    id = Column(Integer, primary_key=True, index=True)
    icon = Column(String(10), nullable=False)
    description = Column(String(500), nullable=False)
    
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("UserDB", back_populates="news")

# ========== MODELOS PYDANTIC (SCHEMAS) ==========

class AccountBase(BaseModel):
    number: str
    agency: str
    balance: float
    limit: float
    model_config = ConfigDict(from_attributes=True)

class CardBase(BaseModel):
    number: str
    limit: float
    model_config = ConfigDict(from_attributes=True)

class FeatureBase(BaseModel):
    icon: str
    description: str
    model_config = ConfigDict(from_attributes=True)

class NewsBase(BaseModel):
    icon: str
    description: str
    model_config = ConfigDict(from_attributes=True)

class UserBase(BaseModel):
    name: str
    email: Optional[str] = None

class UserCreate(UserBase):
    account: AccountBase
    card: CardBase
    features: List[FeatureBase]
    news: List[NewsBase]

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None

class UserResponse(UserBase):
    id: int
    created_at: str
    account: AccountBase
    card: CardBase
    features: List[FeatureBase]
    news: List[NewsBase]
    model_config = ConfigDict(from_attributes=True)

# ========== MODELOS PARA REQUESTS POST ==========

class DepositRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Valor do depósito")

class WithdrawRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Valor do saque")

class TransferRequest(BaseModel):
    to_user_id: int = Field(..., description="ID do usuário destino")
    amount: float = Field(..., gt=0, description="Valor da transferência")

class SimpleUserCreate(BaseModel):
    name: str
    email: Optional[str] = None
    initial_balance: float = Field(1000.0, ge=0)