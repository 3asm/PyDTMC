# -*- coding: utf-8 -*-

__all__ = [
    'plot_eigenvalues',
    'plot_graph',
    'plot_redistributions',
    'plot_walk'
]


###########
# IMPORTS #
###########

# Standard

from inspect import (
    trace
)

from io import (
    BytesIO
)

# noinspection PyPep8Naming
from subprocess import (
    call,
    PIPE as pipe
)

# Libraries

import matplotlib.colors as mplc
import matplotlib.image as mpli
import matplotlib.pyplot as mplp
import matplotlib.ticker as mplt
import networkx as nx
import numpy as np
import numpy.linalg as npl

# Internal

from .custom_types import (
    oint,
    oplot,
    ostate,
    ostatus,
    tdists_flex,
    tlist_str,
    tmc,
    twalk_flex
)

from .utilities import (
    generate_validation_error
)

from .validation import (
    validate_boolean,
    validate_distribution,
    validate_dpi,
    validate_enumerator,
    validate_integer,
    validate_markov_chain,
    validate_state,
    validate_states,
    validate_status
)


#############
# CONSTANTS #
#############

_color_black = '#000000'
_color_gray = '#E0E0E0'
_color_white = '#FFFFFF'
_colors = ['#80B1D3', '#FFED6F', '#B3DE69', '#BEBADA', '#FDB462', '#8DD3C7', '#FB8072', '#FCCDE5']


#############
# FUNCTIONS #
#############

def plot_eigenvalues(mc: tmc, dpi: int = 100) -> oplot:

    """
    The function plots the eigenvalues of the Markov chain on the complex plane.

    | **Notes:**

    * If `Matplotlib <https://matplotlib.org/>`_ is in `interactive mode <https://matplotlib.org/stable/users/interactive.html>`_, the plot is immediately displayed and the function does not return the plot handles.

    :param mc: the target Markov chain.
    :param dpi: the resolution of the plot expressed in dots per inch.
    :raises ValidationError: if any input argument is not compliant.
    """

    try:

        mc = validate_markov_chain(mc)
        dpi = validate_dpi(dpi)

    except Exception as e:  # pragma: no cover
        raise generate_validation_error(e, trace()) from None

    figure, ax = mplp.subplots(dpi=dpi)

    handles = []
    labels = []

    theta = np.linspace(0.0, 2.0 * np.pi, 200)

    values = npl.eigvals(mc.p).astype(complex)
    values_final = np.unique(np.append(values, np.array([1.0]).astype(complex)))

    x_unit_circle = np.cos(theta)
    y_unit_circle = np.sin(theta)

    if mc.is_ergodic:

        values_abs = np.sort(np.abs(values))
        values_ct1 = np.isclose(values_abs, 1.0)

        if not np.all(values_ct1):

            mu = values_abs[~values_ct1][-1]

            if not np.isclose(mu, 0.0):

                x_slem_circle = mu * x_unit_circle
                y_slem_circle = mu * y_unit_circle

                cs = np.linspace(-1.1, 1.1, 201)
                x_spectral_gap, y_spectral_gap = np.meshgrid(cs, cs)
                z_spectral_gap = x_spectral_gap**2.0 + y_spectral_gap**2.0

                h = ax.contourf(x_spectral_gap, y_spectral_gap, z_spectral_gap, alpha=0.2, colors='r', levels=[mu**2.0, 1.0])
                handles.append(mplp.Rectangle((0.0, 0.0), 1.0, 1.0, fc=h.collections[0].get_facecolor()[0]))
                labels.append('Spectral Gap')

                ax.plot(x_slem_circle, y_slem_circle, color='red', linestyle='--', linewidth=1.5)

    ax.plot(x_unit_circle, y_unit_circle, color='red', linestyle='-', linewidth=3.0)

    h, = ax.plot(np.real(values_final), np.imag(values_final), color='blue', linestyle='None', marker='*', markersize=12.5)
    handles.append(h)
    labels.append('Eigenvalues')

    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-1.1, 1.1)
    ax.set_aspect('equal')

    formatter = mplt.FormatStrFormatter('%g')
    ax.xaxis.set_major_formatter(formatter)
    ax.yaxis.set_major_formatter(formatter)
    ax.set_xticks(np.linspace(-1.0, 1.0, 9))
    ax.set_yticks(np.linspace(-1.0, 1.0, 9))
    ax.grid(which='major')

    ax.legend(handles[::-1], labels[::-1], bbox_to_anchor=(0.5, -0.1), loc='upper center', ncol=len(handles))
    ax.set_title('Eigenplot', fontsize=15.0, fontweight='bold')

    mplp.subplots_adjust(bottom=0.2)

    if mplp.isinteractive():  # pragma: no cover
        mplp.show(block=False)
        return None

    return figure, ax


