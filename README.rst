===
rhf
===


.. image:: https://img.shields.io/pypi/v/rhf.svg
        :target: https://pypi.python.org/pypi/rhf

.. image:: https://travis-ci.com/anrputina/rhf.svg?branch=master
        :target: https://travis-ci.com/anrputina/rhf

.. image:: https://readthedocs.org/projects/rhf/badge/?version=latest
        :target: https://rhf.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status




Python implementation of Random Histogram Forest (RHF)

Installation and Usage
=======
To install rhf ::

    pip install rhf

To use rhf in a project::

    from rhf import RHF

    my_rhf = RHF(num_trees = 100, max_height = 5, split_criterion='kurtosis')
    output_scores = my_rhf.fit(data)




Credits
-------

* Free software: MIT license
* Documentation: https://rhf.readthedocs.io.

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
