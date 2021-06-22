import aiogram
from bd_helper import BD
import asyncio
import aiogram_keyboards as keyboards
from config import dict_url_tv, token_gavelON, payment_token_tranzzo, payment_token_UKassa, cents, URL
from aiogram.utils.markdown import text, bold, code
from aiogram.types import ParseMode, LabeledPrice, PreCheckoutQuery, ContentType, \
    ShippingOption, ShippingAddress, ShippingQuery
import re
from datetime import datetime
import pytz
from fpdf import FPDF
from utils import Authorization_Code_States
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import logging
from aiogram.contrib.middlewares.logging import LoggingMiddleware
import hashlib
import time

logging.basicConfig(filename='bot_log.txt',
                    filemode='w',
                    format=u'%(filename)+13s [ LINE:%(lineno)-4s] %(levelname)-8s [%(asctime)s] %(message)s',
                    level=logging.DEBUG)

bot = aiogram.Bot(token=token_gavelON)
loop = asyncio.get_event_loop()
di_bot = aiogram.dispatcher.Dispatcher(bot=bot, loop=loop, storage=MemoryStorage())
di_bot.middleware.setup(LoggingMiddleware())

Belorussian_Post_Shipping_Option = ShippingOption(id='by_post', title='БЕЛПОШТА')
Belorussian_Post_Shipping_Option.add(LabeledPrice('Дополнительная защита для груза', 5 * cents))
Belorussian_Post_Shipping_Option.add(LabeledPrice('Отправление в течение 1-2 дней', 10 * cents))
Belorussian_Fast_Post_Shipping_Option = ShippingOption(id='by_fast_post', title='БЕЛПОШТА Срочная')
Belorussian_Fast_Post_Shipping_Option.add(LabeledPrice('Срочная посылка отправка в этот же день', 15 * cents))
Belorussian_Fast_Post_Shipping_Option.add(LabeledPrice('Дополнительная защита для груза', 5 * cents))
Courier_Minsk_Shipping_Option = ShippingOption(id='minsk_courier', title='Курьер')
Courier_Minsk_Shipping_Option.add(LabeledPrice('Курьер по Минску', 5 * cents))
Russian_Post_Shipping_Option = ShippingOption(id='ru_post', title='Почта России')
Russian_Post_Shipping_Option.add(LabeledPrice('Дополнительная защита для груза', 5 * cents))
Russian_Post_Shipping_Option.add(LabeledPrice('Отправление в течение 1-2 дней', 10 * cents))
Russian_Fast_Post_Shipping_Option = ShippingOption(id='ru_fast_post', title='Почта России Срочная')
Russian_Fast_Post_Shipping_Option.add(LabeledPrice('Срочная посылка отправка в этот же день', 15 * cents))
Russian_Fast_Post_Shipping_Option.add(LabeledPrice('Дополнительная защита для груза', 5 * cents))
EMS_Post_Shipping_Option = ShippingOption(id='ems_post', title='Международная почта EMS')
EMS_Post_Shipping_Option.add(LabeledPrice('Срочная международная почта', 25 * cents))
FedEx_Post_Shipping_Option = ShippingOption(id='id_fedex', title='Экспресс-доставка FedEx')
FedEx_Post_Shipping_Option.add(LabeledPrice('Самая знаменитая экспресс-доставка в мире FedEx', 35 * cents))
Teleporting_Post_Shipping_Option = ShippingOption(id='id_teleport', title='Телепорт - мгновенная доставка')
Teleporting_Post_Shipping_Option.add(LabeledPrice('Мгновенная доставка', 1000000 * cents))


def generate_check_in_pdf(arr):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    text_check = arr
    pdf.cell(200, 10, txt='fff', ln=1, align='C')
    pdf.output('check.pdf')


@di_bot.message_handler(commands=['start'])
async def send_start(message):
    print(message)
    msg = f'Привет ' + message.from_user.first_name + ', я бот онлайн-аукциона gavelON.\n ' \
                                                      'Можем начинать, список команд можешь посмотреть в /help'
    await message.reply(msg)


