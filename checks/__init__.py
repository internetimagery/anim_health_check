# Load up all modules

import euler
import stepped
import partials
import doubleups
import overshoots
import movinghold

modules = [
    euler.Euler_Check(),
    stepped.Stepped_Check(),
    partials.Partial_Key_Check(),
    doubleups.DoubleUp_Check(),
    overshoots.Overshoot_Check(),
    movinghold.Movinghold_Check()
    ]
