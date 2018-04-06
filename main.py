import json
import random
import tools
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, ConversationHandler

start_keyboard = [["/day_photo", "/mars"], ["/quiz", "/help"]]
markup = ReplyKeyboardMarkup(start_keyboard)
quest = json.load(open("questions.json", mode="r"))
LENTH_JSON = len(quest)
LENTH_QUEST = 5

def start(bot, update):
    update.message.reply_text(
    """"Hi, i'am a Space Travel bot, - you companion in the space
    I have 4 commands:
    /day_photo - bot gives you amazing image of the space. Updates every day. You should to try it.
    /mars - bot gives you random photo from curiosity rover
    /quiz - bot gives you 10 questions and you can get certificate of Space explorer!
    /help - some information about us""", reply_markup=markup)


def hlp(bot, update):
    update.message.reply_text("""
    This bot uses NASA open api https://api.nasa.gov
    Made by Pokrovsky Valery (valer1435) for training.
    Project repository: https://github.com/valer1435/Space_travel_bot
    Thanks to Maxim Kitanin for writing questions for the quiz
    The Certificate is created on http://www.certificatemagic.com/ 
    """, reply_markup=markup)
    return ConversationHandler.END


def day_photo(bot, update):
    img, exp, tit, cop = tools.get_day_photo()
    if img == 1 or img == 2:
        update.message.reply_text("Something works wrong! Try again", reply_markup=markup)
    else:
        bot.send_photo(photo=img, chat_id=update.message.chat_id, caption= "{}. Author: {}".format(tit, cop))
        update.message.reply_text(exp, reply_markup=markup)
    return ConversationHandler.END


def mars(bot, update):
    img, date = tools.get_mars_picture()
    if img:
        bot.send_photo(chat_id=update.message.chat_id, photo=img, caption="Date: {}".format(date), reply_markup=markup)
    else:
        update.message.reply_text("Something works wrong!", reply_markup=markup)
    return ConversationHandler.END


def quiz(bot, update, user_data):
    user_data["quiz"] = []
    user_data["score"] = 0
    user_data["count"] = 0
    user_data["hint"] = True
    update.message.reply_text("Hi! I have some questions for you.")
    q = quest[random.choice(range(LENTH_JSON))]
    answer_keyboard = [[q["A"], q["B"]], [q["C"], q["D"]]]
    markup = ReplyKeyboardMarkup(answer_keyboard)
    update.message.reply_text(q["question"], reply_markup=markup)
    user_data["quiz"].append(q)
    return 1


def question(bot, update, user_data):
    answer = update.message.text
    q = user_data["quiz"][-1]
    true_value = q["true"]
    print(answer, q[true_value])
    if answer == q[true_value]:
        user_data["score"] += 1

    else:
        if user_data["hint"]:
            answer_keyboard = [[q["A"], q["B"]], [q["C"], q["D"]], ["/hint"]]
            markup = ReplyKeyboardMarkup(answer_keyboard)
            update.message.reply_text("Wrong! I can give you an one hint.", reply_markup=markup)
            return 1
        else:
            update.message.reply_text("Wrong!")
    user_data["count"] += 1
    while True:

        q = quest[random.choice(range(LENTH_JSON))]
        flag = False
        for i in user_data["quiz"]:
            if q == i:
                flag = True
                break
        if flag:
            continue
        break
    answer_keyboard = [[q["A"], q["B"]], [q["C"], q["D"]]]
    markup = ReplyKeyboardMarkup(answer_keyboard)
    update.message.reply_text(q["question"], reply_markup=markup)
    user_data["quiz"].append(q)
    print(user_data["score"], user_data["count"] )
    if user_data["count"] == LENTH_QUEST-1:
        return 3
    return 1


def hint(bot, update, user_data):
    if not user_data["hint"]:
        update.message.reply_text("I'm not so stupid")
        if user_data["count"] == LENTH_QUEST-1:
            return 3
        return 1
    q = user_data["quiz"][-1]
    user_data["hint"] = False
    answer_keyboard = [[q[q["true"]]]]
    markup = ReplyKeyboardMarkup(answer_keyboard)
    update.message.reply_text("Try! You can do this!", reply_markup=markup)
    print(user_data["count"])
    if user_data["count"] == LENTH_QUEST-1:
        return 3
    return 1


def all_sumbit(bot, update, user_data):
    answer = update.message.text
    q = user_data["quiz"][-1]
    if answer == q[q["true"]]:
        user_data["score"] += 1
    else:
        if user_data["hint"]:
            answer_keyboard = [[q["A"], q["B"]], [q["C"], q["D"]], ["/hint"]]
            mark= ReplyKeyboardMarkup(answer_keyboard)
            update.message.reply_text("Wrong! I can give you an one hint.", reply_markup=mark)
            return 3
        else:
            update.message.reply_text("Wrong!")
    user_data["count"] += 1
    if user_data["score"] == LENTH_QUEST:
        update.message.reply_text("Congratulations! You are now a Space expert! You scored 5 points. Welcome to our spaceship!", reply_markup=markup)
        bot.send_photo(chat_id=update.message.chat_id, photo=open('certificate.png', 'rb'))

    elif user_data["score"] in [LENTH_QUEST-1, LENTH_QUEST-2]:
        update.message.reply_text("Hmmm! You have good knowledge about the space! You scored {} points. But it isn't enough for became  a space Explorer!!".format(user_data["score"]), reply_markup=markup)
    else:
        update.message.reply_text("Oh my God! Seriously? You must to get more information! You scored {} points".format(user_data["score"]), reply_markup=markup)
    return ConversationHandler.END


def stop_quiz(bot, update):
    update.message.reply_text("Does it so hard for you?", reply_markup=markup)
    return ConversationHandler.END


def stop(bot, update):
    update.message.reply_text("Bye!", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def main():
    updater = Updater("     ")
    dp = updater.dispatcher


# вот сейчас костыль, но без него - никак
    quiz_handler = ConversationHandler(
        entry_points=[ CommandHandler("quiz", quiz, pass_user_data=True), CommandHandler("start", start), CommandHandler("day_photo", day_photo), CommandHandler("mars", mars), CommandHandler("help", hlp)],
        states={
            1: [MessageHandler(Filters.text, question, pass_user_data=True), CommandHandler("hint", hint, pass_user_data=True), CommandHandler("stop", stop), CommandHandler("start", start), CommandHandler("day_photo", day_photo), CommandHandler("mars", mars), CommandHandler("help", hlp)],
            3: [MessageHandler(Filters.text, all_sumbit, pass_user_data=True), CommandHandler("hint", hint, pass_user_data=True), CommandHandler("stop", stop), CommandHandler("start", start), CommandHandler("day_photo", day_photo), CommandHandler("mars", mars), CommandHandler("help", hlp)]
        },
        fallbacks=[CommandHandler("stopquiz", stop_quiz)]
    )

    dp.add_handler(quiz_handler)
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("day_photo", day_photo))
    dp.add_handler(CommandHandler("mars", mars))
    dp.add_handler(CommandHandler("help", hlp))
    dp.add_handler(CommandHandler("stop", stop))
    print("Бот стартует")

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()