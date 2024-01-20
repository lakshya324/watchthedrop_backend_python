from flask import Flask, request, jsonify
from pricing import priceFlipkart, priceAmazon
import google.generativeai as genai
from tracker import update_tracker, add_to_tracker
from datetime import datetime
import threading
import time

app = Flask(__name__)

genai.configure(api_key="AIzaSyCv1C_gOBfyahXvj4ujp7oBHA4c9ha1aIg")
model = genai.GenerativeModel('gemini-pro')
chatbot_name = "Chariot"
primary = ""
chats = []
running = False

def generate(prompt):
    try:
        response=model.generate_content(prompt).text
        if "<r>" in response:
            response = response.replace("<r>", "").strip()
        return response
    except Exception as e:
        print(f"Error generating content: {str(e)}")

def product_tracker():
    while running:
        print("->Function is Triggered! ",datetime.now())
        update_tracker()
        print("->Function is Completed! ",datetime.now())
        # print("Function is running!",time.time())
        time.sleep(20)




@app.route("/start", methods=['POST'])
def chat_start():
    try:
        global primary
        data = request.json
        primary = f"You are a ChatBot for a product tracker and recommendation site which is used to suggest the best product to the user based on their need and budget. and your name is '{chatbot_name}'. The user is confused between the following products and wants to know which one is best for him. and these are the following products:\n\n"
        for i in range(len(data)):
            primary += str(i + 1) + ". " + str(data[i]) + "\n"
        primary += f"\nNOTE: Output should only use given data and avoid external references. and just return the {chatbot_name} response. and start response with <r> tag."
        primary += "\nNow, Greet the User with Hi and ask him which product he wants to buy"
        print("--->",primary)
        response = generate(primary)
        chats.append({chatbot_name: response})
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": f"Error in start: {str(e)}"}), 500

@app.route("/chat/<message>", methods=['GET'])
def chat_get(message):
    try:
        previous_prompt = primary
        previous_prompt += "\n\nthere is th chats which is already done:\n\n"
        for i in chats:
            previous_prompt += str(i)[1:-1] + "\n"	
        prompt = f"{previous_prompt}\n\nNow the user asks please reply accordingly.\n{message}"
        response = generate(prompt)
        chats.append({'user': message})
        chats.append({chatbot_name: response})
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": f"Error in get: {str(e)}"}), 500

@app.route("/pricing/", methods=['POST'])
def price():
    try:
        payload = request.get_json()
        source = payload['source']
        url = payload['url']

        if "flipkart" in source.lower():
            return jsonify(priceFlipkart(url))
        elif "amazon" in source.lower():
            return jsonify(priceAmazon(url))
        else:
            return jsonify({"error": "Invalid source"}), 500

    except Exception as e:
        return jsonify({"error": f"Error in price: {str(e)}"}), 500

@app.route('/tracker/start', methods=['GET'])
def start_function():
    global running
    if not running:
        running = True
        threading.Thread(target=product_tracker).start()
        return jsonify({"status": "success", "message": "Function started successfully"})
    else:
        return jsonify({"status": "error", "message": "Function is already running"})

@app.route('/tracker/stop', methods=['GET'])
def stop_function():
    global running
    if running:
        running = False
        return jsonify({"status": "success", "message": "Function stopped successfully"})
    else:
        return jsonify({"status": "error", "message": "Function is not running"})

@app.route('/tracker/add', methods=['POST'])
def add_tracker():
    try:
        payload = request.json
        product_url = payload['url']
        add_to_tracker(product_url)
        return jsonify({"status": "success", "message": "Added to tracker successfully"})
    except Exception as e:
        return jsonify({"error": f"Error in add_to_tracker: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)