import telebot
from telegram import Update
import re
import requests

import apiai
import json
from translate import translator
import urllib3
from bs4 import BeautifulSoup
import random
import cv2 as cv
from special_data import *

bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    text = f'Привет ' + message.from_user.first_name + ', я Jarvis и я могу многое.\n ' \
                                                       'Можем начинать, список команд можешь посмотреть в /help'
    bot.reply_to(message, text)


def get_url(str, url1):
    contents = requests.get(url1).json()
    url = contents[str]
    return url


def get_image_url(f_str, url1):
    allowed_extension = ['jpg', 'jpeg', 'png']
    file_extension = ''
    url = ""
    while file_extension not in allowed_extension:
        url = get_url(f_str, url1)
        file_extension = re.search("([^.]*)$", url).group(1).lower()
    return url


@bot.message_handler(commands=['cat', 'dog'])
def send_random_photo(message):
    url = ""
    if message.text == '/cat':
        url = get_image_url(file_str, cat_url)
    elif message.text == '/dog':
        url = get_image_url(url_str, dog_url)
    chat_id = message.from_user.id
    bot.send_photo(chat_id=chat_id, photo=url)


@bot.message_handler(commands=['translate_en_ru'])
def get_text_translate(message):
    if message.text == '/translate_en_ru':
        translate_text = message.text.replace('/translate_en_ru ', '')
        new_text = translator('en', 'ru-RU', translate_text)
    else:
        translate_text = message.text.replace('/translate_ru_en ', '')
        new_text = translator('ru', 'en-EN', translate_text)
    bot.reply_to(message, new_text[0][0][0])


@bot.message_handler(commands=['pressball_main'])
def get_pressball(message):
    http = urllib3.PoolManager()
    response = http.request('GET', 'https://www.pressball.by/rss/rambler.xml')
    soup = BeautifulSoup(response.data)
    # print(soup.prettify())
    # soup.split('http', 1)[1].lstrip()
    strr = str(soup)
    mas_url = []
    res = re.search(r'title>', strr)
    strr = strr[res.end():]
    res = re.search(r'<', strr)
    mas_url.append(strr[:res.start()])
    res = re.search(r'https', strr)
    while res:
        strr = strr[res.start():]
        res = re.search(r'<', strr)
        mas_url.append(strr[:res.start()])
        strr = strr[res.start():]
        res = re.search('https', strr)
    bot.send_message(chat_id=message.from_user.id, text=mas_url[0])
    mas_url = mas_url[4:]
    for text in mas_url:
        bot.send_message(chat_id=message.from_user.id, text=text)


@bot.message_handler(commands=['pressball_random'])
def get_pressball(message):
    http = urllib3.PoolManager()
    response = http.request('GET', 'https://www.pressball.by/rss/rambler_actual.xml')
    soup = BeautifulSoup(response.data)
    # print(soup.prettify())
    # soup.split('http', 1)[1].lstrip()
    strr = str(soup)
    mas_url = []
    res = re.search(r'title>', strr)
    strr = strr[res.end():]
    res = re.search(r'<', strr)
    mas_url.append(strr[:res.start()])
    res = re.search(r'https', strr)
    while res:
        strr = strr[res.start():]
        res = re.search(r'<', strr)
        mas_url.append(strr[:res.start()])
        strr = strr[res.start():]
        res = re.search('https', strr)
    # bot.send_message(chat_id=message.from_user.id, text=mas_url[0])
    mas_url = mas_url[4:]
    bot.send_message(chat_id=message.from_user.id, text=mas_url[random.randint(0, len(mas_url))])
    """for text in mas_url:
        bot.send_message(chat_id=message.from_user.id, text=text)"""


def qr_decoder(photo_name):
    # img = Image.open(photo_name)
    img = cv.imread(photo_name)
    det = cv.QRCodeDetector()
    results, points, straight_qrcode = det.detectAndDecode(img)
    print(results)
    return results


@bot.message_handler(content_types=['photo'])
def get_qr_code(message):
    file_ID = message.photo[-1].file_id
    file_info = bot.get_file(file_ID)
    downloaded_photo = bot.download_file(file_info.file_path)
    with open('qr_bot_test.jpg', 'wb') as new_photo:
        new_photo.write(downloaded_photo)
    print(new_photo.name)
    res = qr_decoder(new_photo.name)
    if res == "":
        res = 'lollol'
    bot.send_message(chat_id=message.from_user.id, text=res)


@bot.message_handler(commands=['help'])
def send_nearest_lot(message):
    bot.send_message(chat_id=message.from_user.id,
                     text='Список доступных команд:\n'
                          '/')


@bot.message_handler(commands=['weather'])
def get_weather(message):
    mes = message.text[9:]
    params = {"access_key": code_weatherAPI, "query": mes}
    response = requests.get(weather_url, params)
    api_response = response.json()
    try:
        temper = api_response['current']['temperature']
        last = abs(temper) % 10
        if last == 0 or last > 4:
            text = f"Сейчас в " + mes + " " + str(temper) + " градусов"
        elif last == 1:
            text = f"Сейчас в " + mes + " " + str(temper) + " градус"
        else:
            text = f"Сейчас в " + mes + " " + str(temper) + " градуса"
        bot.send_message(chat_id=message.from_user.id, text=text)
    except Exception:
        text = 'Такс похоже ты написал/а либо не город, либо я такого города не знаю :('
        bot.send_message(chat_id=message.from_user.id, text=text)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    request = apiai.ApiAI(code_ApiAI).text_request()
    request.lang = 'ru'
    request.session_id = 'Some_JARVIS_BOT'
    request.query = message.text
    responseJson = json.loads(request.getresponse().read().decode('utf-8'))
    response = responseJson['result']['fulfillment']['speech']
    if response:
        bot.send_message(chat_id=message.from_user.id, text=response)
    else:
        bot.send_message(chat_id=message.from_user.id, text='Не пиши мне такое, я просто JARVIS')


if __name__ == "__main__":
    bot.polling(none_stop=True)
