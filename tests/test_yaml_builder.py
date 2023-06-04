from dataclasses import dataclass
from typing import Dict

import jinja2

from templa.config import Config
from templa.config import ConfigData
from templa.config import ConfigDataNotLoadedError
from templa.yaml_builder import YAMLBuilder


def test_yaml_builder(tmp_path: str) -> None:
    @dataclass(frozen=True)
    class StubConfigData(ConfigData):
        foo: int
        bar: int
        zoo: int

    class StubConfig(Config[StubConfigData]):
        def __init__(self, raw_config_dict: Dict[str, int]):
            super().__init__(raw_config_dict, StubConfigData)

        def get_render_context(self) -> Dict[str, int]:
            if self.data is None:
                raise ConfigDataNotLoadedError
            return {
                "foo": self.data.foo + 1,
                "bar": self.data.bar + 2,
                "zoo": self.data.zoo + 3,
            }

    template_text = """---
foo:
  foo_one: {{ foo }}
  foo_two: {{ foo }}
  foo_three: {{ foo }}
bar:
  bar_one: {{ bar }}
  bar_two: {{ bar }}
  bar_three: {{ bar }}
zoo:
  zoo_one: {{ zoo }}
  zoo_two: {{ zoo }}
  zoo_three: {{ zoo }}
    """

    class StubTemplateGetter:
        def get_template(self) -> jinja2.Template:
            name = "template.txt"
            environment = jinja2.Environment(
                loader=jinja2.DictLoader({name: template_text})
            )
            return environment.get_template(name)

    raw_config_dict = {"foo": 0, "bar": 0, "zoo": 0}
    config = StubConfig(raw_config_dict)
    builder = YAMLBuilder[Dict[str, int]](
        config=config,
        yaml_template_getter=StubTemplateGetter(),
    )

    target_initialized = builder.init_builder_target()
    target_processed = builder.process_template(target_initialized)
    target_built = builder.build(target_processed)

    template_text = """foo:
  foo_one: 1
  foo_two: 1
  foo_three: 1
bar:
  bar_one: 2
  bar_two: 2
  bar_three: 2
zoo:
  zoo_one: 3
  zoo_two: 3
  zoo_three: 3
"""

    assert builder.fetch_built(target_built) == template_text
