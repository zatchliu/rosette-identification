from src.image_input import ImageInput
from image import Image

class TestImageInput:
    def test_get_image(self):
        """
        Tests the get_image method.
        
        Returns:
            None
        """
        input = ImageInput()
        input.get_image_lone()
        pass
    
    def test_get_directory(self):
        """
        Tests the get_directory method.

        Returns:
            None
        """
        input = ImageInput()
        input.get_image_directory()
        pass

    def test_process_image(self):
        """
        Tests the process_image method

        Returns:
            None
        """
        image = Image('')
        input = ImageInput()
        input.process_image(image, 0, 0)
        pass