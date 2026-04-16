import sys
from pathlib import Path

# Add the service root to sys.path so absolute imports work in tests
sys.path.insert(0, str(Path(__file__).parent))
