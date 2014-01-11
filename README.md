tower_defense_pygame
====================

This is a prototype that shows off the A* path finding algorithm.  I wrote it a few 
years ago and I haven't upgraded or played with it in a long time.  This project is 
disorganized and the assets and the code are sprinkled throughout.  

Dependencies
* PyGame
* libSDL
* Python

Running it:
./tower_defense.py

Left click to set a new "tower" down.
Space bar to add a new creeper (add lots of them and rapidly click)
tab to select a tower (you'll need to comment out the heat map to see the tower selection)
u to upgrade a tower (the range increases, and I think the power might too).

By default, the map is drawing a heat map that the creeper avoids.


Simulator, a cheesy BOIDs simulator.

Same requirements as above.

./simulator.py

Keys:
```
Escape      Quit

g           Toggle Grid

Shift +
Shift .     Increase velocity by %10

+           Double the velocity
.           

Shift -
Shift ,     Decrease velocity by %10

-           Halve the velocity
,           

1           Toggle Alignment
2           Toggle Clustering
3           Toggle Avoidance
 
Up          Add 10 boids
Down        Subtract 10 boids

Right       Increase Flee Range
Left        Decrease Flee Range

f           Toggle Fullscreen
w           Toggle Wrap
d           Toggle Debug
i           Toggle Info                    
```                    
