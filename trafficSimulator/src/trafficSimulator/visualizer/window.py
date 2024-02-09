# les commentaires sont en anglais et en français
import dearpygui.dearpygui as dpg
import random as rng
from trafficSimulator.core.vehicle import *

class Window:
    def __init__(self, simulation):
        
        self.simulation = simulation

        # parameters for the camera
        self.zoom = 7
        self.offset = (0, 0)
        self.speed = 1

        self.is_running = False

        self.is_dragging = False
        self.old_offset = (0, 0)
        self.zoom_speed = 1
        
        ######## ajout pour le "ghost vehicle" ########
        
        self.vehicles_position = {} #parametre pas utilisé pour l'instant pour avoir le x et y sur l'affichage graphique des vehicules
        self.trusted_vehicule = None # le vehicule de confiance (notre point de vue)
        self.attacker_vehicule = None # le vehicule attaquant (celui qu'on veut suivre)
        self.ghost_vehicule = None # le ghost vehicle
        
        self.ghost_vehicule_position_offset = 10 # positif pour mettre le ghost vehicle devant le attacker vehicle (pour l'instant pas négatif il faudrait changer le code)
        self.ghost_vehicule_is_spotted = False # Used to know if the ghost vehicle is spotted
        self.ghost_vehicule_is_spotted_indicator = False # Used to draw the indicator only once 
        self.ghost_vehicule_is_spotted_counter = 0 # Used to count the number of time the ghost vehicle is spotted
        self.ghost_vehicule_is_spotted_counter_for_trusted = 0 # Used to count the number of time the trusted vehicle receive the message from other vehicles spotter
        self.List_vehicule_spotter = [] # Used to store the id of the vehicles that have spotted the ghost vehicle
        self.List_vehicule_spotter_message_received = [] # Used to store the id of the vehicles that have spotted the ghost vehicle and the trusted vehicle receive the message from them
        
        self.List_vehicule_collision_check = [] # liste des vehicules qui ont déjà été utilisé pour une collision check optimisation        
        self.List_vehicule_collision_check_already_collision_find = [] # liste des vehicules qui ont déjà été utilisé pour une collision check optimisation
        
        self.radio_distance = 120 # distance radio pour la détection des vehicules
        self.collion_detection_distance = 20 # distance de détection de collision
        
        ######## fin ajout #########
        
        self.setup()
        self.setup_themes()
        self.create_windows()
        self.create_handlers()
        self.resize_windows()
        

    def setup(self):
        dpg.create_context()
        dpg.create_viewport(title="TrafficSimulator", width=1280, height=720)
        dpg.setup_dearpygui()

    def setup_themes(self):
        with dpg.theme() as global_theme:

            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5, category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1, category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_WindowBorderSize, 0, category=dpg.mvThemeCat_Core)
                # dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, (8, 6), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_Button, (90, 90, 95))
                dpg.add_theme_color(dpg.mvThemeCol_Header, (0, 91, 140))
                
            with dpg.theme_component(dpg.mvInputInt):
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (90, 90, 95), category=dpg.mvThemeCat_Core)
                # dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5, category=dpg.mvThemeCat_Core)

        dpg.bind_theme(global_theme)

        # dpg.show_style_editor()

        with dpg.theme(tag="RunButtonTheme"):
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, (5, 150, 18))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (12, 207, 23))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (2, 120, 10))

        with dpg.theme(tag="StopButtonTheme"):
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, (150, 5, 18))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (207, 12, 23))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (120, 2, 10))

    def create_windows(self):
        dpg.add_window(
            tag="MainWindow",
            label="Simulation",
            no_close=True,
            no_collapse=True,
            no_resize=True,
            no_move=True
        )
        
        dpg.add_draw_node(tag="OverlayCanvas", parent="MainWindow")
        dpg.add_draw_node(tag="Canvas", parent="MainWindow")

        with dpg.window(
            tag="ControlsWindow",
            label="Controls",
            no_close=True,
            no_collapse=True,
            no_resize=True,
            no_move=True
        ):
            with dpg.collapsing_header(label="Simulation Control", default_open=True):

                with dpg.group(horizontal=True):
                    dpg.add_button(label="Run", tag="RunStopButton", callback=self.toggle)
                    dpg.add_button(label="Next frame", callback=self.simulation.update)

                dpg.add_slider_int(tag="SpeedInput", label="Speed", min_value=1, max_value=100,default_value=1, callback=self.set_speed)
            
            with dpg.collapsing_header(label="Simulation Status", default_open=True):

                with dpg.table(header_row=False):
                    dpg.add_table_column()
                    dpg.add_table_column()
                    
                    with dpg.table_row():
                        dpg.add_text("Status:")
                        dpg.add_text("_", tag="StatusText")

                    with dpg.table_row():
                        dpg.add_text("Time:")
                        dpg.add_text("_s", tag="TimeStatus")

                    with dpg.table_row():
                        dpg.add_text("Frame:")
                        dpg.add_text("_", tag="FrameStatus")
                        
                        
            
            
            with dpg.collapsing_header(label="Camera Control", default_open=True):
    
                dpg.add_slider_float(tag="ZoomSlider", label="Zoom", min_value=0.1, max_value=100, default_value=self.zoom,callback=self.set_offset_zoom)            
                with dpg.group():
                    dpg.add_slider_float(tag="OffsetXSlider", label="X Offset", min_value=-100, max_value=100, default_value=self.offset[0], callback=self.set_offset_zoom)
                    dpg.add_slider_float(tag="OffsetYSlider", label="Y Offset", min_value=-100, max_value=100, default_value=self.offset[1], callback=self.set_offset_zoom)
                    
            with dpg.collapsing_header(label="Legend", default_open=True):
                # Add a text to explain the color of the vehicles
                with dpg.group(horizontal=True):
                    dpg.add_color_button(default_value=(0, 255, 0, 255), no_border=True, no_alpha=True, width=20, height=20)
                    dpg.add_text("Green: Trusted vehicle")

                with dpg.group(horizontal=True):
                    dpg.add_color_button(default_value=(255, 0, 0, 255), no_border=True, no_alpha=True, width=20, height=20)
                    dpg.add_text("Red: Attacker vehicle")
                
                with dpg.group(horizontal=True):
                    dpg.add_color_button(default_value=(0, 0, 255, 255), no_border=True, no_alpha=True, width=20, height=20)
                    dpg.add_text("Blue: Other vehicle")

                with dpg.group(horizontal=True):
                    dpg.add_color_button(default_value=(125, 125, 125, 125), no_border=True, no_alpha=True, width=20, height=20)
                    dpg.add_text("Grey: Spotter ghost ")

                with dpg.group(horizontal=True):
                    dpg.add_color_button(default_value=(255, 255, 0, 255), no_border=True, no_alpha=True, width=20, height=20)
                    dpg.add_text("Yellow: Ghost vehicle")        
                     
            with dpg.collapsing_header(label="Vehicle Control", default_open=True):
                dpg.add_button(label="Add Vehicle", callback=self.add_vehicle)
            
                # Add a button to define the trusted vehicle and the attacker
                dpg.add_button(label=f"Define Trusted and attacker", callback=self.define_trusted_and_attacker)
                
                # Add a button to create a ghost vehicle
                dpg.add_button(label=f"Create ghost vehicle", callback=self.create_ghost_vehicle)
                
            with dpg.collapsing_header(label="Ghost Vehicle Status", default_open=True):
                
                with dpg.table(header_row=False):
                    dpg.add_table_column()
                    dpg.add_table_column()
                    
                    with dpg.table_row():
                        dpg.add_text('Counter spotter:')
                        dpg.add_text("_", tag="CounterSpottedGhostVehicle")
                        
                    with dpg.table_row():
                        dpg.add_text("Status for Trusted:")
                        dpg.add_text("not spotted", tag="GhostVehicleStatusForTrustedVehicle")
                
                dpg.add_text("Ghost vehicle not spotted",color=(0, 255, 0), tag="GhostVehicleStatus")
                
                
                
                
        
    def resize_windows(self):
        width = dpg.get_viewport_width()
        height = dpg.get_viewport_height()

        dpg.set_item_width("ControlsWindow", 300)
        dpg.set_item_height("ControlsWindow", height-38)
        dpg.set_item_pos("ControlsWindow", (0, 0))

        dpg.set_item_width("MainWindow", width-315)
        dpg.set_item_height("MainWindow", height-38)
        dpg.set_item_pos("MainWindow", (300, 0))

    def create_handlers(self):
        with dpg.handler_registry():
            dpg.add_mouse_down_handler(callback=self.mouse_down)
            dpg.add_mouse_drag_handler(callback=self.mouse_drag)
            dpg.add_mouse_release_handler(callback=self.mouse_release)
            dpg.add_mouse_wheel_handler(callback=self.mouse_wheel)
        dpg.set_viewport_resize_callback(self.resize_windows)

    def update_panels(self):
        # Update status text
        if self.is_running:
            dpg.set_value("StatusText", "Running")
            dpg.configure_item("StatusText", color=(0, 255, 0))
        else:
            dpg.set_value("StatusText", "Stopped")
            dpg.configure_item("StatusText", color=(255, 0, 0))
        
        # Update time and frame text
        dpg.set_value("TimeStatus", f"{self.simulation.t:.2f}s")
        dpg.set_value("FrameStatus", self.simulation.frame_count)

    def mouse_down(self):
        if not self.is_dragging:
            if dpg.is_item_hovered("MainWindow"):
                self.is_dragging = True
                self.old_offset = self.offset
        
    def mouse_drag(self, sender, app_data):
        if self.is_dragging:
            self.offset = (
                self.old_offset[0] + app_data[1]/self.zoom,
                self.old_offset[1] + app_data[2]/self.zoom
            )

    def mouse_release(self):
        self.is_dragging = False

    def mouse_wheel(self, sender, app_data):
        if dpg.is_item_hovered("MainWindow"):
            self.zoom_speed = 1 + 0.01*app_data

    def update_inertial_zoom(self, clip=0.005):
        if self.zoom_speed != 1:
            self.zoom *= self.zoom_speed
            self.zoom_speed = 1 + (self.zoom_speed - 1) / 1.05
        if abs(self.zoom_speed - 1) < clip:
            self.zoom_speed = 1

    def update_offset_zoom_slider(self):
        dpg.set_value("ZoomSlider", self.zoom)
        dpg.set_value("OffsetXSlider", self.offset[0])
        dpg.set_value("OffsetYSlider", self.offset[1])

    def set_offset_zoom(self):
        self.zoom = dpg.get_value("ZoomSlider")
        self.offset = (dpg.get_value("OffsetXSlider"), dpg.get_value("OffsetYSlider"))

    def set_speed(self):
        self.speed = dpg.get_value("SpeedInput")


    def to_screen(self, x, y):
        return (
            self.canvas_width/2 + (x + self.offset[0] ) * self.zoom,
            self.canvas_height/2 + (y + self.offset[1]) * self.zoom
        )

    def to_world(self, x, y):
        return (
            (x - self.canvas_width/2) / self.zoom - self.offset[0],
            (y - self.canvas_height/2) / self.zoom - self.offset[1] 
        )
    
    @property
    def canvas_width(self):
        return dpg.get_item_width("MainWindow")

    @property
    def canvas_height(self):
        return dpg.get_item_height("MainWindow")


    def draw_bg(self, color=(250, 250, 250)):
        dpg.draw_rectangle(
            (-10, -10),
            (self.canvas_width+10, self.canvas_height+10), 
            thickness=0,
            fill=color,
            parent="OverlayCanvas"
        )

    def draw_axes(self, opacity=80):
        x_center, y_center = self.to_screen(0, 0)
        
        dpg.draw_line(
            (-10, y_center),
            (self.canvas_width+10, y_center),
            thickness=2, 
            color=(0, 0, 0, opacity),
            parent="OverlayCanvas"
        )
        dpg.draw_line(
            (x_center, -10),
            (x_center, self.canvas_height+10),
            thickness=2,
            color=(0, 0, 0, opacity),
            parent="OverlayCanvas"
        )

    def draw_grid(self, unit=10, opacity=50):
        x_start, y_start = self.to_world(0, 0)
        x_end, y_end = self.to_world(self.canvas_width, self.canvas_height)

        n_x = int(x_start / unit)
        n_y = int(y_start / unit)
        m_x = int(x_end / unit)+1
        m_y = int(y_end / unit)+1

        for i in range(n_x, m_x):
            dpg.draw_line(
                self.to_screen(unit*i, y_start - 10/self.zoom),
                self.to_screen(unit*i, y_end + 10/self.zoom),
                thickness=1,
                color=(0, 0, 0, opacity),
                parent="OverlayCanvas"
            )

        for i in range(n_y, m_y):
            dpg.draw_line(
                self.to_screen(x_start - 10/self.zoom, unit*i),
                self.to_screen(x_end + 10/self.zoom, unit*i),
                thickness=1,
                color=(0, 0, 0, opacity),
                parent="OverlayCanvas"
            )

    def collision_check(self, vehicle_position, vehicle_radius_detection, vehicle_id, vehicle_radius_message_detection):
        # Check if the vehicle is in collision with another vehicle
        # the code is not optimized
        for segment in self.simulation.segments:
            for other_vehicle_id in segment.vehicles:
                
                # code pour l'optimisation:
                # - ne pas faire de collision check si le vehicule à déjà vu en collision avec un autre vehicule
                if (vehicle_id in self.List_vehicule_collision_check_already_collision_find) and other_vehicle_id != (self.ghost_vehicule or self.trusted_vehicule):
                        return True
                    
                if other_vehicle_id != vehicle_id and ( (other_vehicle_id not in self.List_vehicule_collision_check) or (other_vehicle_id in self.List_vehicule_spotter)):
                    other_vehicle = self.simulation.vehicles[other_vehicle_id]
                    progress = other_vehicle.x / segment.get_length()
                    other_position = segment.get_point(progress)
                    
                    distance = ((vehicle_position[0] - other_position[0])**2 +
                                (vehicle_position[1] - other_position[1])**2)**0.5
                    
                    
                    if vehicle_id == self.trusted_vehicule and distance < vehicle_radius_message_detection:
                        # Check if 2 vehicles with spotter argument are in the message detection range
                        if other_vehicle_id in self.List_vehicule_spotter:
                            if other_vehicle_id not in self.List_vehicule_spotter_message_received:
                                self.List_vehicule_spotter_message_received.append(other_vehicle_id)
                                self.ghost_vehicule_is_spotted_counter_for_trusted += 1
                                self.List_vehicule_spotter.remove(other_vehicle_id)
                            return 
                        
                        
                    if distance < vehicle_radius_detection:   
                        # Check if the vehicle is the ghost vehicle for the spot
                        if other_vehicle_id == self.ghost_vehicule:
                            
                            if vehicle_id != (self.attacker_vehicule or self.trusted_vehicule): # cas ou le vehicule est un autre
                                if vehicle_id not in (self.List_vehicule_spotter or self.List_vehicule_spotter_message_received):
                                    self.ghost_vehicule_is_spotted_counter += 1
                                    self.List_vehicule_spotter.append(vehicle_id)
                                if self.ghost_vehicule_is_spotted_counter_for_trusted >= 2 or vehicle_id == self.trusted_vehicule:
                                    self.ghost_vehicule_is_spotted = True
                            
                            elif vehicle_id == self.attacker_vehicule: # cas ou le vehicule est l'attaquant
                                pass
                            
                            elif vehicle_id == self.trusted_vehicule: # cas ou le vehicule est le vehicule de confiance
                                self.ghost_vehicule_is_spotted = True
                        
                        if other_vehicle_id != self.trusted_vehicule: # pour être sur que le vehicule de confiance fasse la boucle entière pour la limite de distance radio
                            self.List_vehicule_collision_check.append(vehicle_id)
                            self.List_vehicule_collision_check_already_collision_find.append(other_vehicle_id)
                        return True
                    
        self.List_vehicule_collision_check.append(vehicle_id)
        return False
    
    def add_vehicle(self):
        veh1 = Vehicle({'path': [0,8,4,17,15,13,7,3,1], 'v': 16.6})
        veh2 = Vehicle({'path': [0,2,6,12,14,16,5,11,1], 'v': 16.6})
        veh3 = Vehicle({'path': [0,2,6,12,14,16,5,9,6,12,14,16,5,11,1], 'v': 16.6})
        veh = rng.choice([veh1, veh2, veh3])
        self.simulation.add_vehicle(veh) # Add the vehicle to the simulation
    
    def define_trusted_and_attacker(self):
        choice = []
        for segment in self.simulation.segments:
            for vehicle_id in segment.vehicles:
                choice.append(vehicle_id)
                
        # Implement the logic to define a random vehicle only on a segment as trusted and in green
        self.trusted_vehicule = rng.choice(choice)
        
        # Remove the trusted vehicle from the list of vehicles
        choice.remove(self.trusted_vehicule)

        # Implement the logic to define a random vehicle as attacker and in red
        self.attacker_vehicule = rng.choice(choice)
        
        
    def create_ghost_vehicle(self):
        # Create a ghost vehicle in front of the attacker vehicle
        
        # Get the position of the attacker vehicle
        attacker_vehicle = self.simulation.vehicles[self.attacker_vehicule]
        
        # Get the segment of the attacker vehicle and it index in the list of segments
        for segment in self.simulation.segments: 
            if self.attacker_vehicule in segment.vehicles:
                attacker_vehicle_segment = segment
                break
            
                    
        # delete the last ghost vehicle from the simulation and reset the ghost vehicle indicator in the control panel
        for segment in self.simulation.segments:
            if self.ghost_vehicule in segment.vehicles:
                segment.vehicles.remove(self.ghost_vehicule) # remove the ghost vehicle from the segment
        # reset the ghost vehicle indicator
        self.ghost_vehicule_is_spotted_indicator = False
        self.ghost_vehicule_is_spotted = False
        self.ghost_vehicule_is_spotted_counter = 0
        self.ghost_vehicule_is_spotted_counter_for_trusted = 0
        dpg.delete_item("GhostVehicleStatus")
        dpg.add_text("Ghost vehicle not spotted",color=(0, 255, 0), parent="ControlsWindow", tag="GhostVehicleStatus")
    
        # create the ghost vehicle
        ghost_veh = Vehicle({'path': [0,2,6,12,14,16,5,11,1], 'v': 16.6})
        self.simulation.add_vehicle(ghost_veh, ghost=True, attacker=attacker_vehicle, attacker_vehicle_segment=attacker_vehicle_segment, ghost_vehicle_position_offset=self.ghost_vehicule_position_offset)
        self.ghost_vehicule = ghost_veh.id  
    
    def collision(self, position, collision_radius, vehicle_id, collision_radius_message, node):
        if self.collision_check(position, collision_radius, vehicle_id, collision_radius_message) == True:     
            # Draw a circle around the vehicle
            circle_radius = collision_radius 
            dpg.draw_circle(
                (0, 0),
                circle_radius * self.zoom,
                color=(255, 0, 0),  # Adjust the color as needed
                thickness=0.5*self.zoom,
                parent=node
            )
        else:
            circle_radius = collision_radius  
            dpg.draw_circle(
                (0, 0),
                circle_radius * self.zoom,
                color=(0, 255, 0),  # Adjust the color as needed
                thickness=0.5*self.zoom,
                parent=node
            )
                
        
    
    def draw_segments(self):
        for segment in self.simulation.segments:
            dpg.draw_polyline(segment.points, color=(180, 180, 220), thickness=3.5*self.zoom, parent="Canvas")
            dpg.draw_arrow(segment.points[-1], segment.points[-2], thickness=0, size=2, color=(0, 0, 0, 50), parent="Canvas")

    def draw_vehicles(self):
               
        for segment in self.simulation.segments:
            for vehicle_id in segment.vehicles:
                vehicle = self.simulation.vehicles[vehicle_id]
                progress = vehicle.x / segment.get_length()
                position = segment.get_point(progress)
                heading = segment.get_heading(progress)                
                
                node = dpg.add_draw_node(parent="Canvas")
                
                # collision check dans cette fonction car on a besoin de la position du vehicule et celle ci est calculée ici (par le draw voir fin de la fonction)
                collision_radius = self.collion_detection_distance
                message_detection_radius  = self.radio_distance
                if vehicle_id != self.ghost_vehicule:
                    self.collision(position, collision_radius, vehicle_id, message_detection_radius, node)
                

                # Draw message detection range only for the trusted vehicle
                if vehicle_id == self.trusted_vehicule:
                    dpg.draw_circle(
                        (0, 0),
                        message_detection_radius * self.zoom,
                        color=(200, 200, 100),
                        thickness=0.3*self.zoom,
                        parent=node
                    )
                
                
                # Draw the vehicle as a line
                # change la couleur pour chaque type vehicule
                if vehicle_id == self.trusted_vehicule:
                    dpg.draw_line(
                    (-vehicle.l/2, 0),
                    (vehicle.l/2, 0),
                    thickness=1.76*self.zoom,
                    color=(0, 255, 0),
                    parent=node
                )
                
                            
                elif vehicle_id == self.attacker_vehicule:
                    dpg.draw_line(
                    (-vehicle.l/2, 0),
                    (vehicle.l/2, 0),
                    thickness=1.76*self.zoom,
                    color=(255, 0, 0),
                    parent=node
                )
                    
                elif vehicle_id == self.ghost_vehicule:
                    dpg.draw_line(
                    (-vehicle.l/2, 0),
                    (vehicle.l/2, 0),
                    thickness=1.76*self.zoom,
                    color=(255, 255, 0),
                    parent=node
                )
                
                elif vehicle_id in (self.List_vehicule_spotter or self.List_vehicule_spotter_message_received):
                    dpg.draw_line(
                    (-vehicle.l/2, 0),
                    (vehicle.l/2, 0),
                    thickness=1.76*self.zoom,
                    color=(125, 125, 125),
                    parent=node
                )
                    
                else:
                    dpg.draw_line(
                    (-vehicle.l/2, 0),
                    (vehicle.l/2, 0),
                    thickness=1.76*self.zoom,
                    color=(0, 0, 255),
                    parent=node
                    )
                

                translate = dpg.create_translation_matrix(position)
                rotate = dpg.create_rotation_matrix(heading, [0, 0, 1])
                dpg.apply_transform(node, translate*rotate)
    
    def draw_indicator_other(self):
        # add the counter of the number of time the ghost vehicle is spotted
        dpg.set_value("CounterSpottedGhostVehicle", self.ghost_vehicule_is_spotted_counter)
        # add the counter of the number of time the trusted vehicle receive the message from other vehicles spotter
        dpg.set_value("GhostVehicleStatusForTrustedVehicle", self.ghost_vehicule_is_spotted_counter_for_trusted)
                
    def draw_indicator(self):
        # Draw a indicator on the top left corner of the screen if the ghost vehicle is spotted
        if self.ghost_vehicule_is_spotted:
            self.ghost_vehicule_is_spotted_indicator = True
            dpg.delete_item("GhostVehicleStatus")
            dpg.add_text("Ghost vehicle spotted",color=(255, 0, 0), parent="ControlsWindow", tag="GhostVehicleStatus")

    def apply_transformation(self):
        screen_center = dpg.create_translation_matrix([self.canvas_width/2, self.canvas_height/2, -0.01])
        translate = dpg.create_translation_matrix(self.offset)
        scale = dpg.create_scale_matrix([self.zoom, self.zoom])
        dpg.apply_transform("Canvas", screen_center*scale*translate)


    def render_loop(self):
                
        # Events
        self.update_inertial_zoom()
        self.update_offset_zoom_slider()

        # Remove old drawings
        dpg.delete_item("OverlayCanvas", children_only=True)
        dpg.delete_item("Canvas", children_only=True)
        
        # update list vehicles + positions
        for segment in self.simulation.segments:
            for vehicle_id in segment.vehicles:
                vehicle = self.simulation.vehicles[vehicle_id]
                if  (vehicle_id == self.ghost_vehicule):
                    if vehicle.x >= segment.get_length():
                        print("ghost")
                        print(vehicle.x)
                        print(segment.get_length())
                progress = vehicle.x / segment.get_length()
                position = segment.get_point(progress)
                
                self.vehicles_position[vehicle_id] = [position[0],position[1]]

            
                
                    
        self.List_vehicule_collision_check = [] # reset la liste des vehicules qui ont déjà été utilisé pour une collision check
        self.List_vehicule_collision_check_already_collision_find = [] # reset la liste des vehicules qui ont une collision avec un autre vehicule
 
        

        
        # New drawings
        self.draw_bg()
        self.draw_axes()
        self.draw_grid(unit=10)
        self.draw_grid(unit=50)
        self.draw_segments()
        self.draw_vehicles()
        self.draw_indicator_other()
        if not self.ghost_vehicule_is_spotted_indicator:
            self.draw_indicator()

        # Apply transformations
        self.apply_transformation()

        # Update panels
        self.update_panels()

        # Update simulation
        if self.is_running:
            self.simulation.run(self.speed)
            

    def show(self):
        dpg.show_viewport()
        while dpg.is_dearpygui_running():
            self.render_loop()
            dpg.render_dearpygui_frame()
        dpg.destroy_context()

    def run(self):
        self.is_running = True
        dpg.set_item_label("RunStopButton", "Stop")
        dpg.bind_item_theme("RunStopButton", "StopButtonTheme")

    def stop(self):
        self.is_running = False
        dpg.set_item_label("RunStopButton", "Run")
        dpg.bind_item_theme("RunStopButton", "RunButtonTheme")

    def toggle(self):
        if self.is_running: self.stop()
        else: self.run()