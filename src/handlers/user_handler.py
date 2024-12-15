
from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile, URLInputFile, PollAnswer, ReplyKeyboardRemove
from config import bot, supabase

from src.states.user_states import User
from src.keyboards.user_keyboard import give_phone_keyboard

user_router = Router()


def remove_leading_plus(s):
    # Проверяем, начинается ли строка с символа '+'
    if s.startswith('+'):
        # Убираем первый символ
        return s[1:]
    return s  # Возвращаем строку без изменений, если первого символа нет


@user_router.message(StateFilter(User.final))
async def final(message: Message, state: FSMContext):
    response = supabase.table('UserData').select('age').eq('chat_id', message.from_user.id).execute()
    match response.data[0]['age']:
        case "Младше 9":
            text = """
                🎉 <b>Ты молодец</b>, в рамках новогодней акции мы дарим Тебе <b>сертификат на скидку 20%</b> в <a href="https://t.me/bubblehubb">Bubble Hub</a> 🧋 — просто покажи сообщение бариста и получи скидку. Не забудь подписаться на наш канал, чтобы получить свой подарок и знать про все акции! 🎁

👉 <a href="https://t.me/algo_omsk">Подписаться на канал</a>
                """
        case "9-11":
            text = """
                🎉 <b>Ты молодец</b>, в рамках новогодней акции мы дарим Тебе <b>сертификат на месяц бесплатного обучения</b> на курсе <i>"Визуальное программирование"</i>. Чтобы получить приз дождись сообщение от нашего менеджера, а также не забудь подписаться на наш канал, чтобы получить свой подарок и знать про все акции! 🎁

👉 <a href="https://t.me/algo_omsk">Подписаться на канал</a>

                """
        case "12-15":
            text = """
                🎉 <b>Ты молодец</b>, в рамках новогодней акции мы дарим Тебе <b>сертификат на месяц бесплатного обучения</b> на курсе <i>"Python Start"</i>. Чтобы получить приз дождись сообщение от нашего менеджера, а также не забудь подписаться на наш канал, чтобы получить свой подарок и знать про все акции! 🎁

👉 <a href="https://t.me/algo_omsk">Подписаться на канал</a>

                """
        case _:
            text = """
                🎉 <b>Вы молодец</b>, в рамках новогодней акции мы дарим Вам <b>сертификат на месяц бесплатного обучения</b> на курсе <i>"Python Pro"</i>. Чтобы получить приз дождись сообщение от нашего менеджера, а также не забудь подписаться на наш канал, чтобы получить свой подарок и знать про все акции! 🎁

👉 <a href="https://t.me/algo_omsk">Подписаться на канал</a>
                """

    await bot.send_photo(
        chat_id=message.from_user.id,
        photo=FSInputFile("present.jpg"),
        caption=text,
        message_effect_id="5046509860389126442",
        protect_content=True
    )


@user_router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.set_state(User.wait_phone_number)
    chat_id = message.from_user.id
    try:
        response = supabase.table('UserData').select('*').eq('chat_id', chat_id).execute()
        if not response.data:
            supabase.table('UserData').insert(
                {'chat_id': chat_id, 'username': '@' + message.from_user.username}).execute()
    except:
        pass
    await bot.send_photo(
        chat_id=message.from_user.id,
        photo=URLInputFile('https://avatars.mds.yandex.net/get-altay/4054675/2a000001758a78a219db3943ea4b9aea90a1/XXL'),
        caption="""Привет! 🎉

Я — бот Алгоритмики, крутой школы, где мы учим программированию и многим другим современным навыкам. 🚀

Хочешь узнать, насколько ты разбираешься в IT? 🤔
Пройди нашу увлекательную викторину, узнай свой уровень и получи классные призы! 🎁

Готов начать? 😉""",
        reply_markup=give_phone_keyboard()
    )


