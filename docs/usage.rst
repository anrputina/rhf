=====
Usage
=====

To use rhf in a project::

    from rhf import RHF

    my_rhf = RHF(num_trees = 100, max_height = 5, split_criterion='kurtosis')
    output_scores = my_rhf.fit(data)
