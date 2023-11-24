import telebot
import ast
import time
import threading
import pytz
import requests
from persiantools.jdatetime import JalaliDate, JalaliDateTime

API_TOKEN = 'API_TOKEN'

bot = telebot.TeleBot(API_TOKEN)
bot.set_webhook()

def get_users():
    with open("notif_users.txt") as file:
        data = file.read()
    users = ast.literal_eval(data)
    return users
    
users = get_users()

with open("output.txt", "w") as file:
  file.write(f"\nApp started with {len(users)} subscribers\nList : {users}")

sent_users = []

commands = {
    'start': 'روشن',
    'date': 'زوج و فرد',
    'end': "خاموش",
    'id': "آیدی اساتید",
}

bot.set_my_commands([
    telebot.types.BotCommand("/date", "زوج و فرد"),
    telebot.types.BotCommand("/id", "آیدی اساتید"),
    telebot.types.BotCommand("/start", "روشن"),
    telebot.types.BotCommand("/end", "خاموش"),
])

# Handle '/start'
@bot.message_handler(commands=['start'])
def send_welcome(message):
    cid = message.chat.id
    if cid not in users:
        users[cid] = 0
        bot.reply_to(
            message, "اطلاعات شما ثبت شد ✔\nپیام یادآوری رزرو غذا و تکالیف ارسال می‌شود.")
        try:
            users_file = open('notif_users.txt', 'wt')
            users_file.write(str(users))
            users_file.close()
        except:
            print("\nUnable to write to file")
    else:
        bot.reply_to(
            message, "ربات قبلا روشن شده!")
    with open("output.txt", "a") as file:
          file.write(f"\n{now_time()} - start command by user {cid}\nusers = {users}")

# Handle '/date'
@bot.message_handler(commands=['date'])
def send_date(message):
  string_value = odd_even()
  bot.reply_to(message, string_value)

def odd_even():
  day_num = days_switch()
  today_num = int(JalaliDateTime.now(pytz.timezone("Asia/Tehran")).strftime("%c").split(' ', 2)[1])
  day_num -= 30
  if day_num < 0:
    day_num *= (-1)
  start_day = day_num
  end_day = day_num + 6
  month = int(JalaliDate(JalaliDate.today()).isoformat()[5:7])
  if end_day > 30:
      end_day -= 30
      if today_num < 6:
          period = f"بازه : {month-1}/{start_day} تا {month}/{end_day}"
      else:
          period = f"بازه : {month}/{start_day} تا {month+1}/{end_day}"
  else:
    period = f"بازه : {month}/{start_day} تا {month}/{end_day}"
  if day_num % 2 == 0:
    strnig_value = f"این هفته زوجه✔\n{period}\n(تک ساعتی‌های نیمه دوم برگزار میشن)"
  else:
    strnig_value = f"این هفته فرده✔\n{period}\n(تک ساعتی‌های نیمه اول برگزار میشن)"

  return(strnig_value)
  
def days_switch():
  day_str = JalaliDateTime.now(pytz.timezone("Asia/Tehran")).strftime("%c").split(' ', 1)[0]
  day_num = int(JalaliDateTime.now(pytz.timezone("Asia/Tehran")).strftime("%c").split(' ', 2)[1])
  day_num = day_num + 30

  if day_str == "Shanbeh":
    day_num = day_num - 0
  elif day_str == "Yekshanbeh":
    day_num = day_num - 1
  elif day_str == "Doshanbeh":
    day_num = day_num - 2
  elif day_str == "Seshanbeh":
    day_num = day_num - 3
  elif day_str == "Chaharshanbeh":
    day_num = day_num - 4
  elif day_str == "Panjshanbeh":
    day_num = day_num - 5
  elif day_str == "Jomeh":
    day_num = day_num - 6

  return day_num

# Handle '/end'
@bot.message_handler(commands=['end'])
def remove_user(message):
    cid = message.chat.id
    if cid not in users:
        bot.reply_to(
            message, "ربات قبلا خاموش شده!")
    else:
        del users[cid]
        bot.reply_to(
            message, "دستور خاموش کردن دریافت شد. پیامی ارسال نخواهد شد❌")
        try:
            users_file = open('notif_users.txt', 'wt')
            users_file.write(str(users))
            users_file.close()
        except:
            print("\nUnable to write to file")
    with open("output.txt", "a") as file:
          file.write(f"\n{now_time()} - end command by user {cid}\nusers = {users}")

