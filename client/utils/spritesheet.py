import pygame

class SpriteSheet:
	def __init__(self, image) -> None:
		self.sheet = image

	def get_image(self, frame, y_offset, width, height, scale, colour) -> pygame.Surface:
		image = pygame.Surface((width, height)).convert_alpha()
		image.blit(self.sheet, (0, 0), ((frame * width), (height * y_offset), width, height))
		image = pygame.transform.scale(image, (width * scale, height * scale))
		image.set_colorkey(colour)

		return image