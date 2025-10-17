from image import Image
class ImageInput:
    def __init__(self):
        """
        Initialize the ImageInput object.

        """
        pass

    def get_image_lone(self, image_path) -> Image:
        """
        Get the image from the image path.

        Args: 
            image_path(str): Path of the desired image

        Returns:
            An Image object containing the given path
        """
        image = Image(image_path)
        print("test_image_lone")
        return image
    
    def get_image_directory(self, dir_path) -> list[Image]:
        """
        Get images from directory

        Args: 
            dir_path(str): Path of the desired image database
        
        Returns:
            list of images from directory
        """
        image_dataset = []
        print("test_image_directory")
        return image_dataset

    def process_image(self, image: Image, noise, contrast):
        """
        Preprocess image for segmentation.

        Args: 
            image(Image): Path of the desired image
            noise(float): desired noise for processed image
            contrast(float): desired contrast for desired iamge

        Returns:
            None
        """
        image.contrast(contrast)
        image.noise(noise)
        print("test process_image")
        return