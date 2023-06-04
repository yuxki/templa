import os
import sys
from copy import deepcopy
from dataclasses import dataclass
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import jinja2
import pytest
import yaml

from templa.builder import Builder
from templa.builder import BuilderTargetBuilt
from templa.builder import BuilderTargetInitialized
from templa.builder import BuilderTargetProcessed
from templa.builder import NotSameBuilderInstanceError
from templa.builder import TemplateGettable
from templa.config import Config
from templa.config import ConfigData


def is_more_than_py_ver_311() -> bool:
    return sys.version_info[0] == 3 and sys.version_info[1] >= 11


def parse_rendered_template_stub_int(rendered_str: str) -> int:
    return 1


def build_processed_stub_str(
    processed: Optional[int],
) -> Optional[str]:
    return "abc"


class StubTemplateGetter:
    def __init__(self, environment: jinja2.Environment, name: str):
        self.environment = environment
        self.name = name

    def get_template(self) -> jinja2.Template:
        return self.environment.get_template(self.name)


@dataclass(frozen=True)
class StubConfigData(ConfigData):
    foo: str
    bar: str


class StubConfig(Config[StubConfigData]):
    def __init__(self, raw_config_dict: Dict[str, str]):
        super().__init__(raw_config_dict, StubConfigData)


def test_new_builder() -> None:
    builder = Builder[Any, Any](
        config=StubConfig({"foo": "FOO", "bar": "BAR"}),
        template_getter=StubTemplateGetter(jinja2.Environment(), "foo"),
        parse_rendered_template=parse_rendered_template_stub_int,
        build_processed=build_processed_stub_str,
    )

    target_initialized = builder.init_builder_target()
    if is_more_than_py_ver_311():
        from typing import assert_type

        assert_type(target_initialized, BuilderTargetInitialized)
        assert_type(builder.config, Config[Any])
        assert_type(builder.template_getter, TemplateGettable)
        assert_type(builder.fetch_render_context(target_initialized), Dict[Any, Any])

    assert isinstance(target_initialized, Builder)
    assert isinstance(builder.config, StubConfig)
    assert isinstance(builder.template_getter, StubTemplateGetter)
    assert isinstance(builder.fetch_render_context(target_initialized), dict)


def test_builder_config_immutable() -> None:
    builder = Builder[Any, Any](
        config=StubConfig({"foo": "FOO", "bar": "BAR"}),
        template_getter=StubTemplateGetter(jinja2.Environment(), "foo"),
        parse_rendered_template=parse_rendered_template_stub_int,
        build_processed=build_processed_stub_str,
    )

    config = builder.config
    config.__dict__.update({"zoo": "zoo"})

    assert builder.config.__dict__.get("zoo") is None


def test_builder_template_getter_immutable() -> None:
    builder = Builder[Any, Any](
        config=StubConfig({"foo": "FOO", "bar": "BAR"}),
        template_getter=StubTemplateGetter(jinja2.Environment(), "foo"),
        parse_rendered_template=parse_rendered_template_stub_int,
        build_processed=build_processed_stub_str,
    )
    template_getter = builder.template_getter
    template_getter.__dict__.update({"updated": "updated"})

    assert builder.template_getter.__dict__.get("updated") is None


@dataclass(frozen=True)
class StubYamlConfigData(ConfigData):
    foo: str
    bar: str


class StubYamlConfig(Config[StubYamlConfigData]):
    def __init__(self, raw_config_dict: Dict[str, Union[int, str]]):
        super().__init__(raw_config_dict, StubYamlConfigData)


class StubYamlTemplateGetter:
    def __init__(self, environment: jinja2.Environment, name: str):
        self.environment = environment
        self.name = name

    def get_template(self) -> jinja2.Template:
        return self.environment.get_template(self.name)


def parse_rendered_template_yaml_stub(rendered_str: str) -> Optional[List[str]]:
    processed = yaml.safe_load(rendered_str)
    assert isinstance(processed, list) or processed is None
    return processed


def build_processed_yaml_stub(
    processed: Optional[List[str]],
) -> Optional[str]:
    built = yaml.dump(processed, Dumper=yaml.SafeDumper)
    assert isinstance(built, str)
    return built


