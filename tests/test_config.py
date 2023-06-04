from dataclasses import dataclass
from typing import Any
from typing import Dict
from typing import Optional

from templa.config import Config
from templa.config import ConfigData
from templa.config import ConfigDataNotLoadedError


def test_config_new() -> None:
    raw_config_dict: Dict[Any, Any] = {}
    config = Config(raw_config_dict=raw_config_dict, ConfigDataClass=ConfigData)

    assert config.data is None
    assert config.raw_config_dict == {}
    assert config.get_render_context() == {}


def test_config_raw_config_dict_is_immutable() -> None:
    raw_config_dict: Dict[Any, Any] = {}
    config = Config(raw_config_dict=raw_config_dict, ConfigDataClass=ConfigData)
    config.raw_config_dict.update({"a": "b"})

    assert config.raw_config_dict == {}


def test_config_sub_class_load_config() -> None:
    @dataclass(frozen=True)
    class BarConfigData(ConfigData):
        bar: str
        foo: int

    class BarConfig(Config[BarConfigData]):
        def __init__(self, raw_config_dict: Dict[Any, Any]) -> None:
            super().__init__(raw_config_dict, BarConfigData)

        @property
        def bar(self) -> str:
            if self.data is None:
                raise ConfigDataNotLoadedError
            return self.data.bar

        @property
        def foo(self) -> int:
            if self.data is None:
                raise ConfigDataNotLoadedError
            return self.data.foo

    bar_raw_config_dict = {
        "bar": "abc",
        "foo": 5,
    }

    bar_config = BarConfig(bar_raw_config_dict)
    bar_config.load_config()
    assert bar_config.bar == "abc"
    assert bar_config.foo == 5
    assert bar_config.get_render_context() == bar_raw_config_dict


def test_config_sub_class_override_get_render_context() -> None:
    @dataclass(frozen=True)
    class BarConfigData(ConfigData):
        bar: str
        foo: int

    class BarConfig(Config[BarConfigData]):
        def __init__(self, raw_config_dict: Dict[Any, Any]) -> None:
            super().__init__(raw_config_dict, BarConfigData)

        def _get_render_context(self, data: Optional[BarConfigData]) -> Dict[Any, Any]:
            context = super()._get_render_context(data)
            context.update({"zoo": "ZOO"})
            return context

    bar_raw_config_dict = {
        "bar": "abc",
        "foo": 5,
    }

    want_render_context = {
        "bar": "abc",
        "foo": 5,
        "zoo": "ZOO",
    }

    bar_config = BarConfig(bar_raw_config_dict)
    bar_config.load_config()
    assert bar_config.get_render_context() == want_render_context


def test_config_sub_class_override_get_render_context_with_none() -> None:
    @dataclass(frozen=True)
    class BarConfigData(ConfigData):
        bar: str
        foo: int

    class BarConfig(Config[BarConfigData]):
        def __init__(self, raw_config_dict: Dict[Any, Any]) -> None:
            super().__init__(raw_config_dict, BarConfigData)

        def _get_render_context(self, data: Optional[BarConfigData]) -> Dict[Any, Any]:
            if data is None:
                return {}
            context = super()._get_render_context(None)
            context.update({"zoo": data.foo + 5})
            return context

    bar_raw_config_dict = {
        "bar": "abc",
        "foo": 5,
    }

    want_render_context = {
        "zoo": 10,
    }

    bar_config = BarConfig(bar_raw_config_dict)
    bar_config.load_config()
    assert bar_config.get_render_context() == want_render_context
