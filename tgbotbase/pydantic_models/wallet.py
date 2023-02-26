from pydantic import BaseModel


class BaseWallet(BaseModel):
    wallet_address: str


class CreateWallet(BaseWallet):
    pass


class Wallet(BaseWallet):
    id: int
    user_id: int

    class Config:
        orm_mode = True