async def process_buy_command(message):
    if payment_token_tranzzo.split(':')[1] == 'TEST':
        await bot.send_message(message.from_user.id, text='Сейчас бот работает в тестовом режиме,\n'
                                                          'для оплаты вам нужно использовать карточку с\n'
                                                          'данными 4242 4242 4242 4242, 12/26, CVC 000.')
    product_cap = str(message.message.caption)
    num = product_cap.find('№')
    id_lot_str = product_cap[num + 1:]
    id_lot = int(id_lot_str)
    db = BD()
    dict_results = db.get_image_cur_price_lot(id_lot)
    price = [LabeledPrice(label=dict_results['name'], amount=(round(dict_results['current_price'] // 2.56 * 100)))]
    if dict_results['image'] == '' and dict_results['name'] in dict_url_tv:
        dict_results['image'] = dict_url_tv[dict_results['name']]
    else:
        dict_results['image'] = URL
    start_par = f"some-product-num-{id_lot_str}"
    payload = f"invoice-payload-for-gavelON-product-num-{id_lot_str}"
    await bot.send_invoice(message.from_user.id,
                           title=dict_results['name'],
                           description=dict_results['description'],
                           provider_token=payment_token_tranzzo,
                           currency='usd',
                           photo_url=dict_results['image'],
                           photo_height=512,  # !=0/None, иначе изображение не покажется
                           photo_width=512,
                           photo_size=512,
                           need_email=True,
                           need_phone_number=True,
                           need_name=True,
                           send_phone_number_to_provider=True,
                           is_flexible=True,  # True если конечная цена зависит от способа доставки
                           prices=price,
                           start_parameter=start_par,
                           payload=payload
                           )


@di_bot.shipping_query_handler(lambda query: True)
async def process_shipping_query(shipping_query: ShippingQuery):
    if shipping_query.shipping_address.country_code == 'SS':
        return await bot.answer_shipping_query(
            shipping_query.id,
            ok=False,
            error_message='Посмотрел недавно выпуск The Люди, поэтому стремно отправлять туда'
        )
    if shipping_query.shipping_address.country_code == 'IN':
        return await bot.answer_shipping_query(
            shipping_query.id,
            ok=False,
            error_message='Извините, но это эпицентр короны'
        )

    shipping_options = [Teleporting_Post_Shipping_Option, EMS_Post_Shipping_Option, FedEx_Post_Shipping_Option]

    if shipping_query.shipping_address.country_code == 'BY':
        shipping_options.append(Belorussian_Post_Shipping_Option)
        shipping_options.append(Belorussian_Fast_Post_Shipping_Option)
        if shipping_query.shipping_address.city == 'Минск':
            shipping_options.append(Courier_Minsk_Shipping_Option)
    if shipping_query.shipping_address.country_code == 'RU':
        shipping_options.append(Russian_Post_Shipping_Option)
        shipping_options.append(Russian_Fast_Post_Shipping_Option)

    await bot.answer_shipping_query(
        shipping_query.id,
        ok=True,
        shipping_options=shipping_options
    )


@di_bot.pre_checkout_query_handler(lambda query: True)
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    print('order_info')
    print(pre_checkout_query.order_info)
    print('@' * 222)
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@di_bot.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def process_successful_payment(message):
    print('successful_payment:')
    pmnt = message.successful_payment.to_python()
    for key, val in pmnt.items():
        print(f'{key} = {val}')

    msg = f"Платеж на сумму {message.successful_payment.total_amount // 100} " \
          f"{message.successful_payment.currency} совершен успешно! "
    print('=' * 222)
    final_price = round(int(message.successful_payment.total_amount) / 100 * 2.56)
    telegram_id = message.from_user.id
    id_lot = message.successful_payment.invoice_payload[40:]
    db = BD()
    db.sold_now(id_lot, telegram_id, final_price)
    await bot.send_message(message.chat.id, msg)


def normalize_time(time):
    now = datetime.now()
    mytimezone = pytz.timezone("Europe/Minsk")
    now3 = mytimezone.localize(now)
    div_time = str(time - now3)
    search_days = re.match(r'-?\d+', div_time)
    days = int(div_time[search_days.start():search_days.end()])
    last_day = abs(days) % 10
    if last_day in [0, 5, 6, 7, 8, 9]:
        div_time = div_time.replace('days', 'дней')
    elif abs(days) in [12, 13, 14]:
        div_time = div_time.replace('days', 'дней')
    elif last_day in [2, 3, 4]:
        div_time = div_time.replace('days', 'дня')
    else:
        if abs(days) % 100 == 11:
            div_time = div_time.replace('days', 'дней')
        else:
            div_time = div_time.replace('days', 'день')
            div_time = div_time.replace('day', 'день')
    dot = div_time.find('.')
    div_time = div_time[:(dot - 3)]
    hour_pos = dot - 8
    if div_time[hour_pos] == '1':
        hour = None
    else:
        hour = int(div_time[dot - 7])
    min_pos = dot - 5
    if div_time[min_pos] == '1':
        minute = None
    else:
        minute = int(div_time[dot - 4])
    if hour in [0, 5, 6, 7, 8, 9]:
        div_time = div_time.replace(':', ' часов ')
    elif hour in [2, 3, 4]:
        div_time = div_time.replace(':', ' часа ')
    elif hour == 1:
        div_time = div_time.replace(':', ' час ')
    else:
        div_time = div_time.replace(':', ' часов ')
    if minute in [0, 5, 6, 7, 8, 9]:
        div_time = div_time + ' минут!'
    elif minute in [2, 3, 4]:
        div_time = div_time + ' минуты!'
    elif minute == 1:
        div_time = div_time + ' минута!'
    else:
        div_time = div_time + ' минут!'
    div_time = div_time.replace(',', '')
    return div_time


async def send_five_lots_one_subcat(chat_id, subcategory):
    url = URL
    db = BD()
    arr_results = db.get_some_lots(chat_id, subcategory)
    for dict_res in arr_results:
        div_time = normalize_time(dict_res['end_time'])
        capa_text = f"{dict_res['name']}\nТекущая ставка: {str(dict_res['start_price'])}\nДо конца аукциона: " \
                    f"{div_time}\nСостояние: {dict_res['condition']} \nОписание: {dict_res['description']}" \
                    f"\nТовар №{dict_res['id']}"
        if dict_res['image'] == '' and dict_res['name'] in dict_url_tv:
            url = dict_url_tv[dict_res['name']]

        await bot.send_photo(chat_id=chat_id, photo=url, caption=capa_text, parse_mode=ParseMode.MARKDOWN,
                             reply_markup=keyboards.keyboards_nearest_lot(dict_res['current_price'],
                                                                          dict_res['min_price_increase'],
                                                                          dict_res['id']))


@di_bot.callback_query_handler(lambda call: call.data and call.data.startswith('inline_btn_subcat_'))
async def process_callback_btn_subcat(callback_query: aiogram.types.CallbackQuery):
    code = callback_query.data[-1]
    msg = str(callback_query.message.text)
    num = msg.find('1')
    msg = msg[num:]
    msg = re.sub(r'\d+\)', '', msg)
    msg_arr = msg.split('\n')
    if code.isdigit():
        code = int(code)
    if code <= len(msg_arr):
        await bot.answer_callback_query(callback_query.id, text=f"Выбрана подкатегория {msg_arr[code - 1]}")
        id_chat = callback_query.from_user.id
        await send_five_lots_one_subcat(id_chat, msg_arr[code - 1])
        # await get_subcategory_keyboards(msg_arr[code - 1], id_chat, msg)
    else:
        print("Что-то не так")
        await bot.answer_callback_query(callback_query.id, text=f"Ты нажал что-то не то")
        await bot.send_message(chat_id=callback_query.from_user.id, text=f"Ты нажал что-то не то")


async def get_subcategory_keyboards(category, id_chat, msg):
    bd = BD()
    arr_subcategory = bd.get_subcategory(category)
    msg = msg + '\nВыберите одну из следующих подкатегорий:\n'
    i = 1
    for subcategory in arr_subcategory:
        msg = msg + str(i) + ')' + subcategory + '\n'
    try:
        msg = text(msg)
        await bot.send_message(chat_id=id_chat, text=msg, parse_mode=ParseMode.MARKDOWN,
                               reply_markup=keyboards.keyboards_subcategory(arr_subcategory))
    except Exception:
        await bot.send_message(chat_id=id_chat, text='ой ой ой что то не так')


@di_bot.callback_query_handler(lambda call: call.data and call.data.startswith('inline_btn_cat_'))
async def process_callback_btn_cat(callback_query: aiogram.types.CallbackQuery):
    code = callback_query.data[-1]
    msg = str(callback_query.message.text)
    num = msg.find('1')
    msg = msg[num:]
    msg = re.sub(r'\d+\)', '', msg)
    msg_arr = msg.split('\n')
    btn = 'inline_btn_cat_'
    if code.isdigit():
        code = int(code)
    if code <= len(msg_arr):
        await bot.answer_callback_query(callback_query.id, text=f"Выбрана категория {msg_arr[code - 1]}")
        id_chat = callback_query.from_user.id
        msg = f"Категория: {msg_arr[code - 1]}"
        await get_subcategory_keyboards(msg_arr[code - 1], id_chat, msg)
    else:
        print("Что-то не так")
        await bot.answer_callback_query(callback_query.id, text=f"Ты нажал что-то не то")
        await bot.send_message(chat_id=callback_query.from_user.id, text=f"Ты нажал что-то не то")


@di_bot.message_handler(commands=['subcategory_lot'])
async def get_tovar(message):
    bd = BD()
    arr_id, arr_category = bd.get_category()
    msg = 'Выберите одну из следующих категорий:\n'
    for id in arr_id:
        msg = msg + str(id) + ')' + arr_category[int(id) - 1] + '\n'
    try:
        msg = text(msg)
        await bot.send_message(chat_id=message.from_user.id, text=msg, parse_mode=ParseMode.MARKDOWN,
                               reply_markup=keyboards.keyboards_category(arr_category))
    except Exception:
        await bot.send_message(chat_id=message.from_user.id, text='ой ой ой что то не так')


@di_bot.callback_query_handler(lambda call: call.data and call.data.startswith('btn_bet_'))
async def process_callback_btn_bet(callback_query: aiogram.types.CallbackQuery):
    code = callback_query.data[8:]
    telegram_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    message_id = callback_query.message.message_id
    product_cap = callback_query.message.text
    num1 = product_cap.find('№')
    num2 = product_cap.find('\n')
    id_lot = product_cap[num1 + 1:num2]
    str_now_price = 'Текущая ставка: '
    num = product_cap.find(str_now_price)
    price_now = product_cap[num + len(str_now_price):]
    num = price_now.find('\n')
    price_now = price_now[:num]
    str_min_price = 'Минимальная ставка '
    num = product_cap.find(str_min_price)
    price_min = product_cap[num + len(str_min_price):]
    num = price_min.find('\n')
    price_min = price_min[:num]
    str_my_price = 'Ваша текущая ставка: '
    num = product_cap.find(str_my_price)
    price_my = product_cap[num + len(str_my_price):]
    num = price_my.find('\n')
    price_my = price_my[:num]
    price_my_int = int(price_my)
    msg = 'Товар №' + id_lot + '\n' + str_now_price + price_now + \
          '\n' + str_min_price + price_min + '\nВаша текущая ставка: '

    if code == '1':
        await bot.answer_callback_query(callback_query.id, text=f"Увеличен размер ставки на 1")
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                    text=msg + str(price_my_int + int(code)) + '\n'
                                                                               'Подтвердите ставку или увельчьте '
                                                                               'ставку нажав соответсвующую кнопку',
                                    reply_markup=keyboards.keyboards_plus_bet())
    elif code == '10':
        await bot.answer_callback_query(callback_query.id, text=f"Увеличен размер ставки на 10")
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                    text=msg + str(price_my_int + int(code)) + '\n'
                                                                               'Подтвердите ставку или увельчьте '
                                                                               'ставку нажав соответсвующую кнопку',
                                    reply_markup=keyboards.keyboards_plus_bet())
    elif code == '100':
        await bot.answer_callback_query(callback_query.id, text=f"Увеличен размер ставки на 100")
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                    text=msg + str(price_my_int + int(code)) + '\n'
                                                                               'Подтвердите ставку или увельчьте '
                                                                               'ставку нажав соответсвующую кнопку',
                                    reply_markup=keyboards.keyboards_plus_bet())
    elif code == 'ok':
        await bot.answer_callback_query(callback_query.id, text=f"Нажата кнопка подтверждения ставки")
        bd = BD()
        check = bd.place_bet(id_lot, price_my, telegram_id)
        print(check, ' == ', 'ok')
        if check:
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                        text=f'Ваша ставка {price_my} принята!')
        else:
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                        text=f'Вас уже обогнали, попробуйте сделать ставку выше!')
            print("Что-то не так")
    else:
        print("Что-то не так")


