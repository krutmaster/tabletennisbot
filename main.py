# by krutmaster (telegram: @krutmaster1)
import configparser
import random
import telebot


def str_in_dict(dict_in_str):
    return eval(dict_in_str)


config = configparser.ConfigParser()
config.read('config.ini')
token = config.get('Settings', 'token')
user1_score = {}
user2_score = {}
user1 = 'игрок 1'
user2 = 'игрок 2'
count = {}
part = {}
last_point = {}
total_score = str_in_dict(config.get('Settings', 'total_score'))
old_messages = str_in_dict(config.get('Settings', 'old_messages'))
bot = telebot.TeleBot(token)


@bot.message_handler(commands=["left"])
def left_user(message):
    global last_point
    user_id = str(message.chat.id)
    plus_point(message, 0)
    last_point[user_id] = 0


@bot.message_handler(commands=["right"])
def right_user(message):
    global last_point
    user_id = str(message.chat.id)
    plus_point(message, 1)
    last_point[user_id] = 1


@bot.message_handler(commands=["start"])
def start_game(message):
    global user1_score, user2_score, user1, user2, count, part, old_messages, config
    user_id = str(message.chat.id)

    try:

        try:
            bot.delete_message(user_id, old_messages[user_id])
            del old_messages[user_id]
        except Exception:
            pass

        user1_score[user_id] = 0
        user2_score[user_id] = 0
        split = (len(user1) - 1) * ' ' + '   '
        status = f'{user1}   {user2}\n{user1_score[user_id]}{split}{user2_score[user_id]}\n'
        part[user_id] = random.randint(0, 1)
        count[user_id] = 0
        smile = u"\U0001F3BE"
        smile_back = u"\U0001F519"

        if not part[user_id]:
            status += f'{smile}'
        else:
            status += f'{len(user1) * " "}   {smile}'

        keyboard = telebot.types.ReplyKeyboardMarkup()
        keyboard.row(telebot.types.KeyboardButton(f'/left {user1}'),
                     telebot.types.KeyboardButton(f'/right {user2}'))
        keyboard.add(telebot.types.KeyboardButton(f'/step_back {smile_back}'))
        old_message = bot.send_message(user_id, status, reply_markup=keyboard)
        old_messages[user_id] = old_message.message_id
        config.set('Settings', 'old_messages', str(old_messages))

        with open('config.ini', 'w') as config_file:
            config.write(config_file)

    except Exception as e:
        bot.send_message(538231919, f'Start game: {e}')


@bot.message_handler(commands=["cancel"])
def cancel(message):
    global config, total_score
    user_id = str(message.chat.id)

    try:

        try:
            bot.delete_message(user_id, old_messages[user_id])
            del old_messages[user_id]
        except Exception:
            pass

        del total_score[user_id]
        keyboard = telebot.types.ReplyKeyboardRemove()
        bot.reply_to(message, 'Счёт обнулён', reply_markup=keyboard)
    except Exception as e:
        bot.send_message(538231919, f'Cancel: {e}')


@bot.message_handler(commands=["help"])
def help(message):
    bot.reply_to(message, '/start, чтобы начать партию. Если нужно обнулить партию, то нажмите ещё раз'
                          ' /start. /cancel, чтобы сбросить весь счёт.')


