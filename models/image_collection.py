# TODO
# Load image files from base directory recursively
# Filter images by folder names (the "tag" system)
# Get random images from specified folders
# Possible edge cases (empty folders, no images found, etc)

from pathlib import Path
from typing import List, Set, Optional
import random
import os

def is_nsfw_image(filepath: Path) -> bool:
    """Check if image filename contains _nsfw tag (case-insensitive)"""
    filename = os.path.basename(str(filepath)).lower()
    return '_nsfw' in filename

class ImageCollection:
    """Manages reference images with folder-based tagging"""
    def __init__(self, base_path: Path):
        """
        Initialize

        base_path: Root directory containing reference images (Path("references/"))
        """
        self.base_path = base_path
        self.images: List[Path] = []
        self._load_images()

    def _load_images(self):
        """Recursively find all image files in base_path"""
        # Supported image formats
        extensions = {'.jpg', '.jpeg', '.png'}

        # rglob to find all files recursively
        for file_path in self.base_path.rglob("*"):
            if file_path.is_file():
                # .lower() converts all string to lowercase
                # need this bc mac/linux usually suffix lowercase, windows is uppercase
                if file_path.suffix.lower() in extensions:
                    self.images.append(file_path)

    def refresh_file(self, old_path: Path, new_path: Path):
        """Update internal cache when a file is renamed"""
        if old_path in self.images:
            index = self.images.index(old_path)
            self.images[index] = new_path

    def get_available_folders(self) -> Set[str]:
        """
        Get all unique folder names with images in them

        Returns:
            Set of folder names, e.g., {"hands", "faces", "full-body", "detailed"}
        
        :param self: Description
        :return: Description
        :rtype: Set[str]
        """
        folders = set()
        base_str = str(self.base_path)

        for image_path in self.images:
            img_str = str(image_path)

            if img_str.startswith(base_str):
                for parent in image_path.parents:
                    parent_str = str(parent)

                    if parent_str.startswith(base_str) and parent_str != base_str:
                        if parent.name:
                            folders.add(parent.name)
        return folders
    
    def get_folder_list(self) -> List[str]:
        """
        Get sorted list of available folder names to display

        :return: sorted list of folder names
        """
        folders = self.get_available_folders()
        return sorted(list(folders))


    def get_images_by_folders(self, folder_names: List[str]) -> List[Path]:
        """
        Get all images in a specific folder
        
        :param self: Description
        :param folder_names: Description
        :type folder_names: List[str]
        :return: Description
        :rtype: List[Path]
        """
        matching_images = []

        for image_path in self.images:
            parent_names = [parent.name for parent in image_path.parents]

            for folder in folder_names:
                if folder in parent_names:
                    matching_images.append(image_path)
                    break

        return matching_images

    def get_random_image(
            self, 
            folder_names: Optional[List[str]] = None, 
            exclude: Optional[Path] = None,
            nsfw_filter: str = "all"
            ) -> Path:
        """
        Get one random image from specified folder with NSFW filtering
        
        :param self: Description
        :param folder_names: List of folder names to search
        :type folder_names: List[str]
        :param exclude: Image to exclude
        :type exclude: Optional[Path]
        :param nsfw_filter: Filter mode - "all", "sfw", or "nsfw"
        :type nsfw_filter: str
        :return: Random image path
        :rtype: Path
        """
        if folder_names:
            candidates = self.get_images_by_folders(folder_names)
        else:
            candidates = self.images.copy()
        
        # Apply NSFW filter (case-insensitive)
        if nsfw_filter == "sfw":
            candidates = [img for img in candidates if not is_nsfw_image(img)]
        elif nsfw_filter == "nsfw":
            candidates = [img for img in candidates if is_nsfw_image(img)]
        # "all" = no filtering
        
        if exclude and exclude in candidates:
            candidates.remove(exclude)

        if len(candidates) == 0:
            if folder_names:
                raise ValueError(f"Error, no images found in folders: {folder_names}")
            else:
                raise ValueError("No images found in collection")
        
        return random.choice(candidates)