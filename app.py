from Chatbot import chatbot
from flask import Flask
from flask import render_template, jsonify, request
import requests
# from models import *
import random
app = Flask(__name__, template_folder='../Chatbot/templates')
app.secret_key = '12345'


@app.route('/')
def hello_world():
    return render_template('home.html')


@app.route('/chat', methods=["POST"])
def chat():
    query = request.form["text"].lower()
    return chatbot.reply(query)


app.config["DEBUG"] = True
app.run(port=8080)

