from typing import Literal
import matplotlib.pyplot as plt 
import pandas as pd
import numpy as np
from helpers import Trial

from helpers.metadata import PERCENT_INTENSITIES, PIXEL_DISTANCES, PIXEL_RAIL_BOTTOM, PIXEL_RAIL_TOP

PLOT_CONFIG = {
    'errorbar_offset': 1.5,
    'y_padding': 0,
    'colors': {'pre': 'g', 'post': 'b', 'true': 'darkorange'},
    'font_sizes': {'tick': 7, 'label': 8, 'title': 10}
}

INTENSITIES = np.array(PERCENT_INTENSITIES)
DISTANCES = np.array(PIXEL_DISTANCES)


def plot_predictions(intensities, distances):
    """
    Data should be last recorded data point in case of reaching 
    or threshold intersection in case of avoiding.
    """
    # Config
    Y_PADDING = 50
    fig, ax = _setup_plot()
    _configure_tablet_axes(ax, INTENSITIES, DISTANCES, padding=Y_PADDING)

    # Plot
    ax.scatter(intensities, distances, s=10, alpha=0.3)

    # Styling
    fig.tight_layout()
    
    plt.show()

def plot_prepost_comparison(pre_data, post_data, mapping: Literal['direct', 'inverse']):
    """Plot comparison of pre/post-test data with true distances."""
    # Config
    config = PLOT_CONFIG
    fig, ax = _setup_plot()
    _configure_tablet_axes(ax, INTENSITIES, DISTANCES)
    
    # Plots
    _plot_errorbars(ax, INTENSITIES, pre_data['means'], pre_data['stds'], 
                   -config['errorbar_offset'], config['colors']['pre'], 'Pre-Test')
    _plot_errorbars(ax, INTENSITIES, post_data['means'], post_data['stds'], 
                   config['errorbar_offset'], config['colors']['post'], 'Post-Test')
    _plot_true_distances(ax, INTENSITIES, DISTANCES, mapping)
    
    # Styling
    ax.grid(True, axis='y', linestyle=':', alpha=0.7)
    ax.set_title('Mean ± SD of Predicted Distance by Intensity', 
                fontsize=config['font_sizes']['title'], pad=10)
    ax.legend(loc='best', fontsize=7)
    fig.tight_layout()

    plt.show()

def plot_poly_regress_prediction(intensities, distances, order):
    # Fitting
    predict_coeffs             = np.polyfit(intensities, distances, order)
    true_slope, true_intercept = np.polyfit(INTENSITIES, DISTANCES, 1)

    x = np.linspace(INTENSITIES.min(), INTENSITIES.max(), num=100)
    y1 = np.poly1d(predict_coeffs)
    y2 = true_slope * x + true_intercept

    # Config
    Y_PADDING = 300
    fig, ax = plt.subplots()
    _configure_tablet_axes(ax, INTENSITIES, DISTANCES, padding=Y_PADDING)
    
    # Plots
    ax.plot(x, y1(x), label='Predicted Mapping')
    ax.plot(x, y2, label='True Mapping')

    # Styling
    ax.set_xlabel('Intensity')
    ax.set_ylabel('Predicted Distance')
    ax.set_title('Linear Regression Findings of Predicted Mapping')
    ax.legend(loc='upper left')
    fig.tight_layout()
    
    plt.show()

def _setup_plot():
    fig, ax = plt.subplots(figsize=(5, 3.5), dpi=300)
    rail_top_ax = ax.twiny()
    rail_top_ax.set_xticks([])
    for spine in [ax.spines, rail_top_ax.spines]:
        spine['left'].set_visible(False)
        spine['right'].set_visible(False)
    return fig, ax

def _configure_tablet_axes(ax, intensities, distances, padding=0):
    ax.set_xlim(intensities.min()-5, intensities.max()+5)
    ax.set_ylim(PIXEL_RAIL_BOTTOM-padding, PIXEL_RAIL_TOP+padding)
    ax.set_xticks(intensities)
    ax.set_yticks([PIXEL_RAIL_BOTTOM, *distances, PIXEL_RAIL_TOP])
    ax.set_yticklabels(['Rail Bot', *[f"{d:.1f}" for d in distances], 'Rail Top'])
    ax.set_xlabel('Intensity (%)', fontsize=PLOT_CONFIG['font_sizes']['label'])
    ax.set_ylabel('Predicted Distance (Pixels)', fontsize=PLOT_CONFIG['font_sizes']['label'])

def _plot_errorbars(ax, x, means, stds, offset, color, label):
    eb = ax.errorbar(
        x + offset, means, yerr=stds, fmt='o', color=color,
        ecolor='gray', elinewidth=1.2, capsize=4, label=label, zorder=3
    )
    eb[0].set_alpha(0.5)
    return eb

def _plot_true_distances(ax, intensities, distances, mapping):
    if mapping == 'direct':
        ax.scatter(intensities, distances, c='darkorange', s=30, label='True Distance', zorder=4, alpha=0.5)
    elif mapping == 'inverse':
        ax.scatter(intensities, distances[::-1], c='darkorange', s=30, label='True Distance', zorder=4, alpha=0.5)
    else:
        raise ValueError(f'Mapping {mapping} does not exist.')