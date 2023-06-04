Basic Usage
===========

Composition & Factory
---------------------

One of the basic usage patterns is the creation of a builder factory through composition.

For example, let's say there is an API that retrieves the following JSON for a hotel
where the menu changes daily based on the availability of ingredients.

.. include:: basic_usage/factory/apis.py
   :code: python3

.. include:: basic_usage/factory/todays_food_data.json
   :code: python3

The hotel is planning to start a service where they will share today's menu,
which they have already been using for internal employees, with customers in
advance via email to enhance anticipation. They have also decided to include
Japanese translation in the email as there are a considerable number of
Japanese guests.

.. include:: basic_usage/factory/todays_menu_template.jinja
   :code: python3

First, create a data class to accept the JSON as a template rendering context.
Here, we can utilize `Pydantic`_, which allows us to perform data validation on the raw data.

.. _Pydantic: https://github.com/pydantic/pydantic

.. code-block:: python3

  from pydantic.dataclasses import dataclass
  from templa import ConfigData


  @dataclass(frozen=True)
  class FoodAndIngredients:
      food: str
      ingredients: List[str]


  @dataclass(frozen=True)
  class TodaysFoodData(ConfigData):
      data: List[FoodAndIngredients]

Next, define a class with a get_template() method that returns a jinja2.Template.

.. code-block:: python3

  class MenuTemplateGetter:
      def get_template(self) -> jinja2.Template:
          with open("todays_menu_template.jinja", encoding="utf-8") as f:
              template_text = f.read()

          environment = jinja2.Environment(
              loader=jinja2.DictLoader({"menu": template_text})
          )
          return environment.get_template("menu")

Next, we will define a function to format the rendered menu into an email format
for customers. The Optional[str] here indicates that the "str" is optional and
can be determined by the user. It will be used as the argument type for the next
function we define.

.. code-block:: python3

  def format_menu_to_welcome_message(rendered_str: str) -> Optional[str]:
      mail_body = "We have finalized today's menu, and we would like to inform you.\n\n"
      mail_body += "********** Todays Menu **********\n"
      mail_body += rendered_str + "\n"
      mail_body += "*********************************\n"
      mail_body += "Our staff is looking forward to your visit.\n"
      return mail_body

Finally, we will define a function to translate the created email message.
The Optional[str] here also indicates that the string is optional and can be
determined by the user. It will be used as the type for the artifact obtained
from the templa.Builder instance.

.. code-block:: python3

  def translate_en2jp(en_text: str) -> str:
      jp_text = en_text
      en2jp_maps = (
          (
              "We have finalized today's menu, and we would like to inform you.",
              "本日のメニューが決まりましたので、ご連絡させていただきます。",
          ),
          (
              "Our staff is looking forward to your visit.",
              "従業員一同、お客様のお越しをお待ちしております。",
          ),
          ("Todays Menu", "本日のお品書き"),
          ("food", "御食事"),
          ("ingredients", "食材"),
          ("sushi", "鮨"),
          ("tempura", "天麩羅"),
          ("simmered fish", "煮付け"),
          ("cherry salmon", "サクラマス"),
          ("Sea bream", "真鯛"),
          ("scallop", "帆立"),
          ("conger eel", "穴子"),
          ("asparagus", "アスパラガス"),
          ("bamboo shoots", "筍"),
          ("fava beans", "そら豆"),
          ("japanese rockfish", "メバル"),
      )
      for en2jp_map in en2jp_maps:
          jp_text = re.sub(en2jp_map[0], en2jp_map[1], jp_text, flags=re.I)
      return jp_text

  def support_multilingual(
      parsed_rendered_template: Optional[str],
  ) -> Optional[str]:
      if parsed_rendered_template is None:
          raise RuntimeError

      multilingual = parsed_rendered_template + "\n"
      multilingual += translate_en2jp(parsed_rendered_template)
      return multilingual

We will now define a factory function that composes these classes and functions into
a templa.Builder. The templa.Config class will be instantiated with the dictionary provided
as an argument during instance creation, and it will be expanded into the corresponding
data class, which is also passed as an argument.

.. code-block:: python3

  def create_menu_mail_message_builder(todays_food_data: Dict) -> Builder:
      config = Config(raw_config_dict=todays_food_data, ConfigDataClass=TodaysFoodData)
      menu_template_getter = MenuTemplateGetter()
      buider = Builder(
          config=config,
          template_getter=menu_template_getter,
          parse_rendered_template=format_menu_to_welcome_message,
          build_processed=support_multilingual,
      )
      return buider

Here is the complete file including the factory function:

.. include:: basic_usage/factory/menu_mail_message_builder.py
   :code: python3

The main code will be as follows:

.. include:: basic_usage/factory/main.py
   :code: python3

The output will be as follows:

.. code-block:: console

  $ python3 main.py
  We have finalized today's menu, and we would like to inform you.

  ********** Todays Menu **********

  * Food: Sushi
    Ingredients: Cherry salmon, Sea bream, Scallop, Conger eel

  * Food: Tempura
    Ingredients: Asparagus, Bamboo shoots, Fava beans

  * Food: Simmered fish
    Ingredients: Japanese rockfish

  *********************************
  Our staff is looking forward to your visit.

  本日のメニューが決まりましたので、ご連絡させていただきます。

  ********** 本日のお品書き **********

  * 御食事: 鮨
    食材: サクラマス, 真鯛, 帆立, 穴子

  * 御食事: 天麩羅
    食材: アスパラガス, 筍, そら豆

  * 御食事: 煮付け
    食材: メバル

  *********************************
  従業員一同、お客様のお越しをお待ちしております。
