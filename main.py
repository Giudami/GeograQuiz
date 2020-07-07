
import logging
import requests
import random
import json

from functools import reduce
from telegram import (Poll, ParseMode, KeyboardButton, KeyboardButtonPollType,
                      ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, PollAnswerHandler, PollHandler, MessageHandler,
                          Filters)
from telegram.utils.helpers import mention_html

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

sessions = {}
options_number = 3
countries = None
countries_count = 0
index_for_uri = {}
quiz_types = 4
rounds_count = 10


###################################
#   HANDLERS
###################################

def help_handler(update, context):

    if (update.message.chat.type == 'group'):

        context.bot.send_message(update.message.chat.id,
                                 text="""
🌍 Benvenuto su GeograQuiz! 🌎

Gioca insieme ai tuoi amici rispondendo alle seguenti 10 domande sulla geografia mondiale! Chi saprà fare di meglio? 😉

Puoi utilizzare i seguenti comandi:

👉 /nuovo
    per creare un nuovo quiz

👉 /partecipo
    per partecipare al quiz

👉 /avvia
    per avviare il quiz

👉 /avanti
    per richiedere la prossima
    domanda

👉 /termina
    per terminare il quiz


Inizia a giocare! 🇮🇹🇸🇰🇧🇪🇧🇷🇺🇦🇻🇳""", parse_mode=ParseMode.HTML)

    else:
        context.bot.send_message(update.message.chat.id,
                                 'Questo bot è pensato per i gruppi, aggiungilo ad un gruppo! @GeograQuizBot')


def new_handler(update, context):

    chat_id = update.message.chat.id
    if chat_id in sessions:
        update.message.reply_text(
            'C \'è già un quiz in corso\n\n digita 👉 /termina per terminarlo')
    elif update.message.chat.type == 'group':
        # mettere numero round variabile
        sessions[chat_id] = {'participants': {}, 'usernames': {},
                             'is_started': False, 'can_request': False, 'rounds_left': rounds_count}
        update.message.reply_text(
            'Digita\n\n👉 /partecipo per prendere parte al quiz\n\n👉 /avvia quando siete pronti per avviare il quiz')
    else:
        update.message.reply_text(
            'Questo bot è pensato per i gruppi, aggiungilo ad un gruppo @GeograQuizBot')


def taking_part_handler(update, context):
    chat_id = update.message.chat.id
    user_id = update.message.from_user.id
    if chat_id in sessions:
        if sessions[chat_id]['is_started']:
            update.message.reply_text(
                'Non puoi prendere parte ad un quiz già iniziato! 😢')
        elif user_id not in sessions[chat_id]['participants']:
            sessions[chat_id]['participants'][user_id] = 0
            sessions[chat_id]['usernames'][user_id] = update.message.from_user.username
        else:
            update.message.reply_text('Sei già un partecipante! 😎')
    else:
        if update.message.chat.type == 'group':
            update.message.reply_text(
                'Digita 👉 /nuovo per avviare un nuovo quiz!')
        else:
            update.message.reply_text(
                'Questo bot è pensato per i gruppi, aggiungilo ad un gruppo @GeograQuizBot')


def stop_handler(update, context):

    chat_id = update.message.chat.id
    if chat_id in sessions:
        del sessions[chat_id]
        update.message.reply_text('Quiz cancellato 😢')
    else:
        update.message.reply_text('Non c\'è nessun quiz in corso 🤔')


def start_handler(update, context):
    chat_id = update.message.chat.id
    if chat_id in sessions:
        if sessions[chat_id]['is_started']:
            update.message.reply_text('Il quiz è già avviato 😎')
        else:
            if len(sessions[chat_id]['participants']) > 1:
                sessions[chat_id]['is_started'] = True
                sessions[chat_id]['can_request'] = True
                update.message.reply_text(
                    'Digita 👉 /avanti per la prossima domanda')
            else:
                update.message.reply_text(
                    'Servono almeno due partecipanti, Digita\n\n👉 /partecipo per prendere parte al quiz')

    else:
        update.message.reply_text(
            'Digita 👉 /nuovo per creare un nuovo quiz prima di avviarlo')


def next_question_handler(update, context):
    chat_id = update.message.chat.id
    user_id = update.message.from_user.id
    if chat_id not in sessions:
        update.message.reply_text(
            'Digita 👉 /nuovo per avviare un nuovo quiz!')
    else:
        session = sessions[chat_id]
        if user_id not in session['participants']:
            update.message.reply_text(
                'Digita 👉 /avanti per la prossima domanda')
        elif not session['is_started']:
            update.message.reply_text(
                'Digita 👉 /avanti per avviare un nuovo quiz')
        elif not session['can_request']:
            update.message.reply_text(
                'Dovete dare tutti una risposta prima di procedere alla prossima domanda! 😉')
        else:
            session['can_request'] = False
            quiz_type = random.randrange(quiz_types)

            questions = [population_question,
                         country_for_capital_question,
                         map_question,
                         flag_question]

            result = random.choice(questions)()

            if result['image'] is not None:
                update.effective_message.reply_photo(svg2png(result['image']))

            message = update.effective_message.reply_poll(result['title'],
                                                          result['options'],
                                                          type=Poll.QUIZ,
                                                          is_anonymous=False,
                                                          explanation=result['explanation'],
                                                          correct_option_id=result['correct'])

            # Save some info about the poll the bot_data for later use in receive_quiz_answer
            payload = {
                message.poll.id: {
                    'chat_id':
                    update.effective_chat.id,
                    'message_id':
                    message.message_id,
                    'correct_option_id': result['correct'],
                    'current_answers': 0
                }
            }
            context.bot_data.update(payload)


