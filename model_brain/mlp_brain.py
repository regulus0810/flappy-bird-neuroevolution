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

    # --- THÊM 1: Cầu nối nạp 89 số gen vào các tầng PyTorch ---
    def set_weight(self, chromosome):
        if chromosome is not None:
            tensor_weights = torch.tensor(chromosome, dtype=torch.float32)
            nn.utils.vector_to_parameters(tensor_weights, self.parameters())

    def predict(self, inputs):
        with torch.no_grad():
            x = torch.tensor(inputs, dtype=torch.float32)
            output = self.forward(x)
            return output.item()

# --- THÊM 3: Lưu và đọc bộ gen của MLP ---
def save_best_bird(chromosome, filename="best_bird_mlp.json"):
    if hasattr(chromosome, "tolist"):
        chromosome = chromosome.tolist()
    with open(filename, "w") as f:
        json.dump(chromosome, f, indent=4)
    print(f"Lưu thành công mô hình MLP vào {filename}")
def load_best_bird(filename="best_bird_mlp.json"):
    with open(filename, "r") as f:
        chromosome = json.load(f)
    return chromosome



