import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from glob import glob
from tqdm import tqdm
from datetime import datetime

def validate_image_areas(folder_path, z_thresh=2.0):
    image_paths = sorted(glob(os.path.join(folder_path, '*.png')))
    areas = []
    widths = []
    heights = []

    print(f"\nProcessing {len(image_paths)} image(s)...\n")

    for path in tqdm(image_paths, desc="Loading images"):
        img = cv2.imread(path)
        if img is None:
            print(f"Warning: Unable to read image {path}")
            continue
        h, w = img.shape[:2]
        area = w * h
        areas.append(area)
        widths.append(w)
        heights.append(h)

    if not areas:
        print("No valid images found.")
        return

    areas = np.array(areas)
    widths = np.array(widths)
    heights = np.array(heights)

    mean_area = np.mean(areas)
    std_area = np.std(areas)
    z_scores = (areas - mean_area) / std_area
    outliers = np.abs(z_scores) > z_thresh

    log_filename = f"image_outliers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    with open(log_filename, "w") as log_file:
        log_file.write(f"Image Area Validation Log - {datetime.now()}\n")
        log_file.write(f"Directory: {folder_path}\n")
        log_file.write(f"Mean Area: {mean_area:.2f}\n")
        log_file.write(f"Standard Deviation: {std_area:.2f}\n")
        log_file.write(f"Outlier Threshold: ±{z_thresh}σ\n\n")

        outlier_count = 0
        for idx, is_outlier in enumerate(outliers):
            if is_outlier:
                outlier_count += 1
                line = (f"Outlier: {os.path.basename(image_paths[idx])} "
                        f"- {widths[idx]}x{heights[idx]} (Area: {areas[idx]})\n")
                log_file.write(line)
                print(line.strip())

        log_file.write(f"\nTotal outliers: {outlier_count} out of {len(image_paths)} images\n")

    print(f"\nLog written to: {log_filename}")

    # Plotting
    plt.figure(figsize=(10, 5))
    plt.scatter(range(len(areas)), areas, label='Images', color='blue')
    plt.scatter(np.where(outliers)[0], areas[outliers], label='Outliers', color='red')
    plt.axhline(mean_area, color='green', linestyle='--', label='Mean Area')
    plt.axhline(mean_area + z_thresh * std_area, color='orange', linestyle='--', label='+2σ')
    plt.axhline(mean_area - z_thresh * std_area, color='orange', linestyle='--', label='−2σ')
    plt.xlabel('Image Index')
    plt.ylabel('Image Area (pixels²)')
    plt.title('Scatterplot of Image Areas')
    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    folder = input("Enter the path to the folder containing .png images: ").strip()
    if not os.path.isdir(folder):
        print("Invalid directory. Please try again.")
    else:
        validate_image_areas(folder)
