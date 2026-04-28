#!/usr/bin/env python3
"""PyTorch implementation of the full UA-MSTCN smoke backbone.

The existing ``ua_mstcn.py`` module intentionally remains the lightweight
quantile-forest surrogate used in the submitted revision. This module is a
separate deep temporal backbone for the post-QLR Full UA-MSTCN ladder.
"""

from __future__ import annotations

import torch
from torch import nn
from torch.nn import functional as F


class CausalConv1d(nn.Module):
    """One-dimensional convolution with left-only temporal padding."""

    def __init__(self, in_channels: int, out_channels: int, kernel_size: int, dilation: int = 1) -> None:
        super().__init__()
        self.left_padding = (kernel_size - 1) * dilation
        self.conv = nn.Conv1d(
            in_channels,
            out_channels,
            kernel_size=kernel_size,
            dilation=dilation,
            padding=0,
        )

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        padded = F.pad(inputs, (self.left_padding, 0))
        return self.conv(padded)


class MultiScaleTemporalBlock(nn.Module):
    """Residual causal block with parallel temporal kernels."""

    def __init__(
        self,
        channels: int,
        *,
        dilation: int,
        kernel_sizes: tuple[int, ...] = (3, 5, 7),
        dropout: float = 0.10,
    ) -> None:
        super().__init__()
        self.branches = nn.ModuleList(
            [CausalConv1d(channels, channels, kernel_size=kernel, dilation=dilation) for kernel in kernel_sizes]
        )
        self.projection = nn.Conv1d(channels * len(kernel_sizes), channels, kernel_size=1)
        self.norm = nn.GroupNorm(1, channels)
        self.dropout = nn.Dropout(dropout)
        self.activation = nn.SiLU()

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        branch_outputs = [branch(inputs) for branch in self.branches]
        merged = torch.cat(branch_outputs, dim=1)
        update = self.projection(merged)
        update = self.norm(update)
        update = self.activation(update)
        update = self.dropout(update)
        return inputs + update


class FullUAMSTCN(nn.Module):
    """Multi-horizon quantile TCN with non-crossing P50/P90 outputs."""

    def __init__(
        self,
        *,
        input_channels: int,
        horizons: tuple[int, ...] = (1, 5, 10),
        hidden_width: int = 32,
        dilations: tuple[int, ...] = (1, 2, 4),
        dropout: float = 0.10,
        num_entities: int | None = None,
        entity_embedding_dim: int = 0,
    ) -> None:
        super().__init__()
        self.horizons = tuple(horizons)
        self.entity_embedding: nn.Embedding | None = None
        if num_entities is not None and entity_embedding_dim > 0:
            self.entity_embedding = nn.Embedding(num_entities, entity_embedding_dim)
        self.stem = CausalConv1d(input_channels, hidden_width, kernel_size=3)
        self.blocks = nn.ModuleList(
            [
                MultiScaleTemporalBlock(
                    hidden_width,
                    dilation=dilation,
                    dropout=dropout,
                )
                for dilation in dilations
            ]
        )
        head_input_width = hidden_width + (entity_embedding_dim if self.entity_embedding is not None else 0)
        self.head = nn.Sequential(
            nn.LayerNorm(head_input_width),
            nn.Linear(head_input_width, hidden_width),
            nn.SiLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_width, len(self.horizons) * 2),
        )

    def forward(self, inputs: torch.Tensor, entity_ids: torch.Tensor | None = None) -> torch.Tensor:
        """Return tensor shaped ``[batch, horizons, quantiles]``.

        Inputs are expected as ``[batch, time, channels]``. The second quantile
        is parameterized as a positive spread above P50 to prevent crossings.
        """

        if inputs.ndim != 3:
            raise ValueError(f"Expected [batch, time, channels], got shape {tuple(inputs.shape)}")
        features = inputs.transpose(1, 2)
        features = self.stem(features)
        for block in self.blocks:
            features = block(features)
        pooled = features[:, :, -1]
        if self.entity_embedding is not None:
            if entity_ids is None:
                raise ValueError("entity_ids are required when entity embeddings are enabled")
            pooled = torch.cat([pooled, self.entity_embedding(entity_ids.long())], dim=1)
        raw = self.head(pooled).view(inputs.shape[0], len(self.horizons), 2)
        p50 = raw[:, :, 0]
        spread = F.softplus(raw[:, :, 1])
        p90 = p50 + spread
        return torch.stack([p50, p90], dim=-1)


def pinball_loss(
    predictions: torch.Tensor,
    targets: torch.Tensor,
    *,
    quantiles: tuple[float, ...] = (0.5, 0.9),
) -> torch.Tensor:
    """Mean multi-horizon pinball loss for ``[batch, horizon, quantile]`` predictions."""

    if predictions.ndim != 3:
        raise ValueError("predictions must be shaped [batch, horizon, quantile]")
    if targets.ndim != 2:
        raise ValueError("targets must be shaped [batch, horizon]")
    losses = []
    for quantile_index, quantile in enumerate(quantiles):
        error = targets - predictions[:, :, quantile_index]
        losses.append(torch.maximum((quantile - 1.0) * error, quantile * error))
    return torch.stack(losses, dim=-1).mean()
