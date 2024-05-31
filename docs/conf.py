"""Sphinx configuration file."""

import os
import shutil

project = "TopoBenchmarkX"
copyright = "2022-2023, PyT-Team, Inc."
author = "PyT-Team Authors"

extensions = [
    "nbsphinx",
    "nbsphinx_link",
    "numpydoc",
    "sphinx.ext.autodoc",
    "sphinx.ext.coverage",
    "sphinx.ext.doctest",
    "sphinx.ext.githubpages",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_gallery.load_style",
]

# Configure nbsphinx for notebook execution
nbsphinx_execute_arguments = [
    "--InlineBackend.figure_formats={'svg', 'pdf'}",
    "--InlineBackend.rc={'figure.dpi': 96}",
]

nbsphinx_execute = "never"

# To get a prompt similar to the Classic Notebook, use
nbsphinx_input_prompt = " In [%s]:"
nbsphinx_output_prompt = " Out [%s]:"

nbsphinx_allow_errors = True

templates_path = ["_templates"]

source_suffix = [".rst"]

master_doc = "index"

language = "en"

nbsphinx_prolog = r"""
{% set docname = env.doc2path(env.docname, base=None) %}

.. raw:: latex
    \nbsphinxstartnotebook{\scriptsize\noindent\strut
    \textcolor{gray}{The following section was generated from
    \sphinxcode{\sphinxupquote{\strut {{ docname | escape_latex }}}} \dotfill}}
    """
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "**.ipynb_checkpoints"]

pygments_style = None

html_theme = "pydata_sphinx_theme"
html_baseurl = "pyt-team.github.io"
htmlhelp_basename = "pyt-teamdoc"
html_last_updated_fmt = "%c"

latex_elements = {}


latex_documents = [
    (
        master_doc,
        "topobenchmarkx.tex",
        "TopoBenchmarkX Documentation",
        "PyT-Team",
        "manual",
    ),
]

man_pages = [(master_doc, "topobenchmarkx", "TopoBenchmarkX Documentation", [author], 1)]

texinfo_documents = [
    (
        master_doc,
        "topobenchmarkx",
        "TopoBenchmarkX Documentation",
        author,
        "topobenchmarkx",
        "One line description of project.",
        "Miscellaneous",
    ),
]

epub_title = project
epub_exclude_files = ["search.html"]


def copy_thumbnails():
    """Copy the thumbnail files in the _build
    directory to enable thumbnails in the gallery"""
    src_directory = "./_thumbnails"
    des_directory = "./_build/_thumbnails"

    des_directory_walked = os.walk(src_directory)
    all_thumbnails = []

    for a, b, c in des_directory_walked:
        if len(c) == 0:
            all_directories = b
            continue
        if len(b) != 0:
            raise NotImplementedError(
                "Not yet implemented for the case with more than one nested directory."
            )

        for file in c:
            full_filename = a + "/" + file
            all_thumbnails.append(full_filename)

    os.mkdir("./_build")
    os.mkdir(des_directory)

    for directory in all_directories:
        os.mkdir(des_directory + "/" + directory)

    for thumbnail in all_thumbnails:
        shutil.copyfile(thumbnail, "./_build/" + thumbnail[2:])


copy_thumbnails()

nbsphinx_thumbnails = {
    "notebooks/can_train": "_thumbnails/can_train.png",
}

# configure intersphinx
intersphinx_mapping = {
    "networkx": ("https://networkx.org/documentation/stable/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "python": ("https://docs.python.org/3/", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/", None),
    "toponetx": ("https://pyt-team.github.io/toponetx/", None),
}

# configure numpydoc
numpydoc_validation_checks = {"all", "GL01", "ES01", "SA01", "EX01"}
numpydoc_show_class_members = False
numpydoc_class_members_toctree = False
