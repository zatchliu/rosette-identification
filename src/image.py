from pathlib import Path


class Image:
    """
    Represents a single image within the Rosette Identification workflow.
    """

    def __init__(self, img_path: str):
        """
        Initialize an Image object.

        Args:
            img_path (str): Filesystem path to the image file.

        Returns:
            None
        """
        self.img_path = Path(img_path)

    def contrast(self, contrast: float) -> None:
        """
        Adjust the contrast of the image.

        Args:
            contrast (float): Desired contrast factor.

        Returns:
            None
        """
        # Placeholder — will later use OpenCV or similar
        return

    def noise(self, noise: float) -> None:
        """
        Apply noise reduction to the image.

        Args:
            noise (float): Noise reduction level.

        Returns:
            None
        """
        # Placeholder — will later use OpenCV or similar
        return

    @staticmethod
    def from_path(img_path: str) -> "Image":
        """
        Create an Image object from a filesystem path.

        Args:
            img_path (str): Filesystem path to the image.

        Returns:
            Image: Wrapped image instance.
        """
        return Image(img_path)

    def __repr__(self) -> str:
        """
        Return a string representation for debugging.

        Returns:
            str: Readable description of the image object.
        """
        return f"Image(path='{self.img_path}')"