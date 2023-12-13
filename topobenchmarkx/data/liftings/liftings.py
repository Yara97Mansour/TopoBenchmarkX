import torch
import torch_geometric

from topobenchmarkx.data.liftings.lifting import AbstractLifting


class KHopLifting(torch_geometric.transforms.BaseTransform):
    def __init__(self, k=1):
        super().__init__()
        self.k = k

    def forward(self, data: torch_geometric.data.Data) -> dict:
        n_nodes = data.x.shape[0]
        incidence_1 = torch.zeros(n_nodes, n_nodes)
        edge_index = torch_geometric.utils.to_undirected(data.edge_index)
        for n in range(n_nodes):
            neighbors, _, _, _ = torch_geometric.utilsk_hop_subgraph(
                n, self.k, edge_index
            )
            incidence_1[n, neighbors] = 1
        incidence_1 = torch.Tensor(incidence_1).to_sparse_coo()
        data["hyperedges"] = incidence_1
        return data
