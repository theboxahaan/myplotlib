import numpy as np

from myplotlib import Grid, Subplot

if __name__ == '__main__':
  x = np.linspace(start=0, stop=10, num=200)
  y = x - np.random.rand(x.shape[0])*10
  print(x)
  print(y)

  grid = Grid(subplots=[
    Subplot(title='First Plot',labels=['first', 'second', 'third'], window=10), 
    Subplot(title='Second Plot', labels=['first', 'second'], window=30),
    Subplot(title='Third Plot', labels=['first', 'second'], window=30, zoom=True)
    ], max_cols=3)
  for _x,_y in zip(x,y):
    grid.update([{'first':[(_x,_y)], 'second':[(_x,_y+10)], 'third':[(_x,_y-10 if _y>1 else None)]},
                 {'first':[(_x,_y)], 'second':[(_x, _y+1.2)]},
                 {'first':[(_x,_y)], 'second':(_x, _y+1.2)}])
  
  grid.plot()