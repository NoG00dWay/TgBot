from aiogram import Bot, types, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message,ReplyKeyboardMarkup, KeyboardButton
import asyncio
from cogs.get_stats_by_category import get_stats_by_category
from cogs import add_transaction,delete_last_record,view_by_dates,get_stats_by_date,get_balance,init_db

bot = Bot(token="7686061976:AAE_kmb32agJY0oevxPj_Cg9dxlOqkmmmsI")
dp = Dispatcher()

class StatsStates(StatesGroup):
    choosing_categories = State()

class TransactionStates(StatesGroup):
    waiting_for_date = State()
    waiting_for_amount = State()
    waiting_for_category = State()
    waiting_for_description = State()

class TransactionStatesIncome(StatesGroup):
    waiting_for_date = State()
    waiting_for_amount = State()
    waiting_for_category = State()
    waiting_for_description = State()


class BalanceByDate(StatesGroup):
    waiting_for_first_date = State()
    waiting_for_second_date = State()


keyboard_main = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Баланс')],
        [KeyboardButton(text='Расходы')],
        [KeyboardButton(text='Доходы')],
        [KeyboardButton(text='Удалить последнюю запись')]
    ],
    resize_keyboard=True
)

keyboard_categories = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Развлечение')],
        [KeyboardButton(text='Еда')],
        [KeyboardButton(text='Дом')],
        [KeyboardButton(text='Подарки')],
        [KeyboardButton(text='Учёба')],
        [KeyboardButton(text='Вещи')],
        [KeyboardButton(text='Неожиданные расходы')],
        [KeyboardButton(text='Транспорт')],
        [KeyboardButton(text='Нет')]
    ]
)

keyboard_balance = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Доходы и расходы за определенный период')],
        [KeyboardButton(text='Доходы и расходы за всё время')]
    ],
    resize_keyboard=True
)

keyboard_expenses = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Добавить строку расхода')],
        [KeyboardButton(text='Расходы по категориям')]

    ],
    resize_keyboard=True
)

keyboard_income = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Добавить строку дохода')],
    ],
    resize_keyboard=True
)


