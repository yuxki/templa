API
===

Builder
-------

.. module:: templa
    :noindex:

.. autoclass:: Builder
   :members: config,template_getter,init_builder_target,fetch_render_context,
    process_template,_process_template,fetch_processed,build,_build,fetch_built

.. autoexception:: NotSameBuilderInstanceError

.. autodata:: BuilderTargetInitialized
   :annotation: = NewType("BuilderTargetInitialized", "Builder")

   A NewType of the builder instance as the initial target.

.. autodata:: BuilderTargetProcessed
   :annotation: = NewType("BuilderTargetProcessed", "Builder[Any, Any]")

   A NewType of the builder instance as the target after processing template.

.. autodata:: BuilderTargetBuilt
   :annotation: = NewType("BuilderTargetBuilt", "Builder[Any, Any]")

   A NewType of the builder instance as the target after building step.

.. autoclass:: TemplateGettable()
   :members: get_template

Config
------

.. autoclass:: ConfigData

.. autoclass:: Config
   :members: raw_config_dict,load_config,data,get_render_context,_get_render_context

.. autoexception:: ConfigDataNotLoadedError


YAMLBuilder
-----------

.. autoclass:: YAMLBuilder

.. autoclass:: OrderedDictLoader

.. autoclass:: OrderedDictDumper
