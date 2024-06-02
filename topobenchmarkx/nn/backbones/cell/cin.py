"""CWN class."""

import torch
import torch.nn as nn
import torch.nn.functional as F
from topomodelx.base.conv import Conv
from torch_geometric.nn.models import MLP


class CWN(torch.nn.Module):
    """Implementation of a specific version of CW network.
    From Bodnar, et al. Weisfeiler and Lehman go cellular: CW networks.
    NeurIPS 2021. https://arxiv.org/abs/2106.12575

    Args:
        in_channels_0 (int): Dimension of input features on nodes (0-cells).
        in_channels_1 (int): Dimension of input features on edges (1-cells).
        in_channels_2 (int): Dimension of input features on faces (2-cells).
        hid_channels (int): Dimension of hidden features.
        n_layers (int): Number of CWN layers.
    """

    def __init__(
        self,
        in_channels_0,
        in_channels_1,
        in_channels_2,
        hid_channels,
        n_layers,
    ):
        super().__init__()

        self.proj_0 = torch.nn.Linear(in_channels_0, hid_channels)
        self.proj_1 = torch.nn.Linear(in_channels_1, hid_channels)
        self.proj_2 = torch.nn.Linear(in_channels_2, hid_channels)

        self.layers = torch.nn.ModuleList(
            CWNLayer(
                in_channels_0=hid_channels,
                in_channels_1=hid_channels,
                in_channels_2=hid_channels,
                out_channels=hid_channels,
            )
            for _ in range(n_layers)
        )

    def forward(
        self,
        x_0,
        x_1,
        x_2,
        neighborhood_1_to_1,
        neighborhood_2_to_1,
        neighborhood_0_to_1,
    ):
        """Forward computation through projection, convolutions, linear layers
        and average pooling.

        Args:
            x_0 (torch.Tensor): Input features on the nodes (0-cells).
            x_1 (torch.Tensor): Input features on the edges (1-cells).
            x_2 (torch.Tensor): Input features on the faces (2-cells).
            neighborhood_1_to_1 (torch.Tensor): Upper-adjacency matrix of rank 1.
            neighborhood_2_to_1 (torch.Tensor): Boundary matrix of rank 2.
            neighborhood_0_to_1 (torch.Tensor): Coboundary matrix of rank 1.
        Returns:
            x_0 (torch.Tensor): Final hidden states of the nodes (0-cells).
            x_1 (torch.Tensor): Final hidden states the edges (1-cells).
            x_2 (torch.Tensor): Final hidden states of the faces (2-cells).
        """
        x_0 = F.elu(self.proj_0(x_0))
        x_1 = F.elu(self.proj_1(x_1))
        x_2 = F.elu(self.proj_2(x_2))

        for layer in self.layers:
            x_1 = layer(
                x_0,
                x_1,
                x_2,
                neighborhood_1_to_1,
                neighborhood_2_to_1,
                neighborhood_0_to_1,
            )

        return x_0, x_1, x_2


