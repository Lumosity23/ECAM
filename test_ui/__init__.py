"""
pygame_ui - Lightweight UI toolkit for pygame
"""

# Core
from pygame_ui.core.ui_element import UIElement
from pygame_ui.core.ui_manager import UIManager

# Widgets - re-exported for convenience
from pygame_ui.widgets.text import UIText
from pygame_ui.widgets.icon import UIIcon
from pygame_ui.widgets.dot import UIDot
from pygame_ui.widgets.panel import UIPanel
from pygame_ui.widgets.button import UIButton
from pygame_ui.widgets.slider import UISlider
from pygame_ui.widgets.switch import UISwitch
from pygame_ui.widgets.scroll import UIScroll
from pygame_ui.widgets.tourniquet import UITourniquet
from pygame_ui.widgets.progress_bar import UIProgressBar
from pygame_ui.widgets.range import UIRange
from pygame_ui.widgets.stat import UIStat
from pygame_ui.widgets.floating_text import UIFloatingText
from pygame_ui.widgets.upgrade_board import UIUpgradeBoard
from pygame_ui.widgets.compose import UICompose
from pygame_ui.widgets.text_input import UIInput

__version__ = "0.1.0"
__author__ = "Lumosity23"
__email__ = "timochazot00@gmail.com"

__all__ = [
    # Core
    "UIElement",
    "UIManager",
    # Widgets
    "UIText",
    "UIIcon",
    "UIDot",
    "UIPanel",
    "UIButton",
    "UISlider",
    "UISwitch",
    "UIScroll",
    "UITourniquet",
    "UIProgressBar",
    "UIRange",
    "UIStat",
    "UIFloatingText",
    "UIUpgradeBoard",
    "UICompose",
    "UIInput",
]