# Handle '/id'
@bot.message_handler(commands=['id'])
def send_req(message):
  msg = bot.reply_to(message, "نام خانوادگی استاد مورد نظر را وارد کنید.\n(ارسال \"همه\" برای دریافت لیست.)")
  bot.register_next_step_handler(msg, get_id)

def get_id(message):
  person = message.text
  string_value = fitch_id(person)
  bot.reply_to(message, string_value)

def fitch_id(person):
  with open("per_list.txt") as file:
    data = file.read()
  per_list = ast.literal_eval(data)
  string_value = ""
  if person == "همه" :
    for item in per_list:
      string_value += f"استاد {item} : {per_list[item]}\n"
  else:
    id = per_list.get(person)
    if id is not None:
      string_value = f"استاد {person} : {id}"
    else:
      string_value = "استاد مورد نظر یافت نشد!"

  return string_value
  
# Messages Handling
def now_time():
    while True:
        try:
            time_api = requests.get(
                "http://worldtimeapi.org/api/timezone/Asia/Tehran")
            time_api = time_api.json()
            break
        except ValueError:
            continue
        except:
            continue
    time_now = time_api['datetime'][11:16]
    return time_now

# Kalinan messages handler
def kalinan_timer():
    while True:
      with open("kalinan.txt") as file:
        data = file.read()
      kalinan = ast.literal_eval(data)
      day_str = JalaliDateTime.now(pytz.timezone("Asia/Tehran")).strftime("%c").split(' ', 1)[0]
      time_now = now_time()
      key = day_str + " " + time_now
      response = kalinan.get(key)
      if response is not None:
          kalinan_sender()
          time.sleep(60)
      else:
          time.sleep(10)

def kalinan_sender():
    messages_deleter()
    i = 1
    with open("output.txt", "a") as file:
      file.write(f"\n{now_time()} Sending Kalinan messages :")
      for user in users:
          if (user not in sent_users):
             try:
                sending = bot.send_message(
                    user, "یادآوری رزرو غذا در سامانه کالینان 🔴\nآدرس سامانه : https://shrfood.ui.ac.ir/")
                file.write(f"\n{i} -> Kalinan Message sent to: {user}")
                sent_users.append(user)
                users[user] = sending.message_id
             except:
               file.write(f"\n{i} -> Kalinan Message can't send to: {user}")  
             time.sleep(0.5)
             i += 1
    users_updater()
      


# LMS messages handler
def lms_timer():
    while True:
      with open("lms_list.txt") as file:
        data = file.read()
      lms_list = ast.literal_eval(data)
      today = JalaliDate(JalaliDate.today()).isoformat()
      time_now = now_time()
      key = today + " " + time_now
      message = lms_list.get(key)
      if message is not None:
        lms_sender(message)
        time.sleep(60)
      else:
        time.sleep(10)

def lms_sender(message):
   messages_deleter()
   i = 1
   with open("output.txt", "a") as file:
      file.write(f"\n{now_time()} Sending LMS messages :")
      for user in users:
        if (user not in sent_users):
          try:
            sending = bot.send_message(
                        user, message)
            file.write(f"\n{i} -> LMS Message sent to: {user}")
            sent_users.append(user)
            users[user] = sending.message_id
          except:
            file.write(f"\n{i} -> LMS Message can't send to: {user}")
          time.sleep(0.5)
          i += 1
   users_updater()

# Deleter function
def delete_timer():
    while True:
        del_time = now_time()
        if del_time == "00:00" or del_time == "12:00":
            messages_deleter()
            time.sleep(60)
        time.sleep(10)
        
def messages_deleter():
    users = get_users()
    i = 1
    with open("output.txt", "a") as file:
        file.write(f"\n{now_time()} Try for Deleting :")
        for user in users:
            try:
                bot.delete_message(user, users[user])
                time.sleep(1)
                users[user] = 0
                file.write(f"\n{i} -> Message deleted for: {user}")
                i += 1
            except:
                file.write(f"\n{i} -> Message not found for: {user}")
                i += 1
            

# notif_users updater
def users_updater():
    users_file = open('notif_users.txt', 'wt')
    users_file.write(str(users))
    users_file.close()
    sent_users.clear()

# Messaging thread
kalinan_app = threading.Thread(target=kalinan_timer)
kalinan_app.start()

lms_app = threading.Thread(target=lms_timer)
lms_app.start()

deleter = threading.Thread(target=delete_timer)
deleter.start()

bot.infinity_polling()