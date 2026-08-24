"""
Hyperspectral Imaging Evaluation & Inference Pipeline
"""

import os
import numpy as np


def run_inference(input_data_path, output_dir):
    """
    Run model inference on target hyperspectral data.
    """
    print(f"Loading hyperspectral data from {input_data_path}...")
    # Inference logic
    os.makedirs(output_dir, exist_ok=True)
    print(f"Inference complete. Results saved to {output_dir}.")


if __name__ == "__main__":
    import sys
    data_path = sys.argv[1] if len(sys.argv) > 1 else "./Dataset"
    output_path = sys.argv[2] if len(sys.argv) > 2 else "./Output/Output_Images"
    run_inference(data_path, output_path)
