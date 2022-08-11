from Chatbot import system_model as sm
from Chatbot import conversation_model
from flask import render_template, jsonify, request
def reply(query):
    query = query.replace("?", " ?")
    query = query.replace(".", " .")
    try:
        
        elif  "write this down" in query or "remember this" in query or "remember that" in query:
            file_name = "note.txt"
            query = query.replace("remember that", "")
            query = query.replace("write this down", "")
            with open(file_name, "w") as f:
                f.write(query)
            res = "I've made a note of that."

        elif 'memory' in query or 'what did i tell you to remember' in query:
            remvr = sm.retrieve_remeber()
            res = 'You told me, \n' + str(remvr)

        elif 'what is the time' in query or 'what time is it' in query:
            time = sm.say_time()
            res = time
        elif 'brightness' in query:
            isChanged = sm.brightness(query)
            if isChanged:
                res = 'Done.'
            else:
                res = 'Sorry, I cannot recognize'

        elif 'battery' in query:
            res = sm.battery_condition()

        
        # last elif (wikipedia)
        elif ('who is' in query or 'what is' in query or 'tell me about' in query):
            res = sm.wikipedia_search(query)
            if res:
                res = 'According to wikipedia, \n' + sm.wikipedia_search(query)
            else:
                res = 'Sorry, I cannot find any information.'
        #otherwise find answer from TransformerChatbot model
        else:
            res = conversation_model.chat(query)

        return jsonify({"status": "success", "response": res})
         
    except Exception as e:
        print(e)

        return jsonify({"status": "success", "response": "Sorry I didn't get that."})