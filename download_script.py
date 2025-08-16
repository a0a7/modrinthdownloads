#!/usr/bin/env python3
"""
Download script that handles various downloads based on probability.
"""

import random
import requests
import os
import sys
from datetime import datetime
import subprocess


def log_message(message):
    """Log a message with timestamp."""
    timestamp = datetime.now().isoformat()
    print(f"[{timestamp}] {message}")


def download_huggingface_dataset(repo_id):
    """Download HuggingFace dataset to increase download count."""
    try:
        from huggingface_hub import snapshot_download
        import tempfile
        import shutil
        log_message(f"Downloading HuggingFace dataset: {repo_id}")
        
        # Download to a temporary directory that gets auto-cleaned
        with tempfile.TemporaryDirectory() as temp_dir:
            download_path = snapshot_download(
                repo_id=repo_id,
                repo_type="dataset",
                cache_dir=temp_dir,
                token=os.getenv('HUGGINGFACE_HUB_TOKEN')
            )
            log_message(f"Successfully downloaded {repo_id} to temporary location (will be auto-deleted)")
            # temp_dir automatically gets cleaned up when exiting the with block
        return True
    except Exception as e:
        log_message(f"Failed to download HuggingFace dataset {repo_id}: {e}")
        return False


def download_huggingface_model(repo_id):
    """Download HuggingFace model to increase download count."""
    try:
        from huggingface_hub import snapshot_download
        import tempfile
        import shutil
        log_message(f"Downloading HuggingFace model: {repo_id}")
        
        # Download to a temporary directory that gets auto-cleaned
        with tempfile.TemporaryDirectory() as temp_dir:
            download_path = snapshot_download(
                repo_id=repo_id,
                repo_type="model",
                cache_dir=temp_dir,
                token=os.getenv('HUGGINGFACE_HUB_TOKEN')
            )
            log_message(f"Successfully downloaded {repo_id} to temporary location (will be auto-deleted)")
            # temp_dir automatically gets cleaned up when exiting the with block
        return True
    except Exception as e:
        log_message(f"Failed to download HuggingFace model {repo_id}: {e}")
        return False


def check_npm_package_exists(package_name):
    """Check if an npm package exists."""
    try:
        response = requests.get(f"https://registry.npmjs.org/{package_name}", timeout=10)
        return response.status_code == 200
    except Exception as e:
        log_message(f"Error checking npm package {package_name}: {e}")
        return False


