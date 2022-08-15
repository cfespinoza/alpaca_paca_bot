#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=W0613, C0116
# type: ignore[union-attr]
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
import datetime
import json
import logging
import pickle

import requests
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler, \
    PicklePersistence

# Enter your API key here
api_key = "xYOWOvD0ulYpGehAsRGhEpGTPArAANgq"

codigo_cuzco = "257812"
codigo_aguasCalientes = "262837"
codigo_lima = "264120"
codigo_huaraz = "256878"
codigo_paracas = "4252"

# base_url variable to store url
base_url = "http://dataservice.accuweather.com/forecasts/v1/daily/5day/"

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

usuarios_permitidos = ["cafloresp", "karemmr", "fermoygra", "espergon", "Mar_igl", "elisacampo13", "jlaherradon", "Camynero"]
msg_rechaza = '¡¡Tú no juegas brother, seguro eres Víctor Caminero, ahí no más joven, siga leyendo no más!!'

with open("./planif.json", "r") as f:
    data_planificacion = json.load(f)


def _envia_mensaje(update: Update, msg: str) -> None:
    update.message.reply_text(
        msg
    )


def _envia_mensaje_html(update: Update, msg: str) -> None:
    update.message.reply_html(
        msg
    )


def toCelsius(temp):
    return (temp - 32) * 5 / 9


def parseForecast(data):
    forecasts = data["DailyForecasts"]
    prevision = ""
    for i in forecasts:
        datetimeobject = datetime.datetime.strptime(i["Date"][0:10], '%Y-%m-%d')
        fechaFormat = datetimeobject.strftime('%d-%m-%Y')
        maxima = i["Temperature"]["Maximum"]["Value"]
        maxima = round(toCelsius(maxima), 1)
        realFeelmaxima = i["RealFeelTemperature"]["Maximum"]["Value"]
        realFeelmaxima = round(toCelsius(realFeelmaxima), 1)
        minima = i["Temperature"]["Minimum"]["Value"]
        minima = round(toCelsius(minima), 1)
        realFeelMinima = i["RealFeelTemperature"]["Minimum"]["Value"]
        realFeelMinima = round(toCelsius(realFeelMinima), 1)
        tiempo = i["Day"]["IconPhrase"] + " "

        prevision += "<b>Día: " + fechaFormat + "</b>"
        prevision += "\nPrevisión: " + addIcons(tiempo)
        prevision += "\nTemperatura máxima \U00002B06\U0001F321: " + str(maxima) + "ºC (Sensación de " + str(
            realFeelmaxima) + "ºC)"
        prevision += "\nTemperatura mínima \U00002B07\U0001F321: " + str(minima) + "ºC (Sensación de " + str(
            realFeelMinima) + "ºC)\n\n"
    return prevision


def addIcons(weather):
    if ("lluv" in weather):
        weather += "\U0001F327"
    if ("chuba" in weather):
        weather += "\U0001F327"
    if "Chuba" in weather:
        weather += "\U0001F327"
    if ("clar" in weather):
        weather += "\U00002600"
    if ("espejad" in weather):
        weather += "\U00002600"
    if ("sol" in weather):
        weather += "\U00002600"
    if ("nub" in weather):
        weather += "\U00002601"
    if ("Nub" in weather):
        weather += "\U00002601"
    if ("niev" in weather):
        weather += "\U000026C4"
    if ("torm" in weather):
        weather += "\U0001F329"
    return weather


def _is_allowed(update: Update) -> bool:
    # username = update.message.chat.username
    username = update.message.from_user.username
    logger.info(f" => Mensaje del usuario: {username}")
    return username in usuarios_permitidos


def _get_msg(update: Update, allowed_msg: str, reject_msg: str = msg_rechaza) -> str:
    """Send a message when the command /start is issued."""
    msg = reject_msg
    if _is_allowed(update):
        msg = allowed_msg  # '¡¡Habla, causa!!'
    return msg


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    aux_msg = '¡¡Habla, causa!!'
    msg = _get_msg(update, aux_msg)
    _envia_mensaje(update, msg)