async def choose_size_bet(callback_query):
    product_cap = str(callback_query.message.caption)
    num = product_cap.find('№')
    id_lot_str = product_cap[num + 1:]
    id_lot = int(id_lot_str)
    str_now_price = 'Текущая ставка: '
    num = product_cap.find(str_now_price)
    price_now = product_cap[num + len(str_now_price):]
    num = price_now.find('\n')
    price_now = price_now[:num]
    price_min = callback_query.message.reply_markup.inline_keyboard[0][1].text
    str_min_price = 'Сделать ставку '
    price_min = price_min[len(str_min_price):]
    chat_id = callback_query.from_user.id
    my_bet = str(int(price_now) + int(price_min))
    str_min_price = 'Минимальная ставка '
    msg = 'Товар №' + id_lot_str + '\n' + str_now_price + price_now + \
          '\n' + str_min_price + price_min + '\n' \
                                             'Ваша текущая ставка: ' + my_bet + '\n' \
                                                                                'Подтвердите ставку или увельчьте ставку ' \
                                                                                'нажав соответсвующую кнопку'

    await bot.send_message(chat_id=chat_id, text=msg, reply_markup=keyboards.keyboards_plus_bet())


@di_bot.callback_query_handler(lambda call: call.data and call.data.startswith('inline_btn_lot_'))
async def process_callback_btn_lot(callback_query: aiogram.types.CallbackQuery):
    code = callback_query.data[-1]
    if code.isdigit():
        code = int(code)
        bd = BD()
        if not bd.is_telegram_auth(callback_query.from_user.id):
            code = 'not auth'
    if code == 1:
        await bot.answer_callback_query(callback_query.id,
                                        text='Нажата кнопка для мгновенной покупки')
        await process_buy_command(callback_query)
    elif code == 2:
        await bot.answer_callback_query(callback_query.id,
                                        text='Нажата кнопка для того, чтобы сделать ставку')
        await choose_size_bet(callback_query)
    else:
        await bot.answer_callback_query(callback_query.id,
                                        text='Вы не авторизованы!')
        await bot.send_message(callback_query.from_user.id, text='Вы не авторизованы!\n'
                                                                 'Используйте команду /authorization')
        print("Что-то не так")


