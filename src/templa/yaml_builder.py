from __future__ import annotations

from collections import OrderedDict
from typing import Any

import yaml
from jinja2 import Environment
from jinja2 import Template

from templa.builder import Builder
from templa.builder import PROCESSED
from templa.builder import TemplateGettable
from templa.config import Config


class OrderedDictLoader(yaml.Loader):
    """Subclass of yaml.Loader using OrderedDict collection
    as a constructor."""


def ordered_dict_constructor(
    loader: OrderedDictLoader, node: yaml.MappingNode
) -> OrderedDict[Any, Any]:  # pylint: disable=unsubscriptable-object
    value = loader.construct_mapping(node)
    return OrderedDict(value)


OrderedDictLoader.add_constructor(
    yaml.resolver.Resolver.DEFAULT_MAPPING_TAG, ordered_dict_constructor
)


class OrderedDictDumper(yaml.Dumper):
    """Subclass of yaml.Dumper using OrderedDict collection
    as a representer."""


def ordered_dict_representer(
    dumper: OrderedDictDumper,
    data: OrderedDict[Any, Any],  # pylint: disable=unsubscriptable-object
) -> yaml.MappingNode:
    mapping_node = dumper.represent_mapping(
        yaml.resolver.Resolver.DEFAULT_MAPPING_TAG, data
    )
    keys = [value[0].value for value in mapping_node.value]
    ordered_value = []
    for key in data.keys():
        ordered_value.append(mapping_node.value[keys.index(key)])
    mapping_node.value = ordered_value
    return mapping_node


OrderedDictDumper.add_representer(OrderedDict, ordered_dict_representer)


def get_template(environment: Environment, name: str) -> Template:
    return environment.get_template(name)


def load_rendered_yaml_str(rendered_str: str) -> Any:
    parsed_obj = yaml.load(rendered_str, OrderedDictLoader)
    return parsed_obj


def dump_parsed_obj(processed: PROCESSED) -> str:
    built = yaml.dump(processed, Dumper=OrderedDictDumper)
    assert isinstance(built, str)
    return built


class YAMLBuilder(Builder[PROCESSED, str]):
    """Subclass of templa.Builder that uses templa.OrderedDictLoader and
    templa.OrderedDictDumper. Receives and renders a YAML template, and builds
    YAML while preserving the order of the received YAML.

    :param PROCESSED: The Type parameter specifies the type of
        the parsed and rendered template.

    :param config: An instance of templa.Config that provides
        the rendering context.

    :param yaml_template_getter: An implementation of the templa.TemplateGettable
        protocol that provides access to a jinja2.Template which provides
        YAML template.

    """

    def __init__(
        self,
        config: Config[Any],
        yaml_template_getter: TemplateGettable,
    ) -> None:
        super().__init__(
            config=config,
            template_getter=yaml_template_getter,
            parse_rendered_template=load_rendered_yaml_str,
            build_processed=dump_parsed_obj,
        )
