# apis.py


def fetch_todays_food_data() -> str:
    with open("todays_food_data.json", encoding="utf-8") as f:
        todays_food_data_json = f.read()
    return todays_food_data_json