def plot_graph(mc: tmc, nodes_color: bool = True, nodes_type: bool = True, edges_color: bool = True, edges_value: bool = True, force_standard: bool = False, dpi: int = 100) -> oplot:

    """
    The function plots the directed graph of the Markov chain.

    | **Notes:**

    * If `Matplotlib <https://matplotlib.org/>`_ is in `interactive mode <https://matplotlib.org/stable/users/interactive.html>`_, the plot is immediately displayed and the function does not return the plot handles.
    * `Graphviz <https://graphviz.org/>`_ and `pydot <https://pypi.org/project/pydot/>`_ are not required, but they provide access to extended graphs with additional features.

    :param mc: the target Markov chain.
    :param nodes_color: a boolean indicating whether to display colored nodes based on communicating classes.
    :param nodes_type: a boolean indicating whether to use a different shape for every node type.
    :param edges_color: a boolean indicating whether to display edges using a gradient based on transition probabilities, valid only for extended graphs.
    :param edges_value: a boolean indicating whether to display the transition probability of every edge.
    :param force_standard: a boolean indicating whether to use a standard graph even if extended graphs are available.
    :param dpi: the resolution of the plot expressed in dots per inch.
    :raises ValidationError: if any input argument is not compliant.
    """

    def edge_colors(hex_from: str, hex_to: str, steps: int) -> tlist_str:

        begin = [int(hex_from[i:i + 2], 16) for i in range(1, 6, 2)]
        end = [int(hex_to[i:i + 2], 16) for i in range(1, 6, 2)]

        clist = [hex_from]

        for s in range(1, steps):
            vector = [int(begin[j] + (float(s) / (steps - 1)) * (end[j] - begin[j])) for j in range(3)]
            rgb = [int(v) for v in vector]
            clist.append(f'#{"".join(["0{0:x}".format(v) if v < 16 else "{0:x}".format(v) for v in rgb])}')

        return clist

    def node_colors(count: int) -> tlist_str:

        colors_limit = len(_colors) - 1
        offset = 0

        clist = []

        while count > 0:

            clist.append(_colors[offset])
            offset += 1

            if offset > colors_limit:  # pragma: no cover
                offset = 0

            count -= 1

        return clist

    try:

        mc = validate_markov_chain(mc)
        nodes_color = validate_boolean(nodes_color)
        nodes_type = validate_boolean(nodes_type)
        edges_color = validate_boolean(edges_color)
        edges_value = validate_boolean(edges_value)
        force_standard = validate_boolean(force_standard)
        dpi = validate_dpi(dpi)

    except Exception as e:  # pragma: no cover
        raise generate_validation_error(e, trace()) from None

    if force_standard:
        extended_graph = False
    else:

        extended_graph = True

        # noinspection PyBroadException
        try:
            call(['dot', '-V'], stdout=pipe, stderr=pipe)
        except Exception:  # pragma: no cover
            extended_graph = False

        try:
            import pydot  # noqa
        except ImportError:  # pragma: no cover
            extended_graph = False

    g = mc.to_graph()

    if extended_graph:

        g_pydot = nx.nx_pydot.to_pydot(g)

        if nodes_color:
            c = node_colors(len(mc.communicating_classes))
            for node in g_pydot.get_nodes():
                state = node.get_name()
                for index, cc in enumerate(mc.communicating_classes):
                    if state in cc:
                        node.set_style('filled')
                        node.set_fillcolor(c[index])
                        break

        if nodes_type:
            for node in g_pydot.get_nodes():
                if node.get_name() in mc.transient_states:
                    node.set_shape('box')
                else:
                    node.set_shape('ellipse')

        if edges_color:
            c = edge_colors(_color_gray, _color_black, 20)
            for edge in g_pydot.get_edges():
                probability = mc.transition_probability(edge.get_destination(), edge.get_source())
                x = int(round(probability * 20.0)) - 1
                edge.set_style('filled')
                edge.set_color(c[x])

        if edges_value:
            for edge in g_pydot.get_edges():
                probability = mc.transition_probability(edge.get_destination(), edge.get_source())
                edge.set_label(f' {round(probability,2):g} ')

        buffer = BytesIO()
        buffer.write(g_pydot.create_png())
        buffer.seek(0)

        img = mpli.imread(buffer)
        img_x = img.shape[0] / dpi
        img_xi = img_x * 1.1
        img_xo = ((img_xi - img_x) / 2.0) * dpi
        img_y = img.shape[1] / dpi
        img_yi = img_y * 1.1
        img_yo = ((img_yi - img_y) / 2.0) * dpi

        figure = mplp.figure(figsize=(img_y * 1.1, img_x * 1.1), dpi=dpi)
        figure.figimage(img, yo=img_yo, xo=img_xo)
        ax = figure.gca()
        ax.axis('off')

    else:

        mpi = mplp.isinteractive()
        mplp.interactive(False)

        figure, ax = mplp.subplots(dpi=dpi)

        positions = nx.spring_layout(g)
        node_colors_all = node_colors(len(mc.communicating_classes))

        for node in g.nodes:

            node_color = None

            if nodes_color:
                for index, cc in enumerate(mc.communicating_classes):
                    if node in cc:
                        node_color = node_colors_all[index]
                        break

            if nodes_type:
                if node in mc.transient_states:
                    node_shape = 's'
                else:
                    node_shape = 'o'
            else:
                node_shape = None

            if node_color is not None and node_shape is not None:
                nx.draw_networkx_nodes(g, positions, ax=ax, nodelist=[node], edgecolors='k', node_color=node_color, node_shape=node_shape)
            elif node_color is not None and node_shape is None:
                nx.draw_networkx_nodes(g, positions, ax=ax, nodelist=[node], edgecolors='k', node_color=node_color)
            elif node_color is None and node_shape is not None:
                nx.draw_networkx_nodes(g, positions, ax=ax, nodelist=[node], edgecolors='k', node_shape=node_shape)
            else:
                nx.draw_networkx_nodes(g, positions, ax=ax, edgecolors='k')

        nx.draw_networkx_labels(g, positions, ax=ax)

        nx.draw_networkx_edges(g, positions, ax=ax, arrows=False)

        if edges_value:

            edges_values = {}

            for edge in g.edges:
                probability = mc.transition_probability(edge[1], edge[0])
                edges_values[(edge[0], edge[1])] = f' {round(probability,2):g} '

            nx.draw_networkx_edge_labels(g, positions, ax=ax, edge_labels=edges_values, label_pos=0.7)

        mplp.interactive(mpi)

    if mplp.isinteractive():  # pragma: no cover
        mplp.show(block=False)
        return None

    return figure, ax


