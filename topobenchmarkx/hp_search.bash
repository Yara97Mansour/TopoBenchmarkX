#python train.py model.backbone.hidden_channels=32,64,128 model.backbone.n_layers=1,2 dataset.parameters.batch_size=64,128 dataset.parameters.data_seed=1,2,3 --multirun

#python train.py dataset=REDDIT-BINARY model=cwn model.backbone.hidden_channels=32,64,128 model.backbone.n_layers=1,2,3,4 dataset.parameters.batch_size=64,128 dataset.parameters.data_seed=1,2,3 --multirun
python train.py dataset=REDDIT-BINARY model=cwn model.optimizer.lr=0.1,0.01 model.optimizer.weight_decay=0,0.01 model.backbone.hid_channels=32,64,128 model.backbone.n_layers=1,2,3,4 dataset.parameters.batch_size=64,128 dataset.parameters.data_seed=3 --multirun

python train.py dataset=REDDIT-BINARY model=unignn2 model.optimizer.lr=0.1,0.01 model.optimizer.weight_decay=0,0.01 model.backbone.hidden_channels=32,64,128 model.backbone.n_layers=1,2,3,4 dataset.parameters.batch_size=64,128 dataset.parameters.data_seed=3 --multirun


python train.py dataset=IMBD-BINARY model=cwn model.optimizer.lr=0.1,0.01 model.optimizer.weight_decay=0,0.01 model.backbone.hid_channels=32,64,128 model.backbone.n_layers=1,2,3,4 dataset.parameters.batch_size=64,128 dataset.parameters.data_seed=3 --multirun

python train.py dataset=NCI1 model=cwn model.optimizer.lr=0.01,0.001 model.optimizer.weight_decay=0,0.01 model.backbone.hid_channels=16,32,64 model.backbone.n_layers=4 dataset.parameters.batch_size=32,64,128 dataset.parameters.data_seed=3 --multirun


python train.py dataset=NCI1 model=gin model.optimizer.lr=0.01,0.001 model.optimizer.weight_decay=0,0.01 model.backbone.hidden_channels=16,32,64 model.backbone.dropout=0,0.25,0.5 model.backbone.num_layers=2,3,4 dataset.parameters.batch_size=32,64,128 dataset.parameters.data_seed=1,2,3 logger.wandb.project="NCI1_dataset" --multirun
python train.py dataset=NCI1 model=gin model.optimizer.lr=0.01,0.001 model.optimizer.weight_decay=0,0.01 model.backbone.hidden_channels=16,32,64 dataset.parameters.data_seed=1,2,3 logger.wandb.project=NCI1_dataset --multirun

python train.py dataset=NCI1 model=gin model.optimizer.lr=0.01,0.001 model.optimizer.weight_decay=0,0.01 model.backbone.hidden_channels=16,32,64 model.backbone.num_layers=2,3,4 dataset.parameters.batch_size=32,64,128 dataset.parameters.data_seed=1,2,3 logger.wandb.project=NCI1_dataset --multirun


# Search for the best hyperparameters for the NCI1 dataset using the GIN model
python train.py dataset=NCI1 model=gin model.optimizer.lr=0.01,0.001 model.optimizer.weight_decay=0,0.01 model.backbone.hidden_channels=16,32 model.backbone.num_layers=2,3,4,5 dataset.parameters.batch_size=32,128 dataset.parameters.data_seed=1,4,6 model.backbone.dropout=0,0.25,0.5 logger.wandb.project=NCI1_dataset --multirun
# Best GIN parameters for NCI1 dataset all seeds
python train.py dataset=NCI1 model=graph/gin model.optimizer.lr=0.001 model.optimizer.weight_decay=0 model.backbone.hidden_channels=16 model.backbone.num_layers=4 dataset.parameters.batch_size=32 dataset.parameters.data_seed=0,2,3,4,5,7,8,9 model.backbone.dropout=0 logger.wandb.project=NCI1_dataset_newsplits --multirun

# ZINC
python train.py dataset=ZINC model=graph/gin model.optimizer.lr=0.01,0.001 model.optimizer.weight_decay=0 model.backbone.hidden_channels=16,32,64,128 model.backbone.num_layers=1,2,3,4 dataset.parameters.batch_size=128,256 dataset.parameters.data_seed=0 model.backbone.dropout=0,0.25,0.5 logger.wandb.project=ZINC_sanityckeck --multirun

python train.py dataset=ZINC model=cell/cwn model.optimizer.lr=0.01,0.001 model.backbone.hid_channels=16,32,64,128 model.backbone.n_layers=1,2,3,4 dataset.parameters.batch_size=128,256 dataset.parameters.data_seed=0 logger.wandb.project=ZINC_sanityckeck --multirun


python train.py dataset=ZINC model=cell/ccxn model.optimizer.lr=0.01,0.001 model.backbone_additional_params.hidden_channels=16,32,64,128 model.backbone.n_layers=1,2,3,4 dataset.parameters.batch_size=128,256 dataset.parameters.data_seed=0 logger.wandb.project=ZINC_sanityckeck --multirun
#python train.py dataset=PROTEINS_TU +transforms.transform_chain_proteins_g2s=transforms.transform_chain_proteins_g2hp model=unignn2  --multirunpython train.py dataset=NCI1 model=gin model.optimizer.lr=0.01,0.001 model.optimizer.weight_decay=0,0.01 model.backbone.hidden_channels=16,32,64 model.backbone.dropout=0,0.25,0.5 model.backbone.num_layers=2,3,4 dataset.parameters.batch_size=32,64,128 dataset.parameters.data_seed=1,2,3 logger.wandb.project="NCI1_dataset" --multirun