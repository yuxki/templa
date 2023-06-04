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
