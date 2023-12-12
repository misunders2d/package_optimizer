# -*- coding: utf-8 -*-
"""
Created on Thu Dec  7 19:51:53 2023

@author: Sergey
"""
import pandas as pd
import numpy as np
import itertools
from io import BytesIO
from PIL import Image
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

SMALL_STANDARD = 'Small standard size'
LARGE_STANDARD = 'Large standard size'
SMALL_OVERSIZE = 'Small oversize'
MEDIUM_OVERSIZE = 'Medium oversize'
LARGE_OVERSIZE = 'Large oversize'
SPECIAL_OVERSIZE = 'Special oversize'
ROUND = 4
TOP_BEST = 3


class Box:
    
    def __init__(self, s1 = 4, s2 = 6, s3 = 10, weight = 3):
        self.s1 = float(s1)
        self.s2 = float(s2)
        self.s3 = float(s3)
        self.weight = float(weight)
        sides = sorted([self.s1,self.s2, self.s3])
        self.min_side = sides[0]
        self.median_side = sides[1]
        self.max_side = sides[2]
        self.cu_ft = (self.min_side * self.median_side * self.max_side) / 1728
        self.shape = (self.min_side, self.median_side, self.max_side)
        self.square = 2 * (self.s1*self.s2 + self.s1*self.s3 + self.s2*self.s3)
        self.__get_size_tier()
        self.__get_fulfillment_fees()
        self.__get_storage_fees()
        self.total_fee = self.fulfillment_fees['combined'] + self.storage_fees['combined']
        
    def __get_size_tier(self):
        weight = self.weight
        min_side, median_side, max_side = self.min_side, self.median_side, self.max_side
        ship_weight = round(max((min_side*median_side*max_side) / 139,weight),2)
        ship_weight_oversize = round(max((max(2,min_side)*max(2,median_side)*max_side) / 139,weight),2)
        
        conditions = (
            (SMALL_STANDARD,
             min_side <= 0.75 and median_side <= 12 and max_side <= 15 and ship_weight <= 1),
            
            (LARGE_STANDARD,
             min_side <= 8 and median_side <= 14 and max_side <= 18 and ship_weight <= 20),
            
            (SMALL_OVERSIZE,
             (min_side+median_side)*2+max_side <= 130 and median_side <= 30 and max_side <= 60 and ship_weight_oversize <= 70),
            
            (MEDIUM_OVERSIZE,
             (min_side+median_side)*2+max_side <= 130 and max_side <= 108 and ship_weight_oversize <= 150),
            
            (LARGE_OVERSIZE,
             (min_side+median_side)*2+max_side <= 165 and max_side <= 108 and ship_weight_oversize <= 150),
            
            (SPECIAL_OVERSIZE,
             (min_side+median_side)*2+max_side >165 and max_side <= 108 or ship_weight_oversize > 150)
            )
        for c in conditions:
            if c[1]:
                self.size_tier = c[0]
                self.dim_weight = ship_weight if 'standard' in c[0] else ship_weight_oversize
                break
    
    def __get_fulfillment_fees(self):
        dim_weight = self.dim_weight
        weight = self.weight
        size_tier = self.size_tier
    
        weight_to_use = {
            SMALL_STANDARD:weight,
            LARGE_STANDARD:max(dim_weight,weight),
            SMALL_OVERSIZE:max(dim_weight,weight),
            MEDIUM_OVERSIZE:max(dim_weight,weight),
            LARGE_OVERSIZE:max(dim_weight,weight),
            SPECIAL_OVERSIZE:weight
            }
        
        fba_conditions = (
            (size_tier == SMALL_STANDARD and weight_to_use[SMALL_STANDARD] <= 4/16,
              {'Jan-Sept':3.22,'Oct-Dec':3.42}),
            
            (size_tier == SMALL_STANDARD and 4/16 < weight_to_use[SMALL_STANDARD] <= 8/16,
              {'Jan-Sept':3.4,'Oct-Dec':3.6}),
            
            (size_tier == SMALL_STANDARD and 8/16 < weight_to_use[SMALL_STANDARD] <= 12/16,
              {'Jan-Sept':3.58,'Oct-Dec':3.78}),
            
            (size_tier == SMALL_STANDARD and 12/16 < weight_to_use[SMALL_STANDARD] <= 16/16,
              {'Jan-Sept':3.77,'Oct-Dec':3.97}),
            
            (size_tier == LARGE_STANDARD and weight_to_use[LARGE_STANDARD] <= 4/16,
              {'Jan-Sept':3.86,'Oct-Dec':4.16}),
            
            (size_tier == LARGE_STANDARD and 4/16 < weight_to_use[LARGE_STANDARD] <= 8/16,
              {'Jan-Sept':4.08,'Oct-Dec':4.38}),
            
            (size_tier == LARGE_STANDARD and 8/16 < weight_to_use[LARGE_STANDARD] <= 12/16,
              {'Jan-Sept':4.24,'Oct-Dec':4.54}),
            
            (size_tier == LARGE_STANDARD and 12/16 < weight_to_use[LARGE_STANDARD] <= 16/16,
              {'Jan-Sept':4.75,'Oct-Dec':5.05}),
            
            (size_tier == LARGE_STANDARD and 1 < weight_to_use[LARGE_STANDARD] <= 1.5,
              {'Jan-Sept':5.40,'Oct-Dec':5.70}),
            
            (size_tier == LARGE_STANDARD and 1.5 < weight_to_use[LARGE_STANDARD] <= 2,
              {'Jan-Sept':5.69,'Oct-Dec':5.99}),
            
            (size_tier == LARGE_STANDARD and 2 < weight_to_use[LARGE_STANDARD] <= 2.5,
              {'Jan-Sept':6.10,'Oct-Dec':6.60}),
            
            (size_tier == LARGE_STANDARD and 2.5 < weight_to_use[LARGE_STANDARD] <= 3,
              {'Jan-Sept':6.39,'Oct-Dec':6.89}),
            
            (size_tier == LARGE_STANDARD and 3 < weight_to_use[LARGE_STANDARD] <= 20,
              {'Jan-Sept':7.17+(max((weight_to_use[LARGE_STANDARD]-3)*2,0)*0.16),
              'Oct-Dec':7.67+(max((weight_to_use[LARGE_STANDARD]-3)*2,0)*0.16)}),
            
            (size_tier == SMALL_OVERSIZE and weight_to_use[SMALL_OVERSIZE] <= 70,
              {'Jan-Sept':9.73+(max((weight_to_use[SMALL_OVERSIZE]-1),0)*0.42),
              'Oct-Dec':10.73+(max((weight_to_use[SMALL_OVERSIZE]-1),0)*0.42)}),
            
            (size_tier == MEDIUM_OVERSIZE and weight_to_use[MEDIUM_OVERSIZE] <= 150,
              {'Jan-Sept':19.05+(max((weight_to_use[MEDIUM_OVERSIZE]-1),0)*0.42),
              'Oct-Dec':21.55+(max((weight_to_use[MEDIUM_OVERSIZE]-1),0)*0.42)}),
            
            (size_tier == LARGE_OVERSIZE and weight_to_use[LARGE_OVERSIZE] <= 150,
              {'Jan-Sept':89.98+(max((weight_to_use[LARGE_OVERSIZE]-90),0)*0.83),
              'Oct-Dec':92.48+(max((weight_to_use[LARGE_OVERSIZE]-90),0)*0.83)}),
            
            (size_tier == SPECIAL_OVERSIZE and weight_to_use[SPECIAL_OVERSIZE] > 150,
              {'Jan-Sept':158.49+(max((weight_to_use[SPECIAL_OVERSIZE]-90),0)*0.83),
              'Oct-Dec':160.99+(max((weight_to_use[SPECIAL_OVERSIZE]-90),0)*0.83)})
            )
        
        for c in fba_conditions:
            if c[0]:
                self.fulfillment_fees = c[1]
                self.fulfillment_fees['combined'] = round((c[1]['Jan-Sept']*9 + c[1]['Oct-Dec']*3) / 12, 4)
                break
        

    def __get_storage_fees(self):
        fee_jan_sept = {'standard':0.87, 'oversize':0.56}
        fee_oct_dec = {'standard':2.40, 'oversize':1.40}
        cu_ft = self.cu_ft
        if 'standard' in self.size_tier:
            jan_sept = round(fee_jan_sept['standard']*cu_ft,ROUND)
            oct_dec = round(fee_oct_dec['standard']*cu_ft,ROUND)
            self.storage_fees =  {
                'Jan-Sept':jan_sept,
                'Oct-Dec':oct_dec,
                'combined': round((jan_sept*9 + oct_dec*3)/12,ROUND)}
        else:
            jan_sept = round(fee_jan_sept['oversize']*cu_ft,ROUND)
            oct_dec = round(fee_oct_dec['oversize']*cu_ft,ROUND)
            self.storage_fees =  {
                'Jan-Sept': jan_sept,
                'Oct-Dec': oct_dec,
                'combined': round((jan_sept*9 + oct_dec*3)/12,ROUND)}

    
    
    def __create_shape(self,ax, size):
        x,y,z = (0,0,0)
        width, depth, height = size
    
        # Define the eight vertices of the parallelepiped
        zero = [x,y,z]
        bottom_right = [x+width,y,z]
        upper_right = [x+width, y+height, z]
        upper_left = [x, y+ height, z]

        far_bottom_right = [x+width, y, z+depth]
        far_bottom_left = [x, y, z+depth]
        far_top_left = [x, y+height, z+depth]
        far_top_right = [x+width, y+height, z+depth]

        faces = [
            [zero, bottom_right, upper_right, upper_left],
            [far_bottom_left, far_bottom_right, far_top_right, far_top_left],
            [zero, far_bottom_left, far_top_left, upper_left],
            [bottom_right, far_bottom_right, far_top_right, upper_right],
            [zero, far_bottom_left, far_bottom_right, bottom_right],
            [upper_left, far_top_left, far_top_right, upper_right]
        ]
    
        # Create a Poly3DCollection object and add it to the Axes3D
        poly3d = Poly3DCollection(faces, facecolors='red', linewidths=1, edgecolors='cyan', alpha=0.5)
        ax.add_collection3d(poly3d)
    
    def draw(self):
        size = (self.s1, self.s2, self.s3)
        s1,s2,s3 = size[0], size[1], size[2]
        # Create a figure and 3D axes
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        
        # Set the limits for the axes
        ax.set_xlim([0, max(size)])
        ax.set_ylim([0, max(size)])
        ax.set_zlim([0, max(size)])
        ax.tick_params(axis='x', colors='red')
        ax.tick_params(axis='y', colors='red')
        ax.tick_params(axis='z', colors='red')
        # Call the function to draw the parallelepiped
        self.__create_shape(ax, size=size)
        
        buf = BytesIO()
        plt.savefig(buf, format = 'png', transparent = True)
        plt.close()
        # buf.seek(0)
        # img = Image.open(buf)
        # buf.close()
        return buf
    
    
    def reshape(self, limit = 0.5, mode = 'lengths'):
        min_side = max(round(self.min_side*2)/2,1)
        median_side = max(round(self.median_side*2)/2,1)
        max_side = max(round(self.max_side*2)/2,1)
        weight = self.weight
        half_perimeter = min_side+median_side+max_side
        square = self.square
        
        base = np.arange(max(round(min_side/2),limit), half_perimeter, 0.5)
        combis = itertools.combinations(base, 3)

        shapes = []
        if mode == 'lengths':
          for values in combis:
              if sum(values) == half_perimeter and min(values) > 0:
                  variant = Box(*values, weight)
                  shapes.append(variant)
        elif mode == 'square':
            for values in combis:
                if (square * 0.9) < (2 * (values[0]*values[1] + values[0]*values[2] + values[1]*values[2])) < (square * 1.1):
                  variant = Box(*values, weight)
                  shapes.append(variant)
        best_3 = sorted(shapes, key = lambda variant: variant.total_fee)[:3]
        return best_3
    