def receive_question_answer(update, context):
    answer = update.poll_answer
    poll_id = answer.poll_id
    chat_id = context.bot_data[poll_id]['chat_id']
    user_id = answer.user.id
    option_id = answer['option_ids'][0]
    correct_option_id = context.bot_data[poll_id]['correct_option_id']

    if chat_id in sessions and user_id in sessions[chat_id]['participants']:

        participants = sessions[chat_id]['participants']
        context.bot_data[poll_id]['current_answers'] += 1

        if option_id == correct_option_id:
            participants[user_id] += 1

        if context.bot_data[poll_id]['current_answers'] == len(participants):
            context.bot.stop_poll(
                chat_id, context.bot_data[poll_id]['message_id'])

            sessions[chat_id]['can_request'] = True
            sessions[chat_id]['rounds_left'] -= 1
            if sessions[chat_id]['rounds_left'] == 0:
                sorted_partecipants = sorted(
                    participants.items(), key=lambda x: x[1], reverse=True)
                text = '\n'
                for i, x in enumerate(sorted_partecipants):
                    text += str(i + 1) + '. @' + sessions[chat_id]['usernames'][x[0]] + \
                        ' ' + str(x[1]) + ' corrette\n\n'
                context.bot.send_message(
                    chat_id, text='🏆 CLASSIFICA 🏆\n' + text)
                del sessions[chat_id]
            else:
                context.bot.send_message(
                    chat_id, text='👉 /avanti per la prossima domanda')


###################################
#   QUESTIONS
###################################

def question_data():
    country = countries[random.randrange(countries_count)]
    options = random_elems(country['related'], options_number)
    options.append(country['country'])
    random.shuffle(options)
    correct_index = options.index(country['country'])
    options = [get_country_label(o) for o in options]
    return (country, options, correct_index)


def map_question():

    (country, options, correct_index) = question_data()
    return {
        'title': 'Qual è la nazione in figura?',
        'options': options,
        'correct': correct_index,
        'explanation': country['article'],
        'image': random.choice(country['maps'])
    }


def population_question():
    (country, options, correct_index) = question_data()
    population = int(country['population'])
    options = [population]
    for i in range(options_number):
        x = random.randrange(4)
        if (x == 0):
            x = 5
        elif (x == 1):
            x = 1 / 5
        elif (x == 2):
            x = 8
        elif (x == 3):
            x = 1 / 8
        option = round((population + population * (random.random() - 0.5)) * x)
        options.append(option)
    random.shuffle(options)
    correct_index = options.index(population)
    options = ['{:,}'.format(o).replace(',', '.') for o in options]

    return {
        'title': country['countryLabel'] + ': a quanto ammonta la sua popolazione?',
        'options': options,
        'correct': correct_index,
        'explanation': country['article'],
        'image': None
    }


def country_for_capital_question():
    (country, options, correct_index) = question_data()
    return {
        'title': country['capitalLabel'] + ' è la capitale di quale tra le seguenti nazioni?',
        'options': options,
        'correct': correct_index,
        'explanation': country['article'],
        'image': None
    }


def flag_question():
    (country, options, correct_index) = question_data()
    return {
        'title': 'A quale nazione appartiene questa bandiera?',
        'options': options,
        'correct': correct_index,
        'explanation': country['article'],
        'image': country['flag']
    }


###################################
#   UTILS
###################################

def svg2png(url):
    url = requests.get(url).url
    url = url.split('/')
    ans = 'https://upload.wikimedia.org/wikipedia/commons/thumb/' + \
        url[-3] + '/' + url[-2] + '/' + url[-1] + '/400px-' + url[-1] + '.png'
    return ans


def random_elems(elems, n):
    return [elems[i] for i in random.sample(range(len(elems)), n)]


def get_country_label(URI):
    return countries[index_for_uri[URI]]['countryLabel']


###################################
#   MAIN
###################################

with open('./data.json') as input:
    countries = json.load(input)
    countries_count = len(countries)
    i = 0
    for country in countries:
        index_for_uri[country['country']] = i
        i += 1

updater = Updater(
    '1368648049:AAFIi3WlDUVvRBHRMp_llCBXmrHIcB6KXQ4', use_context=True)

dispatcher = updater.dispatcher
dispatcher.add_handler(CommandHandler('start', help_handler))
dispatcher.add_handler(CommandHandler('aiuto', help_handler))
dispatcher.add_handler(CommandHandler('nuovo', new_handler))
dispatcher.add_handler(CommandHandler('avanti', next_question_handler))
dispatcher.add_handler(CommandHandler('avvia', start_handler))
dispatcher.add_handler(CommandHandler('partecipo', taking_part_handler))
dispatcher.add_handler(CommandHandler('termina', stop_handler))
dispatcher.add_handler(PollAnswerHandler(receive_question_answer))
updater.start_polling()
updater.idle()
