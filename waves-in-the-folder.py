import os

def get_folder_stats_sorted(root_folder='.'):
    folder_stats = []
    
    for foldername, subfolders, filenames in os.walk(root_folder):
        num_files = len(filenames)
        total_size = sum(os.path.getsize(os.path.join(foldername, f)) for f in filenames)
        folder_stats.append((foldername, num_files, total_size))
    
    # Sort by folder name
    folder_stats.sort(key=lambda x: x[0])
    
    # Print the folder info sorted by folder name
    for foldername, num_files, total_size in folder_stats:
        print(f"Folder: {foldername}, Number of files: {num_files}, Total size: {total_size / (1024 * 1024):.2f} MB")

# Run the function on the current folder
get_folder_stats_sorted('.')