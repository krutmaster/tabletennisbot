# by krutmaster (telegram: @krutmaster1)
import configparser
import random
import telebot

print('All ok')
def str_in_dict(dict_in_str):
    return eval(dict_in_str)


config = configparser.ConfigParser()
config.read('config.ini')
token = config.get('Settings', 'token')
ids = str_in_dict(config.get('Settings', 'ids'))
pairs = str_in_dict(config.get('Settings', 'pairs'))
user1_score = {}
user2_score = {}
user1 = {}
user2 = {}
count = {}
part = {}
going_game = {}
total_score = str_in_dict(config.get('Settings', 'total_score'))
old_messages = str_in_dict(config.get('Settings', 'old_messages'))
bot = telebot.TeleBot(token)


@bot.message_handler(commands=["add"])
def add_user(message):
    global ids, config

    try:
        user = message.text.split()[1]
        ids.append(user)
        config.set('Settings', 'ids', str(ids))

        with open('config.ini', 'w') as config_file:
            config.write(config_file)

        bot.reply_to(message, f'{user} успешно добавлен')
    except Exception as e:
        bot.reply_to(message, 'Команда введена неправильно, укажите id')
        bot.send_message(538231919, f'Add: {e}')


@bot.message_handler(commands=["reg"])
def reg(message):
    global ids, config

    try:
        user = str(message.chat.id)
        ids.append(user)
        config.set('Settings', 'ids', str(ids))

        with open('config.ini', 'w') as config_file:
            config.write(config_file)

        name = bot.get_chat(message.chat.id)

        if name.username:
            name = f'@{name.username}'
        else:
            name = f'{name.first_name} {name.last_name}'

        bot.reply_to(message, f'{name} успешно добавлен')
    except Exception as e:
        bot.send_message(538231919, f'Reg: {e}')


