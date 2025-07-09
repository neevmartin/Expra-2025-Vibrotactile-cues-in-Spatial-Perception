# Standard
from typing import (
    Literal, 
    Tuple, 
    List
)
from os.path import sep as OS_SEPARATOR

# Third party
import matplotlib.pyplot as plt 
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.container import ErrorbarContainer
import pandas as pd
import numpy as np

# Intern
from plotting.preprocessor import generate_prepost_comparison
from helpers import Condition
from helpers import Trial
from helpers.validation import validate_oneof
from helpers.metadata import (
    PERCENT_INTENSITIES, PIXEL_DISTANCES, 
    PIXEL_RAIL_BOTTOM, 
    PIXEL_RAIL_TOP
)

# Constants
_PLOT_CONFIG = {
    'errorbar_offset': 1.5,
    'y_padding': {'predictions': 50, 'prepost_comparison': 0, 'regress_prediction': 100},
    'colors': {'pre': 'g', 'post': 'b', 'true': 'darkorange'},
    'font_sizes': {'tick': 7, 'label': 8, 'title': 10}
}

INTENSITIES = np.array(PERCENT_INTENSITIES)
DISTANCES = np.array(PIXEL_DISTANCES)


def plot_predictions(
        intensities: List[float], 
        distances: List[float]
    ) -> Tuple[Figure, Axes]:
    """
    Plots participant prediction (intensity to distance) data points as a scatter plot.

    Each point represents either the last recorded position (reaching)
    or the first threshold-exceeding point (avoiding), depending on the task.

    Args:
        intensities (List[float]): Intensity values (% scale).
        distances (List[float]): Predicted distances (pixel values).

    Returns:
        Tuple[Figure, Axes]: The matplotlib figure and axes containing the plot.
                             NOTE: You can change the design to your liking with these.
    """
    # Config
    fig, ax = _setup_plot()
    _configure_tablet_axes(ax, INTENSITIES, DISTANCES, padding=_PLOT_CONFIG['y_padding']['predictions'])

    # Plot
    ax.scatter(intensities, distances, s=10, alpha=0.3)

    # Styling
    fig.tight_layout()
    
    return fig, ax

def plot_individual_prepost_comparisons(
        participants: Condition, 
        pre_allowed_states: dict, 
        post_allowed_states: dict, 
        mapping: Literal['direct', 'reversed', None], 
        title: str = ''
    ) -> Tuple[Figure, Axes]:
    """
    Plots individual pre- and post-condition comparisons for each participant in a grid of subplots.

    Each subplot corresponds to a single participant and shows the prepost-plot you all know about. 
    The layout is automatically determined based on the number of participants, arranged in a 3-column grid. 
    A shared title is added to the figure, and the last subplot retains the legend for reference.

    Args:
        participants (Condition): Condition object that provides access to participant data and metadata like (rd) in the notebook.
                                  This can be loaded with `Condition.load_conditional_group(path, condition)`.
        pre_allowed_states (list): A list of states to be included in the pre condition analysis.
        post_allowed_states (list): A list of states to be included in the post condition analysis.
        mapping (Literal['direct', 'reversed', None]): A mapping used for plotting i.e. 'direct', 'reversed' or None.
        title (str, optional): The title for the entire figure. Default is no title.

    Returns:
        Tuple[Figure, Axes]: The matplotlib figure and axes containing the plot.
                             NOTE: You can change the design to your liking with these.

    Notes:
        - Legends are only shown on the last subplot for visual clarity.
        - X and Y axis labels are selectively hidden to avoid clutter.
        - If the number of participants is not a multiple of 3, empty subplots are created but left blank.

    Example:
        plot_individual_prepost_comparisons(
            participants=rd, 
            allowed_states={'tasks': ['reaching'], 'mappings': ['direct']}, 
            mapping='direct', 
            title='Reaching Direct Distance Predictions per Participant'
        )
    """
    n_participants = participants.get_participant_count()
    ncols = 3
    nrows = int(np.ceil(n_participants / ncols))
    n_subfigs = nrows * ncols
    
    fig, axs = plt.subplots(nrows=nrows, ncols=ncols, figsize=(14, 14))
    
    for i in range(n_subfigs):
        # Collect participant
        is_participant = i < n_participants
        participant_wrapper = [participants.get_participant_by_index(i)] if is_participant else [] # empty if all participants plotted
        if is_participant: participant = participant_wrapper[0]

        # Compute statistics per participant
        pre_data_meanstds, post_data_meanstds = generate_prepost_comparison(
            participant_wrapper, 
            pre_allowed_states, 
            post_allowed_states
        )

        # Plot plot into axis
        x, y = i % 3, i // 3
        cur_ax = axs[y, x]
        _, participant_ax = plot_prepost_comparison(
            pre_data_meanstds, 
            post_data_meanstds, 
            mapping if is_participant else None, 
            (fig, cur_ax)
        )

        # Add legend to last subfig
        last_subfig = n_subfigs - 1
        if i < last_subfig: participant_ax.legend().remove()
        # Remove unecessary axis labels
        if x > 0: 
            participant_ax.set_ylabel('')
            participant_ax.set_yticklabels([])

        last_row = nrows - 1
        if y < last_row: 
            participant_ax.set_xlabel('')
            participant_ax.set_xticklabels([])

        # Add participant title
        if is_participant:
            try:
                participant_id = participant.get_participant_id().split(OS_SEPARATOR)[-1] # get_participant_id gets the directory as well
                participant_ax.set_title(participant_id)
            except IndexError as e:
                print(f'Invalid participant id. Exception was: {e.with_traceback()}')
        else:
            participant_ax.set_title('')
    
    fig.suptitle(title, fontsize=20, y=1)
    plt.tight_layout()

    return fig, axs

