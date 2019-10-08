import sys, os, shutil
from PIL import Image

import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np

def main(file_name):
  print("Opening {}".format(file_name))

  w,h = 10, 10
  matrix = [[0 for x in range(w)] for y in range(h)]

  with open(file_name, 'r') as f:
    content = f.readlines()
    if len(content)!=2:
      print ("Bad file format")
      return
    semantic_sim = [i.strip() for i in content[0].split(',')]
    syntactic_sim = [i.strip() for i in content[1].split(',')]

    print("Number of points: {}".format(len(semantic_sim)))

    if len(semantic_sim)!=len(syntactic_sim):
      print ("Bad file format")
      return

    max_c = 0
    for i in range(len(semantic_sim)):
      x = int(float(semantic_sim[i])*float(w-1))
      y = int(float(syntactic_sim[i])*float(h-1))
      matrix[x][y] += 1
      max_c = max(max_c, matrix[x][y])


    # sample to a matrix of size 100x100
    
    imgdata = [[0 for x in range(100)] for y in range(100)]
    for x in range(100):
      for y in range(100):
        imgdata[x][y] = matrix[int(float(x)/100.0 * w)][int(float(y)/100.0 * h)]



    plt.imshow(imgdata, cmap='hot', interpolation='nearest')
    plt.colorbar() 
    plt.gca().invert_yaxis()

    plt.ylabel('name similarity')
    plt.xlabel('semantic similarity')

    plt.savefig(file_name.replace('.txt', '.pdf'))

    #plt.show()

    # img = Image.new( 'RGB', (w,h), "white") # create a new black image
    # pixels = img.load() # create the pixel map

    # for x in range(w):
    #   for y in range(h):
    #     c = 255 - int(float(matrix[x][y])*recolor_factor)
    #     pixels[x,y] = (c,c,c)

    # img.show()
    
if __name__ == '__main__':
  main(sys.argv[1])