def download_npm_package(package_name):
    """Download npm package to increase download count."""
    try:
        import tempfile
        import os
        log_message(f"Downloading npm package: {package_name}")
        
        # Download to a temporary directory that gets auto-cleaned
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                result = subprocess.run(
                    ["npm", "pack", package_name],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                if result.returncode == 0:
                    log_message(f"Successfully downloaded npm package {package_name} to temporary location (will be auto-deleted)")
                    return True
                else:
                    log_message(f"Failed to download npm package {package_name}: {result.stderr}")
                    return False
            finally:
                os.chdir(original_cwd)
    except Exception as e:
        log_message(f"Failed to download npm package {package_name}: {e}")
        return False


def check_crates_package_exists(package_name):
    """Check if a crates.io package exists."""
    try:
        response = requests.get(f"https://crates.io/api/v1/crates/{package_name}", timeout=10)
        return response.status_code == 200
    except Exception as e:
        log_message(f"Error checking crates package {package_name}: {e}")
        return False


def download_crates_package(package_name):
    """Download crates.io package to increase download count."""
    try:
        import tempfile
        log_message(f"Downloading crates package: {package_name}")
        
        # Download to a temporary directory that gets auto-cleaned
        with tempfile.TemporaryDirectory() as temp_dir:
            # Use cargo install with --root to install to temp directory
            result = subprocess.run(
                ["cargo", "install", "--force", "--root", temp_dir, package_name],
                capture_output=True,
                text=True,
                timeout=300
            )
            if result.returncode == 0:
                log_message(f"Successfully downloaded crates package {package_name} to temporary location (will be auto-deleted)")
                return True
            else:
                log_message(f"Failed to download crates package {package_name}: {result.stderr}")
                return False
    except Exception as e:
        log_message(f"Failed to download crates package {package_name}: {e}")
        return False


def download_docker_image(image_name):
    """Download Docker image to increase download count."""
    try:
        log_message(f"Downloading Docker image: {image_name}")
        
        # Pull the image (this increases download count)
        result = subprocess.run(
            ["docker", "pull", image_name],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            log_message(f"Successfully downloaded Docker image {image_name}")
            
            # Remove the image immediately to free up space
            cleanup_result = subprocess.run(
                ["docker", "rmi", image_name],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if cleanup_result.returncode == 0:
                log_message(f"Successfully removed Docker image {image_name} to free up space")
            else:
                log_message(f"Warning: Failed to remove Docker image {image_name}: {cleanup_result.stderr}")
            
            return True
        else:
            log_message(f"Failed to download Docker image {image_name}: {result.stderr}")
            return False
    except Exception as e:
        log_message(f"Failed to download Docker image {image_name}: {e}")
        return False


def main():
    """Main function that executes the download logic."""
    log_message("Starting download job")
    
    # Set random seed for reproducibility within the same minute
    random.seed(int(datetime.now().timestamp() / 60))
    
    results = []
    
    # 1. 100% chance to download HuggingFace dataset
    log_message("Task 1: Downloading HuggingFace dataset (100% chance)")
    success = download_huggingface_dataset("a0a7/Gregg-1916")
    results.append(("HuggingFace dataset a0a7/Gregg-1916", success))
    
    # 2. 30% chance to download HuggingFace model
    if random.random() < 0.30:
        log_message("Task 2: Downloading HuggingFace model (30% chance - triggered)")
        success = download_huggingface_model("a0a7/gregg-recognition")
        results.append(("HuggingFace model a0a7/gregg-recognition", success))
    else:
        log_message("Task 2: Skipping HuggingFace model download (30% chance - not triggered)")
        results.append(("HuggingFace model a0a7/gregg-recognition", "skipped"))
    
    # 3. 85% chance to download npm package (with preference check)
    if random.random() < 0.85:
        log_message("Task 3: npm package download (85% chance - triggered)")
        if check_npm_package_exists("fastgeotoolkit"):
            log_message("fastgeotoolkit exists, downloading it instead")
            success = download_npm_package("fastgeotoolkit")
            results.append(("npm package fastgeotoolkit", success))
        else:
            log_message("fastgeotoolkit doesn't exist, downloading heatmap-parse")
            success = download_npm_package("heatmap-parse")
            results.append(("npm package heatmap-parse", success))
    else:
        log_message("Task 3: Skipping npm package download (85% chance - not triggered)")
        results.append(("npm package", "skipped"))
    
    # 4. 95% chance to download crates package (with preference check)
    if random.random() < 0.95:
        log_message("Task 4: crates package download (95% chance - triggered)")
        if check_crates_package_exists("fastgeotoolkit"):
            log_message("fastgeotoolkit crate exists, downloading it instead")
            success = download_crates_package("fastgeotoolkit")
            results.append(("crates package fastgeotoolkit", success))
        else:
            log_message("fastgeotoolkit crate doesn't exist, downloading heatmap-parse")
            success = download_crates_package("heatmap-parse")
            results.append(("crates package heatmap-parse", success))
    else:
        log_message("Task 4: Skipping crates package download (95% chance - not triggered)")
        results.append(("crates package", "skipped"))
    
    # 5. 40% chance to download Docker image
    if random.random() < 0.40:
        log_message("Task 5: Downloading Docker image (40% chance - triggered)")
        success = download_docker_image("a0a7/publicbroadcastarr")
        results.append(("Docker image a0a7/publicbroadcastarr", success))
    else:
        log_message("Task 5: Skipping Docker image download (40% chance - not triggered)")
        results.append(("Docker image a0a7/publicbroadcastarr", "skipped"))
    
    # Summary
    log_message("Download job completed. Summary:")
    for task, result in results:
        log_message(f"  {task}: {result}")
    
    # Log to stdout only (no file saving)
    log_message(f"Job completed at {datetime.now().isoformat()}")


if __name__ == "__main__":
    main()
