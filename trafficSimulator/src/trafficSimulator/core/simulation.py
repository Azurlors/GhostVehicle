from .vehicle_generator import VehicleGenerator
from .geometry.quadratic_curve import QuadraticCurve
from .geometry.cubic_curve import CubicCurve
from .geometry.segment import Segment
from .vehicle import Vehicle


class Simulation:
    def __init__(self):
        self.segments = []
        self.vehicles = {}
        self.vehicle_generator = []
        self.vehicles_type = {}

        self.t = 0.0
        self.frame_count = 0
        self.dt = 1/60  


    def add_vehicle(self, veh, ghost=False, attacker=None, attacker_vehicle_segment=None, ghost_vehicle_position_offset=None):
        
        #### ajout ghost vehicle ####
        if ghost:
            
            attacker_vehicle_segment_length = attacker_vehicle_segment.get_length()
            attacker_vehicle = self.vehicles[attacker.id]
            self.vehicles[veh.id] = veh
            
            if len(veh.path) > 0:
                
                
                
                if attacker_vehicle_segment_length < attacker_vehicle.x + ghost_vehicle_position_offset:
                    # if the attacker vehicle is close to the end of the segment, the ghost vehicle is created at the beginning of the next segment
                    
                            
                    nextsegment = attacker_vehicle.path[attacker_vehicle.current_road_index + 1]
                    self.segments[nextsegment].add_vehicle(veh, ghost=True, attacker=attacker)
                    offset_x = attacker_vehicle.x - attacker_vehicle_segment_length
                    offset_x = offset_x + ghost_vehicle_position_offset
                    
                    self.vehicles[veh.id].x = offset_x
                    #update the path of the ghost vehicle
                    self.vehicles[veh.id].path = attacker_vehicle.path[attacker_vehicle.current_road_index+1:]
                else:
                    # the ghost vehicle is created in front of the attacker vehicle
                    attacker_vehicle_segment.add_vehicle(veh, ghost=True, attacker=attacker)
                    offset_x = attacker_vehicle.x + ghost_vehicle_position_offset
                    
                    self.vehicles[veh.id].x = offset_x
                    # update the path of the ghost vehicle
                    self.vehicles[veh.id].path = attacker_vehicle.path[attacker_vehicle.current_road_index :]

        #### fin ajout ghost vehicle ####
  
        else:
            self.vehicles[veh.id] = veh
            if len(veh.path) > 0:
                self.segments[veh.path[0]].add_vehicle(veh)
        

    def add_segment(self, seg):
        self.segments.append(seg)

    def add_vehicle_generator(self, gen):
        self.vehicle_generator.append(gen)

    
    def create_vehicle(self, **kwargs):
        veh = Vehicle(kwargs)
        self.add_vehicle(veh)

    def create_segment(self, *args):
        seg = Segment(args)
        self.add_segment(seg)

    def create_quadratic_bezier_curve(self, start, control, end):
        cur = QuadraticCurve(start, control, end)
        self.add_segment(cur)

    def create_cubic_bezier_curve(self, start, control_1, control_2, end):
        cur = CubicCurve(start, control_1, control_2, end)
        self.add_segment(cur)

    def create_vehicle_generator(self, **kwargs):
        gen = VehicleGenerator(kwargs)
        self.add_vehicle_generator(gen)


    def run(self, steps):
        for _ in range(steps):

            self.update()

    def update(self):
        # Update vehicles
        for segment in self.segments:
            if len(segment.vehicles) != 0:
                self.vehicles[segment.vehicles[0]].update(None, self.dt)
            for i in range(1, len(segment.vehicles)):
                self.vehicles[segment.vehicles[i]].update(self.vehicles[segment.vehicles[i-1]], self.dt)

        # Check roads for out of bounds vehicle
        for segment in self.segments:
            # If road has no vehicles, continue
            if len(segment.vehicles) == 0: continue
            # If not
            vehicle_id = segment.vehicles[0]
            vehicle = self.vehicles[vehicle_id]
            # If first vehicle is out of road bounds
            if vehicle.x >= segment.get_length():
                # If vehicle has a next road
                if vehicle.current_road_index + 1 < len(vehicle.path):
                    # Update current road to next road
                    vehicle.current_road_index += 1
                    # Add it to the next road
                    next_road_index = vehicle.path[vehicle.current_road_index]
                    self.segments[next_road_index].vehicles.append(vehicle_id)
                # Reset vehicle properties
                vehicle.x = 0
                # In all cases, remove it from its road
                segment.vehicles.popleft() 

        # Update vehicle generators
        for gen in self.vehicle_generator:
            gen.update(self)
        # Increment time
        self.t += self.dt
        self.frame_count += 1