def plot_redistributions(mc: tmc, distributions: tdists_flex, initial_status: ostatus = None, plot_type: str = 'projection', dpi: int = 100) -> oplot:

    """
    The function plots a redistribution of states on the given Markov chain.

    | **Notes:**

    * If `Matplotlib <https://matplotlib.org/>`_ is in `interactive mode <https://matplotlib.org/stable/users/interactive.html>`_, the plot is immediately displayed and the function does not return the plot handles.

    :param mc: the target Markov chain.
    :param distributions: a sequence of redistributions or the number of redistributions to perform.
    :param initial_status: the initial state or the initial distribution of the states (*if omitted, the states are assumed to be uniformly distributed*).
    :param plot_type:
     - **heatmap** for displaying an heatmap plot;
     - **projection** for displaying a projection plot.
    :param dpi: the resolution of the plot expressed in dots per inch.
    :raises ValueError: if the "distributions" parameter represents a sequence of redistributions and the "initial_status" parameter does not match its first element.
    :raises ValidationError: if any input argument is not compliant.
    """

    try:

        mc = validate_markov_chain(mc)
        distributions = validate_distribution(distributions, mc.size)
        initial_status = None if initial_status is None else validate_status(initial_status, mc.states)
        plot_type = validate_enumerator(plot_type, ['heatmap', 'projection'])
        dpi = validate_dpi(dpi)

    except Exception as e:  # pragma: no cover
        raise generate_validation_error(e, trace()) from None

    if isinstance(distributions, int):
        distributions = mc.redistribute(distributions, initial_status=initial_status, output_last=False)

    if initial_status is not None and not np.array_equal(distributions[0], initial_status):  # pragma: no cover
        raise ValueError('The "initial_status" parameter, if specified when the "distributions" parameter represents a sequence of redistributions, must match the first element.')

    distributions_len = 1 if isinstance(distributions, np.ndarray) else len(distributions)
    distributions = np.array([distributions]) if isinstance(distributions, np.ndarray) else np.array(distributions)

    figure, ax = mplp.subplots(dpi=dpi)

    if plot_type == 'heatmap':

        color_map = mplc.LinearSegmentedColormap.from_list('ColorMap', [_color_white, _colors[0]], 20)
        ax_is = ax.imshow(np.transpose(distributions), aspect='auto', cmap=color_map, interpolation='none', vmin=0.0, vmax=1.0)

        ax.set_xlabel('Steps', fontsize=13.0)
        ax.set_xticks(np.arange(0.0, distributions_len + 1.0, 1.0 if distributions_len <= 11 else 10.0), minor=False)
        ax.set_xticks(np.arange(-0.5, distributions_len, 1.0), minor=True)
        ax.set_xticklabels(np.arange(0, distributions_len + 1, 1 if distributions_len <= 11 else 10))
        ax.set_xlim(-0.5, distributions_len - 0.5)

        ax.set_yticks(np.arange(0.0, mc.size, 1.0), minor=False)
        ax.set_yticks(np.arange(-0.5, mc.size, 1.0), minor=True)
        ax.set_yticklabels(mc.states)

        ax.grid(which='minor', color='k')

        cb = figure.colorbar(ax_is, drawedges=True, orientation='horizontal', ticks=[0.0, 0.25, 0.5, 0.75, 1.0])
        cb.ax.set_xticklabels([0.0, 0.25, 0.5, 0.75, 1.0])

        ax.set_title('Redistplot (Heatmap)', fontsize=15.0, fontweight='bold')

    else:

        ax.set_prop_cycle('color', _colors)

        if distributions_len == 2:
            for i in range(mc.size):
                ax.plot(np.arange(0.0, distributions_len, 1.0), distributions[:, i], label=mc.states[i], marker='o')
        else:
            for i in range(mc.size):
                ax.plot(np.arange(0.0, distributions_len, 1.0), distributions[:, i], label=mc.states[i])

        if np.allclose(distributions[0, :], np.ones(mc.size, dtype=float) / mc.size):
            ax.plot(0.0, distributions[0, 0], color=_color_black, label="Start", marker='o', markeredgecolor=_color_black, markerfacecolor=_color_black)
            legend_size = mc.size + 1
        else:  # pragma: no cover
            legend_size = mc.size

        ax.set_xlabel('Steps', fontsize=13.0)
        ax.set_xticks(np.arange(0.0, distributions_len + 1.0, 1.0 if distributions_len <= 11 else 10.0), minor=False)
        ax.set_xticks(np.arange(-0.5, distributions_len, 1.0), minor=True)
        ax.set_xticklabels(np.arange(0, distributions_len + 1, 1 if distributions_len <= 11 else 10))
        ax.set_xlim(-0.5, distributions_len - 0.5)

        ax.set_ylabel('Frequencies', fontsize=13.0)
        ax.set_yticks(np.linspace(0.0, 1.0, 11))
        ax.set_ylim(-0.05, 1.05)

        ax.grid()
        ax.legend(bbox_to_anchor=(0.5, -0.15), loc='upper center', ncol=legend_size)
        ax.set_title('Redistplot (Projection)', fontsize=15.0, fontweight='bold')

        mplp.subplots_adjust(bottom=0.2)

    if mplp.isinteractive():  # pragma: no cover
        mplp.show(block=False)
        return None

    return figure, ax


