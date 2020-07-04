
import logging

from telegram import (Poll, ParseMode, KeyboardButton, KeyboardButtonPollType,
                      ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, PollAnswerHandler, PollHandler, MessageHandler,
                          Filters)
from telegram.utils.helpers import mention_html

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

sessions = {}


def start_bot_handler(update, context):
    if (update.message.chat.type == 'group'):
        update.message.reply_text('Digita /nuovo per creare un nuovo quiz')
    else:
        update.message.reply_text(
            'Questo bot è pensato per i gruppi, aggiungilo ad un gruppo @GeograQuizBot')


def new_handler(update, context):

    chat_id = update.message.chat.id
    if (chat_id in sessions):
        update.message.reply_text(
            'Il quiz è già stato avviato, digita /termina per terminarlo')
    elif (update.message.chat.type == 'group'):
        # mettere numero round variabile
        sessions[chat_id] = {"participants": [],
                             "is_started": False, "rounds_left": 6}
        update.message.reply_text(
            'Digita /partecipa per prendere parte al quiz, /avvia per avviare il quiz')
    else:
        update.message.reply_text(
            'Questo bot è pensato per i gruppi, aggiungilo ad un gruppo @GeograQuizBot')


def taking_part_handler(update, context):
    chat_id = update.message.chat.id
    user_id = update.message.from_user.id
    if (chat_id in sessions):
        if (sessions[chat_id]['is_started']):
            update.message.reply_text(
                'Non puoi prendere parte ad un quiz già iniziato')
        elif (user_id not in sessions[chat_id]['participants']):
            sessions[chat_id]['participants'].append(user_id)
            update.message.reply_text('Mo me lo segno')
        else:
            update.message.reply_text('Sei già un partecipante')
    else:
        if (update.message.chat.type == 'group'):
            update.message.reply_text(
                'Digita /nuovo per avviare un nuovo quiz')
        else:
            update.message.reply_text(
                'Questo bot è pensato per i gruppi, aggiungilo ad un gruppo @GeograQuizBot')


def stop_handler(update, context):

    chat_id = update.message.chat.id
    if (chat_id in sessions):
        del sessions[chat_id]
        update.message.reply_text('Quiz cancellato')
    else:
        update.message.reply_text('Non c\'è nessun quiz in corso')


def start_handler(update, context):
    chat_id = update.message.chat.id
    if (chat_id in sessions):
        if (sessions[chat_id]['is_started']):
            update.message.reply_text('Il quiz è già avviato')
        else:
            if (len(sessions[chat_id]['participants']) > 1):
                sessions[chat_id]['is_started'] = True
                update.message.reply_text(
                    'MI DISPIACE MA QUESTA FUNZIONE NON ESISTE ANCORA')
            else:
                update.message.reply_text(
                    'Servono almeno due partecipanti, digita /partecipa per partecipare')

    else:
        update.message.reply_text(
            'Digita /nuovo per creare un nuovo quiz prima di avviarlo')


def main():

    updater = Updater(
        "1368648049:AAFIi3WlDUVvRBHRMp_llCBXmrHIcB6KXQ4", use_context=True)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start_bot_handler))
    dispatcher.add_handler(CommandHandler('avvia', start_handler))
    dispatcher.add_handler(CommandHandler('nuovo', new_handler))
    dispatcher.add_handler(CommandHandler('partecipa', taking_part_handler))
    dispatcher.add_handler(CommandHandler('termina', stop_handler))
    dispatcher.add_handler(CommandHandler('avvia', stop_handler))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
