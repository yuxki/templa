# menu_mail_message_builder.py
import re
from typing import Dict
from typing import List
from typing import Optional

import jinja2
from pydantic.dataclasses import dataclass

from templa import Builder
from templa import Config
from templa import ConfigData


@dataclass(frozen=True)
class FoodAndIngredients:
    food: str
    ingredients: List[str]


@dataclass(frozen=True)
class TodaysFoodData(ConfigData):
    data: List[FoodAndIngredients]


def format_menu_to_welcome_message(rendered_str: str) -> Optional[str]:
    mail_body = "We have finalized today's menu, and we would like to inform you.\n\n"
    mail_body += "********** Todays Menu **********\n"
    mail_body += rendered_str + "\n"
    mail_body += "*********************************\n"
    mail_body += "Our staff is looking forward to your visit.\n"
    return mail_body


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


class MenuTemplateGetter:
    def get_template(self) -> jinja2.Template:
        with open("todays_menu_template.jinja", encoding="utf-8") as f:
            template_text = f.read()

        environment = jinja2.Environment(
            loader=jinja2.DictLoader({"menu": template_text})
        )
        return environment.get_template("menu")


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
