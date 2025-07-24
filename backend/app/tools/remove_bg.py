from rembg import remove


class ImageService:
    def remove_background(self, image: bytes) -> bytes:
        try:
            output_image = remove(image)
            return output_image
        except ValueError:
            raise


def get_image_service():
    return ImageService()



