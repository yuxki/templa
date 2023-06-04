# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "templa"
copyright = "2023, yuxki"
author = "yuxki"

extensions = [
    "sphinx.ext.doctest",
    "sphinx.ext.autodoc",
]

html_title = "templa"
autodoc_typehints = "description"
autodoc_member_order = "bysource"
templates_path = ["_templates"]

html_theme = "furo"
html_static_path = ["_static"]
