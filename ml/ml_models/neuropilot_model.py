import torch
import torch.nn as nn
import torch.nn.functional as F

class NeuropilotModel(nn.Module):
    def __init__(self, num_commands=50, input_size=4, hidden_size=128):
        super().__init__()
        
        # Main sequential network
        self.network = nn.Sequential(
            nn.Linear(input_size, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.3),
        )
        
        # Output heads
        self.hesitation_head = nn.Linear(hidden_size, 1)  # Binary: hesitating or not
        self.command_head = nn.Linear(hidden_size, num_commands)  # Command prediction
        self.confidence_head = nn.Linear(hidden_size, 1)  # Prediction confidence
        
    def forward(self, x):
        features = self.network(x)
        
        hesitation = torch.sigmoid(self.hesitation_head(features))
        commands = F.softmax(self.command_head(features), dim=-1)
        confidence = torch.sigmoid(self.confidence_head(features))
        
        return {
            'hesitation': hesitation,
            'suggested_commands': commands,
            'confidence': confidence
        }

def create_model(num_commands=50, input_size=4):
    """Factory function to create model"""
    return NeuropilotModel(num_commands=num_commands, input_size=input_size)

def load_pretrained_model(model_path, num_commands=50, input_size=4):
    """Load a pretrained model"""
    model = create_model(num_commands, input_size)
    try:
        model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
        model.eval()
        return model
    except Exception as e:
        print(f"Error loading pretrained model: {e}")
        return model
