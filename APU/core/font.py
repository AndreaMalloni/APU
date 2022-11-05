import pygame as pg
import os
from APU.utility import clip, palette_swap

class Font():
    """Font

    Represents a custom font object generated from a font image.
    Provides methods to render any kind of string and to change the font color.
    """
    def __init__(self, path:str, colorkey:pg.Color = (0, 0, 0), spacing:int = 1, separatorRGBAColor:int = 127) -> None:
        """Constructs a custom font object

        Args:
            path (str): font image path
            colorkey (pg.Color, optional): background color, transparency is applied. Defaults to (0, 0, 0) [black].
            spacing (int, optional): pixels of distance between characters in rendered strings. Defaults to 1.
            separatorRGBAColor (int, optional): color value of the separators in font image. Defaults to 127 [grey].

        Raises:
            FileNotFoundError: if the given font image file does not exist.
        """
        if not os.path.exists(path): 
            raise FileNotFoundError(f"Font file not found: {path}")

        self.spacing = spacing
        self.colorkey = colorkey
        self.character_order = [
            'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z',
            'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',
            '.','-',',',':','+','\'','!','?',
            '0','1','2','3','4','5','6','7','8','9',
            '(',')','/','_','=','\\','[',']','*','"','<','>',';'
            ]
     
        self.characters = {}
        
        fontImg = pg.image.load(path).convert()
        fontImg.set_colorkey(self.colorkey)

        self.__splitFontImg(fontImg, separatorRGBAColor)
        self.spaceSize = self.characters['A'].get_width()

    def __splitFontImg(self, fontImg:pg.Surface, separatorRGBAColor:int) -> None:
        """Splits the font image into single characters by iterating through all pixels in x axis at y = 0
        and clipping the image whenever the current pixel color matches separatorRGBAColor.

        This method is private and is used only during object initialization.

        Args:
            fontImg (pg.Surface): font image to split.
            separatorRGBAColor (int): color value of the separators in font image.
        """
        currentCharWidth = 0
        charCount = 0

        for x in range(fontImg.get_width()):
            char = fontImg.get_at((x, 0))
            if char[0] == separatorRGBAColor:
                char_img = clip(fontImg, x - currentCharWidth, 0, currentCharWidth, fontImg.get_height())
                self.characters[self.character_order[charCount]] = char_img.copy()
                charCount += 1
                currentCharWidth = 0
            else:
                currentCharWidth += 1

    def render(self, surf:pg.Surface, text:str, position:tuple[int, int]) -> None:
        """Renders the given text using characters from the font image.

        Args:
            surf (pg.Surface): (pygame) surface to render the text to.
            text (str): string to render.
            position (tuple[int, int]): (x, y) text position on the surface.
        """
        x_offset = 0
        for char in text:
            if char != ' ':
                surf.blit(self.characters[char], (position[0] + x_offset, position[1]))
                x_offset += self.characters[char].get_width() + self.spacing
            else:
                x_offset += self.spaceSize + self.spacing
    
    def changeColor(self, oldColor:pg.Color, newColor:pg.Color) -> None:
        """Changes the the given color in the font with a new one.

        Args:
            oldColor (pg.Color): color to replace.
            newColor (pg.Color): new font color.
        """
        for char in self.characters:
            self.characters[char] = palette_swap(self.characters[char], oldColor, newColor)
            self.characters[char].set_colorkey(self.colorkey)
