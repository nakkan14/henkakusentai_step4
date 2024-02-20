from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Numeric
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql.schema import UniqueConstraint
from datetime import datetime

Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(13), nullable=False, unique=True)  
    name = Column(String(50))
    price = Column(Integer, nullable=False)

class Trade(Base):
    __tablename__ = 'trades'
    id = Column(Integer, primary_key=True, autoincrement=True)
    datetime = Column(DateTime, default=datetime.utcnow)
    emp_cd = Column(String(10), nullable=False)
    store_cd = Column(String(5), nullable=False)
    pos_cd = Column(String(3), nullable=False)
    total_amt = Column(Integer)
    ttl_amt_ex_tax = Column(Integer)

class Tax(Base):
    __tablename__ = 'taxs'
    id = Column(Integer, primary_key=True)
    code = Column(String(2), unique=True) 
    name = Column(String(20))
    percent = Column(Numeric)

class Trade_detail(Base):
    __tablename__ = 'trade_details'
    trd_id = Column(Integer, ForeignKey('trades.id'), nullable=False)
    dtl_id = Column(Integer, primary_key=True, autoincrement=True)
    prd_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    prd_code = Column(String(13), nullable=False)
    prd_name = Column(String(50), nullable=False)
    prd_price = Column(Integer, nullable=False)
    tax_cd = Column(String(2), ForeignKey('taxs.code'))