import torch
import torch.nn as nn

class MlpBrain(nn.Module):
    def __init__(self, in_features=5, hidden_1=8, hidden_2=4, out_features=1):
        # model return a float number range (0.0 to 1.0)
        super(MlpBrain, self).__init__()

        self.fc1 = nn.Linear(in_features, hidden_1)
        self.relu1 = nn.ReLU()

        self.fc2 = nn.Linear(hidden_1, hidden_2)
        self.relu2 = nn.ReLU()

        self.fc3 = nn.Linear(hidden_2, out_features)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu1(x)

        x = self.fc2(x)
        x = self.relu2(x)

        x = self.fc3(x)
        x = self.sigmoid(x)

        return x