class CWNLayer(nn.Module):
    r"""Layer of a CW Network (CWN).

    Implementation of the CWN layer proposed in [1]_.

    This module is composed of the following layers:
    1. A convolutional layer that sends messages from r-cells to r-cells.
    2. A convolutional layer that sends messages from (r-1)-cells to r-cells.
    3. A layer that creates representations in r-cells based on the received messages.
    4. A layer that updates representations in r-cells.

    Args:
        in_channels_0 (int): Dimension of input features on (r-1)-cells (nodes in case r = 1).
        in_channels_1 (int): Dimension of input features on r-cells (edges in case r = 1).
        in_channels_2 (int): Dimension of input features on (r+1)-cells (faces in case r = 1).
        out_channels (int): Dimension of output features on r-cells.
        conv_1_to_1 (torch.nn.Module, optional): A module that convolves the representations of upper-adjacent neighbors of r-cells
            and their corresponding co-boundary (r+1) cells.
        conv_0_to_1 (torch.nn.Module, optional): A module that convolves the representations of (r-1)-cells on the boundary of r-cells.
        aggregate_fn (torch.nn.Module, optional): A module that aggregates the representations of r-cells obtained by convolutional layers.
        update_fn (torch.nn.Module, optional): A module that updates the aggregated representations of r-cells.
        eps (float, optional): A learnable parameter that scales the input features before the first convolutional layer.
    """

    def __init__(
        self,
        in_channels_0,
        in_channels_1,
        in_channels_2,
        out_channels,
        conv_1_to_1=None,
        conv_0_to_1=None,
        aggregate_fn=None,
        update_fn=None,
        eps=0.01,
    ) -> None:
        super().__init__()

        self.conv_1_to_1 = (
            conv_1_to_1
            if conv_1_to_1 is not None
            else _CWNDefaultFirstConv(
                in_channels_1, in_channels_2, out_channels
            )
        )
        self.conv_0_to_1 = (
            conv_0_to_1
            if conv_0_to_1 is not None
            else _CWNDefaultSecondConv(
                in_channels_0, in_channels_1, out_channels
            )
        )
        self.aggregate_fn = (
            aggregate_fn
            if aggregate_fn is not None
            else _CWNDefaultAggregate()
        )
        self.update_fn = (
            update_fn
            if update_fn is not None
            else _CWNDefaultUpdate(out_channels, out_channels)
        )
        self.mlp_arrow = MLP(
            [in_channels_1, in_channels_1, in_channels_1],
            act="relu",
            act_first=False,
            norm=torch.nn.BatchNorm1d(out_channels),
            # norm_kwargs=self.norm_kwargs,
        )

        self.mlp = MLP(
            [in_channels_2 + in_channels_2, out_channels, out_channels],
            act="relu",
            act_first=False,
            norm=torch.nn.BatchNorm1d(out_channels),
        )

        self.eps = torch.nn.Parameter(torch.Tensor([eps]))

    def forward(
        self,
        x_0,
        x_1,
        x_2,
        neighborhood_1_to_1,
        neighborhood_2_to_1,
        neighborhood_0_to_1,
    ):
        r"""Forward pass.

        The forward pass of this layer is composed of two convolutional steps
        that are followed by an aggregation step and a final update step.

        Args:
            x_0 (torch.Tensor): Input features on the (r-1)-cells.
            x_1 (torch.Tensor): Input features on the r-cells.
            x_2 (torch.Tensor): Input features on the (r+1)-cells.
            neighborhood_1_to_1 (torch.Tensor): Neighborhood matrix mapping r-cells to r-cells (A_{up,r}).
            neighborhood_2_to_1 (torch.Tensor): Neighborhood matrix mapping (r+1)-cells to r-cells (B_{r+1}).
            neighborhood_0_to_1 (torch.Tensor): Neighborhood matrix mapping (r-1)-cells to r-cells (B^T_r).
        Returns:
            torch.Tensor: Updated representations of the r-cells.
        """
        x_convolved_1_to_1 = (1 + self.eps) * x_1 + self.conv_1_to_1(
            x_1, x_2, neighborhood_1_to_1, neighborhood_2_to_1
        )
        x_convolved_1_to_1 = self.mlp_arrow(x_convolved_1_to_1)

        x_convolved_0_to_1 = (1 + self.eps) * x_1 + self.conv_0_to_1(
            x_0, neighborhood_0_to_1
        )

        x_aggregated = self.mlp(
            torch.cat([x_convolved_0_to_1, x_convolved_1_to_1], dim=-1)
        )
        return self.update_fn(x_aggregated, x_1)