def plus_point(message, point):
    global count, user1, user2, user1_score, user2_score, part, total_score
    user_id = str(message.chat.id)

    try:
        count[user_id] += 1

        if count[user_id] == 2:
            count[user_id] = 0

            if part[user_id]:
                part[user_id] = 0
            else:
                part[user_id] = 1

        if not point:
            user1_score[user_id] += 1
        else:
            user2_score[user_id] += 1

        try:
            bot.delete_message(user_id, old_messages[user_id])
            del old_messages[user_id]
        except Exception:
            pass

        keyboard = telebot.types.ReplyKeyboardRemove()

        if user1_score[user_id] == 11 or (user2_score[user_id] > 10 and (user1_score[user_id] - user2_score[user_id]) == 2):
            bot.send_message(user_id, f'{user1} WIN!', reply_markup=keyboard)

            if user_id in total_score:
                current_score_user1 = int(total_score[user_id][0]) + 1
                total_score[user_id] = str(current_score_user1) + total_score[user_id][1:]

                if current_score_user1 == 2:
                    bot.send_message(user_id, f'{user1} выиграл со счётом {total_score[user_id]}')
                    del total_score[user_id]
                else:
                    message(user_id, f'Счёт {total_score[user_id]}, сейчас начнётся новая партия')
                    #bot.send_message(user_id, f'Счёт {total_score[user_id]}')
                    start_game(message)
            else:
                total_score[user_id] = '1:0'
                bot.send_message(user_id, f'Счёт {total_score[user_id]}, сейчас начнётся новая партия')
                # bot.send_message(user_id, f'Счёт {total_score[user_id]}')
                start_game(message)

            config.set('Settings', 'total_score', str(total_score))
            config.set('Settings', 'old_messages', str(old_messages))

            with open('config.ini', 'w') as config_file:
                config.write(config_file)

        elif user2_score[user_id] == 11 or (user1_score[user_id] > 10 and (user2_score[user_id] - user1_score[user_id]) == 2):
            bot.send_message(user_id, f'{user2} WIN!', reply_markup=keyboard)

            if user_id in total_score:
                current_score_user2 = int(total_score[user_id][2]) + 1
                total_score[user_id] = total_score[user_id][:2] + str(current_score_user2)

                if current_score_user2 == 2:
                    bot.send_message(user_id, f'{user2} выиграл со счётом {total_score[user_id]}')
                    del total_score[user_id]
                else:
                    bot.send_message(user_id, f'Счёт {total_score[user_id]}, сейчас начнётся новая партия')
                    # bot.send_message(user_id, f'Счёт {total_score[user_id]}')
                    start_game(message)
            else:
                total_score[user_id] = '0:1'
                bot.send_message(user_id, f'Счёт {total_score[user_id]}, сейчас начнётся новая партия')
                # bot.send_message(user_id, f'Счёт {total_score[user_id]}')
                start_game(message)

            config.set('Settings', 'total_score', str(total_score))
            config.set('Settings', 'old_messages', str(old_messages))

            with open('config.ini', 'w') as config_file:
                config.write(config_file)

        else:
            split = (len(user1) - len(str(user1_score[user_id]))) * ' ' + '   '
            status = f'{user1}   {user2}\n{user1_score[user_id]}{split}{user2_score[user_id]}\n'
            smile = u"\U0001F3BE"
            smile_back = u"\U0001F519"

            if not part[user_id]:
                status += f'{smile}'
            else:
                status += f'{len(user1) * " "}   {smile}'

            keyboard = telebot.types.ReplyKeyboardMarkup()
            keyboard.row(telebot.types.KeyboardButton(f'/left {user1}'),
                         telebot.types.KeyboardButton(f'/right {user2}'))
            keyboard.add(telebot.types.KeyboardButton(f'/step_back {smile_back}'))
            old_message = bot.send_message(message.chat.id, status, reply_markup=keyboard)
            old_messages[user_id] = old_message.message_id
            config.set('Settings', 'old_messages', str(old_messages))

            with open('config.ini', 'w') as config_file:
                config.write(config_file)

    except Exception as e:
        bot.send_message(538231919, f'Plus point: {e}')


@bot.message_handler(commands=["step_back"])
def step_back(message):
    global last_point
    user_id = str(message.chat.id)

    try:
        point = last_point[user_id]

        if not point:
            user1_score[user_id] -= 2
        else:
            user2_score[user_id] -= 2

        plus_point(message, last_point[user_id])
    except Exception as e:
        bot.send_message(538231919, f'Step back: {e}')


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    global last_point
    user_id = str(call.message.chat.id)

    if call.data == "plus_point_1":
        plus_point(call.message, 0)
        last_point[user_id] = 0
    elif call.data == 'plus_point_2':
        plus_point(call.message, 1)
        last_point[user_id] = 1
    elif call.data == 'step_back':
        step_back(call.messag)


if __name__ == '__main__':
    bot.polling(none_stop=True)