# def read_prepare_file():
#     file = pd.read_excel(
#         r'G:\Shared drives\30 Sales\30.1 MELLANNI\30.11 AMAZON\30.111 US\Sales\DIMENSIONS.xlsx',
#         skiprows = 1)
#     file = file[['Collection','Size','l','w','h','Individual Weight Lbs']]
#     file = file.dropna(subset = 'l')
#     file = file.dropna(subset = 'Individual Weight Lbs')
#     collections = file.values.tolist()
#     cols = [
#         'Collection','Size','l','w','h','weight','Current size tier','Current fee (yearly avg)',
#         'l option 1','w option 1','h option 1','Size tier 1','fee option 1',
#         'l option 2','w option 2','h option 2','Size tier 2','fee option 2',
#         'l option 3','w option 3','h option 3','Size tier 3','fee option 3']
#     df = pd.DataFrame()
#     for c in collections:
#         item = get_size_tier(c[2], c[3], c[4], c[5])
#         fees = get_storage_fees(item)
#         current_fee = round(fees['Jan-Sept']*9+fees['Oct-Dec']*3,ROUND)
#         best_dims = reshape(item)
#         best = [[x['sides'][0], x['sides'][1], x['sides'][2], x['size tier'], x['fees']] for x in best_dims]

#         file = pd.DataFrame([c+[item['Size tier']]+[current_fee]+best[0]+best[1]+best[2]], columns = cols)
#         df = pd.concat([df, file])
#     df.to_excel(r'c:\temp\pics\fees.xlsx', index = False)
#     return None
    
# if __name__ == '__main__':
#     main()
   
    