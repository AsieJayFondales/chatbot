import os
import json
from flask import Flask, render_template, request, jsonify, Response
import google.generativeai as genai
import nltk
from nltk.tokenize import word_tokenize  # Tokenization
from nltk.tag import pos_tag  # POS tagging
import re  # Regular Expressions

# Initialize Flask app
app = Flask(__name__)

# Configure Generative AI
API_KEY = 'YOUR_API_KEY'
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')
chat = model.start_chat(history=[])

nltk.download('punkt')  # Download tokenizer data
nltk.download('averaged_perceptron_tagger')  # Download POS tagger data

# Store session states in a dictionary (for simplicity, in production consider using a more robust solution)
sessions = {}

@app.route('/')
def root():
    return render_template('nlp_chatbot.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    try:
        session_id = request.json.get('session_id', 'default')
        user_message = request.json['message']

        if session_id not in sessions:
            sessions[session_id] = {'state': 'ask_cuisine'}

        state = sessions[session_id]['state']
        response_text = ""
        show_buttons = False
        buttons = []
        dish_name = ""

        if state == 'ask_cuisine':
            response_text = "Which cuisine do you prefer?"
            buttons = ["Filipino", "Chinese", "Korean", "Japanese", "Thai", "Indian", "French", "Brazilian", "Mexican"]
            show_buttons = True
            sessions[session_id]['state'] = 'ask_ingredients'
        elif state == 'ask_ingredients':
            if user_message not in ["Filipino", "Chinese", "Korean", "Japanese", "Thai", "Indian", "French", "Brazilian", "Mexican"]:
                response_text = "Please choose a valid cuisine from the options provided."
                show_buttons = True
                buttons = ["Filipino", "Chinese", "Korean", "Japanese", "Thai", "Indian", "French", "Brazilian", "Mexican"]
            else:
                response_text = "Please enter the ingredients you have."
                sessions[session_id]['state'] = 'provide_ingredients'
        elif state == 'provide_ingredients':
            ingredients = extract_valid_ingredients(user_message)
            if not ingredients:
                response_text = "Please provide a valid list of ingredients."
            else:
                dish_name = generate_recipe(user_message)
                response_text = f"Here is a dish you can make: {dish_name}"
                sessions[session_id]['state'] = 'ask_cuisine'
    except Exception as e:
        response_text = "An error occurred. Please try again."
        print(f"Error: {e}")

    return jsonify({
        'message': response_text,
        'show_buttons': show_buttons,
        'buttons': buttons,
        'dish_name': dish_name
    })

def extract_valid_ingredients(user_message):
    try:
        ingredients = word_tokenize(user_message)
        pos_tags = pos_tag(ingredients)
        valid_ingredients = []
        for ingredient, tag in pos_tags:
            if tag.startswith('NN'):  # Ensure the word is a noun (NN).
                valid_ingredients.append(ingredient)
        return valid_ingredients
    except Exception as e:
        print(f"Error in extract_valid_ingredients: {e}")
        return []

def generate_recipe(ingredients):
    try:
        # Dummy implementation for generating a recipe based on ingredients
        return "Sample Dish Name"
    except Exception as e:
        print(f"Error in generate_recipe: {e}")
        return "Error generating recipe"

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True, use_reloader=False)
