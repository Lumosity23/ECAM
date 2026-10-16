"""
Showcase/demo for pygame_ui widgets
Run with: python -m pygame_ui.demo.showcase
"""

import pygame
import pygame_ui
from pygame_ui import UIManager, UIButton, UISlider, UISwitch, UIStat, \
    UISlider, UIProgressBar, UIRange, UIText, UIPanel, UITourniquet, UIFloatingText
import random
import time


class DemoState:
    """Hold demo state and callbacks"""
    def __init__(self):
        self.slider_value = 0.5
        self.switch_state = False
        self.progress_value = 0.0
        self.range_value = 0.5
        self.selected_item = "Option A"
        self.counter = 0
        self.last_floating_time = 0
        self.floating_texts = []
        
        # Callback functions
        def on_slider_change(value):
            self.slider_value = value
            self.progress_value = value
            self.range_value = value
            
        def on_switch_change(state):
            self.switch_state = state
            
        def on_tourniquet_select(index):
            items = ["Option A", "Option B", "Option C", "Option D"]
            if 0 <= index < len(items):
                self.selected_item = items[index]
        
        self.on_slider_change = on_slider_change
        self.on_switch_change = on_switch_change
        self.on_tourniquet_select = on_tourniquet_select
    
    def get_counter_text(self):
        return str(self.counter)
    
    def get_fps_text(self):
        return f"{demo_clock.get_fps():.1f} FPS"


def create_demo_panel(ui_manager: UIManager, state: DemoState) -> UIPanel:
    """Create a demo panel showing various widgets"""
    panel = UIPanel(20, 20, 760, 560, color=(30, 30, 40))
    panel.set_label("pygame_ui Widget Demo", 36)
    
    # Title
    title = UIText(40, 80, "Widget Demonstration", 32, (200, 200, 255))
    panel.add_child(title)
    
    # Section: Basic Widgets
    section_y = 130
    section_label = UIText(40, section_y, "Basic Widgets", 24, (150, 150, 255))
    panel.add_child(section_label)
    
    # Button
    def button_click():
        state.counter += 1
        print(f"Button clicked! Count: {state.counter}")
    
    btn = UIButton(40, section_y + 40, "Click Me!", button_click, 
                   color=(70, 130, 180), size_text=24)
    panel.add_child(btn)
    
    # Counter display
    counter_label = UIText(200, section_y + 45, "Clicks:", 24, (200, 200, 200))
    counter_value = UIText(280, section_y + 45, state.get_counter_text, 
                          24, (255, 255, 100), text_update=True)
    panel.add_child(counter_label)
    panel.add_child(counter_value)
    
    # Slider
    slider_label = UIText(40, section_y + 100, "Slider Value:", 24, (200, 200, 200))
    slider_value_text = UIText(250, section_y + 100, 
                              lambda: f"{int(state.slider_value * 100)}%", 
                              24, (255, 255, 100), text_update=True)
    slider = UISlider(350, section_y + 100, 200, 30, 
                     initial_value=state.slider_value,
                     on_change_callback=state.on_slider_change)
    panel.add_child(slider_label)
    panel.add_child(slider_value_text)
    panel.add_child(slider)
    
    # Switch
    switch_label = UIText(40, section_y + 160, "Switch:", 24, (200, 200, 200))
    switch_state_text = UIText(200, section_y + 160,
                              lambda: "ON" if state.switch_state else "OFF",
                              24, (100, 255, 100) if state.switch_state else (255, 100, 100),
                              text_update=True)
    switch = UISwitch(250, section_y + 160, "Enable Feature", 
                     state.on_switch_change,
                     start_state=state.switch_state,
                     size_text=24)
    panel.add_child(switch_label)
    panel.add_child(switch_state_text)
    panel.add_child(switch)
    
    # Progress Bar
    prog_label = UIText(40, section_y + 220, "Progress Bar:", 24, (200, 200, 200))
    prog_text = UIText(250, section_y + 220,
                      lambda: f"{int(state.progress_value * 100)}%",
                      24, (255, 255, 100), text_update=True)
    progress = UIProgressBar(350, section_y + 220, 200, 25,
                            value=state.progress_value,
                            bg_color=(60, 60, 60),
                            fill_color=(70, 130, 180))
    panel.add_child(prog_label)
    panel.add_child(prog_text)
    panel.add_child(progress)
    
    # Range Widget (simplified display)
    range_label = UIText(40, section_y + 270, "Range Indicator:", 24, (200, 200, 200))
    range_text = UIText(200, section_y + 270,
                       lambda: f"Range: {int(state.range_value * 100)}m",
                       24, (255, 255, 100), text_update=True)
    # Simple visual representation
    range_bar = UIProgressBar(300, section_y + 270, 150, 20,
                             value=state.range_value,
                             bg_color=(60, 60, 60),
                             fill_color=(100, 200, 100),
                             show_text=False)
    panel.add_child(range_label)
    panel.add_child(range_text)
    panel.add_child(range_bar)
    
    # Section: Selection Widgets
    section_y = 380
    section_label2 = UIText(40, section_y, "Selection Widgets", 24, (150, 150, 255))
    panel.add_child(section_label2)
    
    # Tourniquet/Carousel
    t_label = UIText(40, section_y + 40, "Choose Option:", 24, (200, 200, 200))
    t_value = UIText(250, section_y + 40,
                    lambda: state.selected_item,
                    24, (255, 255, 100), text_update=True)
    tourniquet = UITourniquet(350, 180, 300, 100,
                             ["Option A", "Option B", "Option C", "Option D", "Option E"])
    # Note: We'd need to connect the tourniquet's selection to our state
    # For demo, we'll just show it
    panel.add_child(t_label)
    panel.add_child(t_value)
    panel.add_child(tourniquet)
    
    # Instructions
    instr_y = 500
    instr1 = UIText(40, instr_y, "Try interacting with the widgets above!", 20, (180, 180, 180))
    instr2 = UIText(40, instr_y + 25, "Press F1 to toggle edit mode (drag widgets)", 20, (180, 180, 180))
    panel.add_child(instr1)
    panel.add_child(instr2)
    
    return panel


def main():
    """Main demo function"""
    pygame.init()
    pygame.font.init()
    
    # Set up display
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("pygame_ui Showcase")
    
    # Create UIManager
    ui = UIManager((width, height))
    
    # Create demo state
    state = DemoState()
    
    # Create and add demo panel
    demo_panel = create_demo_panel(ui, state)
    ui.root.add_child(demo_panel)
    
    # Simple sprite manager mock for panels that need it
    class MockSpriteManager:
        def get_ui_panel(self, w, h, color=(100, 100, 150, 200)):
            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.rect(surf, color, (0, 0, w, h), border_radius=8)
            return surf
    
    sprite_manager = MockSpriteManager()
    ui.set_sprite_manager(sprite_manager)
    
    # Clock for timing
    global demo_clock
    demo_clock = pygame.time.Clock()
    
    # Main loop
    running = True
    while running:
        dt = demo_clock.tick(60) / 1000.0  # Delta time in seconds
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            
            # Let UI handle the event
            ui.handle_event(event)
        
        # Update
        ui.update(dt)
        
        # Draw
        screen.fill((20, 20, 30))  # Dark background
        ui.draw(screen)
        
        # Display FPS
        fps_text = f"FPS: {demo_clock.get_fps():.1f}"
        font = pygame.font.Font(None, 24)
        fps_surface = font.render(fps_text, True, (255, 255, 255))
        screen.blit(fps_surface, (width - 100, 10))
        
        pygame.display.flip()
    
    pygame.quit()


if __name__ == "__main__":
    main()