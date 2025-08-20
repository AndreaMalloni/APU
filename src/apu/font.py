from pathlib import Path

import pygame

from apu.core.tools import ImageTools


class Font:
    """Font

    Represents a custom font object generated from a font image.
    Provides methods to render any kind of string and to change the font color.
    """

    def __init__(
        self,
        path: str,
        color_key: pygame.Color | None = None,
        spacing: int = 1,
        rgba_separator: int = 127,
    ) -> None:
        """Constructs a custom font object

        Args:
            path (str): font image path
            color_key (pygame.Color, optional): background color, transparency is applied.
                Defaults to None.
            spacing (int, optional): pixels of distance between characters in rendered strings.
                Defaults to 1.
            rgba_separator (int, optional): color value of the separators in font image.
                Defaults to 127 [grey].

        Raises:
            FileNotFoundError: if the given font image file does not exist.
        """
        if not Path(path).exists():
            raise FileNotFoundError(f"Font file not found: {path}")

        self.spacing = spacing
        self.color_key = color_key
        self.character_order = [
            "A",
            "B",
            "C",
            "D",
            "E",
            "F",
            "G",
            "H",
            "I",
            "J",
            "K",
            "L",
            "M",
            "N",
            "O",
            "P",
            "Q",
            "R",
            "S",
            "T",
            "U",
            "V",
            "W",
            "X",
            "Y",
            "Z",
            "a",
            "b",
            "c",
            "d",
            "e",
            "f",
            "g",
            "h",
            "i",
            "j",
            "k",
            "l",
            "m",
            "n",
            "o",
            "p",
            "q",
            "r",
            "s",
            "t",
            "u",
            "v",
            "w",
            "x",
            "y",
            "z",
            ".",
            "-",
            ",",
            ":",
            "+",
            "'",
            "!",
            "?",
            "0",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "(",
            ")",
            "/",
            "_",
            "=",
            "\\",
            "[",
            "]",
            "*",
            '"',
            "<",
            ">",
            ";",
        ]

        self.characters: dict[str, pygame.Surface] = {}

        font_image = pygame.image.load(path).convert()
        if self.color_key is not None:
            font_image.set_colorkey(self.color_key)

        self.__split(font_image, rgba_separator)
        self.space_size = self.characters["A"].get_width()

    def __split(self, font_image: pygame.Surface, rgba_separator: int) -> None:
        """
        Splits the font image into single characters by iterating through all pixels in x-axis at
        y = 0 and clipping the image whenever the current pixel color matches separatorRGBAColor.

        This method is private and is used only during object initialization.

        Args:
            font_image (pygame.Surface): font image to split.
            rgba_separator (int): color value of the separators in font image.
        """
        char_w = 0
        char_count = 0

        for x in range(font_image.get_width()):
            char = font_image.get_at((x, 0))
            if char[0] == rgba_separator:
                char_img = ImageTools.clip(
                    font_image, x - char_w, 0, char_w, font_image.get_height()
                )
                self.characters[self.character_order[char_count]] = char_img.copy()
                char_count += 1
                char_w = 0
            else:
                char_w += 1

    def render(
        self,
        surf: pygame.Surface,
        text: str,
        position: tuple[int, int],
        color: pygame.Color | None = None,
    ) -> None:
        """Renders the given text using characters from the font image.

        Args:
            surf (pygame.Surface): (pygame) surface to render the text to.
            text (str): string to render.
            position (tuple[int, int]): (x, y) text position on the surface.
        """
        x_offset = 0
        for char in text:
            if char != " ":
                surf.blit(self.characters[char], (position[0] + x_offset, position[1]))
                x_offset += self.characters[char].get_width() + self.spacing
            else:
                x_offset += self.space_size + self.spacing

    def set_color(self, old_color: pygame.Color, new_color: pygame.Color) -> None:
        """Changes the given color in the font with a new one.

        Args:
            old_color (pygame.Color): color to replace.
            new_color (pygame.Color): new font color.
        """
        for char in self.characters:
            self.characters[char] = ImageTools.palette_swap(
                self.characters[char], old_color, new_color
            )
            self.characters[char].set_colorkey(self.color_key)