@di_bot.message_handler(commands=['random_lot'])
async def send_random_lot(message):
    url = "https://mobistore.by/files/products/1/samsung-galaxy-a31-128gb-pr7128_3.400x400.jpg"
    # url = "http:/localhost:8000/media/products/1619520457048.jpg"
    telegram_id = message.from_user.id
    db = BD()
    dict_res = db.get_random_lot(telegram_id)
    div_time = normalize_time(dict_res['end_time'])
    capa_text = f"{dict_res['name']}\nТекущая ставка: {str(dict_res['start_price'])}\nДо конца аукциона: " \
                f"{div_time}\nСостояние: {dict_res['condition']} \nОписание: {dict_res['description']}" \
                f"\nТовар №{dict_res['id']}"
    if dict_res['image'] == '' and dict_res['name'] in dict_url_tv:
        url = dict_url_tv[dict_res['name']]

    await bot.send_photo(chat_id=telegram_id,
                         photo=url,
                         caption=capa_text,
                         parse_mode=ParseMode.MARKDOWN,
                         reply_markup=keyboards.keyboards_nearest_lot(dict_res['current_price'],
                                                                      dict_res['min_price_increase'],
                                                                      dict_res['id']))


@di_bot.message_handler(commands=['nearest_lot'])
async def send_nearest_lot(message):
    url = "https://mobistore.by/files/products/1/samsung-galaxy-a31-128gb-pr7128_3.400x400.jpg"
    # url = "http:/localhost:8000/media/products/1619520457048.jpg"
    telegram_id = message.from_user.id
    db = BD()
    dict_res = db.get_nearest_lot(telegram_id)
    div_time = normalize_time(dict_res['end_time'])
    capa_text = f"{dict_res['name']}\nТекущая ставка: {str(dict_res['start_price'])}\nДо конца аукциона: " \
                f"{div_time}\nСостояние: {dict_res['condition']} \nОписание: {dict_res['description']}" \
                f"\nТовар №{dict_res['id']}"
    if dict_res['image'] == '' and dict_res['name'] in dict_url_tv:
        url = dict_url_tv[dict_res['name']]

    await bot.send_photo(chat_id=telegram_id,
                         photo=url,
                         caption=capa_text,
                         parse_mode=ParseMode.MARKDOWN,
                         reply_markup=keyboards.keyboards_nearest_lot(dict_res['current_price'],
                                                                      dict_res['min_price_increase'],
                                                                      dict_res['id']))


