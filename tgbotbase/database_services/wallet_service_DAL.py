from sqlalchemy.future import select
from sqlalchemy.orm import Session

from database import get_session
from models import Wallet


class WalletDAL:
    def __init__(self, session: Session = next(get_session())):
        self.session = session

    async def create_wallet(self, wallet_address: str, user_id: str):
        new_wallet = Wallet(
            user_id=user_id,
            wallet_address=wallet_address
        )
        self.session.add(new_wallet)
        await self.session.commit()
        return wallet_address

    async def create_multiple_wallets(self, wallet_data: list[str], user_id: str):
        new_wallets = [Wallet(
            user_id=user_id,
            wallet_address=wallet
        ) for wallet in wallet_data]
        self.session.add_all(new_wallets)
        await self.session.commit()
        return [wallet for wallet in wallet_data]

    async def check_one_wallet(self,
                               wallet_address: str,
                               user_id: str) -> None | Wallet:
        statement = select(Wallet).filter_by(wallet_address=wallet_address, user_id=user_id)
        query = await self.session.execute(statement)
        instance = query.all()
        return instance

    async def check_multiple_wallets(self,
                                     wallet_list: list[str],
                                     user_id: str) -> None | list[Wallet] | Wallet:
        statement = select(Wallet).where(Wallet.wallet_address.in_(wallet_list)) \
            .where(Wallet.user_id == user_id)
        query = await self.session.execute(statement)
        instance = query.scalars()
        return instance

    async def get_user_wallets(self,
                               user_id: str) -> list[str] | None:
        statement = select(Wallet.wallet_address).filter_by(user_id=user_id)
        query = await self.session.execute(statement)
        instance = query.scalars().all()
        return instance or None
