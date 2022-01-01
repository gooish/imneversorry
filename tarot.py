from os import listdir
from random import shuffle, randint
from PIL import Image
from tempfile import NamedTemporaryFile
from telegram import Update
from telegram.ext import CallbackContext
import requests
import db
import re



class Tarot:
    def __init__(self, token, url, admin):
        self.card_data = db.readSelitykset()
        # get stuff fron config
        self.tarot_url = url
        self.tarot_token = token
        self.tarot_admin = admin
    def getCommands(self):
        return dict()

    def explain_card(self, text):
        explanations_to_return = ""

        for datum in self.card_data:
            name = datum[0]
            lname = name.lower()
            if lname in text:
                if "reversed " + lname in text or "ylösalaisin " + lname in text or lname + " reversed" in text or lname + " ylösalaisin" in text:
                    rev_exp = datum[2]
                    explanations_to_return += "Reversed " + name + ": " + rev_exp + "\n\n"
                    continue
                explanation = datum[1]
                explanations_to_return += name + ": " + explanation + "\n\n"

        return explanations_to_return

    def get_tarot(self, update: Update, context: CallbackContext):
        try:
            size = int(update.message.text.lower().split(' ')[1])
        except ValueError :
            context.bot.sendMessage(chat_id=update.message.chat_id, text=":--D")
            return

        # try using tarot server
        try:
            request_params = {
                "token" : self.tarot_token,
                "amount" : size
            }
            r = requests.post(url = self.tarot_url, data = request_params)
            if "502 Bad Gateway" in r.text:
                raise requests.exceptions.HTTPError
            context.bot.sendMessage(chat_id=update.message.chat_id, text=r.text)

        # yell at tarot server admin if doesn't work
        except requests.exceptions.RequestException:
            context.bot.sendMessage(chat_id=update.message.chat_id, text="tarot rikki, " + self.tarot_admin + " korjaa paskas")

    def get_tarot_stats(self, update: Update, context: CallbackContext):
        try:
            r = requests.post(url = self.tarot_url)
            if "502 Bad Gateway" in r.text:
                    raise requests.exceptions.HTTPError
            context.bot.sendMessage(chat_id=update.message.chat_id, text=r.text)
        except requests.exceptions.RequestException:
            context.bot.sendMessage(chat_id=update.message.chat_id, text="tarot rikki, " + self.tarot_admin + " korjaa paskas")


    def getReading(self, update: Update, context: CallbackContext):
        message = self.explain_card(update.message.text.lower())
        if message != "":
            context.bot.sendMessage(chat_id=update.message.chat_id, text=message)

    def messageHandler(self, update: Update, context: CallbackContext):
        msg = update.message
        if msg.text is not None:
            if re.match(r'^/tarot [0-9]+(?!\S)', msg.text.lower()):
                self.get_tarot(update, context)
            elif re.match(r'^/tarotstats', msg.text.lower()):
                self.get_tarot_stats(update, context)
            elif "selitä" in msg.text.lower() or "selitys" in msg.text.lower():
                self.getReading(update, context)
