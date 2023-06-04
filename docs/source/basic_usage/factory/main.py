# main.py
import json
import sys

from apis import fetch_todays_food_data
from menu_mail_message_builder import create_menu_mail_message_builder


def main() -> None:
    todays_food_data_json = fetch_todays_food_data()
    todays_food_data_dict = json.loads(todays_food_data_json)

    builder = create_menu_mail_message_builder(todays_food_data_dict)
    initial_target = builder.init_builder_target()

    # NOTE: Each build process within the Builder class requires a self instance,
    #       which is typed using the NewType returned from the previous build process.
    #       This ensures type safety and allows for the build processes to be executed
    #       in a sequential manner.
    processed_target = builder.process_template(initial_target)
    built_target = builder.build(processed_target)
    print(builder.fetch_built(built_target), file=sys.stdout)


if __name__ == "__main__":
    main()