@bot.message_handler(commands=["make_pairs"])
def make_pairs(message):
    global ids, pairs, config, total_score

    try:

        if len(ids) % 2 == 0:
            pairs = []
            total_score = {}
            free_ids = [i for i in range(len(ids))]

            for i in range(len(ids) // 2):
                user1 = -1

                while user1 == -1:
                    user1 = random.choice(free_ids)

                for i, user in enumerate(free_ids):

                    if user1 == user:
                        free_ids[i] = -1

                user1 = ids[user1]
                user2 = -1

                while user2 == -1:
                    user2 = random.choice(free_ids)

                for i, user in enumerate(free_ids):

                    if user2 == user:
                        free_ids[i] = -1

                user2 = ids[user2]
                pairs.append([user1, user2])

            config.set('Settings', 'pairs', str(pairs))
            config.set('Settings', 'total_score', str(total_score))

            with open('config.ini', 'w') as config_file:
                config.write(config_file)

            bot.reply_to(message, f'Сформированы пары. Список пар по команде /rating')
        else:
            bot.reply_to(message, 'Количество участников нечётное, невозможно разбить на пары.'
                                  ' Удалите одного из учатсников командой /del id участника. '
                                  'Список участников: /list_users')

    except Exception as e:
        bot.send_message(538231919, f'Make pairs: {e}')


@bot.message_handler(commands=["rating"])
def rating(message):
    global pairs, total_score

    try:
        text = '--------\n'

        for i, pair in enumerate(pairs):

            try:
                name1 = bot.get_chat(pair[0])

                if name1.username:
                    name1 = f'@{name1.username}'
                else:
                    name1 = f'{name1.first_name} {name1.last_name}'
            except Exception:
                name1 = pair[0]

            try:
                name2 = bot.get_chat(pair[1])

                if name2.username:
                    name2 = f'@{name2.username}'
                else:
                    name2 = f'{name2.first_name} {name2.last_name}'
            except Exception:
                name2 = pair[1]

            text += f'{i+1}: {name1} vs {name2}\n'

            if i in total_score:
                temp_split = (len(f'{i + 1}: {name1}') - 1) * ' '
                text += f'{temp_split}{total_score[i][0]}    {total_score[i][2]}\n'

        text += '--------'
        bot.reply_to(message, text)
    except Exception as e:
        bot.send_message(538231919, f'Rating: {e}')


@bot.message_handler(commands=["list_users"])
def list_users(message):
    global ids

    try:
        text = '--------\n'

        for i, user in enumerate(ids):

            try:
                name = bot.get_chat(user)

                if name.username:
                    name = f'@{name.username}'
                else:
                    name = f'{name.first_name} {name.last_name}'
            except Exception:
                name = None

            if name:
                text += f'{i+1}. {user} {name}\n'
            else:
                text += f'{i + 1}. {user}\n'

        text += '--------'
        bot.reply_to(message, text)
    except Exception as e:
        bot.send_message(538231919, f'List users: {e}')


@bot.message_handler(commands=["del"])
def del_user(message):
    global ids, config

    try:
        id = message.text.split()[1]

        for i, user in enumerate(ids):

            if user == id:
                ids.pop(i)
                break

        config.set('Settings', 'ids', str(ids))

        with open('config.ini', 'w') as config_file:
            config.write(config_file)

        bot.reply_to(message, 'Пользователь успешно удалён')
    except Exception as e:
        bot.reply_to(message, 'Команда введена неправильно, укажите id пользователя')
        bot.send_message(538231919, f'Del: {e}')


@bot.message_handler(commands=["start"])
def start_game(message, num=None):
    global user1_score, user2_score, user1, user2, count, part, going_game, old_messages, config
    user_id = str(message.chat.id)

    try:

        if not num:
            num = int(message.text.split()[1]) - 1

        user1[user_id] = pairs[num][0]
        user2[user_id] = pairs[num][1]
        going_game[user_id] = num
        user1_score[user_id] = 0
        user2_score[user_id] = 0

        try:
            name1 = bot.get_chat(user1[user_id])

            if name1.username:
                name1 = f'@{name1.username}'
            else:
                name1 = f'{name1.first_name} {name1.last_name}'
        except Exception:
            name1 = user1[user_id]

        try:
            name2 = bot.get_chat(user2[user_id])

            if name2.username:
                name2 = f'@{name2.username}'
            else:
                name2 = f'{name2.first_name} {name2.last_name}'
        except Exception:
            name2 = user2[user_id]

        split = (len(name1) - 1) * ' ' + '   '
        status = f'{name1}   {name2}\n{user1_score[user_id]}{split}{user2_score[user_id]}\n'
        part[user_id] = random.randint(0, 1)
        count[user_id] = 0
        smile = u"\U0001F3BE"

        if not part[user_id]:
            status += f'{smile}'
        else:
            status += f'{len(name1) * " "}   {smile}'

        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(telebot.types.InlineKeyboardButton(user1_score[user_id], callback_data='plus_point_1'),
                     telebot.types.InlineKeyboardButton(user2_score[user_id], callback_data='plus_point_2'))
        old_message = bot.send_message(user_id, status, reply_markup=keyboard)
        old_messages[user_id] = old_message.message_id
        config.set('Settings', 'old_messages', str(old_messages))

        with open('config.ini', 'w') as config_file:
            config.write(config_file)

    except Exception as e:
        bot.reply_to(message, 'Команда введена неправильно, укажите номер пары из /rating')
        bot.send_message(538231919, f'Start game: {e}')


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

        if user1_score[user_id] == 11 or (user1_score[user_id] > 10 and (user1_score[user_id] - user2_score[user_id]) == 2):

            try:
                name = bot.get_chat(user1[user_id])

                if name.username:
                    name = f'@{name.username}'
                else:
                    name = f'{name.first_name} {name.last_name}'

            except Exception:
                name = user1[user_id]

            bot.send_message(user_id, f'{name} WIN!')

            if going_game[user_id] in total_score:
                current_score_user1 = int(total_score[going_game[user_id]][0]) + 1
                total_score[going_game[user_id]] = str(current_score_user1) + total_score[going_game[user_id]][1:]

                if current_score_user1 == 2:
                    bot.send_message(user_id, f'{name} выиграл со счётом {total_score[going_game[user_id]]}')
                else:
                    #bot.send_message(user_id, f'Счёт {total_score[going_game[user_id]]}, сейчас начнётся новая партия')
                    bot.send_message(user_id, f'Счёт {total_score[going_game[user_id]]}')
                    #start_game(message, going_game[user_id])
            else:
                total_score[going_game[user_id]] = '1:0'
                #bot.send_message(user_id, f'Счёт {total_score[going_game[user_id]]}, сейчас начнётся новая партия')
                bot.send_message(user_id, f'Счёт {total_score[going_game[user_id]]}')
                #start_game(message, going_game[user_id])
            config.set('Settings', 'total_score', str(total_score))
            config.set('Settings', 'old_messages', str(old_messages))

            with open('config.ini', 'w') as config_file:
                config.write(config_file)

        elif user2_score[user_id] == 11 or (user2_score[user_id] > 10 and (user2_score[user_id] - user1_score[user_id]) == 2):

            try:
                name = bot.get_chat(user2[user_id])

                if name.username:
                    name = f'@{name.username}'
                else:
                    name = f'{name.first_name} {name.last_name}'

            except Exception:
                name = user2[user_id]

            bot.send_message(user_id, f'{name} WIN!')

            if going_game[user_id] in total_score:
                current_score_user2 = int(total_score[going_game[user_id]][2]) + 1
                total_score[going_game[user_id]] = total_score[going_game[user_id]][:2] + str(current_score_user2)

                if current_score_user2 == 2:
                    bot.send_message(user_id, f'{name} выиграл со счётом {total_score[going_game[user_id]]}')
                else:
                    #bot.send_message(user_id, f'Счёт {total_score[going_game[user_id]]}, сейчас начнётся новая партия')
                    bot.send_message(user_id, f'Счёт {total_score[going_game[user_id]]}')
                    #start_game(message, going_game[user_id])
            else:
                total_score[going_game[user_id]] = '0:1'
                #bot.send_message(user_id, f'Счёт {total_score[going_game[user_id]]}, сейчас начнётся новая партия')
                bot.send_message(user_id, f'Счёт {total_score[going_game[user_id]]}')
                #start_game(message, going_game[user_id])

            config.set('Settings', 'total_score', str(total_score))
            config.set('Settings', 'old_messages', str(old_messages))

            with open('config.ini', 'w') as config_file:
                config.write(config_file)

        else:

            try:
                name1 = bot.get_chat(user1[user_id])

                if name1.username:
                    name1 = f'@{name1.username}'
                else:
                    name1 = f'{name1.first_name} {name1.last_name}'

            except Exception:
                name1 = user1[user_id]

            try:
                name2 = bot.get_chat(user2[user_id])

                if name2.username:
                    name2 = f'@{name2.username}'
                else:
                    name2 = f'{name2.first_name} {name2.last_name}'

            except Exception:
                name2 = user2[user_id]

            split = (len(name1) - len(str(user1_score[user_id]))) * ' ' + '   '
            status = f'{name1}   {name2}\n{user1_score[user_id]}{split}{user2_score[user_id]}\n'
            smile = u"\U0001F3BE"

            if not part[user_id]:
                status += f'{smile}'
            else:
                status += f'{len(name1) * " "}   {smile}'

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

@bot.message_handler()
def echo(message):
    bot.reply_to(message, '/reg чтобы самому зарегаться, /add и желательно айди человека, которого'
                          ' кто-то вручную добавляет, /make_pairs чтобы создать пары, /rating чтобы узнать '
                          'номера пар, /start_game и номер пары, чтобы начать игру. Удалить пользователя: /del id пользователя')


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):

    if call.data == "plus_point_1":
        plus_point(call.message, 0)
    elif call.data == 'plus_point_2':
        plus_point(call.message, 1)


if __name__ == '__main__':
    bot.polling(none_stop=True)
