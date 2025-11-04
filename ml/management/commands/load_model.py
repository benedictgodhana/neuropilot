from django.core.management.base import BaseCommand
from ml.services.model_manager import ModelManager

class Command(BaseCommand):
    help = 'Load the Neuropilot ML model into memory'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--model-version',  # CHANGED: from --version to --model-version
            type=str,
            default='current',
            help='Model version to load'
        )
    
    def handle(self, *args, **options):
        version = options['model_version']  # CHANGED: from version to model_version
        
        self.stdout.write(f'Loading Neuropilot model {version}...')
        
        success = ModelManager.load_model(version)
        
        if success:
            self.stdout.write(
                self.style.SUCCESS(f'Model {version} loaded successfully!')
            )
        else:
            self.stdout.write(
                self.style.ERROR(f'Failed to load model {version}')
            )