def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    print("\n".join([e.type for e in update.message.entities]))
    if "alpaca_paca_bot" in update.message.text and "mention" in [e.type for e in update.message.entities]:
        msg_a_enviar = "".join(["i" if c in "aeouáéíóú" else c for c in update.message.text])
        msg_a_enviar = f"{msg_a_enviar}... Ponte pilas! Eso no lo entiendo..."
        msg = _get_msg(update, msg_a_enviar)
        _envia_mensaje(update, msg)


def _get_restante() -> str:
    today = datetime.date.today()
    timenow = datetime.datetime.now()
    deadline = "2022-08-15 23:55:00"
    current_time = str(today) + " " + str(timenow.strftime("%H:%M:%S"))
    start = datetime.datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S')
    ends = datetime.datetime.strptime(deadline, '%Y-%m-%d %H:%M:%S')
    print(start)
    print(ends)
    return str(ends - start)


def cuantoqueda(update: Update, context: CallbackContext) -> None:
    msg_a_enviar = f"Aquí os digo el tiempo que queda para despegar: {_get_restante()}"
    msg = _get_msg(update, msg_a_enviar)
    _envia_mensaje(update, msg)


def _get_msg_tiempo(sitio: str, codigo: str) -> str:
    complete_url = base_url + codigo + "?apikey=" + api_key + "&&language=es-es&details=true"
    response = requests.get(complete_url)
    data = response.json()
    print(data)
    prevision = parseForecast(data)
    _sitio = sitio.capitalize()
    prevision = f"<b>Previsión en {_sitio} para los próximos 5 días:</b>\n" + prevision
    print(prevision)
    return prevision


def tiempoaguascalientes(update: Update, context: CallbackContext) -> None:
    msg_pronostico = _get_msg_tiempo("aguas calientes", codigo_aguasCalientes)
    msg = _get_msg(update, msg_pronostico)
    _envia_mensaje_html(update, msg)


def tiempocuzco(update: Update, context: CallbackContext) -> None:
    msg_pronostico = _get_msg_tiempo("cuzco", codigo_cuzco)
    msg = _get_msg(update, msg_pronostico)
    _envia_mensaje_html(update, msg)


def tiempolima(update: Update, context: CallbackContext) -> None:
    msg_pronostico = _get_msg_tiempo("lima", codigo_lima)
    msg = _get_msg(update, msg_pronostico)
    _envia_mensaje_html(update, msg)


def tiempohuaraz(update: Update, context: CallbackContext) -> None:
    msg_pronostico = _get_msg_tiempo("Huaraz", codigo_huaraz)
    msg = _get_msg(update, msg_pronostico)
    _envia_mensaje_html(update, msg)


def tiempoparacas(update: Update, context: CallbackContext) -> None:
    msg_pronostico = _get_msg_tiempo("paracas", codigo_paracas)
    msg = _get_msg(update, msg_pronostico)
    _envia_mensaje_html(update, msg)


def _update_db(key: str, update: Update, context: CallbackContext) -> int:
    _value = context.bot_data.get(key, 0)
    if _is_allowed(update):
        _value += 1
        context.bot_data[key] = _value
    return _value


def picaesther(update: Update, context: CallbackContext) -> None:
    _key = "picaduras"
    _value = _update_db(_key, update, context)
    msg_a_enviar = f"Una más para Esther y ya lleva - {_value} - picaduras." if _value > 1 else "Esther ya tiene su primera picadura. \u2713!!"
    msg = _get_msg(update, msg_a_enviar)
    _envia_mensaje(update, msg)


def quejacami(update: Update, context: CallbackContext) -> None:
    _key = "quejas"
    _value = _update_db(_key, update, context)
    msg_a_enviar = f"Otra  y ya lleva - {_value} - quejas." if _value > 1 else "Ya ha empezado, ¿han llegado a Lima?... \U0001F914!!"
    msg = _get_msg(update, msg_a_enviar)
    _envia_mensaje(update, msg)


