# Load up all modules

import stepped
import partials
import doubleups
import overshoots

modules = [
    stepped.Stepped_Check(),
    partials.Partial_Key_Check(),
    doubleups.DoubleUp_Check(),
    overshoots.Overshoot_Check()
    ]