def plot_walk(mc: tmc, walk: twalk_flex, initial_state: ostate = None, plot_type: str = 'histogram', seed: oint = None, dpi: int = 100) -> oplot:

    """
    The function plots a random walk on the given Markov chain.

    | **Notes:**

    * If `Matplotlib <https://matplotlib.org/>`_ is in `interactive mode <https://matplotlib.org/stable/users/interactive.html>`_, the plot is immediately displayed and the function does not return the plot handles.

    :param mc: the target Markov chain.
    :param walk: a sequence of states or the number of simulations to perform.
    :param initial_state: the initial state of the walk (*if omitted, it is chosen uniformly at random*).
    :param plot_type:
     - **histogram** for displaying an histogram plot;
     - **sequence** for displaying a sequence plot;
     - **transitions** for displaying a transitions plot.
    :param seed: a seed to be used as RNG initializer for reproducibility purposes.
    :param dpi: the resolution of the plot expressed in dots per inch.
    :raises ValueError: if the "walk" parameter represents a sequence of states and the "initial_state" parameter does not match its first element.
    :raises ValidationError: if any input argument is not compliant.
    """

    try:

        mc = validate_markov_chain(mc)

        if isinstance(walk, (int, np.integer)):
            walk = validate_integer(walk, lower_limit=(1, False))
        else:
            walk = validate_states(walk, mc.states, 'walk', False)

        if initial_state is not None:
            initial_state = validate_state(initial_state, mc.states)

        plot_type = validate_enumerator(plot_type, ['histogram', 'sequence', 'transitions'])
        dpi = validate_dpi(dpi)

    except Exception as e:  # pragma: no cover
        raise generate_validation_error(e, trace()) from None

    if isinstance(walk, int):
        walk = mc.walk(walk, initial_state=initial_state, output_indices=True, seed=seed)

    if initial_state is not None and (walk[0] != initial_state):  # pragma: no cover
        raise ValueError('The "initial_state" parameter, if specified when the "walk" parameter represents a sequence of states, must match the first element.')

    walk_len = len(walk)

    figure, ax = mplp.subplots(dpi=dpi)

    if plot_type == 'histogram':

        walk_histogram = np.zeros((mc.size, walk_len), dtype=float)

        for index, state in enumerate(walk):
            walk_histogram[state, index] = 1.0

        walk_histogram = np.sum(walk_histogram, axis=1) / np.sum(walk_histogram)

        ax.bar(np.arange(0.0, mc.size, 1.0), walk_histogram, edgecolor=_color_black, facecolor=_colors[0])

        ax.set_xlabel('States', fontsize=13.0)
        ax.set_xticks(np.arange(0.0, mc.size, 1.0))
        ax.set_xticklabels(mc.states)

        ax.set_ylabel('Frequencies', fontsize=13.0)
        ax.set_yticks(np.linspace(0.0, 1.0, 11))
        ax.set_ylim(0.0, 1.0)

        ax.set_title('Walkplot (Histogram)', fontsize=15.0, fontweight='bold')

    elif plot_type == 'sequence':

        walk_sequence = np.zeros((mc.size, walk_len), dtype=float)

        for index, state in enumerate(walk):
            walk_sequence[state, index] = 1.0

        color_map = mplc.LinearSegmentedColormap.from_list('ColorMap', [_color_white, _colors[0]], 2)
        ax.imshow(walk_sequence, aspect='auto', cmap=color_map, interpolation='none', vmin=0.0, vmax=1.0)

        ax.set_xlabel('Steps', fontsize=13.0)
        ax.set_xticks(np.arange(0.0, walk_len + 1.0, 1.0 if walk_len <= 11 else 10.0), minor=False)
        ax.set_xticks(np.arange(-0.5, walk_len, 1.0), minor=True)
        ax.set_xticklabels(np.arange(0, walk_len + 1, 1 if walk_len <= 11 else 10))
        ax.set_xlim(-0.5, walk_len - 0.5)

        ax.set_ylabel('States', fontsize=13.0)
        ax.set_yticks(np.arange(0.0, mc.size, 1.0), minor=False)
        ax.set_yticks(np.arange(-0.5, mc.size, 1.0), minor=True)
        ax.set_yticklabels(mc.states)

        ax.grid(which='minor', color='k')

        ax.set_title('Walkplot (Sequence)', fontsize=15.0, fontweight='bold')

    else:

        walk_transitions = np.zeros((mc.size, mc.size), dtype=float)

        for i in range(1, walk_len):
            walk_transitions[walk[i - 1], walk[i]] += 1.0

        walk_transitions /= np.sum(walk_transitions)

        color_map = mplc.LinearSegmentedColormap.from_list('ColorMap', [_color_white, _colors[0]], 20)
        ax_is = ax.imshow(walk_transitions, aspect='auto', cmap=color_map, interpolation='none', vmin=0.0, vmax=1.0)

        ax.set_xticks(np.arange(0.0, mc.size, 1.0), minor=False)
        ax.set_xticks(np.arange(-0.5, mc.size, 1.0), minor=True)
        ax.set_xticklabels(mc.states)

        ax.set_yticks(np.arange(0.0, mc.size, 1.0), minor=False)
        ax.set_yticks(np.arange(-0.5, mc.size, 1.0), minor=True)
        ax.set_yticklabels(mc.states)

        ax.grid(which='minor', color='k')

        cb = figure.colorbar(ax_is, drawedges=True, orientation='horizontal', ticks=[0.0, 0.25, 0.5, 0.75, 1.0])
        cb.ax.set_xticklabels([0.0, 0.25, 0.5, 0.75, 1.0])

        ax.set_title('Walkplot (Transitions)', fontsize=15.0, fontweight='bold')

    if mplp.isinteractive():  # pragma: no cover
        mplp.show(block=False)
        return None

    return figure, ax
