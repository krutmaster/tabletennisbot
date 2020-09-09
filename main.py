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
total_score = str_in_dict(config.get('Settings', 'total_score'))
old_messages = str_in_dict(config.get('Settings', 'old_messages'))
bot = telebot.TeleBot(token)


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

        if not part[user_id]:
            status += f'{smile}'
        else:
            status += f'{len(user1) * " "}   {smile}'

        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(telebot.types.InlineKeyboardButton(user1_score[user_id], callback_data='plus_point_1'),
                     telebot.types.InlineKeyboardButton(user2_score[user_id], callback_data='plus_point_2'))
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
        bot.reply_to(message, 'Счёт обнулён')
    except Exception as e:
        bot.send_message(538231919, f'Cancel: {e}')


def plus_point(message, point):
    global count, user1, user2, user1_score, user2_score, part, going_game, total_score
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

        if user1_score[user_id] == 11 or (user2_score[user_id] > 10 and (user1_score[user_id] - user2_score[user_id]) == 2):
            bot.send_message(user_id, f'{user1} WIN!')

            if user_id in total_score:
                current_score_user1 = int(total_score[user_id][0]) + 1
                total_score[user_id] = str(current_score_user1) + total_score[user_id][1:]

                if current_score_user1 == 2:
                    bot.send_message(user_id, f'{user1} выиграл со счётом {total_score[user_id]}')
                else:
                    #bot.send_message(user_id, f'Счёт {total_score[going_game[user_id]]}, сейчас начнётся новая партия')
                    bot.send_message(user_id, f'Счёт {total_score[user_id]}')
                    #start_game(message, going_game[user_id])
            else:
                total_score[user_id] = '1:0'
                #bot.send_message(user_id, f'Счёт {total_score[going_game[user_id]]}, сейчас начнётся новая партия')
                bot.send_message(user_id, f'Счёт {total_score[user_id]}')
                #start_game(message, going_game[user_id])
            config.set('Settings', 'total_score', str(total_score))
            config.set('Settings', 'old_messages', str(old_messages))

            with open('config.ini', 'w') as config_file:
                config.write(config_file)

        elif user2_score[user_id] == 11 or (user1_score[user_id] > 10 and (user2_score[user_id] - user1_score[user_id]) == 2):
            bot.send_message(user_id, f'{user2} WIN!')

            if user_id in total_score:
                current_score_user2 = int(total_score[user_id][2]) + 1
                total_score[user_id] = total_score[user_id][:2] + str(current_score_user2)

                if current_score_user2 == 2:
                    bot.send_message(user_id, f'{user2} выиграл со счётом {total_score[user_id]}')
                else:
                    #bot.send_message(user_id, f'Счёт {total_score[going_game[user_id]]}, сейчас начнётся новая партия')
                    bot.send_message(user_id, f'Счёт {total_score[user_id]}')
                    #start_game(message, going_game[user_id])
            else:
                total_score[user_id] = '0:1'
                #bot.send_message(user_id, f'Счёт {total_score[going_game[user_id]]}, сейчас начнётся новая партия')
                bot.send_message(user_id, f'Счёт {total_score[user_id]}')
                #start_game(message, going_game[user_id])

            config.set('Settings', 'total_score', str(total_score))
            config.set('Settings', 'old_messages', str(old_messages))

            with open('config.ini', 'w') as config_file:
                config.write(config_file)

        else:
            split = (len(user1) - len(str(user1_score[user_id]))) * ' ' + '   '
            status = f'{user1}   {user2}\n{user1_score[user_id]}{split}{user2_score[user_id]}\n'
            smile = u"\U0001F3BE"

            if not part[user_id]:
                status += f'{smile}'
            else:
                status += f'{len(user1) * " "}   {smile}'

            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.row(telebot.types.InlineKeyboardButton(user1_score[user_id], callback_data='plus_point_1'),
                         telebot.types.InlineKeyboardButton(user2_score[user_id], callback_data='plus_point_2'))
            old_message = bot.send_message(message.chat.id, status, reply_markup=keyboard)
            old_messages[user_id] = old_message.message_id
            config.set('Settings', 'old_messages', str(old_messages))

            with open('config.ini', 'w') as config_file:
                config.write(config_file)

    except Exception as e:
        bot.send_message(538231919, f'Plus point: {e}')


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):

    if call.data == "plus_point_1":
        plus_point(call.message, 0)
    elif call.data == 'plus_point_2':
        plus_point(call.message, 1)


if __name__ == '__main__':
    bot.polling(none_stop=True)
