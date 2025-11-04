from django.core.management.base import BaseCommand
from django.conf import settings
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import json
from pathlib import Path
from ml.ml_models.neuropilot_model import create_model
from ml.services.model_manager import ModelManager

class Command(BaseCommand):
    help = 'Train the Neuropilot hesitation detection model'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--epochs',
            type=int,
            default=10,
            help='Number of training epochs'
        )
        parser.add_argument(
            '--learning-rate',
            type=float,
            default=0.001,
            help='Learning rate'
        )
        parser.add_argument(
            '--model-version',  # CHANGED: from --version to --model-version
            type=str,
            default='v1.0',
            help='Model version name'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting Neuropilot model training...'))
        
        epochs = options['epochs']
        learning_rate = options['learning_rate']
        version = options['model_version']  # CHANGED: from version to model_version
        
        try:
            # Create synthetic training data (replace with your actual data)
            train_loader = self.create_sample_data()
            
            # Initialize model
            model = create_model(num_commands=20, input_size=4)
            criterion = nn.BCELoss()  # Binary cross entropy for hesitation
            optimizer = optim.Adam(model.parameters(), lr=learning_rate)
            
            # Training loop
            model.train()
            for epoch in range(epochs):
                total_loss = 0
                for batch_idx, (data, target) in enumerate(train_loader):
                    optimizer.zero_grad()
                    output = model(data)
                    loss = criterion(output['hesitation'], target)
                    loss.backward()
                    optimizer.step()
                    total_loss += loss.item()
                
                if (epoch + 1) % 5 == 0:
                    self.stdout.write(
                        f'Epoch [{epoch+1}/{epochs}], Loss: {total_loss/len(train_loader):.4f}'
                    )
            
            # Save the trained model
            ModelManager.save_model(model, version)
            
            self.stdout.write(
                self.style.SUCCESS(f'Training completed! Model saved as {version}')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Training failed: {str(e)}')
            )
    
    def create_sample_data(self):
        """Create sample training data - replace with your actual dataset"""
        # Generate synthetic interaction data
        num_samples = 1000
        X = np.random.random((num_samples, 4)).astype(np.float32)
        y = (X[:, 0] > 0.7).astype(np.float32)  # Hesitation if first feature > 0.7
        
        dataset = torch.utils.data.TensorDataset(
            torch.from_numpy(X),
            torch.from_numpy(y).unsqueeze(1)
        )
        
        return torch.utils.data.DataLoader(dataset, batch_size=32, shuffle=True)
