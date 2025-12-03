import os
import shutil
import random

images_dir = r"C:\Users\zaro\Documents\_Dev\aws\school_proj\dataset\images\train"
labels_dir = r"C:\Users\zaro\Documents\_Dev\aws\school_proj\dataset\labels\train"
dataset_dir = r"C:\Users\zaro\Documents\_Dev\aws\school_proj\dataset"
train_ratio = 0.8
num_classes = 6

for folder in ["train", "val"]:
    os.makedirs(os.path.join(dataset_dir, "images", folder), exist_ok=True)
    os.makedirs(os.path.join(dataset_dir, "labels", folder), exist_ok=True)

all_images = [f for f in os.listdir(images_dir) if f.lower().endswith((".jpg", ".png"))]
random.shuffle(all_images)

split_idx = int(len(all_images) * train_ratio)
train_images = all_images[:split_idx]
val_images = all_images[split_idx:]

def move_files(img_list, split):
    for img in img_list:
        shutil.move(os.path.join(images_dir, img),
                    os.path.join(dataset_dir, "images", split, img))
        
        label_file = os.path.splitext(img)[0] + ".txt"
        label_path = os.path.join(labels_dir, label_file)
        if os.path.exists(label_path):
            fixed_lines = []
            with open(label_path, "r") as f:
                for line in f.readlines():
                    parts = line.strip().split()
                    class_id = int(parts[0])
                    if class_id >= num_classes:
                        class_id = num_classes - 1
                    fixed_lines.append(" ".join([str(class_id)] + parts[1:]))

            with open(label_path, "w") as f:
                f.write("\n".join(fixed_lines) + "\n")
            
            shutil.move(label_path,
                        os.path.join(dataset_dir, "labels", split, label_file))
        else:
            print(f"Warning: Label file not found for {img}")

move_files(train_images, "train")
move_files(val_images, "val")

print("Dataset split complete!")
print(f"Train images: {len(train_images)}, Validation images: {len(val_images)}")
