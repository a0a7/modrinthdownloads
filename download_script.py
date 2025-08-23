#!/usr/bin/env python3
"""
Download script that handles various downloads based on probability.
Week-dependent variant: download probabilities are slightly adjusted per week.
"""

import random
import requests
import os
import sys
from datetime import datetime
import subprocess
import time

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

def download_github_npm_package(pkg_url):
    """
    Download/install a GitHub Packages npm package via npm. 
    Expects a URL like: https://github.com/OWNER/REPO/pkgs/npm/PACKAGE
    """
    # Parse package name, owner, repo from the URL
    # Example: https://github.com/a0a7/fastgeotoolkit/pkgs/npm/fastgeotoolkit
    # Package name: @a0a7/fastgeotoolkit
    try:
        import tempfile
        import re

        log_message(f"Downloading GitHub npm package from {pkg_url}")
        m = re.match(r"https://github.com/([^/]+)/([^/]+)/pkgs/npm/([^/]+)", pkg_url)
        if not m:
            log_message("Invalid GitHub npm package URL format")
            return False
        owner, repo, pkg = m.groups()
        package_name = f"@{owner}/{pkg}"
        
        # Set up .npmrc with GitHub token if provided
        gh_token = os.getenv("GITHUB_TOKEN")
        npmrc_lines = []
        registry_url = f"//npm.pkg.github.com/:_authToken={gh_token}" if gh_token else ""
        if gh_token:
            npmrc_lines.append(f"@{owner}:registry=https://npm.pkg.github.com/")
            npmrc_lines.append(registry_url)
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                if gh_token:
                    with open(".npmrc", "w") as f:
                        f.write("\n".join(npmrc_lines) + "\n")
                result = subprocess.run(
                    ["npm", "pack", package_name],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                if result.returncode == 0:
                    log_message(f"Successfully downloaded GitHub npm package {package_name} to temporary location (will be auto-deleted)")
                    return True
                else:
                    log_message(f"Failed to download GitHub npm package {package_name}: {result.stderr}")
                    return False
            finally:
                os.chdir(original_cwd)
    except Exception as e:
        log_message(f"Failed to download GitHub npm package from {pkg_url}: {e}")
        return False

def download_github_container_image(pkg_url):
    """
    Download/pull a GitHub Container registry image.
    Expects a URL like: https://github.com/OWNER/REPO/pkgs/container/NAME
    """
    # Example: https://github.com/a0a7/publicbroadcastarr/pkgs/container/publicbroadcastarr
    # Image name: ghcr.io/a0a7/publicbroadcastarr:latest
    import re
    try:
        log_message(f"Downloading GitHub container image from {pkg_url}")
        m = re.match(r"https://github.com/([^/]+)/([^/]+)/pkgs/container/([^/]+)", pkg_url)
        if not m:
            log_message("Invalid GitHub container package URL format")
            return False
        owner, repo, name = m.groups()
        image_name = f"ghcr.io/{owner}/{name}:latest"
        return download_docker_image(image_name)
    except Exception as e:
        log_message(f"Failed to download GitHub container image from {pkg_url}: {e}")
        return False

def week_probability_adjustment(week_num):
    """Return a multiplier for probabilities based on the week number."""
    # Use a simple deterministic function: sine wave with some noise
    import math
    # Centered around 1, e.g. from 0.8 to 1.25
    base = 1.0 + 0.15 * math.sin(week_num / 2.0)  # smooth variant week-to-week
    # Add a small deterministic "jitter" per week (repeatable)
    random.seed(week_num ^ 0xA0A7)
    jitter = random.uniform(-0.05, 0.07)
    adj = base + jitter
    # Clamp to [0.7, 1.35] to avoid extremes
    return max(0.7, min(1.35, adj))

def main():
    """Main function that executes the download logic."""
    log_message("Starting download job")
    
    now = datetime.now()
    week_num = now.isocalendar()[1]
    prob_adj = week_probability_adjustment(week_num)
    log_message(f"Week number: {week_num}, probability adjustment multiplier: {prob_adj:.3f}")
    
    # Set random seed for reproducibility within the same minute
    random.seed(int(now.timestamp() / 60))
    
    results = []
    now_ts = int(time.time())
    cutoff_ts = 1762339200  # November 5, 2025

    # 1. 100% chance to download HuggingFace dataset
    log_message("Task 1: Downloading HuggingFace dataset (100% chance)")
    success = download_huggingface_dataset("a0a7/Gregg-1916")
    results.append(("HuggingFace dataset a0a7/Gregg-1916", success))
    
    # 2. 30% chance to download HuggingFace model (week-dependent)
    if random.random() < 0.30 * prob_adj:
        log_message("Task 2: Downloading HuggingFace model (probability adjusted)")
        success = download_huggingface_model("a0a7/gregg-recognition")
        results.append(("HuggingFace model a0a7/gregg-recognition", success))
    else:
        log_message("Task 2: Skipping HuggingFace model download (probability adjusted)")
        results.append(("HuggingFace model a0a7/gregg-recognition", "skipped"))
    
    # 3. 85% chance to download npm package (week-dependent)
    if random.random() < 0.85 * prob_adj:
        log_message("Task 3: npm package download (probability adjusted)")
        if check_npm_package_exists("fastgeotoolkit"):
            log_message("fastgeotoolkit exists, downloading it instead")
            success = download_npm_package("fastgeotoolkit")
            results.append(("npm package fastgeotoolkit", success))
        else:
            log_message("fastgeotoolkit doesn't exist, downloading heatmap-parse")
            success = download_npm_package("heatmap-parse")
            results.append(("npm package heatmap-parse", success))
    else:
        log_message("Task 3: Skipping npm package download (probability adjusted)")
        results.append(("npm package", "skipped"))
    
    # 4. 95% chance to download crates package (week-dependent)
    if random.random() < 0.95 * prob_adj:
        log_message("Task 4: crates package download (probability adjusted)")
        if check_crates_package_exists("fastgeotoolkit"):
            log_message("fastgeotoolkit crate exists, downloading it instead")
            success = download_crates_package("fastgeotoolkit")
            results.append(("crates package fastgeotoolkit", success))
        else:
            log_message("fastgeotoolkit crate doesn't exist, downloading heatmap-parse")
            success = download_crates_package("heatmap-parse")
            results.append(("crates package heatmap-parse", success))
    else:
        log_message("Task 4: Skipping crates package download (probability adjusted)")
        results.append(("crates package", "skipped"))
    
    # 5. 40% chance to download Docker image (week-dependent)
    if random.random() < 0.40 * prob_adj:
        log_message("Task 5: Downloading Docker image (probability adjusted)")
        success = download_docker_image("a0a7/publicbroadcastarr")
        results.append(("Docker image a0a7/publicbroadcastarr", success))
    else:
        log_message("Task 5: Skipping Docker image download (probability adjusted)")
        results.append(("Docker image a0a7/publicbroadcastarr", "skipped"))

    # --- NEW LOGIC for GitHub Packages (until Nov 5, 2025) ---
    if now_ts <= cutoff_ts:
        # 80% chance: download/install fastgeotoolkit from GitHub npm (week-dependent)
        if random.random() < 0.80 * prob_adj:
            log_message("Extra Task: Downloading GitHub npm fastgeotoolkit (probability adjusted)")
            success = download_github_npm_package("https://github.com/a0a7/fastgeotoolkit/pkgs/npm/fastgeotoolkit")
            results.append(("GitHub npm package @a0a7/fastgeotoolkit", success))
        else:
            log_message("Extra Task: Skipping GitHub npm fastgeotoolkit (probability adjusted)")
            results.append(("GitHub npm package @a0a7/fastgeotoolkit", "skipped"))

        # 70% chance: download/pull publicbroadcastarr from GitHub container registry (week-dependent)
        if random.random() < 0.70 * prob_adj:
            log_message("Extra Task: Downloading GitHub container publicbroadcastarr (probability adjusted)")
            success = download_github_container_image("https://github.com/a0a7/publicbroadcastarr/pkgs/container/publicbroadcastarr")
            results.append(("GitHub container image ghcr.io/a0a7/publicbroadcastarr", success))
        else:
            log_message("Extra Task: Skipping GitHub container publicbroadcastarr (probability adjusted)")
            results.append(("GitHub container image ghcr.io/a0a7/publicbroadcastarr", "skipped"))

        # 20% chance: download/install heatmap-parse from GitHub npm (week-dependent)
        if random.random() < 0.20 * prob_adj:
            log_message("Extra Task: Downloading GitHub npm heatmap-parse (probability adjusted)")
            success = download_github_npm_package("https://github.com/a0a7/heatmap-parse/pkgs/npm/heatmap-parse")
            results.append(("GitHub npm package @a0a7/heatmap-parse", success))
        else:
            log_message("Extra Task: Skipping GitHub npm heatmap-parse (probability adjusted)")
            results.append(("GitHub npm package @a0a7/heatmap-parse", "skipped"))

        # 30% chance: download/pull svtplayarr from GitHub container registry (week-dependent)
        if random.random() < 0.30 * prob_adj:
            log_message("Extra Task: Downloading GitHub container svtplayarr (probability adjusted)")
            success = download_github_container_image("https://github.com/a0a7/svtplayarr/pkgs/container/svtplayarr")
            results.append(("GitHub container image ghcr.io/a0a7/svtplayarr", success))
        else:
            log_message("Extra Task: Skipping GitHub container svtplayarr (probability adjusted)")
            results.append(("GitHub container image ghcr.io/a0a7/svtplayarr", "skipped"))

    # Summary
    log_message("Download job completed. Summary:")
    for task, result in results:
        log_message(f"  {task}: {result}")
    
    # Log to stdout only (no file saving)
    log_message(f"Job completed at {datetime.now().isoformat()}")

if __name__ == "__main__":
    main()