def birrafer(update: Update, context: CallbackContext) -> None:
    _key = "birras"
    _value = _update_db(_key, update, context)
    msg_a_enviar = f"Otra y ya lleva - {_value} - chelas. " if _value > 1 else "Empezamos!!! \U0001F37A \U0001F37B!!"
    msg = _get_msg(update, msg_a_enviar)
    _envia_mensaje(update, msg)


def planificacion(update: Update, context: CallbackContext) -> None:
    today = datetime.date.today().strftime("%d%m%Y")
    _dia = datetime.datetime.strptime(today, "%d%m%Y").strftime("%d-%m-%Y")
    mensaje = f"Para el {_dia} tenemos: \n"
    if data_planificacion.get(today):
        mensaje_plani = "".join([f"\t\t\t - A las {datetime.datetime.strptime(today+v, '%d%m%Y%H%M').strftime('%H:%M')}: {v}\n" for k, v in data_planificacion.get(today).items()])
        mensaje += mensaje_plani
    else:
        mensaje += "Nada \U0001F614"
    msg = _get_msg(update, mensaje)
    _envia_mensaje(update, msg)


def full_planificacion(update: Update, context: CallbackContext) -> None:
    lista_mensaje = []
    for dia, plani in data_planificacion.items():
        _dia = datetime.datetime.strptime(dia, "%d%m%Y").strftime("%d-%m-%Y")
        mensaje_plani = f"- Para el día {_dia}: \n" + "".join([f"\t\t\t * A las {datetime.datetime.strptime(dia+h, '%d%m%Y%H%M').strftime('%H:%M')}: {plan}\n" for h, plan in plani.items()]) + "\n"
        lista_mensaje.append(mensaje_plani)
    mensaje = "".join(lista_mensaje)
    msg = _get_msg(update, mensaje)
    _envia_mensaje(update, msg)


def datos_ayuda(update: Update, context: CallbackContext) -> None:
    msg = """
- Persona de contacto en Lima: Justina Espinoza
- Dirección de referencia en Lima: Avenida Carabayllo 260, Urb. Villa Hiper, Comas. Lima.
- Teléfono: +51967909462
- Teléfono policía: 105
- Teléfono embajada españa: 2125155 (https://exteriores.gob.es/Embajadas/lima/es/Embajada/Paginas/Horario,-localizaci%C3%B3n-y-contacto.aspx)    """
    _envia_mensaje(update, msg)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary

    # TOKEN = os.environ.get("TG_TOKEN")
    # updater = Updater(TOKEN, use_context=True)
    persistence = PicklePersistence(filename='alpaca_paca_callback_data.pickle')
    with open('token', 'r') as t:
        token = t.read()
    updater = Updater(token, use_context=True, persistence=persistence)
    # updater = Updater("5068408238:AAFzo8ENdd6b_7FksmSwA7IO_OVVcRGjIIU", use_context=True, persistence=persistence) # CarloBot

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("cuantoqueda", cuantoqueda))
    dispatcher.add_handler(CommandHandler("tiempoparacas", tiempoparacas))
    dispatcher.add_handler(CommandHandler("tiempohuaraz", tiempohuaraz))
    dispatcher.add_handler(CommandHandler("tiempolima", tiempolima))
    dispatcher.add_handler(CommandHandler("tiempocuzco", tiempocuzco))
    dispatcher.add_handler(CommandHandler("tiempoaguascalientes", tiempoaguascalientes))
    dispatcher.add_handler(CommandHandler("planificacion", planificacion))
    dispatcher.add_handler(CommandHandler("picaesther", picaesther))
    dispatcher.add_handler(CommandHandler("quejacami", quejacami))
    dispatcher.add_handler(CommandHandler("cervezafer", birrafer))
    dispatcher.add_handler(CommandHandler("fullplanificacion", full_planificacion))
    dispatcher.add_handler(CommandHandler("datosdeayuda", datos_ayuda))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
