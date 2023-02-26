from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from dispatcher import dp, bot
from pydantic_models.wallet import CreateWallet
from services.wallet_service import WalletService


class DocumentForCheckState(StatesGroup):
    file_to_check = State()


class DocumentToAddState(StatesGroup):
    file_with_wallets = State()


@dp.message_handler(commands=['start', 'help'], commands_prefix='/')
async def send_welcome(
        message: types.Message):
    await message.reply('To add wallets from file - <b>/add_file</b> \n'
                        'To check one wallet - <b>/single_check</b> \n'
                        'To check multiple wallets from file - <b>/check_multiple</b>')


@dp.message_handler(commands='add_wallet')
async def create_one_wallet(
        message: types.Message,
        service: WalletService = WalletService()
):
    wallet_address = message['text'].split('/add_wallet ')
    wallet_data = CreateWallet(wallet_address=wallet_address[1])
    added_wallet = await service.create_one_wallet(wallet_data=wallet_data, user_id=message.from_user["id"])
    await message.reply(f'New wallet create {added_wallet}')


@dp.message_handler(commands='add_file', commands_prefix='/',
                    content_types=['photo', 'document', 'text'])
async def create_wallets_from_file(
        message: types.Message,
):
    await DocumentToAddState.file_with_wallets.set()
    await message.reply(f'Send a txt file with wallets written by columns.')


@dp.message_handler(content_types=['document', 'text'], state=DocumentToAddState.file_with_wallets)
async def scan_message(
        msg: types.Message,
        state: FSMContext,
        service: WalletService = WalletService(),
):
    if not msg.document.file_name.endswith('.txt'):
        await msg.reply('Document extension should be ".txt". Please, try again.')
        return
    await state.finish()
    document_id = msg.document.file_id
    file_info = await bot.get_file(document_id)
    file_id = file_info.file_path
    await service.create_wallets_from_file(msg.from_user['id'], file_id, msg.document)
    await bot.send_message(msg.from_user.id, 'Wallets successfully added.')


@dp.message_handler(commands='single_check')
async def check_one_wallet(
        message: types.Message,
        service: WalletService = WalletService()
):
    wallet_address = message['text'].split('/single_check ')[1]
    result = await service.compare_one_wallet(
        wallet_address=wallet_address,
        user_id=message.from_user['id'])
    await message.reply(result)


@dp.message_handler(commands='check_multiple')
async def check_multiple_wallet_by_file(
        message: types.Message
):
    await DocumentForCheckState.file_to_check.set()
    await message.reply('Send me document with wallets to check.')


@dp.message_handler(commands='get_my_wallets')
async def get_list_of_wallets(
        message: types.Message,
        service: WalletService = WalletService()
):
    user_wallets = await service.get_wallets_by_user_id(user_id=message.from_user['id'])
    for wallet in user_wallets:
        await message.reply(''.join(wallet))


@dp.message_handler(content_types=['document', 'text'], state=DocumentForCheckState.file_to_check)
async def check_multiple_wallets(
        message: types.Message,
        state: FSMContext,
        service: WalletService = WalletService(),
):
    if not message.document.file_name.endswith('.txt'):
        await message.reply('Document extension should be ".txt". Please, try again.')
        return
    await state.finish()
    document_id = message.document.file_id
    file_info = await bot.get_file(document_id)
    file_id = file_info.file_path
    result = await service.compare_multiple_wallets(user_id=message.from_user['id'],
                                                    document=message.document, file_id=file_id)
    await message.reply(f'{result}')
