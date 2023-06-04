"""
API and implementations for building process.
"""
from copy import deepcopy
from typing import Any
from typing import Callable
from typing import Dict
from typing import Generic
from typing import NewType
from typing import Optional
from typing import Protocol
from typing import runtime_checkable
from typing import TypeVar
from typing import Union

from jinja2 import Template

from templa.config import Config


class NotSameBuilderInstanceError(RuntimeError):
    """An error that is raised when the builder instance passed as an argument for
    each build step method is different from the calling instance."""


PROCESSED = TypeVar("PROCESSED")
BUILT = TypeVar("BUILT")

BuilderTargetInitialized = NewType("BuilderTargetInitialized", "Builder[Any, Any]")
BuilderTargetProcessed = NewType("BuilderTargetProcessed", "Builder[Any, Any]")
BuilderTargetBuilt = NewType("BuilderTargetBuilt", "Builder[Any, Any]")
BuilderTargetAnyState = Union[
    BuilderTargetInitialized, BuilderTargetProcessed, BuilderTargetBuilt
]


@runtime_checkable
class TemplateGettable(Protocol):
    """typing.Protocol for retrieving the jinja2.Template object,
    which is used within the templa.Builder composition."""

    def get_template(self) -> Template:
        """Return the jinja2.Template."""