def test_builder_from_process_template_to_build(tmp_path: str) -> None:
    builder = Builder[List[str], str](
        config=StubYamlConfig({"foo": "FOO", "bar": 5}),
        template_getter=StubYamlTemplateGetter(
            jinja2.Environment(
                loader=jinja2.DictLoader(
                    {"template.txt": "---\n- {{ foo }}\n- {{ bar }}"}
                )
            ),
            "template.txt",
        ),
        parse_rendered_template=parse_rendered_template_yaml_stub,
        build_processed=build_processed_yaml_stub,
    )

    target_initialized = builder.init_builder_target()
    target_processed = builder.process_template(target_initialized)
    target_built = builder.build(target_processed)

    fetched_processed = builder.fetch_processed(target_built)
    fetched_built = builder.fetch_built(target_built)

    if is_more_than_py_ver_311():
        from typing import assert_type

        assert_type(target_processed, BuilderTargetProcessed)
        assert_type(target_built, BuilderTargetBuilt)
        assert_type(fetched_processed, Optional[List[str]])
        assert_type(fetched_built, Optional[str])

    assert isinstance(target_processed, Builder)
    assert isinstance(target_built, Builder)
    assert fetched_processed == ["FOO", 5]
    assert fetched_built == "- FOO\n- 5\n"


class StubBuilder(Builder[List[str], str]):
    def __init__(
        self,
        config: Config[Any],
        template_getter: StubYamlTemplateGetter,
        output_path: Optional[str],
    ) -> None:
        super().__init__(
            config=config,
            template_getter=template_getter,
            parse_rendered_template=parse_rendered_template_yaml_stub,
            build_processed=build_processed_yaml_stub,
        )
        self.__output_path = output_path

    def _process_template(self, context: Dict[str, str]) -> Optional[List[str]]:
        context.update({"zoo": "ZOO"})
        processed = super()._process_template(context)

        if is_more_than_py_ver_311():
            from typing import assert_type

            assert_type(processed, Optional[List[str]])

        return processed

    def _build(self, processed: Optional[List[str]]) -> Optional[str]:
        if processed is not None:
            processed[2] = "ZOO_Updated"
        print(f"Building {self.__output_path}", file=sys.stdout)
        built = super()._build(processed)

        if is_more_than_py_ver_311():
            from typing import assert_type

            assert_type(built, Optional[str])

        if built is None:
            return built

        if self.__output_path is None:
            return built

        with open(self.__output_path, "w", encoding="utf-8") as f:
            f.write(built)

        return built


def test_builder_load_to_build_overrided(
    tmp_path: str, capsys: pytest.CaptureFixture[Any]
) -> None:
    test_file_path = os.path.join(tmp_path, "testfile.txt")
    builder = StubBuilder(
        config=StubYamlConfig({"foo": "FOO", "bar": 5}),
        template_getter=StubYamlTemplateGetter(
            jinja2.Environment(
                loader=jinja2.DictLoader(
                    {"template.txt": "---\n- {{ foo }}\n- {{ bar }}\n- {{ zoo }}"}
                )
            ),
            "template.txt",
        ),
        output_path=test_file_path,
    )

    target_initialized = builder.init_builder_target()
    target_processed = builder.process_template(target_initialized)
    fetched_processed = builder.fetch_processed(target_processed)

    assert builder.fetch_processed(target_processed) == [
        "FOO",
        5,
        "ZOO",
    ]

    target_built = builder.build(target_processed)
    fetched_built = builder.fetch_built(target_built)

    if is_more_than_py_ver_311():
        from typing import assert_type

        assert_type(target_processed, BuilderTargetProcessed)
        assert_type(target_built, BuilderTargetBuilt)
        assert_type(fetched_processed, Optional[List[str]])
        assert_type(fetched_built, Optional[str])

    with open(test_file_path, encoding="utf-8") as f:
        wrote = f.read()

    assert builder.fetch_built(target_built) == "- FOO\n- 5\n- ZOO_Updated\n"
    assert wrote == "- FOO\n- 5\n- ZOO_Updated\n"
    assert capsys.readouterr().out == f"Building {test_file_path}\n"


def test_builder_not_same_instance_error() -> None:
    builder = Builder[List[str], str](
        config=StubYamlConfig({"foo": "FOO", "bar": 5}),
        template_getter=StubYamlTemplateGetter(
            jinja2.Environment(
                loader=jinja2.DictLoader(
                    {"template.txt": "---\n- {{ foo }}\n- {{ bar }}"}
                )
            ),
            "template.txt",
        ),
        parse_rendered_template=parse_rendered_template_yaml_stub,
        build_processed=build_processed_yaml_stub,
    )
    another_builder = deepcopy(builder)

    target_initialized = builder.init_builder_target()
    another_target_initialized = another_builder.init_builder_target()

    with pytest.raises(NotSameBuilderInstanceError):
        another_builder.fetch_render_context(target_initialized)

    with pytest.raises(NotSameBuilderInstanceError):
        another_builder.process_template(target_initialized)

    target_processed = builder.process_template(target_initialized)
    another_target_processed = another_builder.process_template(
        another_target_initialized
    )

    with pytest.raises(NotSameBuilderInstanceError):
        another_builder.fetch_processed(target_processed)

    target_built = builder.build(target_processed)
    another_builder.build(another_target_processed)

    with pytest.raises(NotSameBuilderInstanceError):
        another_builder.fetch_built(target_built)
