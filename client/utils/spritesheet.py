import pygame

class SpriteSheet:

	"""
	Classe responsável por manipular e extrair imagens de uma spritesheet.

	Permite o corte de imagens individuais de uma spritesheet, seu redimensionamento e a aplicação de uma cor de transparência.
	"""

	def __init__(self, image) -> None:

		"""
		Inicializa a classe `SpriteSheet`.

		Args:
			image (pygame.Surface): A imagem da spritesheet carregada, que contém todos os sprites.
		"""

		self.sheet = image

	def get_image(self, frame, y_offset, width, height, scale, colour) -> pygame.Surface:

		"""
		Extrai uma imagem específica da spritesheet, redimensiona e aplica uma cor de transparência.

		Args:
			frame (int): O índice da coluna (ou quadro) do sprite na spritesheet.
			y_offset (int): O índice da linha do sprite na spritesheet.
			width (int): A largura de cada sprite (em pixels).
			height (int): A altura de cada sprite (em pixels).
			scale (int): O fator de escala para redimensionar o sprite.
			colour (tuple): A cor (R, G, B) que será tratada como transparente.

		Returns:
			pygame.Surface: A imagem extraída da spritesheet, redimensionada e com a cor de transparência definida.
		"""

		image = pygame.Surface((width, height)).convert_alpha()
		image.blit(self.sheet, (0, 0), ((frame * width), (height * y_offset), width, height))
		image = pygame.transform.scale(image, (width * scale, height * scale))
		image.set_colorkey(colour)

		return image