"""
Shared font configuration for all molipe screens
"""
from tkinter import font as tkfont

# Font families
FONT_FAMILY_PRIMARY = "Sunflower"
FONT_FAMILY_FALLBACK = "TkDefaultFont"

# Font sizes
TITLE_FONT_SIZE = 48
BUTTON_FONT_SIZE = 20
ITEM_FONT_SIZE = 24
STATUS_FONT_SIZE = 14
SMALL_FONT_PT = 27
BIG_FONT_PT = 29
METADATA_FONT_PT = 18

class FontManager:
    """Manages font creation with fallback"""
    
    def __init__(self):
        self._fonts = {}
        self._init_fonts()
    
    def _init_fonts(self):
        """Initialize all fonts with fallback handling"""
        try:
            self._fonts['title'] = tkfont.Font(
                family=FONT_FAMILY_PRIMARY, size=TITLE_FONT_SIZE, weight="bold"
            )
            self._fonts['button'] = tkfont.Font(
                family=FONT_FAMILY_PRIMARY, size=BUTTON_FONT_SIZE, weight="bold"
            )
            self._fonts['item'] = tkfont.Font(
                family=FONT_FAMILY_PRIMARY, size=ITEM_FONT_SIZE, weight="normal"
            )
            self._fonts['status'] = tkfont.Font(
                family=FONT_FAMILY_PRIMARY, size=STATUS_FONT_SIZE, weight="normal"
            )
            self._fonts['small'] = tkfont.Font(
                family=FONT_FAMILY_PRIMARY, size=SMALL_FONT_PT, weight="bold"
            )
            self._fonts['big'] = tkfont.Font(
                family=FONT_FAMILY_PRIMARY, size=BIG_FONT_PT, weight="bold"
            )
            self._fonts['metadata'] = tkfont.Font(
                family=FONT_FAMILY_PRIMARY, size=METADATA_FONT_PT, weight="normal"
            )
        except Exception:
            # Fallback to default fonts
            self._fonts['title'] = tkfont.Font(
                family=FONT_FAMILY_FALLBACK, size=TITLE_FONT_SIZE, weight="bold"
            )
            self._fonts['button'] = tkfont.Font(
                family=FONT_FAMILY_FALLBACK, size=BUTTON_FONT_SIZE, weight="bold"
            )
            self._fonts['item'] = tkfont.Font(
                family=FONT_FAMILY_FALLBACK, size=ITEM_FONT_SIZE, weight="normal"
            )
            self._fonts['status'] = tkfont.Font(
                family=FONT_FAMILY_FALLBACK, size=STATUS_FONT_SIZE, weight="normal"
            )
            self._fonts['small'] = tkfont.Font(
                family=FONT_FAMILY_FALLBACK, size=SMALL_FONT_PT, weight="bold"
            )
            self._fonts['big'] = tkfont.Font(
                family=FONT_FAMILY_FALLBACK, size=BIG_FONT_PT, weight="bold"
            )
            self._fonts['metadata'] = tkfont.Font(
                family=FONT_FAMILY_FALLBACK, size=METADATA_FONT_PT, weight="normal"
            )
    
    def get(self, font_name):
        """Get a font by name"""
        return self._fonts.get(font_name, self._fonts['button'])
    
    @property
    def title(self):
        return self._fonts['title']
    
    @property
    def button(self):
        return self._fonts['button']
    
    @property
    def item(self):
        return self._fonts['item']
    
    @property
    def status(self):
        return self._fonts['status']
    
    @property
    def small(self):
        return self._fonts['small']
    
    @property
    def big(self):
        return self._fonts['big']
    
    @property
    def metadata(self):
        return self._fonts['metadata']