class _CWNDefaultFirstConv(nn.Module):
    r"""Default implementation of the first convolutional step in CWNLayer.

    The self.forward method of this module must be treated as a protocol for
    the first convolutional step in CWN layer.

    Args:
        in_channels_1 (int): Dimension of input features on r-cells.
        in_channels_2 (int): Dimension of input features on (r+1)-cells.
        out_channels (int): Dimension of output features on r-cells.
        eps (float, optional): A learnable parameter that scales the input features before the first convolutional layer.
    """

    def __init__(
        self, in_channels_1, in_channels_2, out_channels, eps: float = 0.0
    ) -> None:
        super().__init__()
        self.conv_1_to_1 = Conv(
            in_channels_1, out_channels, aggr_norm=False, update_func=None
        )
        self.conv_2_to_1 = Conv(
            in_channels_2, out_channels, aggr_norm=False, update_func=None
        )

        self.mlp = MLP(
            [in_channels_1 + in_channels_2, out_channels, out_channels],
            act="relu",
            act_first=False,
            norm=torch.nn.BatchNorm1d(out_channels),
            # norm_kwargs=self.norm_kwargs,
        )

        self.eps = torch.nn.Parameter(torch.Tensor([eps]))

    def forward(self, x_1, x_2, neighborhood_1_to_1, neighborhood_2_to_1):
        r"""Forward pass.

        Args:
            x_1 (torch.Tensor): Input features on the r-cells.
            x_2 (torch.Tensor): Input features on the (r+1)-cells.
            neighborhood_1_to_1 (torch.Tensor): Neighborhood matrix mapping r-cells to r-cells (A_{up,r}).
            neighborhood_2_to_1 (torch.Tensor): Neighborhood matrix mapping (r+1)-cells to r-cells (B_{r+1}).
        Returns:
            torch.Tensor: Updated representations on the r-cells.
        """
        x_up = F.elu(self.conv_1_to_1(x_1, neighborhood_1_to_1))
        x_up = (1 + self.eps) * x_1 + x_up

        x_coboundary = F.elu(self.conv_2_to_1(x_2, neighborhood_2_to_1))
        x_coboundary = (1 + self.eps) * x_1 + x_coboundary

        return self.mlp(torch.cat([x_up, x_coboundary], dim=-1))


class _CWNDefaultSecondConv(nn.Module):
    r"""Default implementation of the second convolutional step in CWNLayer.

    The self.forward method of this module must be treated as a protocol for
    the second convolutional step in CWN layer.

    Args:
        in_channels_0 (int): Dimension of input features on (r-1)-cells.
        out_channels (int): Dimension of output features on r-cells.
    """

    def __init__(self, in_channels_0, out_channels) -> None:
        super().__init__()
        self.conv_0_to_1 = Conv(
            in_channels_0, out_channels, aggr_norm=False, update_func=None
        )

    def forward(self, x_0, neighborhood_0_to_1):
        r"""Forward pass.

        Args:
            x_0 (torch.Tensor): Input features on the (r-1)-cells.
            x_1 (torch.Tensor): Input features on the r-cells.
            neighborhood_0_to_1 (torch.Tensor): Neighborhood matrix mapping (r-1)-cells to r-cells (B^T_r).
        Returns:
            torch.Tensor: Updated representations on the r-cells.
        """
        return F.elu(self.conv_0_to_1(x_0, neighborhood_0_to_1))


class _CWNDefaultAggregate(nn.Module):
    r"""Default implementation of an aggregation step in CWNLayer.

    The self.forward method of this module must be treated as a protocol for
    the aggregation step in CWN layer.
    """

    def __init__(self) -> None:
        super().__init__()

    def forward(self, x, y):
        r"""Forward pass.

        Args:
            x (torch.Tensor): Representations on the r-cells produced by the first convolutional step.
            y (torch.Tensor): Representations on the r-cells produced by the second convolutional step.
        Returns:
            torch.Tensor: Aggregated representations on the r-cells.
        """
        return x + y


class _CWNDefaultUpdate(nn.Module):
    r"""Default implementation of an update step in CWNLayer.

    Args:
        in_channels (int): Dimension of input features on r-cells.
        out_channels (int): Dimension of output features on r-cells.
    """

    def __init__(self, in_channels, out_channels) -> None:
        super().__init__()
        self.transform = nn.Linear(in_channels, out_channels)

    def forward(self, x, x_prev=None):
        r"""Forward pass.

        Args:
            x (torch.Tensor): New representations on the r-cells obtained after the aggregation step.
            x_prev (torch.Tensor): Original representations on the r-cells passed into the CWN layer.
        Returns:
            torch.Tensor: Updated representations on the r-cells.
        """
        return F.elu(self.transform(x))
