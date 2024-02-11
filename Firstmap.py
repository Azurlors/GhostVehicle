from trafficSimulator import *
import time
sim = Simulation()


# SOUTH, EAST, NORTH, WEST


# Intersection in
sim.create_segment((-20,2.5),(50,2.5))
# Intersection out
sim.create_segment((50,-2.5),(-20,-2.5))

# Straight
sim.create_segment((50,2.5),(60,2.5))
sim.create_segment((60,-2.5),(50,-2.5))

sim.create_segment((57.5,-5),(57.5,-52.5))
sim.create_segment((52.5,-52.5),(52.5,-5))

sim.create_segment((60,2.5),(110,2.5))
sim.create_segment((110,-2.5),(60,-2.5))


# Left turn
sim.create_quadratic_bezier_curve((50,2.5),(57.5,2.5),(57.5,-5))
sim.create_quadratic_bezier_curve((52.5,-5),(52.5,2.5),(60,2.5))

# Right turn

sim.create_quadratic_bezier_curve((60,-2.5),(57.5,-2.5),(57.5,-5))
sim.create_quadratic_bezier_curve((52.5,-5),(52.5,-2.5),(50,-2.5))



# Curve
sim.create_quadratic_bezier_curve((110,2.5),(160,2.5),(160,-52.5))
sim.create_quadratic_bezier_curve((155,-52.5),(155,-2.5),(110,-2.5))

sim.create_quadratic_bezier_curve((160,-52.5),(160,-102.5),(110,-102.5))
sim.create_quadratic_bezier_curve((110,-97.5),(155,-97.5),(155,-52.5))

sim.create_quadratic_bezier_curve((110,-102.5),(52.5,-102.5),(52.5,-52.5))
sim.create_quadratic_bezier_curve((57.5,-52.5),(57.5,-97.5),(110,-97.5))


veh = Vehicle({'path': [0,2,6,12,14,16,5,11,1], 'v': 16.6})
sim.add_vehicle(veh)

vg = VehicleGenerator({
    'vehicle_rate': 12,
    'vehicles': [
        (1, {'path': [0,2,6,12,14,16,5,11,1], 'v': 16.6}),
        (1, {'path': [0,2,6,12,14,16,5,9,6,12,14,16,5,11,1], 'v': 16.6}),
        (1, {'path': [0,8,4,17,15,13,7,3,1], 'v': 16.6}),
        ]
    })
sim.add_vehicle_generator(vg)


win = Window(sim)
win.run()
win.show()