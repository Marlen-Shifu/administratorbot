import asyncio

from main import bot

# dp = None
#
# def set_bot(dp_i):
#     global dp
#     print('sddsds')
#     dp = dp_i
#     print(dp)
#

def mail(user_id, text, reply_markup = None):
    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(bot.send_message(user_id, text, reply_markup=reply_markup))
    except Exception as e:
        print(e)
        try:
            loop.create_task(bot.send_message(user_id, text, reply_markup=reply_markup))
        except  Exception as e:
            print(e)


def mail_document(user_id, file, reply_markup = None):
    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(bot.send_document(user_id, file, reply_markup=reply_markup))
    except Exception as e:
        print(e)
        try:
            loop.create_task(bot.send_document(user_id, file, reply_markup=reply_markup))
        except  Exception as e:
            print(e)


# class Mailer():
#
#     bot = None
#
#     def set_bot(self, bot_i):
#         self.bot = bot_i
#
#     def mail(self, user_id, text):
#         loop = asyncio.get_event_loop()
#         loop.create_task(self.bot.send_message(f"{self.bot}"))
#         loop.create_task(self.bot.send_message(user_id, text))
#
# mailer = Mailer()