class Builder(Generic[PROCESSED, BUILT]):
    """
    Builder is the central class in Templa for executing build processes.

    The Builder class defines the core logic of the build processes.
    It allows for method overriding and composition of functions to
    customize the build behavior. The data used in the build processes
    is provided from templa.Config.

    Each build process and artifact fetching requires a self instance as the
    target of the builder, which is typed using the NewType returned from the
    previous build process. This ensures type safety and allows for the build
    processes to be executed sequentially.

    Example:

    .. code-block:: python

        builder = Builder(...)

        target_initialized = builder.init_builder_target()
        target_processed = builder.process_template(target_initialized)
        target_built = builder.build(target_processed)

        built = builder.fetch_built(target_built)


    :param PROCESSED: The Type parameter specifies the type of
        the parsed and rendered template.

    :param BUILT: The Type parameter specifies the type of the built object.

    :param config: An instance of templa.Config that provides
        the rendering context.

    :param template_getter: An implementation of the templa.TemplateGettable
        protocol that provides access to a jinja2.Template.

    :param parse_rendered_template: Parse the rendered jinja2.Template and
        return the processed. The type of the processed
        is defined by the type parameter (PROCESSED) of templa.Builder.

    :param build_processed: Build an object of the type specified
        by the type parameter (BUILT) from the processed.
    """

    def __init__(
        self,
        config: Config[Any],
        template_getter: TemplateGettable,
        parse_rendered_template: Callable[[str], Optional[PROCESSED]],
        build_processed: Callable[[Optional[PROCESSED]], Optional[BUILT]],
    ) -> None:
        self.__config = deepcopy(config)
        self.__config.load_config()
        self.__render_context: Dict[Any, Any] = self.__config.get_render_context()
        self.__template_getter = deepcopy(template_getter)
        self.__parse_rendered_template = parse_rendered_template
        self.__build_processed = build_processed
        self.__processed: Optional[PROCESSED] = None
        self.__built: Optional[BUILT] = None

    @property
    def config(self) -> Config[Any]:
        """Returns a deep copy of the provided templa.Config instance."""
        return deepcopy(self.__config)

    @property
    def template_getter(self) -> TemplateGettable:
        """Returns a deepcopy of the provided template_getter instance."""
        return deepcopy(self.__template_getter)

    def _check_see_if_same_builder_instance(
        self, target: BuilderTargetAnyState
    ) -> None:
        if self != target:
            raise NotSameBuilderInstanceError

    def init_builder_target(self) -> BuilderTargetInitialized:
        """Returns a NewType of the self instance as the initial builder target."""
        return BuilderTargetInitialized(self)

    def fetch_render_context(self, target: BuilderTargetAnyState) -> Dict[Any, Any]:
        """Fetches and returns the rendering context from the self builder
        target. The rendering context is extracted from the provided
        templa.Config, which is used to render the template.

        Raises templa.NotSameBuilderInstanceError if the self instance does
        not match the provided builder instance.

        :param target: NewType of the self instance.
        """
        self._check_see_if_same_builder_instance(target)
        return deepcopy(self.__render_context)

    def process_template(
        self, target: BuilderTargetInitialized
    ) -> BuilderTargetProcessed:
        """Calls _process_template() and returns a NewType of the builder
        target after processing the template.

        Raises templa.NotSameBuilderInstanceError if the self instance does
        not match the provided builder instance.

        :param target: NewType of the self instance.
        """
        self._check_see_if_same_builder_instance(target)
        self._process_template(self.fetch_render_context(target))
        return BuilderTargetProcessed(target)

    def _process_template(self, context: Dict[Any, Any]) -> Optional[PROCESSED]:
        """Runs the template processing logic by obtaining the template, rendering
        it with the context provided by an instance of templa.Config as
        an argument, and parsing the rendered template.

        Returns the parsed and rendered template.

        :param context: A deepcopy of the context passed to jinja2.Template.render().

        Intended to be overridden by a subclass.
        Example:

        .. code-block:: python

            def _process_template(self, context: Dict) -> Optional[PROCESSED]:
                context.update({"zoo": "ZOO"})
                return super()._process_template(context)

        """
        template = self.__template_getter.get_template()
        rendered_str = template.render(context)
        self.__processed = self.__parse_rendered_template(rendered_str)
        return self.__processed

    def fetch_processed(
        self,
        target: Union[BuilderTargetProcessed, BuilderTargetBuilt],
    ) -> Optional[PROCESSED]:
        """Fetches and returns the a deepcopy of the parsed and rendered template,
        which is created during the template processing step.

        Raises templa.NotSameBuilderInstanceError if the self instance does
        not match the provided builder instance.

        :param target: NewType of the self instance.
        """
        self._check_see_if_same_builder_instance(target)
        return deepcopy(self.__processed)

    def build(self, target: BuilderTargetProcessed) -> BuilderTargetBuilt:
        """Calls _process_template() and returns a NewType of the builder
        target after building step.

        Raises templa.NotSameBuilderInstanceError if the self instance does
        not match the provided builder instance.

        :param target: NewType of the self instance.
        """
        self._check_see_if_same_builder_instance(target)
        self._build(self.fetch_processed(target))
        return BuilderTargetBuilt(target)

    def _build(self, processed: Optional[PROCESSED]) -> Optional[BUILT]:
        """Runs the building logic to build the object using the parsed and
        rendered template generated during the template processing step.

        Raises templa.NotSameBuilderInstanceError if the self instance does
        not match the provided builder instance.

        Returns the built artifact.

        :param processed: A deepcopy of the parsed rendered template
            that is passed to jinja2.Template.render().

        Intended to be overridden by a subclass.
        Example:

        .. code-block:: python

            def _build(self, processed: Optional[List[str]]) -> Optional[str]:
                if processed is not None:
                    processed[2] = "ZOO_Updated"
                built_text = super()._build(processed)

                if built_text is None:
                    return None

                with open("/tmp/built.txt", "w", encoding="utf-8") as f:
                    f.write(built_text)

                return built_text

        """
        self.__built = self.__build_processed(processed)
        return self.__built

    def fetch_built(self, target: BuilderTargetBuilt) -> Optional[BUILT]:
        """Fetches and returns a deepcopy of the artifact generated during
        the building step.

        Raises templa.NotSameBuilderInstanceError if the self instance does
        not match the provided builder instance.

        :param target: NewType of the self instance.
        """
        self._check_see_if_same_builder_instance(target)
        return deepcopy(self.__built)