@user_router.message(StateFilter(User.wait_phone_number), F.content_type == "contact")
async def handle_contact(message: Message, state: FSMContext):
    """Обрабатывает контакт пользователя"""

    await state.set_state(User.age_poll)

    contact = message.contact
    chat_id = message.chat.id
    username = message.from_user.username

    # проверка, что tg_phone принадлежит пользователю
    if contact.user_id != message.from_user.id:
        await bot.send_message(
            chat_id=chat_id,
            text="Нажмите на кнопку «Поделиться номером телефона»",
        )
        return

    supabase.table('UserData').update({'phone': remove_leading_plus(contact.phone_number)}).eq('chat_id', chat_id).execute()

    await bot.send_poll(
        chat_id=chat_id,
        question="Сколько Вам Лет?",
        options=["Младше 9", "9-11", "12-15", "16+"],
        is_anonymous=False,
        allows_multiple_answers=False,
        reply_markup=ReplyKeyboardRemove(),
    )


@user_router.poll_answer(StateFilter(User.age_poll))
async def handle_poll_answer(poll_answer: PollAnswer, state: FSMContext):
    """Обрабатывает ответы пользователя на опрос."""
    await state.set_state(User.poll1)
    match poll_answer.option_ids[0]:
        case 0:
            age = "Младше 9"
        case 1:
            age = "9-11"
        case 2:
            age = "12-15"
        case 3:
            age = "16+"
        case _:
            age = "Неизвестно"

    supabase.table('UserData').update({'age': age}).eq('chat_id', poll_answer.user.id).execute()

    await bot.send_poll(
        chat_id=poll_answer.user.id,
        question="Что такое алгоритм?",
        options=[
            "Последовательность действий для решения задачи.",
            "Набор команд для компьютера.",
            "Программа для выполнения задачи.",
            "Всё перечисленное."
        ],
        is_anonymous=False,
        allows_multiple_answers=False,
        type="quiz",
        correct_option_id=0
    )


@user_router.poll_answer(StateFilter(User.poll1))
async def handle_poll_answer_1(poll_answer: PollAnswer, state: FSMContext):
    """Обрабатывает ответы пользователя на опрос."""
    await state.set_state(User.poll2)
    await bot.send_poll(
        chat_id=poll_answer.user.id,
        question="Для чего используются циклы в программировании?",
        options=[
            "Для управления потоком программы.",
            "Для проверки условий.",
            "Для повторения действий.",
            "Для всего перечисленного."
        ],
        is_anonymous=False,
        allows_multiple_answers=False,
        type="quiz",
        correct_option_id=2
    )


@user_router.poll_answer(StateFilter(User.poll2))
async def handle_poll_answer_2(poll_answer: PollAnswer, state: FSMContext):
    """Обрабатывает ответы пользователя на опрос."""
    await state.set_state(User.poll3)
    await bot.send_poll(
        chat_id=poll_answer.user.id,
        question="Какие виды алгоритмов вы знаете?",
        options=[
            "Линейные.",
            "Циклические.",
            "Разветвляющиеся.",
            "Рекурсивные.",
            "Все перечисленные варианты."
        ],
        is_anonymous=False,
        allows_multiple_answers=False,
        type="quiz",
        correct_option_id=4
    )


@user_router.poll_answer(StateFilter(User.poll3))
async def handle_poll_answer_3(poll_answer: PollAnswer, state: FSMContext):
    """Обрабатывает ответы пользователя на опрос."""
    await state.set_state(User.poll4)
    await bot.send_poll(
        chat_id=poll_answer.user.id,
        question="Что такое переменная в программировании?",
        options=[
            "Значение, которое никогда не изменяется.",
            "Место для хранения данных, которые могут изменяться.",
            "Специальный тип файла.",
            "Всё перечисленное."
        ],
        is_anonymous=False,
        allows_multiple_answers=False,
        type="quiz",
        correct_option_id=1
    )

