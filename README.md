# langton_ant
Python/TkInter graphical implementation of Langton's ant

Langton's ant walks on a 2D grid with the following rules :
  - If it is in a white cell, it turns right and the cell it was on becomes black
  - if it was on a black cell, it turns left and the cell it was on becomes white

This simple program offers a TkInter GUI to visualize the trajectory of the ant.
We can observe that :
  - for the first ~ 100 steps, it follows a pretty symetrical pattern
  - for the next ~ 10k moves, the trajectory becomes chaotic
  - then it enters a cyclic pattern moving endlessly, called the "highway"