@di_bot.message_handler(commands=['help'])
async def send_nearest_lot(message):
    await bot.send_message(chat_id=message.from_user.id,
                           text=text('Список доступных команд:\n'
                                     '/random_lot - Выведет случайный лот из открытых\n'
                                     '/subcategory_lot - Выберите интересующую вас категорию и подкатегорию.'
                                     'Затем вы увидете несколько лотов из этой подкатегории.\n'
                                     '/nearest_lot - Выведет лот, который ближе всех к завершению.\n'
                                     '/authorization - Привязка к вашему акаунту с сайта.'))


@di_bot.message_handler(commands=['terms'])
async def send_terms(message):
    await message.reply("Спасибо что выбрали нашего бота для участия в интернет-аукционе."
                        "\nЕсли у вас возникнут проблемы, то мы не виноваты ;)", reply=False)


@di_bot.callback_query_handler(lambda call: call.data and call.data.startswith('inline_btn_auth_1'))
async def process_callback_btn_lot(callback_query: aiogram.types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id, text='Нажата кнопка для ввода кода авторизации')
    await bot.send_message(callback_query.from_user.id, "Отправьте код авторизации сообщением.")


@di_bot.message_handler(commands=['my_bets'])
async def get_authorization_msg(message):
    url = URL
    bd = BD()
    if bd.is_telegram_auth(message.from_user.id):
        arr_results, bool_arr, arr_lose, stats = bd.get_some_lots_with_history(message.from_user.id)
        print('='*20)
        print(arr_results)
        counter_1 = 0
        bool_counter = 0
        win = []
        lose = []
        counter_2 = 1
        for dict_res in arr_results:
            if not bool_arr[bool_counter]:
                lose.append(counter_2)
                counter_2 += 1
                div_time = normalize_time(dict_res['end_time'])
                capa_text = f"В данном лоте вашу ставку перебили!!!\nВаша ставка была равна {arr_lose[counter_1]}\n" \
                            f"{dict_res['name']}\nТекущая ставка: {str(dict_res['start_price'])}\nДо конца аукциона: " \
                            f"{div_time}\nСостояние: {dict_res['condition']} \nОписание: {dict_res['description']}" \
                            f"\nТовар №{dict_res['id']}"

                if dict_res['image'] == '' and dict_res['name'] in dict_url_tv:
                    url = dict_url_tv[dict_res['name']]
                counter_1 += 1
                bool_counter += 1
                await bot.send_photo(chat_id=message.from_user.id, photo=url, caption=capa_text,
                                     parse_mode=ParseMode.MARKDOWN,
                                     reply_markup=keyboards.keyboards_nearest_lot(dict_res['current_price'],
                                                                                  dict_res['min_price_increase'],
                                                                                  dict_res['id']))
            else:
                win.append(counter_2)
                counter_2 += 1
                div_time = normalize_time(dict_res['end_time'])
                capa_text = f"В данном лоте вы все еще первые, поздравляю!!!\n" \
                            f"{dict_res['name']}\nТекущая ставка: {str(dict_res['start_price'])}\nДо конца аукциона: " \
                            f"{div_time}\nСостояние: {dict_res['condition']} \nОписание: {dict_res['description']}" \
                            f"\nТовар №{dict_res['id']}"
                if dict_res['image'] == '' and dict_res['name'] in dict_url_tv:
                    url = dict_url_tv[dict_res['name']]
                bool_counter += 1
                await bot.send_photo(chat_id=message.from_user.id, photo=url, caption=capa_text,
                                     parse_mode=ParseMode.MARKDOWN)
        if stats[0] + stats[1] == 0:
            await bot.send_message(chat_id=message.from_user.id, text='Сейчас у вас нет ни одной активной ставки!')
        else:
            msg = f"СТАТИСТИКА!!!\nВы до сих пор учавствуете в {stats[0] + stats[1]} аукционах\n" \
                  f"Соответственно побеждаете в {stats[0]}, а именно {win}"\
                  f"\nА в {stats[1]} вашу ставку перебили.\nЭтими аукционами оказались {lose}"
            await bot.send_message(chat_id=message.from_user.id, text=msg)
    else:
        await bot.send_message(message.from_user.id, text='Вы не авторизованы!\n'
                                                          'Используйте команду /authorization')


