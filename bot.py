#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
Basic example for a bot that works with polls. Only 3 people are allowed to interact with each
poll/quiz the bot generates. The preview command generates a closed poll/quiz, excatly like the
one the user sends the bot
"""
from telegram.utils.helpers import mention_html
from telegram.ext import (Updater, CommandHandler, PollAnswerHandler, PollHandler, MessageHandler,
                          Filters)
from telegram import (Poll, ParseMode, KeyboardButton, KeyboardButtonPollType,
                      ReplyKeyboardMarkup, ReplyKeyboardRemove)
import logging

import random

import json

import request


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

optionsNumber = 3
countries = None
countriesCount = 0
indexForUri = {}
quizTypes = 2


def start(update, context):
    """Inform user about what this bot can do"""
    update.message.reply_text('Please select /poll to get a Poll, /quiz to get a Quiz or /preview'
                              ' to generate a preview for your poll')


def poll(update, context):
    """Sends a predefined poll"""
    questions = ["Good", "Really good", "Fantastic", "Great"]
    message = context.bot.send_poll(update.effective_user.id, "How are you?", questions,
                                    is_anonymous=False, allows_multiple_answers=True)
    # Save some info about the poll the bot_data for later use in receive_poll_answer
    payload = {message.poll.id: {"questions": questions, "message_id": message.message_id,
                                 "chat_id": update.effective_chat.id, "answers": 0}}
    context.bot_data.update(payload)


def receive_poll_answer(update, context):
    """Summarize a users poll vote"""
    answer = update.poll_answer
    poll_id = answer.poll_id
    try:
        questions = context.bot_data[poll_id]["questions"]
    # this means this poll answer update is from an old poll, we can't do our answering then
    except KeyError:
        return
    selected_options = answer.option_ids
    answer_string = ""
    for question_id in selected_options:
        if question_id != selected_options[-1]:
            answer_string += questions[question_id] + " and "
        else:
            answer_string += questions[question_id]
    user_mention = mention_html(
        update.effective_user.id, update.effective_user.full_name)
    context.bot.send_message(context.bot_data[poll_id]["chat_id"],
                             "{} feels {}!".format(
                                 user_mention, answer_string),
                             parse_mode=ParseMode.HTML)
    context.bot_data[poll_id]["answers"] += 1
    # Close poll after three participants voted
    if context.bot_data[poll_id]["answers"] == 3:
        context.bot.stop_poll(context.bot_data[poll_id]["chat_id"],
                              context.bot_data[poll_id]["message_id"])


def quiz(update, context):
    quizType = random.randrange(quizTypes)
    if (quizType == 0):

        result = countryForCapitalQuestion()
        questions = result["options"]
        correct_option = questions.index(result["correct"])
        questions = [getCountryLabel(question)
                     for question in questions]

    elif (quizType == 1):
        result = mapQuestion()
        questions = result["options"]
        correct_option = questions.index(result["correct"])
        questions = [getCountryLabel(question)
                     for question in questions]

        svg2png(result["image"])

    # print(indexForUri)
    message = update.effective_message.reply_poll(result["title"],
                                                  questions, type=Poll.QUIZ, correct_option_id=correct_option)
    # Save some info about the poll the bot_data for later use in receive_quiz_answer
    payload = {message.poll.id: {"chat_id": update.effective_chat.id,
                                 "message_id": message.message_id}}
    context.bot_data.update(payload)


def getCountryLabel(URI):
    return countries[indexForUri[URI]]["countryLabel"]


def receive_quiz_answer(update, context):
    """Close quiz after three participants took it"""
    # the bot can receive closed poll updates we don't care about
    if update.poll.is_closed:
        return
    if update.poll.total_voter_count == 3:
        try:
            quiz_data = context.bot_data[update.poll.id]
        # this means this poll answer update is from an old poll, we can't stop it then
        except KeyError:
            return
        context.bot.stop_poll(quiz_data["chat_id"], quiz_data["message_id"])


def preview(update, context):
    """Ask user to create a poll and display a preview of it"""
    # using this without a type lets the user chooses what he wants (quiz or poll)
    button = [
        [KeyboardButton("Press me!", request_poll=KeyboardButtonPollType())]]
    message = "Press the button to let the bot generate a preview for your poll"
    # using one_time_keyboard to hide the keyboard
    update.effective_message.reply_text(message,
                                        reply_markup=ReplyKeyboardMarkup(button,
                                                                         one_time_keyboard=True))


def receive_poll(update, context):
    """On receiving polls, reply to it by a closed poll copying the received poll"""
    actual_poll = update.effective_message.poll
    # Only need to set the question and options, since all other parameters don't matter for
    # a closed poll
    update.effective_message.reply_poll(
        question=actual_poll.question,
        options=[o.text for o in actual_poll.options],
        # with is_closed true, the poll/quiz is immediately closed
        is_closed=True,
        reply_markup=ReplyKeyboardRemove()
    )


def help_handler(update, context):
    """Display a help message"""
    update.message.reply_text("Use /quiz, /poll or /preview to test this "
                              "bot.")


def randomElems(elems, n):
    return [elems[i] for i in random.sample(range(len(elems)), n)]


def mapQuestion():
    countryIndex = random.randrange(countriesCount)
    country = countries[countryIndex]
    mapIndex = random.randrange(len(country["maps"]))
    image = country["maps"][mapIndex]
    options = randomElems(country["related"], optionsNumber)
    options.append(country["country"])
    result = {"title": "Qual è la nazione in figura?",
              "image": image, "options": options, "correct": country["country"]}
    drawing = svg2rlg("")
    renderPDF.drawToFile(drawing, "file.pdf")
    renderPM.drawToFile(drawing, "file.png", fmt="PNG")
    return result


def countryForCapitalQuestion():
    countryIndex = random.randrange(countriesCount)
    country = countries[countryIndex]
    options = randomElems(country["related"], optionsNumber)
    options.append(country["country"])
    result = {"title": country["capitalLabel"] + " è la capitale di quale tra le seguenti nazioni?",
              "options": options, "correct": country["country"]}
    return result


def svg2png(url):
    url = requests.get(url).url
    url = url.split("/")
    ans = "https://upload.wikimedia.org/wikipedia/commons/thumb/" + url[-3] + "/" + url[-2] + "/" + \
        url[-1] + "/600px-" + url[-1] + ".png"
    return ans


def main():

    # print(countryForCapitalQuestion())
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(
        "1368648049:AAFIi3WlDUVvRBHRMp_llCBXmrHIcB6KXQ4", use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('poll', poll))
    dp.add_handler(PollAnswerHandler(receive_poll_answer))
    dp.add_handler(CommandHandler('quiz', quiz))
    dp.add_handler(PollHandler(receive_quiz_answer))
    dp.add_handler(CommandHandler('preview', preview))
    dp.add_handler(MessageHandler(Filters.poll, receive_poll))
    dp.add_handler(CommandHandler('help', help_handler))

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


with open("./assets/query.json") as input:
    countries = json.load(input)
    countriesCount = len(countries)
    i = 0
    for country in countries:
        indexForUri[country["country"]] = i
        i += 1


if __name__ == '__main__':
    main()