@dp.message(Command("start"))
async def start_handler(message: Message):
    init_db() # Создаём базу данных

    await message.answer("Добро пожаловать в финансового бота!")
    await message.answer('Выберите действие:', reply_markup=keyboard_main)

    @dp.message(lambda message: message.text in ['Баланс', 'Расходы', 'Доходы','Удалить последнюю запись'])
    async def expense_actions(message: Message):
        if message.text == 'Удалить последнюю запись':
            user_id = message.from_user.id
            delete_last_record(user_id)
            await message.answer('Выберите действие:', reply_markup=keyboard_main)

        elif message.text == 'Баланс':
            await message.answer('Выберите действие:', reply_markup=keyboard_balance)

            @dp.message(lambda  message: message.text == 'Доходы и расходы за всё время')
            async def get_balance_for_user(message: Message):
                await message.answer(get_balance(message.from_user.id),reply_markup=keyboard_main)

            @dp.message(lambda message: message.text == 'Доходы и расходы за определенный период')
            async def start_get_balance_by_date(message: Message, state: FSMContext):
                await state.set_state(BalanceByDate.waiting_for_first_date)
                await message.answer('Введите первую дату в формате YYYY-MM-DD')

            @dp.message(BalanceByDate.waiting_for_first_date)
            async def get_second_date(message: Message, state: FSMContext):
                await state.update_data(first_date = message.text)
                await state.set_state(BalanceByDate.waiting_for_second_date)
                await message.answer('Введите вторую дату в формате YYYY-MM-DD')

            @dp.message(BalanceByDate.waiting_for_second_date)
            async def end_get_balance_by_date(message : Message, state: FSMContext):
                data = await state.get_data()
                user_id = message.from_user.id
                first_date = data['first_date']
                second_date = message.text

                balance = get_stats_by_date(first_date, second_date, user_id)
                await state.clear()
                if isinstance(balance, dict):
                    if 'error' in balance:
                        response = balance['error']
                    else:
                        response = (
                            f"Доходы: {balance.get('Доходы', 0)} руб.\n"
                            f"Расходы: {balance.get('Расходы', 0)} руб."
                        )
                else:
                    response = str(balance)

                await message.answer(response, reply_markup=keyboard_main)



        # Часть кода с кнопкой расходы


        elif message.text == 'Расходы':
            await message.answer('Выдерите действие:', reply_markup=keyboard_expenses)


            # Добавление расходов

                # Добавление строки рахсдов

            @dp.message(lambda message: message.text == 'Добавить строку расхода')
            async def start_adding_expense(message: Message, state: FSMContext):
                await state.set_state(TransactionStates.waiting_for_date)
                await message.answer('Введите дату в формате YYYY-MM-DD')

            @dp.message(TransactionStates.waiting_for_date)
            async def process_date(message: Message, state: FSMContext):
                await state.update_data(date=message.text)
                await state.set_state(TransactionStates.waiting_for_amount)
                await message.answer('Введите сумму расхода:')

            @dp.message(TransactionStates.waiting_for_amount)
            async def process_amount(message: Message, state: FSMContext):
                try:
                    amount = float(message.text)
                    await state.update_data(amount=-abs(amount))
                    await state.set_state(TransactionStates.waiting_for_category)
                    await message.answer('Введите категорию расхода:',reply_markup=keyboard_categories)
                except ValueError:
                    await message.answer('Пожалуйста, введите корректную сумму (число):')

            @dp.message(TransactionStates.waiting_for_category)
            async def process_descryption(message: Message, state: FSMContext):
                await state.update_data(category=message.text)
                await state.set_state(TransactionStates.waiting_for_description)
                await message.answer('Введите описание')

            @dp.message(TransactionStates.waiting_for_description)
            async def process_description(message: Message, state: FSMContext):
                data = await state.get_data()
                user_id = message.from_user.id
                date = data['date']
                amount = data['amount']
                category = data['category']
                description = message.text

                add_transaction(user_id, date, category, amount, description)

                await state.clear()
                await message.answer('Транзакция успешно добавлена!', reply_markup=keyboard_main)



                # Статистика расходов по категориям




            @dp.message(lambda message: message.text == 'Расходы по категориям')
            async def start_stats_by_category(message: Message, state: FSMContext):
                await message.answer('Выберите нужные категории:', reply_markup=keyboard_categories)
                await state.set_state(StatsStates.choosing_categories)


            @dp.message(StatsStates.choosing_categories)
            async def process_categories(message: Message, state: FSMContext):
                user_id = message.from_user.id
                data = await state.get_data()
                categories = data.get('categories', [])

                if message.text == 'Нет':
                    if not categories:
                        await message.answer('Вы не выбрали ни одной категории.', reply_markup=keyboard_main)
                    else:
                        results, total = get_stats_by_category(categories, user_id)
                        message_result = '\n'.join(
                            f'{category}: {amount} руб.'
                            for category, amount in results.items()
                        )
                        await message.answer(
                            f'{message_result}\n\nОбщая сумма расходов: {total} руб.',
                            reply_markup=keyboard_main
                        )
                    await state.clear()
                    return

                if message.text in categories:
                    await message.answer('Эта категория уже выбрана. Выберите другую или нажмите "Нет".')
                    return

                categories.append(message.text)
                await state.update_data(categories=categories)
                await message.answer(
                    'Категория добавлена. Выберите ещё или нажмите "Нет".',
                    reply_markup=keyboard_categories
                )


            # Часть кода с кнопкой доходы

        elif message.text == 'Доходы':
            await message.answer('Выдерите действие:', reply_markup=keyboard_income)

            @dp.message(lambda message: message.text == 'Добавить строку дохода')
            async def start_adding_expense(message: Message, state: FSMContext):
                await state.set_state(TransactionStatesIncome.waiting_for_date)
                await message.answer('Введите дату в формате YYYY-MM-DD')

            @dp.message(TransactionStatesIncome.waiting_for_date)
            async def process_date(message: Message, state: FSMContext):
                await state.update_data(date=message.text)
                await state.set_state(TransactionStatesIncome.waiting_for_amount)
                await message.answer('Введите сумму дохода:')

            @dp.message(TransactionStatesIncome.waiting_for_amount)
            async def process_amount(message: Message, state: FSMContext):
                try:
                    amount = float(message.text)
                    await state.update_data(amount=amount)
                    await state.set_state(TransactionStatesIncome.waiting_for_category)
                    await message.answer('Введите категорию дохода:')
                except ValueError:
                    await message.answer('Пожалуйста, введите корректную сумму (число):')

            @dp.message(TransactionStatesIncome.waiting_for_category)
            async def process_descryption(message: Message, state: FSMContext):
                await state.update_data(category=message.text)
                await state.set_state(TransactionStatesIncome.waiting_for_description)
                await message.answer('Введите описание')

            @dp.message(TransactionStatesIncome.waiting_for_description)
            async def process_description(message: Message, state: FSMContext):
                data = await state.get_data()
                user_id = message.from_user.id
                date = data['date']
                amount = data['amount']
                category = data['category']
                description = message.text

                add_transaction(user_id, date, category, amount, description)

                await state.clear()
                await message.answer('Транзакция успешно добавлена!', reply_markup=keyboard_main)


async def main():
    await dp.start_polling(bot)

asyncio.run(main())