import json
import openai
from flask import Flask, request, render_template
import requests
import time
from dotenv import load_dotenv
import os
import uuid
from database import initialize_db, add_row, delete_row, fetch_row_by_uuid, update_single_column
from threading import Thread
from make_sting import get_menu_for_week

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')
app = Flask(__name__)
initialize_db()


def food_api_request():
    food_plan = "No food available this week. Don't generate a diet plan, just abort."
    for request_trials in range(3):
        try:
            food_plan = requests.get(
                'https://esb.integration.smartcity.hn/rad/schwarz.it.eu.bildungscampus.ws:v1/mensa/menu')
            if food_plan.status_code == 200:
                break
            print("Food API Request failed, trying again!")
            time.sleep(5)
        except:
            print("Food API Request failed, trying again!")
            time.sleep(5)
    if food_plan.json():
        return food_plan.json()
    else:
        return food_plan


def ai_generation(diet_plan: str, food_plan):
    food_plan_formatted = get_menu_for_week(food_plan)
    prompt = f"Generate a {diet_plan} diet plan for this week, only lunch, composed of the following available meals: {food_plan_formatted}"
    completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}])
    print(str(completion.choices[0].message.content))
    return str(completion.choices[0].message.content)


def run_generation(diet_plan: str, uuid_identifier: str):
    add_row(uuid_identifier, 0, "0")
    # request meal data from api
    food_data = food_api_request()
    # generate diet plan with openai api
    result = ai_generation(diet_plan, food_data)
    update_single_column(uuid_identifier, "status", 1)
    update_single_column(uuid_identifier, "content", result)


@app.route("/request-diet-plan", methods=['POST'])
def handler():
    if request.method == 'POST':
        try:
            uuid_identifier = str(uuid.uuid1())
            diet_preference = request.get_json()
            thread = Thread(target=run_generation, args=(diet_preference['diet'], uuid_identifier,))
            thread.start()
            return json.dumps({"uuid": uuid_identifier}), 200
        except KeyError:
            return 400


@app.route("/request-diet-plan-status/<request_uuid>", methods=['GET'])
def get_generation_status(request_uuid):
    status, content = fetch_row_by_uuid(request_uuid)
    print(status, content)
    print(f"request status uuid: {request_uuid}")
    if status == 1:
        json_result = {'result': content}
        delete_row(request_uuid)
        return json.dumps(json_result), 200
    elif status == 0:
        return "", 202
    else:
        return "", 400

@app.route("/web", methods=['GET'])
def web_interface():
    return render_template('index.html')


# app.run(port=5556)