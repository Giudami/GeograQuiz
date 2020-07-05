from telegram.utils.helpers import mention_html
from telegram.ext import (Updater, CommandHandler,
                          PollAnswerHandler, PollHandler, MessageHandler, Filters)
from telegram import (Poll, ParseMode, KeyboardButton, KeyboardButtonPollType,
                      ReplyKeyboardMarkup, ReplyKeyboardRemove)
import logging
import random
import json
import requests


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

options_number = 3
countries = None
countries_count = 0
index_for_uri = {}
quiz_types = 4


def start(update, context):

    update.message.reply_text(
        'Digita /nuovo per avviare un nuovo quiz')


def new_quiz(update, context):
    print(update, context)


def quiz(update, context):
    quizType = random.randrange(quiz_types)

    if (quizType == 0):
        result = country_for_capital_question()
        questions = result["options"]
        correct_option = questions.index(result["correct"])
        questions = [get_country_label(question) for question in questions]

    elif (quizType == 1):
        result = map_question()
        questions = result["options"]
        correct_option = questions.index(result["correct"])
        questions = [get_country_label(question)
                     for question in questions]

        image = svg2png(result["image"])

        update.message.reply_photo(image)

    elif (quizType == 2):
        result = flag_question()
        questions = result["options"]
        correct_option = questions.index(result["correct"])
        questions = [get_country_label(question)
                     for question in questions]

        image = svg2png(result["image"])

        update.message.reply_photo(image)

    elif (quizType == 3):
        result = population_question()
        questions = result["options"]
        correct_option = questions.index(result["correct"])

    message = update.effective_message.reply_poll(result["title"],
                                                  questions, type=Poll.QUIZ,
                                                  is_anonymous=False,
                                                  correct_option_id=correct_option)

    # Save some info about the poll the bot_data for later use in receive_quiz_answer
    payload = {
        message.poll.id: {
            "chat_id":
            update.effective_chat.id,
            "message_id":
            message.message_id
        }
    }

    print("id:", payload)  # id della chat

    context.bot_data.update(payload)


def get_country_label(URI):
    if (URI in index_for_uri):
        return countries[index_for_uri[URI]]["countryLabel"]
    else:
        return URI


def receive_quiz_answer(update, context):
    print(update)  # id dell'utente
    """Summarize a users poll vote"""
    answer = update.poll_answer
    poll_id = answer.poll_id
    try:
        questions = context.bot_data[poll_id]["questions"]
    # this means this poll answer update is from an old poll, we can't do our answering then
    except KeyError:
        return

    if context.bot_data[poll_id]["answers"] == 3:
        context.bot.stop_poll(context.bot_data[poll_id]["chat_id"],
                              context.bot_data[poll_id]["message_id"])


def help_handler(update, context):
    """Display a help message"""
    update.message.reply_text("Use /quiz, /poll or /preview to test this "
                              "bot.")


def random_elems(elems, n):
    return [elems[i] for i in random.sample(range(len(elems)), n)]


def map_question():
    country_index = random.randrange(countries_count)
    country = countries[country_index]
    options = random_elems(country["related"], options_number)
    options.append(country["country"])
    random.shuffle(options)
    mapIndex = random.randrange(len(country["maps"]))
    image = country["maps"][mapIndex]

    result = {
        "title": "Qual è la nazione in figura?",
        "image": image,
        "options": options,
        "correct": country["country"]
    }
    return result


def population_question():
    country_index = random.randrange(countries_count)
    country = countries[country_index]
    population = int(country["population"])
    options = ['{:,}'.format(population).replace(',', '.')]
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
        pop = round((population + population * (random.random() - 0.5)) * x)
        options.append('{:,}'.format(pop).replace(',', '.'))

    random.shuffle(options)
    result = {
        "title": country["countryLabel"] + ": a quanto ammonta la sua popolazione?",
        "options": options,
        "correct": '{:,}'.format(population).replace(',', '.')
    }
    return result


def country_for_capital_question():
    countryIndex = random.randrange(countries_count)
    country = countries[countryIndex]
    options = random_elems(country["related"], options_number)
    options.append(country["country"])
    random.shuffle(options)
    result = {
        "title": country["capitalLabel"] + " è la capitale di quale tra le seguenti nazioni?",
        "options": options,
        "correct": country["country"]
    }
    return result


def flag_question():
    country_index = random.randrange(countries_count)
    country = countries[country_index]
    options = random_elems(country["related"], options_number)
    options.append(country["country"])
    random.shuffle(options)
    image = country["flag"]

    result = {
        "title": "A quale nazione appartiene questa bandiera?",
        "image": image,
        "options": options,
        "correct": country["country"]
    }
    return result


def svg2png(url):
    url = requests.get(url).url
    url = url.split("/")
    ans = "https://upload.wikimedia.org/wikipedia/commons/thumb/" + \
        url[-3] + "/" + url[-2] + "/" + url[-1] + "/400px-" + url[-1] + ".png"
    return ans


def main():

    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    updater = Updater(
        "1368648049:AAFIi3WlDUVvRBHRMp_llCBXmrHIcB6KXQ4", use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('nuovo', new_quiz))
    dp.add_handler(CommandHandler('quiz', quiz))
    dp.add_handler(PollAnswerHandler(receive_quiz_answer))
    dp.add_handler(CommandHandler('help', help_handler))

    updater.start_polling()

    updater.idle()


with open("./data.json") as input:
    countries = json.load(input)
    countries_count = len(countries)
    i = 0
    for country in countries:
        index_for_uri[country["country"]] = i
        i += 1


if __name__ == '__main__':
    main()
