[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Run Tests](https://github.com/yuxki/templa/actions/workflows/tests.yml/badge.svg)](https://github.com/yuxki/templa/actions/workflows/tests.yml)
[![Documentation Status](https://readthedocs.org/projects/templa/badge/?version=latest)](https://templa.readthedocs.io/en/latest/?badge=latest)
[![Coverage Status](https://coveralls.io/repos/github/yuxki/templa/badge.svg?branch=master)](https://coveralls.io/github/yuxki/templa?branch=master)

# templa

Templa is a Python library that offers a flexible and typed building system using
Jinja2 templates for your code. It allows you to easily render, parse, process,
and build. The following are the assumed build processes in Templa:

- Define the required context with dataclass for rendering a Jinja2 formatted template.
- Render the template with Jinja2 library using the provided context.
- Extract relevant information and elements from the rendered template for further processing.
- Perform necessary processing on the parsed rendered template.
- Utilize the processed rendered template to generate desired outputs or objects.

```python
from dataclasses import dataclass
from typing import List
from typing import Optional

import jinja2
import yaml

from templa.builder import Builder
from templa.config import Config
from templa.config import ConfigData


def parse_rendered_template_yaml_stub(rendered_str: str) -> Optional[List[str]]:
    parsed_rendered_template = yaml.safe_load(rendered_str)
    assert (
        isinstance(parsed_rendered_template, list) or parsed_rendered_template is None
    )
    return parsed_rendered_template


def build_parsed_rendered_template_yaml_stub(
    parsed_rendered_template: Optional[List[str]],
) -> Optional[str]:
    built = yaml.dump(parsed_rendered_template, Dumper=yaml.SafeDumper)
    assert isinstance(built, str)
    return built


class SampleTemplateGetter:
    def get_template(self) -> jinja2.Template:
        environment = jinja2.Environment(
            loader=jinja2.DictLoader(
                {"template.txt": "---\n- {{ foo }}\n- {{ bar }}\n- {{ zoo }}"}
            )
        )
        return environment.get_template("template.txt")


@dataclass(frozen=True)
class SampleConfigData(ConfigData):
    foo: str
    bar: str


class SampleBuilder(Builder[List[str], str]):
    def __init__(
        self,
    ) -> None:
        super().__init__(
            config=Config[SampleConfigData]({"foo": "FOO", "bar": 5}, SampleConfigData),
            template_getter=SampleTemplateGetter(),
            parse_rendered_template=parse_rendered_template_yaml_stub,
            build_processed=build_parsed_rendered_template_yaml_stub,
        )

    def _build(self, processed: Optional[List[str]]) -> Optional[str]:
        if processed is not None:
            processed[2] = "ZOO_Updated"
        return super()._build(processed)


def build_sample_template() -> None:
    builder = SampleBuilder()
    initialized_target = builder.init_builder_target()

    # It will be typing error because the builder variable is in a
    # state of an unfinished type before the build process is
    # completed, causing a type error.
    # builder.build(initialized_target)
    # ->  Argument 1 to "build" of "Builder" has incompatible type
    #     "BuilderTargetInitialized"; expected "BuilderTargetProcessed"  [arg-type]

    processed_target = builder.process_template(initialized_target)
    built_target = builder.build(processed_target)
    print(builder.fetch_built(built_target))


if __name__ == "__main__":
    build_sample_template()
```

## Install
```shell
$ pip install 'templa@git+https://github.com/yuxki/templa.git'
```
