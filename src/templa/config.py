from copy import deepcopy
from dataclasses import asdict
from dataclasses import dataclass
from typing import Any
from typing import Dict
from typing import Generic
from typing import Optional
from typing import Type
from typing import TypeVar


class ConfigDataNotLoadedError(RuntimeError):
    """Used when a ConfigData instance is not created properly."""


@dataclass(frozen=True)
class ConfigData:
    """A simple dataclasses.dataclass with frozen
    set to True to ensure integrity."""


CONFIG_DATA = TypeVar("CONFIG_DATA", bound=ConfigData)


class Config(Generic[CONFIG_DATA]):
    """Provides a template rendering context created from a dataclass.
    It can be accessed and modified as needed by overriding. The
    dataclass is created from a dictionary provided as an argument.

    :param CONFIG_DATA: The Type parameter specifies the type of
        the ConfigData instance.

    :param raw_config_dict: A variadic argument for ConfigDataClass.

    :param ConfigDataClass: A ConfigData class.

    """

    def __init__(
        self, raw_config_dict: Dict[Any, Any], ConfigDataClass: Type[CONFIG_DATA]
    ) -> None:
        self.__raw_config_dict = raw_config_dict
        self.__ConfigData = ConfigDataClass
        self.__data: Optional[CONFIG_DATA] = None

    @property
    def raw_config_dict(self) -> Dict[Any, Any]:
        """Returns a deep copy of the provided raw_config_dict."""
        return deepcopy(self.__raw_config_dict)

    def load_config(self) -> None:
        """Creates a ConfigData instance using the Config.raw_config_dict."""
        self.__data = self.__ConfigData(**self.__raw_config_dict)

    @property
    def data(self) -> Optional[CONFIG_DATA]:
        """Returns a ConfigData instance created by Config.load_config().
        The `frozen` option of the returned ConfigData instance is set to True,
        which means it does not use deepcopy."""
        return self.__data

    def get_render_context(self) -> Dict[Any, Any]:
        """Calls Config._get_render_context() and returns the returned context."""
        return self._get_render_context(self.__data)

    def _get_render_context(self, data: Optional[CONFIG_DATA]) -> Dict[Any, Any]:
        """Returns a dictionary created from the provided ConfigData instance.
        If the instance is None, an empty dictionary is returned.

        Intended to be overridden by a subclass.

        .. code-block:: python

            def _get_render_context(self, data: Optional[BarConfigData]) -> Dict:
                context = super()._get_render_context(data)
                context.update({"zoo": "ZOO"})
                return context

        :param data: ConfigData instance created by Config.load_config().

        """
        if data is None:
            return {}
        return asdict(data)
