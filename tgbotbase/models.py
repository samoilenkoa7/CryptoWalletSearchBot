import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Wallet(Base):
    __tablename__ = 'wallets'

    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.String(20), nullable=False)
    wallet_address = sa.Column(sa.String(100), nullable=False, unique=True)
