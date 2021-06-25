# -*- coding: utf-8 -*-


###########
# IMPORTS #
###########

# Full

import networkx as nx
import numpy as np

# Partial

from ast import (
    parse
)

from types import (
    CodeType,
    FunctionType
)

# Internal

from pydtmc.validation import *


#############
# FUNCTIONS #
#############

def _string_to_function(source):

    ast_tree = parse(source)
    module_object = compile(ast_tree, '<ast>', 'exec')
    code_object = [c for c in module_object.co_consts if isinstance(c, CodeType)][0]

    # noinspection PyArgumentList
    f = FunctionType(code_object, {})

    return f


#########
# TESTS #
#########

def test_validate_boolean(value, is_valid):

    # noinspection PyBroadException
    try:
        result = validate_boolean(value)
        result_is_valid = True
    except Exception:
        result = None
        result_is_valid = False
        pass

    actual = result_is_valid
    expected = is_valid

    assert actual == expected

    if result is not None:

        actual = isinstance(result, bool)
        expected = True

        assert actual == expected


def test_validate_boundary_condition(value, is_valid):

    # noinspection PyBroadException
    try:
        result = validate_boundary_condition(value)
        result_is_valid = True
    except Exception:
        result = None
        result_is_valid = False
        pass

    actual = result_is_valid
    expected = is_valid

    assert actual == expected

    if result is not None:

        actual = isinstance(result, float) or isinstance(result, int) or isinstance(result, str)
        expected = True

        assert actual == expected


def test_validate_dpi(value, is_valid):

    # noinspection PyBroadException
    try:
        result = validate_dpi(value)
        result_is_valid = True
    except Exception:
        result = None
        result_is_valid = False
        pass

    actual = result_is_valid
    expected = is_valid

    assert actual == expected

    if result is not None:

        actual = isinstance(result, int)
        expected = True

        assert actual == expected


def test_validate_dictionary(dictionary_elements, key_tuple, is_valid):

    d = {}

    for dictionary_element in dictionary_elements:
        if key_tuple:
            d[tuple(dictionary_element[:-1])] = dictionary_element[-1]
        else:
            d[dictionary_element[0]] = dictionary_element[1]

    # noinspection PyBroadException
    try:
        result = validate_dictionary(d)
        result_is_valid = True
    except Exception:
        result = None
        result_is_valid = False
        pass

    actual = result_is_valid
    expected = is_valid

    assert actual == expected

    if result is not None:

        actual = isinstance(result, dict)
        expected = True

        assert actual == expected


def test_validate_enumerator(value, possible_values, is_valid):

    # noinspection PyBroadException
    try:
        result = validate_enumerator(value, possible_values)
        result_is_valid = True
    except Exception:
        result = None
        result_is_valid = False
        pass

    actual = result_is_valid
    expected = is_valid

    assert actual == expected

    if result is not None:

        actual = isinstance(result, str)
        expected = True

        assert actual == expected


def test_validate_float(value, lower_limit, upper_limit, is_valid):

    lower_limit = None if lower_limit is None else tuple(lower_limit)
    upper_limit = None if upper_limit is None else tuple(upper_limit)

    # noinspection PyBroadException
    try:
        result = validate_float(value, lower_limit, upper_limit)
        result_is_valid = True
    except Exception:
        result = None
        result_is_valid = False
        pass

    actual = result_is_valid
    expected = is_valid

    assert actual == expected

    if result is not None:

        actual = isinstance(result, float)
        expected = True

        assert actual == expected


def test_validate_graph(graph_data, is_valid):

    if isinstance(graph_data, list) and all(isinstance(x, list) for x in graph_data):
        g = nx.from_numpy_matrix(np.array(graph_data), create_using=nx.DiGraph()) if len(graph_data) > 0 else nx.DiGraph()
        g = nx.relabel_nodes(g, dict(zip(range(len(g.nodes)), [str(i + 1) for i in range(len(g.nodes))])))
    else:

        g = nx.DiGraph()

        for x in graph_data:
            g.add_node(x)

    # noinspection PyBroadException
    try:
        result = validate_graph(g)
        result_is_valid = True
    except Exception:
        result = None
        result_is_valid = False
        pass

    actual = result_is_valid
    expected = is_valid

    assert actual == expected

    if result is not None:

        actual = isinstance(result, nx.DiGraph)
        expected = True

        assert actual == expected

    if isinstance(graph_data, list) and all(isinstance(x, list) for x in graph_data):
        g = nx.from_numpy_matrix(np.array(graph_data), create_using=nx.DiGraph()) if len(
            graph_data) > 0 else nx.DiGraph()
        g = nx.relabel_nodes(g, dict(zip(range(len(g.nodes)), [str(i + 1) for i in range(len(g.nodes))])))
    else:

        g = nx.DiGraph()

        for x in graph_data:
            g.add_node(x)

    # noinspection PyBroadException
    try:
        result = validate_graph(g)
        result_is_valid = True
    except Exception:
        result = None
        result_is_valid = False
        pass

    actual = result_is_valid
    expected = is_valid

    assert actual == expected

    if result is not None:

        actual = isinstance(result, nx.DiGraph)
        expected = True

        assert actual == expected


def test_validate_integer(value, lower_limit, upper_limit, is_valid):

    lower_limit = None if lower_limit is None else tuple(lower_limit)
    upper_limit = None if upper_limit is None else tuple(upper_limit)

    # noinspection PyBroadException
    try:
        result = validate_integer(value, lower_limit, upper_limit)
        result_is_valid = True
    except Exception:
        result = None
        result_is_valid = False
        pass

    actual = result_is_valid
    expected = is_valid

    assert actual == expected

    if result is not None:

        actual = isinstance(result, int)
        expected = True

        assert actual == expected


def test_validate_hyperparameter(value, size, is_valid):

    # noinspection PyBroadException
    try:
        result = validate_hyperparameter(value, size)
        result_is_valid = True
    except Exception:
        result = None
        result_is_valid = False
        pass

    actual = result_is_valid
    expected = is_valid

    assert actual == expected

    if result is not None:

        actual = isinstance(result, np.ndarray)
        expected = True

        assert actual == expected


def test_validate_interval(value, is_valid):

    value = tuple(value) if isinstance(value, list) else value

    # noinspection PyBroadException
    try:
        result = validate_interval(value)
        result_is_valid = True
    except Exception:
        result = None
        result_is_valid = False
        pass

    actual = result_is_valid
    expected = is_valid

    assert actual == expected

    if result is not None:

        actual = all(isinstance(v, float) for v in result)
        expected = True

        assert actual == expected


def test_validate_state(value, current_states, is_valid):

    # noinspection PyBroadException
    try:
        result = validate_state(value, current_states)
        result_is_valid = True
    except Exception:
        result = None
        result_is_valid = False
        pass

    actual = result_is_valid
    expected = is_valid

    assert actual == expected

    if result is not None:

        actual = isinstance(result, int)
        expected = True

        assert actual == expected

        actual = result
        expected = current_states.index(value) if isinstance(value, str) else current_states.index(current_states[value])

        assert actual == expected


def test_validate_transition_function(value, is_valid):

    if isinstance(value, str):
        if value.startswith('def'):
            value = _string_to_function(value)
        elif value.startswith('lambda'):
            value = eval(value)

    # noinspection PyBroadException
    try:
        result = validate_transition_function(value)
        result_is_valid = True
    except Exception:
        result = None
        result_is_valid = False
        pass

    actual = result_is_valid
    expected = is_valid

    assert actual == expected

    if result is not None:

        actual = callable(result)
        expected = True

        assert actual == expected
