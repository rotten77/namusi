import sys
import pygame
from .namusi_gui import NamusiGUI as namusi_gui
from .namusi_buttons import NamusiButtons, NamusiButtonsActions
from .namusi_dialogs import NamusiDialogs as namusi_dialogs
from .namusi_image import NamusiImage
from .namusi_notes import NamusiNotes, NamusiNotesActions
from .namusi_grid import NamusiGrid

def main():
    pygame.init()
    window = pygame.display.set_mode((namusi_gui.WIDTH, namusi_gui.HEIGHT))
    # clock = pygame.time.Clock()

    # pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_ARROW)
    buttons = NamusiButtons(window)
    buttons.add_button('load_image', 'Load image', (0, namusi_gui.HEIGHT-namusi_gui.BUTTON_HEIGHT), (namusi_gui.BUTTON_WIDTH, namusi_gui.BUTTON_HEIGHT), color=(0, 80, 255))
    buttons.add_button('rotate_image', 'Rotate image', (namusi_gui.BUTTON_WIDTH*1, namusi_gui.HEIGHT-namusi_gui.BUTTON_HEIGHT), (namusi_gui.BUTTON_WIDTH, namusi_gui.BUTTON_HEIGHT), color=(0, 80, 255))
    buttons.add_button('select_region', 'Select area', (namusi_gui.BUTTON_WIDTH*2, namusi_gui.HEIGHT-namusi_gui.BUTTON_HEIGHT), (namusi_gui.BUTTON_WIDTH, namusi_gui.BUTTON_HEIGHT), color=(0, 80, 255))
    # buttons.add_button('export_midi', 'Export MIDI', (namusi_gui.BUTTON_WIDTH*1, namusi_gui.HEIGHT-namusi_gui.BUTTON_HEIGHT), (namusi_gui.BUTTON_WIDTH, namusi_gui.BUTTON_HEIGHT), color=(0, 120, 80))
    # buttons.add_button('set_scale', 'Set scale', (namusi_gui.BUTTON_WIDTH*2, namusi_gui.HEIGHT-namusi_gui.BUTTON_HEIGHT), (namusi_gui.BUTTON_WIDTH, namusi_gui.BUTTON_HEIGHT), color=(0, 120, 80))
    # buttons.add_button('set_octaves', 'Set octaves', (namusi_gui.BUTTON_WIDTH*3, namusi_gui.HEIGHT-namusi_gui.BUTTON_HEIGHT), (namusi_gui.BUTTON_WIDTH, namusi_gui.BUTTON_HEIGHT), color=(0, 120, 80))
    # buttons.add_button('play', 'Play', (namusi_gui.BUTTON_WIDTH*4, namusi_gui.HEIGHT-namusi_gui.BUTTON_HEIGHT), (namusi_gui.BUTTON_WIDTH, namusi_gui.BUTTON_HEIGHT), color=(0, 120, 80))
    buttons.add_button('quit', 'Quit', (namusi_gui.WIDTH-namusi_gui.BUTTON_WIDTH, namusi_gui.HEIGHT-namusi_gui.BUTTON_HEIGHT), (namusi_gui.BUTTON_WIDTH, namusi_gui.BUTTON_HEIGHT), color=(255, 80, 120))
    note_dragged = -1
    notes = NamusiNotes(window)
    image = NamusiImage(window)
    namusi_grid = NamusiGrid(window)

    running = True
    note_pressed = -1
    note_dragged = False
    note_mouse_offset = (0, 0)

    # ===
    # image.load(r'C:\\Users\\zatloukal\\Documents\\dev\\namusi\\11412072_10207290495084702_3856441424234167424_o.jpg')
    # namusi_gui.region = ((100, 100), (800, 600))
    # ===

    while running:
        mouse = pygame.mouse.get_pos()
        buttons_actions = NamusiButtonsActions(window, mouse, buttons)
        window.fill(namusi_gui.BACKGROUND)
        namusi_gui.any_button_hovered = False
        namusi_gui.any_note_hovered = False

        image.draw()
        namusi_grid.draw()
        
        if not image.is_set():
            buttons_actions.disable(['rotate_image', 'select_region'])
        else:
            buttons_actions.enable(['rotate_image'])
            if not namusi_gui.region_selection_start and not namusi_gui.region_selection:
                buttons_actions.enable(['select_region'])
        buttons_actions.draw()

        notes_actions = NamusiNotesActions(window, mouse, notes)
        notes_actions.draw()



        for event in pygame.event.get():
            buttons_actions = NamusiButtonsActions(window, mouse, buttons)
            button_id = buttons_actions.button_pressed()
        
            if event.type == pygame.QUIT:
                running = False
            
            
            if event.type == pygame.MOUSEMOTION:
                if namusi_gui.region_selection:
                    namusi_gui.region = (namusi_gui.region[0], event.pos)
                
                if note_pressed > -1:
                    # print(f"MOUSEMOTION: {note_pressed}")
                    note_dragged = True
                    notes_actions.move(note_pressed, event, note_mouse_offset)
                    
                # note_dragged = True
                # if note_pressed > -1:
                #     note_dragged = note_pressed
                # else:
                #     note_dragged = -1
            if event.type == pygame.MOUSEBUTTONDOWN:
                note_pressed = notes_actions.note_pressed()
                note_mouse_offset = notes_actions.note_mouse_offset(note_pressed)
                namusi_gui.region_selection = False
                if namusi_gui.region_selection_start:
                    namusi_gui.region = (event.pos, (event.pos[0]+5, event.pos[1]+5))
                    namusi_gui.region_selection = True
                    namusi_gui.region_selection_start = False
                # print(f"MOUSEBUTTONDOWN: {note_pressed}")

            if event.type == pygame.MOUSEBUTTONUP:
                if namusi_gui.region_selection:
                    namusi_gui.region = (namusi_gui.region[0], event.pos)
                    namusi_gui.region_selection = False
                    buttons_actions.enable('select_region')
                    break
                # print(f"MOUSEBUTTONUP: {note_pressed}")


                if note_pressed == -1 and button_id == '':
                    notes.add_note((mouse[0], mouse[1]))
                elif note_pressed > -1 and button_id == '':
                    if not note_dragged:
                        if event.button == 1: # left click
                            notes_actions.set_length(note_pressed)
                        if event.button == 3: # right click
                            notes_actions.remove(note_pressed)
                note_pressed = -1
                note_dragged = False

                if button_id == 'quit':
                    if namusi_dialogs.yesno('Quit?', 'Are you sure want to quit?'):
                        running = False

                if button_id == 'rotate_image':
                    if image.is_set():
                        image.rotate()
                
                if button_id == 'select_region':
                    namusi_gui.region_selection_start = True
                    buttons_actions.disable('select_region')

                if button_id == 'load_image':
                    load_image = True
                    if image.is_set():
                        load_image = namusi_dialogs.yesno('Load a new image', 'Are you sure want to load a new image?')

                    if load_image:
                        file_name = namusi_dialogs.select_file([("Images", '*.png *.jpg *.jpeg *.tiff')])
                        if file_name != "":
                            try:
                                image.load(file_name)
                            except Exception as ex:
                                namusi_dialogs.error('Exception', str(ex))

      
        region_surface = pygame.Surface(window.get_size(), pygame.SRCALPHA)
        pygame.draw.rect(region_surface, (0, 0, 0, 128), pygame.Rect(0, 0, namusi_gui.region[0][0], namusi_gui.HEIGHT-namusi_gui.BUTTON_HEIGHT))
        pygame.draw.rect(region_surface, (0, 0, 0, 128), pygame.Rect(namusi_gui.region[0][0], 0, namusi_gui.region[1][0]-namusi_gui.region[0][0], namusi_gui.region[0][1]))
        pygame.draw.rect(region_surface, (0, 0, 0, 128), pygame.Rect(namusi_gui.region[0][0], namusi_gui.region[1][1], namusi_gui.region[1][0]-namusi_gui.region[0][0], namusi_gui.HEIGHT-namusi_gui.region[1][1]-namusi_gui.BUTTON_HEIGHT))
        pygame.draw.rect(region_surface, (0, 0, 0, 128), pygame.Rect(namusi_gui.region[1][0], 0, namusi_gui.WIDTH-namusi_gui.region[1][0], namusi_gui.HEIGHT-namusi_gui.BUTTON_HEIGHT))
        window.blit(region_surface, (0, 0))
            
            
        cursor = pygame.SYSTEM_CURSOR_CROSSHAIR
        if namusi_gui.any_button_hovered:
            cursor = pygame.SYSTEM_CURSOR_HAND
        if namusi_gui.any_note_hovered:
            cursor = pygame.SYSTEM_CURSOR_SIZEALL 
        pygame.mouse.set_system_cursor(cursor)
        # pygame.display.flip()
        pygame.display.update()
        # clock.tick(FPS)
    pygame.quit()

if __name__ == '__main__':
    sys.exit(main())