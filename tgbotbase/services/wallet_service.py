import datetime
import logging
import os
import urllib

import aiofiles
from aiogram import types

from config import settings
from database_services.wallet_service_DAL import WalletDAL
from pydantic_models.wallet import CreateWallet


class WalletService:
    TELEGRAM_BASE_URL = 'https://api.telegram.org/file/bot'

    def __init__(self, db_service: WalletDAL = WalletDAL()):
        self.db_service = db_service

    @classmethod
    def _create_file_path(cls, document: types.Document):
        time_now = datetime.datetime.utcnow()
        file_path = settings.media_root + document.file_name + str(time_now)
        return file_path

    @classmethod
    def save_file_in_media(cls,
                           file_path: str,
                           file_id: str) -> None:
        if not os.path.exists(settings.media_root):
            os.mkdir(settings.media_root)
        try:
            urllib.request.urlretrieve(f'{cls.TELEGRAM_BASE_URL}{settings.bot_token}/{file_id}',
                                       f'{file_path}')
        except Exception as ex:
            logging.error(msg=f'File wasn\'t saved with EXCEPTION:  {ex}')

    @classmethod
    def delete_used_file(cls,
                         file_path: str):
        try:
            os.remove(file_path)
        except Exception as ex:
            logging.warning(msg=f'File wasn\'t deleted with EXCEPTION:  {ex}')

    async def create_one_wallet(self,
                                wallet_data: CreateWallet,
                                user_id: int) -> str:
        wallet_address = wallet_data.wallet_address
        user_id = str(user_id)
        new_wallet = await self.db_service.create_wallet(wallet_address=wallet_address, user_id=user_id)
        return new_wallet

    async def create_wallets_from_file(self,
                                       user_id: int,
                                       file_id: str,
                                       document: types.Document) -> list[str]:
        user_id = str(user_id)
        file_path = self._create_file_path(document=document)
        self.save_file_in_media(file_path=file_path, file_id=file_id)
        async with aiofiles.open(file_path, mode='r') as file:
            wallets_list = await file.readlines()
        created_wallets = await self.db_service.create_multiple_wallets(wallet_data=wallets_list, user_id=user_id)
        self.delete_used_file(file_path)
        return created_wallets

    async def compare_one_wallet(self,
                                 wallet_address: str,
                                 user_id: int) -> str:
        user_wallets = await self.db_service.check_one_wallet(
            wallet_address=wallet_address,
            user_id=str(user_id)
        )
        if len(user_wallets) > 1:
            return 'Wallet was found'
        else:
            return 'Wallet was not found'

    async def compare_multiple_wallets(self,
                                       user_id: int,
                                       document: types.Document,
                                       file_id: str) -> str | list[str]:
        user_id = str(user_id)
        file_path = self._create_file_path(document=document)
        self.save_file_in_media(file_path, file_id=file_id)
        async with aiofiles.open(file_path, mode='r') as file:
            wallets_list = await file.readlines()
        user_wallets = await self.db_service.check_multiple_wallets(wallet_list=wallets_list, user_id=str(user_id))
        self.delete_used_file(file_path)
        user_wallets = [i.wallet_address[:-2] for i in user_wallets]
        if len(user_wallets) > 1:
            return user_wallets
        else:
            return 'Wallets not found'

    async def get_wallets_by_user_id(self,
                                     user_id: int) -> list[str]:
        user_id = str(user_id)
        user_wallets = await self.db_service.get_user_wallets(user_id)

        response_message = [user_wallets[i:i + 90] for i in range(0, len(user_wallets), 90)]
        return response_message