@user_router.poll_answer(StateFilter(User.poll4))
async def handle_poll_answer_4(poll_answer: PollAnswer, state: FSMContext):
    """Обрабатывает ответы пользователя на опрос."""
    await state.set_state(User.poll5)
    await bot.send_poll(
        chat_id=poll_answer.user.id,
        question="Что такое условие в программе?",
        options=[
            "Команда для компьютера следовать инструкции.",
            "Проверка истинности утверждения для выбора дальнейшего действия.",
            "Набор случайных чисел.",
            "Описание задачи."
        ],
        is_anonymous=False,
        allows_multiple_answers=False,
        type="quiz",
        correct_option_id=1
    )


@user_router.poll_answer(StateFilter(User.poll5))
async def handle_poll_answer_5(poll_answer: PollAnswer, state: FSMContext):
    """Обрабатывает ответы пользователя на опрос."""
    await state.set_state(User.poll6)
    await bot.send_poll(
        chat_id=poll_answer.user.id,
        question="Что такое цикл с условием?",
        options=[
            "Команда, выполняющаяся только один раз.",
            "Повторение действий, пока выполняется условие.",
            "Последовательность инструкций для программы.",
            "Ошибка в коде."
        ],
        is_anonymous=False,
        allows_multiple_answers=False,
        type="quiz",
        correct_option_id=1
    )


@user_router.poll_answer(StateFilter(User.poll6))
async def handle_poll_answer_6(poll_answer: PollAnswer, state: FSMContext):
    """Обрабатывает ответы пользователя на опрос."""
    await state.set_state(User.final)
    response = supabase.table('UserData').select('age').eq('chat_id', poll_answer.user.id).execute()
    match response.data[0]['age']:
        case "Младше 9":
            text = """
            🎉<b>Ты молодец</b>, в рамках новогодней акции мы дарим Тебе <b>сертификат на скидку 20%</b> в <a href="https://t.me/bubblehubb">Bubble Hub</a> 🧋 — просто покажи сообщение бариста и получи скидку. Не забудь подписаться на наш канал, чтобы получить свой подарок и знать про все акции! 🎁

👉 <a href="https://t.me/algo_omsk">Подписаться на канал</a>
            """
        case "9-11":
            text = """
            🎉 <b>Ты молодец</b>, в рамках новогодней акции мы дарим Тебе <b>сертификат на месяц бесплатного обучения</b> на курсе <i>"Визуальное программирование"</i>. Чтобы получить приз дождись сообщение от нашего менеджера, а также не забудь подписаться на наш канал, чтобы получить свой подарок и знать про все акции! 🎁

👉 <a href="https://t.me/algo_omsk">Подписаться на канал</a>

            """
        case "12-15":
            text = """
            🎉 <b>Ты молодец</b>, в рамках новогодней акции мы дарим Тебе <b>сертификат на месяц бесплатного обучения</b> на курсе <i>"Python Start"</i>. Чтобы получить приз дождись сообщение от нашего менеджера, а также не забудь подписаться на наш канал, чтобы получить свой подарок и знать про все акции! 🎁

👉 <a href="https://t.me/algo_omsk">Подписаться на канал</a>

            """
        case _:
            text = """
            🎉 <b>Вы молодец</b>, в рамках новогодней акции мы дарим Вам <b>сертификат на месяц бесплатного обучения</b> на курсе <i>"Python Pro"</i>. Чтобы получить приз дождись сообщение от нашего менеджера, а также не забудь подписаться на наш канал, чтобы получить свой подарок и знать про все акции! 🎁

👉 <a href="https://t.me/algo_omsk">Подписаться на канал</a>
            """

    await bot.send_photo(
        chat_id=poll_answer.user.id,
        photo=FSInputFile("present.jpg"),
        caption=text,
        message_effect_id="5046509860389126442",
        protect_content=True
    )
    supabase.table('UserData').update({'poll': True}).eq('chat_id', poll_answer.user.id).execute()
