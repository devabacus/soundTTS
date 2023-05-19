from .ui import setup_menu_item, on_browser_context_menu
from anki.hooks import addHook

addHook("browser.setupMenus", setup_menu_item)
addHook("browser.onContextMenu", on_browser_context_menu)
