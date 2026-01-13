import torch
import torch.nn.functional as F
from torch_geometric.nn import SAGEConv
from torch_geometric.data import Data

class FraudSAGE(torch.nn.Module):
    def __init__(self, in_channels, hidden_channels, out_channels):
        super(FraudSAGE, self).__init__()
        self.conv1 = SAGEConv(in_channels, hidden_channels)
        self.conv2 = SAGEConv(hidden_channels, out_channels)

    def forward(self, x, edge_index):
        x = self.conv1(x, edge_index)
        x = F.relu(x)
        x = F.dropout(x, p=0.5, training=self.training)
        x = self.conv2(x, edge_index)
        return F.log_softmax(x, dim=1)

def train_mule_detector(data):
    model = FraudSAGE(data.num_node_features, 16, 2) # Binary: Fraud vs Legitimate
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01, weight_decay=5e-4)
    
    model.train()
    for epoch in range(100):
        optimizer.zero_grad()
        out = model(data.x, data.edge_index)
        # Assuming we have labels for a small subset
        # loss = F.nll_loss(out[data.train_mask], data.y[data.train_mask])
        # loss.backward()
        optimizer.step()
    return model