@di_bot.message_handler(commands=['authorization'])
async def get_authorization_msg(message):
    await bot.send_message(chat_id=message.from_user.id,
                           text=text('Нажмите кнопку ввести код авторизации, если он у вас есть\n '
                                     'если же кода у вас нет, то перейдите на сайт и получите его'),
                           reply_markup=keyboards.keyboards_authorization())


@di_bot.message_handler(regexp=r'[0-9a-fA-F]{32}$')
async def get_authorization_msg(message):
    if len(message.text) == 32:
        db = BD()
        dict_user = db.binding_account(message.text, message.from_user.id)
        if dict_user is not None:
            txt = 'Вы авторизованы как ' + dict_user['username']
            await bot.send_message(chat_id=message.from_user.id, text=txt)
        else:
            await bot.send_message(chat_id=message.from_user.id, text='С вашим кодом авторизации, что-то не так. '
                                                                      '\nСкопируйте код на сайте и попробуйте еще раз')
    else:
        await bot.send_message(chat_id=message.from_user.id, text='С вашим кодом авторизации, что-то не так. '
                                                                  '\nСкопируйте код на сайте и попробуйте еще раз')


@di_bot.message_handler(content_types=['text'])
async def get_text_messages(message):
    await bot.send_message(chat_id=message.from_user.id,
                           text='Нажми /help, там написаны команды, которые мне можно писать')


if __name__ == '__main__':
    aiogram.executor.start_polling(di_bot, skip_updates=True)
