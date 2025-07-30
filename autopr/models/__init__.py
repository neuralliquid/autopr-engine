"""
Models Package

This package contains data models and schemas used throughout the AutoPR system.
"""

import os
import pathlib

# Create models directory if it doesn't exist
os.makedirs(pathlib.Path(__file__).parent, exist_ok=True)

# Create artifacts module
artifacts_path = os.path.join(pathlib.Path(__file__).parent, "artifacts.py")
if not pathlib.Path(artifacts_path).exists():
    with open(artifacts_path, "w", encoding="utf-8") as f:
        f.write(
            '"""\nArtifacts Module\n\nThis module contains data models for various artifacts used in the AutoPR system.\n"""\n\nfrom dataclasses import dataclass\nfrom enum import Enum\nfrom typing import Any, Dict, List, Optional\n\n\nclass EnhancementType(str, Enum):\n    """Types of enhancements that can be applied to a prototype."""\n    PRODUCTION = "production"\n    TESTING = "testing"\n    SECURITY = "security"\n\n\n@dataclass\nclass PrototypeEnhancerInputs:\n    """Input model for the PrototypeEnhancer."""\n    platform: str\n    enhancement_type: "EnhancementType"\n    project_path: str\n    config: Optional[Dict[str, Any]] = None\n    dry_run: bool = False\n\n\n@dataclass\nclass PrototypeEnhancerOutputs:\n    """Output model for the PrototypeEnhancer."""\n    success: bool\n    message: str\n    generated_files: List[str]\n    modified_files: List[str]\n    next_steps: List[str]\n    metadata: Optional[Dict[str, Any]] = None\n'
        )

# Create a placeholder for other model files
for model_file in ["base.py", "config.py", "events.py"]:
    file_path = os.path.join(pathlib.Path(__file__).parent, model_file)
    if not pathlib.Path(file_path).exists():
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(
                f'"""\n{model_file.capitalize().replace("_", " ").replace(".py", "")}\n\nThis module contains data models for {model_file.replace("_", " ").replace(".py", "")}.\n"""'
            )

# Export the models for easier imports
__all__ = [
    "EnhancementType",
    "PrototypeEnhancerInputs",
    "PrototypeEnhancerOutputs",
]