def plot_prepost_comparison(
        pre_data: dict | pd.DataFrame, 
        post_data: dict | pd.DataFrame, 
        mapping: Literal['direct', 'reversed', None],
        figax: Tuple[Figure, Axes] = []
    ) -> Tuple[Figure, Axes]:
    """
    Plots a comparison of pre- and post-test predicted distances with true distances.

    Displays error bars for means and standard deviations across intensity levels,
    and overlays the true distances based on the given mapping.

    Args:
        pre_data (dict): Dictionary with 'means' and 'stds' from the pre-test condition.
        post_data (dict): Dictionary with 'means' and 'stds' from the post-test condition.
        mapping (Literal['direct', 'reversed']): The mapping type to determine true distances.

    Returns:
        Tuple[Figure, Axes]: The matplotlib figure and axes containing the plot.
                             NOTE: You can change the design to your liking with these.
    """
    # Config
    config = _PLOT_CONFIG
    if len(figax) == 0:
        fig, ax = _setup_plot()
    else:
        fig, ax = figax
    
    _configure_tablet_axes(ax, INTENSITIES, DISTANCES, 
                           padding=_PLOT_CONFIG['y_padding']['prepost_comparison'])
    
    # Plots
    _plot_errorbars(ax, INTENSITIES, pre_data['means'], pre_data['stds'], 
                   -config['errorbar_offset'], config['colors']['pre'], 'Pre-Test')
    _plot_errorbars(ax, INTENSITIES, post_data['means'], post_data['stds'], 
                   config['errorbar_offset'], config['colors']['post'], 'Post-Test')
    _plot_true_distances(ax, mapping)
    
    # Styling
    ax.grid(True, axis='y', linestyle=':', alpha=0.7)
    ax.set_title('Mean ± SD of Predicted Distance by Intensity', 
                fontsize=config['font_sizes']['title'], pad=10)
    ax.legend(loc='best', fontsize=7)
    fig.tight_layout()

    return fig, ax

def plot_poly_regress_prediction(
        intensities: List[float], 
        distances: List[float], 
        order: int
    ) -> Tuple[Figure, Axes]:
    """
    Plots a polynomial regression fit over predicted distances compared to the true mapping.

    Fits a polynomial of given order to the input intensities/distances and overlays the true linear mapping.

    Args:
        intensities (list): Played intensity values.
        distances (list): Predicted distance values corresponding to intensities.
        order (int): Order of the polynomial to fit.

    Returns:
        Tuple[Figure, Axes]: The matplotlib figure and axes containing the plot.
                             NOTE: You can change the design to your liking with these.
    """
    # Fitting
    predict_coeffs             = np.polyfit(intensities, distances, order)
    true_slope, true_intercept = np.polyfit(INTENSITIES, DISTANCES, 1)

    intensities = np.linspace(INTENSITIES.min(), INTENSITIES.max(), num=100)
    y_predict = np.poly1d(predict_coeffs)
    y_true = true_slope * intensities + true_intercept

    # Config
    fig, ax = _setup_plot()
    _configure_tablet_axes(ax, INTENSITIES, DISTANCES, 
                           padding=_PLOT_CONFIG['y_padding']['regress_prediction'])
    
    # Plots
    ax.plot(intensities, y_predict(intensities), label='Predicted Mapping')
    ax.plot(intensities, y_true, label='True Mapping')

    # Styling
    ax.set_xlabel('Intensity')
    ax.set_ylabel('Predicted Distance')
    ax.set_title('Polynomial Regression Findings of Predicted Mapping')
    ax.legend(loc='upper left')
    fig.tight_layout()
    
    return fig, ax

