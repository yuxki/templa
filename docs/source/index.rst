Flexible and Typed Template Building System
===========================================

Templa is a Python library that offers a flexible and typed building system using
Jinja2 templates for your code. It allows you to easily render, parse, process,
and build. The following are the assumed build processes in Templa:

- Define the required context with dataclass for rendering a `Jinja2`_ formatted template.
- Render the template with Jinja2 library using the provided context.
- Extract relevant information and elements from the rendered template for further processing.
- Perform necessary processing on the parsed rendered template.
- Utilize the processed rendered template to generate desired outputs or objects.

.. _Jinja2: https://github.com/pallets/jinja

Here is an example of a program using Templa:

.. include:: index_example.py
   :code: python3


When you execute this program:

.. code-block:: console

  $ python sample.py


It prints:

.. code-block::

  - FOO
  - 5
  - ZOO_Updated

Documentation
-------------

.. toctree::
   :maxdepth: 2

   design
   usage
   api
