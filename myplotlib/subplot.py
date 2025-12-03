import numpy as np
import matplotlib.pyplot as plt
import math
import itertools

from . import defaults

__all__ = ['Subplot', 'Grid']

def moving_average(arr:list[float]|np.ndarray=None, window_size:int=1, smooth_inital:bool=False) -> np.ndarray:
  """compute the sliding window average using np.convolve
  returns numpy array containing the smoothed plot
  """
  if not isinstance(arr, np.ndarray): arr = np.asarray(arr)
  if arr.shape[0] <= window_size: return arr
  weights = np.ones(window_size)/window_size
  conv_arr = np.convolve(arr, weights, mode='full')[:len(arr)]
  if smooth_inital: conv_arr[:window_size] = conv_arr[window_size]
  return conv_arr

class Curve:
  def __init__(self, name:str='', points:list[tuple[float,float]]=None):
    self.name   = name
    self.buffer = []
    if points: self.add(points) 

  def add(self, points:list[tuple[float, float]]): 
    self.buffer.extend(points)

  def __len__(self): 
    return len(self.buffer)

  @property
  def xy(self) -> tuple[np.ndarray, np.ndarray]:
    if not self.buffer: return [], []
    else:
      self.buffer.sort()
      return zip(*self.buffer)
  
class Subplot:
  def __init__(self, title:str='', labels:list[str]=None, y_scale:str='linear', window:int=1, 
               zoom:bool=False):
    self.title   = title
    self.curves  = {l:Curve(name=l) for l in labels}
    self.VX      = []
    self.zoom    = zoom
    self.y_scale = y_scale 
    self.window  = window
  
  def update(self, update_dict:dict[str, list[tuple[float,float]]]):
    # TODO update VX lines.
    for key, points in update_dict.items(): self.curves[key].add(points)

  def plot_on_ax(self, ax:plt.Axes):
    ax.clear()
    ax.set_title(self.title)
    ax.set_yscale(self.y_scale)  
    ax.ticklabel_format(style='sci',scilimits=(0,0),axis='x')
    ax.tick_params(axis='y', which='both', colors="black", labelrotation=0)
    ax.spines['left'].set_color('black')
    ax.grid(color='grey', linestyle='--')
    
    cycler = itertools.cycle(defaults.color_cycle)
    for label, curve in self.curves.items():
      x_list, y_list = curve.xy
      color_n = next(cycler)
      ax.plot(x_list, y_list, color=color_n, lw=defaults.lw_actual, alpha=defaults.alpha_actual)
      ax.plot(x_list, moving_average(y_list, self.window), color=color_n,
              label=label, linestyle=defaults.linestyle_smoothed, lw=defaults.lw_smoothed)
      
    for x in self.VX:
      ax.axvline(x=x, color='black', linestyle='-', linewidth=1)
      ax.text(x+0.08, ax.get_ylim()[0]+0.08, f'{x}', verticalalignment='center', rotation=90, color='black')
    
    axis_handles, axis_labels= ax.get_legend_handles_labels()
    ax.legend(axis_handles, axis_labels, loc='best')

class Grid:
  """ A `Grid` is a container of `Subplot` objects to be used for convenient plotting and updating """
  def __init__(self, subplots:list[Subplot]=None, max_cols:int=-1):
    self.subplot_list = subplots 
    self.ncol = len(self.subplot_list) if max_cols == -1 else min(max_cols, len(self.subplot_list))
    self.nrow = max(1, math.ceil(len(self.subplot_list)/self.ncol))
    self.fig, self.axs = plt.subplots(self.nrow, self.ncol, 
                                      figsize=(defaults.figsize[0]*self.ncol,defaults.figsize[0]*self.nrow), 
                                      constrained_layout=True, squeeze=False)
    
  def update(self, update_list:list[dict[str, list[tuple[float,float]]]]):
    for subplot, update_d in zip(self.subplot_list, update_list):
      subplot.update(update_dict=update_d)

  def plot(self, loc:str='plot'):
    for ctr, subplot in enumerate(self.subplot_list):
      r, c = ctr//self.ncol, ctr%self.ncol
      subplot.plot_on_ax(self.axs[r,c])
    for i in range(len(self.subplot_list), self.ncol*self.nrow):
      self.fig.delaxes(self.axs[i//self.ncol, i%self.ncol])
    self.fig.savefig(f'{loc}.png', dpi=100, bbox_inches='tight')
  
  def close(self):
    plt.close(self.fig)