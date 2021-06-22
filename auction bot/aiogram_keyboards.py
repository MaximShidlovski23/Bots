from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def keyboards_nearest_lot(cur_price, min_increase, id_product):
    inline_kb_lot = InlineKeyboardMarkup(row_width=2)
    inline_btn_lot_1 = InlineKeyboardButton(f'Купить сейчас за {cur_price}',
                                            callback_data='inline_btn_lot_1')
    inline_btn_lot_2 = InlineKeyboardButton(f'Сделать ставку {min_increase}',
                                            callback_data='inline_btn_lot_2')
    inline_btn_lot_3 = InlineKeyboardButton('Перейти к лоту', url=f'http://127.0.0.1:8000/api/product/{id_product}/')
    inline_kb_lot.add(inline_btn_lot_1, inline_btn_lot_2)
    inline_kb_lot.add(inline_btn_lot_3)

    return inline_kb_lot


def keyboards_category(arr_cat):
    inline_kb_category = InlineKeyboardMarkup(row_width=2)
    btn_arr = []
    i = 1
    for cat in arr_cat:
        name_btn = 'inline_btn_cat_' + str(i)
        inline_btn = InlineKeyboardButton(cat, callback_data=name_btn)
        btn_arr.append(inline_btn)
        i += 1
    len_arr = len(btn_arr)
    ost = len_arr % 3
    int_len = len_arr // 3
    i = 0
    for i_l in range(int_len):
        inline_kb_category.add(btn_arr[i], btn_arr[i + 1], btn_arr[i + 2])
        i = i + 3
    if ost == 1:
        inline_kb_category.add(btn_arr[-1])
    elif ost == 2:
        inline_kb_category.add(btn_arr[-2], btn_arr[1])
    return inline_kb_category


def keyboards_subcategory(arr_subcat):
    inline_kb_subcategory = InlineKeyboardMarkup(row_width=2)
    btn_arr = []
    i = 1
    for cat in arr_subcat:
        name_btn = 'inline_btn_subcat_' + str(i)
        inline_btn = InlineKeyboardButton(cat, callback_data=name_btn)
        btn_arr.append(inline_btn)
        i += 1
    len_arr = len(btn_arr)
    ost = len_arr % 3
    int_len = len_arr // 3
    i = 0
    for i_l in range(int_len):
        inline_kb_subcategory.add(btn_arr[i], btn_arr[i + 1], btn_arr[i + 2])
        i = i + 3
    if ost == 1:
        inline_kb_subcategory.add(btn_arr[-1])
    elif ost == 2:
        inline_kb_subcategory.add(btn_arr[-2], btn_arr[1])
    return inline_kb_subcategory


def keyboards_authorization():
    inline_kb_auth = InlineKeyboardMarkup(row_width=2)
    inline_btn_auth_1 = InlineKeyboardButton(f'Ввести код авторизации', callback_data='inline_btn_auth_1')
    inline_btn_auth_2 = InlineKeyboardButton(f'Перейти на сайт', url='http://127.0.0.1:8000/api/login')
    inline_kb_auth.add(inline_btn_auth_1, inline_btn_auth_2)
    return inline_kb_auth

def keyboards_plus_bet():
    inline_kb_bet = InlineKeyboardMarkup(row_width=3)
    inline_btn_bet_1 = InlineKeyboardButton('1', callback_data='btn_bet_1')
    inline_btn_bet_2 = InlineKeyboardButton('10', callback_data='btn_bet_10')
    inline_btn_bet_3 = InlineKeyboardButton('100', callback_data='btn_bet_100')
    inline_btn_bet_ok = InlineKeyboardButton('Подтвердить ставку', callback_data='btn_bet_ok')
    inline_kb_bet.add(inline_btn_bet_1, inline_btn_bet_2, inline_btn_bet_3)
    inline_kb_bet.add(inline_btn_bet_ok)
    return inline_kb_bet

