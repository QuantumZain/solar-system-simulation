# Solar system simulation
A simple solar system simulation written in python and pygame. The simulation uses newton's laws of gravitation to calculate the forcces exterted on each planet for each frame, then I use an euler approximation method to simulate the position and velocity of the bodies based on the acceleration obtained from the force. This is an approximation since I am assuming the acceleration remains constant between the frames. This means a higher framrate results in a more accurate simulation

## Installation
- python 3 - get from python's main website
- pygame
Simply install pygame using pip as follows:

```
pip install pygame
```
## Controls

- use ```WASD``` keys to control the weird planet
- use the ```shift``` modifer with ```WASD``` to accelerate the planet
- ```p``` to pause
- Hover over planets to get their info
- If paused, planets may be dragged around - Note however they retain their initial velocities so you won't get the result your expecting yet :)
- press ```delete``` to toggle the border, now planets will rebound off of the window's edges.
- press ```x``` to toggle planet's trail. It only hides the trails, but they are still being processed behind the scenes

  ### To add planets or bodies
  Go to the file and navigate to where the bodies are being initialized. Use the commented template in the file to add the bodies with your custom settings
  
