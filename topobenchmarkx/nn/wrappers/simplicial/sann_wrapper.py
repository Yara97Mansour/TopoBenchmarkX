"""Wrapper for the SANN model."""

from topobenchmarkx.nn.wrappers import AbstractWrapper


class SANNWrapper(AbstractWrapper):
    r"""Wrapper for the SANN."""

    def __call__(self, batch):
        r"""Forward pass for the model.

        This method calls the forward method and adds the residual connection.

        Parameters
        ----------
        batch : torch_geometric.data.Data
            Batch object containing the batched data.

        Returns
        -------
        dict
            Dictionary containing the model output.
        """
        model_out = self.forward(batch)
        return model_out

    def forward(self, batch):
        """Forward pass of the SANN.

        Parameters
        ----------
        batch : Dict
            Dictionary containing the batched domain data.

        Returns
        -------
        dict
            Dictionary containing the model output.
        """
        # Prepare the input data for the backbone
        # by aggregating the data in a dictionary
        x_all = dict()
        for i in range(3):
            x_tmp = dict()
            for j in range(3):
                x_tmp[j] = batch[f"x{i}_{j}"]
            x_all[i] = x_tmp

        x_out = self.backbone(x_all)

        model_out = {"labels": batch.y, "batch_0": batch.batch_0}

        model_out["x_0"] = x_out[0]
        model_out["x_1"] = x_out[1]
        model_out["x_2"] = x_out[2]

        return model_out
