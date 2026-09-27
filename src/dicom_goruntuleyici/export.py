"""PNG export, shared by every CLI subcommand. Uses the non-interactive Agg
backend so it works headless (CI, no display)."""

from __future__ import annotations

import numpy as np


def save_image(path: str, windowed_array: np.ndarray, *, title: str = "") -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    ax.imshow(windowed_array, cmap="gray", vmin=0, vmax=255)
    ax.set_title(title)
    ax.axis("off")
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def save_comparison_grid(path: str, images: dict[str, np.ndarray], *, suptitle: str = "") -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    n = len(images)
    cols = min(n, 4)
    rows = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(4 * cols, 4 * rows))
    axes = np.atleast_1d(axes).ravel()
    for ax, (label, arr) in zip(axes, images.items()):
        ax.imshow(arr, cmap="gray", vmin=0, vmax=255)
        ax.set_title(label)
        ax.axis("off")
    for ax in axes[len(images):]:
        ax.axis("off")
    fig.suptitle(suptitle)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def save_montage(path: str, slices: list[np.ndarray], *, suptitle: str = "") -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    n = len(slices)
    cols = min(n, 6)
    rows = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(2.2 * cols, 2.2 * rows))
    axes = np.atleast_1d(axes).ravel()
    for i, ax in enumerate(axes):
        if i < n:
            ax.imshow(slices[i], cmap="gray", vmin=0, vmax=255)
            ax.set_title(str(i), fontsize=8)
        ax.axis("off")
    fig.suptitle(suptitle)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