### Private plot macros

def _setup_plot() -> Tuple[Figure, Axes]:
    """
    Initializes a standardized plot layout with a hidden top twin axis.

    Returns:
        Tuple[Figure, Axes]: The main figure and axes object for further plotting.
    """
    fig, ax = plt.subplots(figsize=(5, 3.5), dpi=300)

    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)

    return fig, ax

def _configure_tablet_axes(
        ax: Axes, 
        intensities: List | np.ndarray, 
        distances, 
        padding : float = 0.
    ) -> None:
    """
    Configures axis limits, ticks, and labels for tablet plots based on intensity and distance ranges.

    Args:
        ax (Axes): Matplotlib axes to configure.
        intensities: List of intensity values to use as x-ticks.
        distances: List of predicted distances to mark on the y-axis.
        padding (float, optional): Extra vertical padding added to the top and bottom of the rail area.
    """
    if len(intensities) == 0 or len(distances) == 0:
        raise ValueError("There are no ")
    ax.set_xlim(min(intensities)-5, max(intensities)+5) # NOTE: hard coded x-padding
    ax.set_ylim(PIXEL_RAIL_BOTTOM-padding, PIXEL_RAIL_TOP+padding)
    ax.set_xticks(intensities)
    ax.set_yticks([PIXEL_RAIL_BOTTOM, *distances, PIXEL_RAIL_TOP])
    ax.set_yticklabels(['Rail Bot', *[f"{d:.1f}" for d in distances], 'Rail Top'])
    ax.tick_params(axis='y', length=0)
    ax.set_xlabel('Intensity (%)', fontsize=_PLOT_CONFIG['font_sizes']['label'])
    ax.set_ylabel('Predicted Distance (Pixels)', fontsize=_PLOT_CONFIG['font_sizes']['label'])

def _plot_errorbars(
        ax: Axes, 
        intensity: float, 
        means: List[float], 
        stds: List[float], 
        offset: float, 
        color: str, 
        label: str
    ) -> ErrorbarContainer:
    """
    Plots a vertical errorbar series at an offset x-position.

    Args:
        ax (Axes): Matplotlib axes on which to draw.
        intensity (float): Intensity class the error bar belongs to.
        means (List[float]): Mean values to plot as y-points.
        stds (List[float]): Standard deviations corresponding to each mean.
        offset (float): Horizontal offset applied to intensity for visual separation in comparison.
        color (str): Color of the data markers.
        label (str): Label used in the legend.

    Returns:
        ErrorbarContainer: Matplotlib container object for the plotted error bars.
    """
    eb = ax.errorbar(
        intensity + offset, means, yerr=stds, fmt='o', color=color,
        ecolor='gray', elinewidth=1.2, capsize=4, label=label, zorder=3
    )
    eb[0].set_alpha(0.5)
    return eb

def _plot_true_distances(
        ax: Axes, 
        mapping: Literal['direct', 'reversed', None]
    ) -> None:
    """
    Plots the true intensity-to-distance mapping as scatter points.

    Args:
        ax (Axes): Matplotlib axes on which to plot.
        mapping (Literal['direct', 'reversed', None]): Either 'direct' or 'reversed', determining the y-value order.
                                                       If None is given no distances will be plotted.

    Raises:
        ValueError: If the mapping is not 'direct', 'reversed' or None.
    """
    if mapping == None: return
    validate_oneof(mapping, ['direct', 'reversed'], 'mapping')

    x = INTENSITIES
    y = DISTANCES if mapping == 'direct' else DISTANCES[::-1]

    ax.scatter(x, y, c='darkorange', s=30, label='True Distance', zorder=4, alpha=0.5)