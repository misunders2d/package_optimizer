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
LARGE_BULKY = 'Large bulky'
EXTRA_LARGE_0_50 = 'Extra large 0-50'
EXTRA_LARGE_50_70 = 'Extra large 50-70'
EXTRA_LARGE_70_150 = 'Extra large 70-150'
EXTRA_LARGE_150 = 'Extra large 150+'
ROUND = 4

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
        ship_weight = round(max((min_side*median_side*max_side) / 139, weight),4)
        ship_weight_oversize = round(max((max(2,min_side)*max(2,median_side)*max_side) / 139, weight),4)
        
        conditions = (
            (SMALL_STANDARD,
             min_side <= 0.75 and median_side <= 12 and max_side <= 15 and weight <= 1),
            
            (LARGE_STANDARD,
             min_side <= 8 and median_side <= 14 and max_side <= 18 and ship_weight <= 20),
            
            (LARGE_BULKY,
             (min_side+median_side)*2+max_side <= 130 and median_side <= 33 and max_side <= 59 and ship_weight <= 50),
            
            (EXTRA_LARGE_0_50, ship_weight <= 50),
            
            (EXTRA_LARGE_50_70, 50 < ship_weight <= 70),
            
            (EXTRA_LARGE_70_150, 70 < ship_weight <= 150),

            (EXTRA_LARGE_150, weight >150 )
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
            LARGE_BULKY:max(dim_weight,weight),
            EXTRA_LARGE_0_50:max(dim_weight,weight),
            EXTRA_LARGE_50_70:max(dim_weight,weight),
            EXTRA_LARGE_70_150:weight,
            EXTRA_LARGE_150:weight
            }
        
        fba_conditions = (
            (size_tier == SMALL_STANDARD and weight_to_use[SMALL_STANDARD] <= 2/16, {'Jan-Sept':3.06,'Oct-Dec':3.06}),
            
            (size_tier == SMALL_STANDARD and (2/16 < weight_to_use[SMALL_STANDARD] <= 4/16), {'Jan-Sept':3.15,'Oct-Dec':3.15}),

            (size_tier == SMALL_STANDARD and (4/16 < weight_to_use[SMALL_STANDARD] <= 6/16), {'Jan-Sept':3.24,'Oct-Dec':3.24}),

            (size_tier == SMALL_STANDARD and (6/16 < weight_to_use[SMALL_STANDARD] <= 8/16), {'Jan-Sept':3.33,'Oct-Dec':3.33}),

            (size_tier == SMALL_STANDARD and (8/16 < weight_to_use[SMALL_STANDARD] <= 10/16), {'Jan-Sept':3.43,'Oct-Dec':3.43}),

            (size_tier == SMALL_STANDARD and (10/16 < weight_to_use[SMALL_STANDARD] <= 12/16), {'Jan-Sept':3.53,'Oct-Dec':3.53}),

            (size_tier == SMALL_STANDARD and (12/16 < weight_to_use[SMALL_STANDARD] <= 14/16), {'Jan-Sept':3.60,'Oct-Dec':3.60}),

            (size_tier == SMALL_STANDARD and (14/16 < weight_to_use[SMALL_STANDARD] <= 16/16), {'Jan-Sept':3.65,'Oct-Dec':3.65}),

            
            (size_tier == LARGE_STANDARD and weight_to_use[LARGE_STANDARD] <= 4/16, {'Jan-Sept':3.68,'Oct-Dec':3.68}),
            
            (size_tier == LARGE_STANDARD and (4/16 < weight_to_use[LARGE_STANDARD] <= 8/16), {'Jan-Sept':3.90,'Oct-Dec':3.90}),
            
            (size_tier == LARGE_STANDARD and (8/16 < weight_to_use[LARGE_STANDARD] <= 12/16), {'Jan-Sept':4.15,'Oct-Dec':4.15}),

            (size_tier == LARGE_STANDARD and (12/16 < weight_to_use[LARGE_STANDARD] <= 16/16), {'Jan-Sept':4.55,'Oct-Dec':4.55}),

            (size_tier == LARGE_STANDARD and (1 < weight_to_use[LARGE_STANDARD] <= 1.25), {'Jan-Sept':4.99,'Oct-Dec':4.99}),

            (size_tier == LARGE_STANDARD and (1.25 < weight_to_use[LARGE_STANDARD] <= 1.5), {'Jan-Sept':5.37,'Oct-Dec':5.37}),

            (size_tier == LARGE_STANDARD and (1.5 < weight_to_use[LARGE_STANDARD] <= 1.75), {'Jan-Sept':5.52,'Oct-Dec':5.52}),

            (size_tier == LARGE_STANDARD and (1.75 < weight_to_use[LARGE_STANDARD] <= 2), {'Jan-Sept':5.77,'Oct-Dec':5.77}),

            (size_tier == LARGE_STANDARD and (2 < weight_to_use[LARGE_STANDARD] <= 2.25), {'Jan-Sept':5.87,'Oct-Dec':5.87}),

            (size_tier == LARGE_STANDARD and (2.25 < weight_to_use[LARGE_STANDARD] <= 2.5), {'Jan-Sept':6.05,'Oct-Dec':6.05}),

            (size_tier == LARGE_STANDARD and (2.5 < weight_to_use[LARGE_STANDARD] <= 2.75), {'Jan-Sept':6.21,'Oct-Dec':6.21}),

            (size_tier == LARGE_STANDARD and (2.75 < weight_to_use[LARGE_STANDARD] <= 3), {'Jan-Sept':6.62,'Oct-Dec':6.62}),

            (size_tier == LARGE_STANDARD and (3 < weight_to_use[LARGE_STANDARD] <= 20),
              {'Jan-Sept':6.92+(max((weight_to_use[LARGE_STANDARD]-3)*4,0)*0.08),
              'Oct-Dec':6.92+(max((weight_to_use[LARGE_STANDARD]-3)*4,0)*0.08)}),



            (size_tier == LARGE_BULKY and weight_to_use[LARGE_BULKY] <= 50,
              {'Jan-Sept':9.61+(max((weight_to_use[LARGE_BULKY]-1),0)*0.38),
              'Oct-Dec':9.61+(max((weight_to_use[LARGE_BULKY]-1),0)*0.38)}),
            
            (size_tier == EXTRA_LARGE_0_50 and weight_to_use[EXTRA_LARGE_0_50] <= 50,
              {'Jan-Sept':26.33+(max((weight_to_use[EXTRA_LARGE_0_50]-1),0)*0.38),
              'Oct-Dec':26.33+(max((weight_to_use[EXTRA_LARGE_0_50]-1),0)*0.38)}),
            
            (size_tier == EXTRA_LARGE_50_70 and (50 < weight_to_use[EXTRA_LARGE_50_70] <= 70),
              {'Jan-Sept':40.12+(max((weight_to_use[EXTRA_LARGE_50_70]-51),0)*0.75),
              'Oct-Dec':40.12+(max((weight_to_use[EXTRA_LARGE_50_70]-51),0)*0.75)}),
            
            (size_tier == EXTRA_LARGE_70_150 and (70 < weight_to_use[EXTRA_LARGE_70_150] <= 150),
              {'Jan-Sept':54.81+(max((weight_to_use[EXTRA_LARGE_70_150]-71),0)*0.75),
              'Oct-Dec':54.81+(max((weight_to_use[EXTRA_LARGE_70_150]-71),0)*0.75)}),

            (size_tier == EXTRA_LARGE_150 and weight_to_use[EXTRA_LARGE_150] > 150,
              {'Jan-Sept':194.95+(max((weight_to_use[EXTRA_LARGE_150]-151),0)*0.19),
              'Oct-Dec':194.95+(max((weight_to_use[EXTRA_LARGE_150]-151),0)*0.19)})
            )
        
        for c in fba_conditions:
            if c[0]:
                self.fulfillment_fees = c[1]
                self.fulfillment_fees['combined'] = round((c[1]['Jan-Sept']*9 + c[1]['Oct-Dec']*3) / 12, 4)
                break
        

    def __get_storage_fees(self):
        fee_jan_sept = {'standard':0.78, 'oversize':0.56}
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

    def __str__(self):
        return(f'''Box with the shape of {self.shape}\nFBA fees combined: {self.fulfillment_fees["combined"]}\nStorage fees combined: {self.storage_fees["combined"]}''')

    def __repr__(self):
        return self.__str__()

    def __lt__(self, other):
        return self.total_fee < other.total_fee

    def __le__(self, other):
        return self.total_fee <= other.total_fee

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
    
    
    def reshape(self, limit = 0.5, limit2 = 0.5, mode = 'lengths', top_best = 30):
        min_side = max(round(self.min_side*2)/2,1)
        median_side = max(round(self.median_side*2)/2,1)
        max_side = max(round(self.max_side*2)/2,1)
        weight = self.weight
        half_perimeter = min_side+median_side+max_side
        square = self.square
        
        base = np.arange(round(min_side/2), half_perimeter, 0.5)
        combis = itertools.combinations(base, 3)
        shapes = []
        for values_unsorted in combis:
            values = sorted(values_unsorted)
            if mode == 'lengths':
                if sum(values) == half_perimeter and (values[0] >= limit and values[1] >= limit2):
                  variant = Box(*values, weight)
                  if variant and (variant < self):
                      shapes.append(variant)
            elif mode == 'square':
                if (square * 0.9) < (2 * (values[0]*values[1] + values[0]*values[2] + values[1]*values[2])) < (square * 1.1) and (values[0] >= limit and values[1] >= limit2):
                    variant = Box(*values, weight)
                    if variant and (variant < self):
                        shapes.append(variant)
        best_3 = sorted(shapes)[:top_best]
        return best_3
  
def create_upload_template():
    df = pd.DataFrame(columns = ['Product', 'side1', 'side2', 'side3', 'weight, lbs'])
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine = 'xlsxwriter') as writer:
        df.to_excel(writer, index = False)
    return buf

def read_prepare_file(file_obj, limit = 0.5, limit2 = 0.5, mode = 'lengths', top_best = 30):
    file = pd.read_excel(file_obj)
    if not all(file.columns == ['Product', 'side1', 'side2', 'side3', 'weight, lbs']):
        return None
    file = file.dropna(subset = ['side1', 'side2', 'side3', 'weight, lbs'])
    products = file.values.tolist()
    
    columns = ['Product', 'option','side1', 'side2', 'side3', 'weight, lbs', 'size tier', 'storage fee','fulfillment fee', 'total fee']
    
    df = pd.DataFrame(columns = columns)
    for c in products:
        c[1:4] = sorted(c[1:4])
        item = Box(c[1], c[2], c[3], c[4])
        temp_product = pd.DataFrame([c], columns = ['Product', 'side1', 'side2', 'side3', 'weight, lbs'])
        temp_product['size tier'] = item.size_tier
        temp_product['storage fee'] = item.storage_fees['combined']
        temp_product['fulfillment fee'] = item.fulfillment_fees['combined']
        temp_product['total fee'] = item.total_fee
        temp_product['option'] = 'original'
        temp_product = temp_product[columns]

        best_options = item.reshape(limit, limit2, mode, top_best)
        temp_option = pd.DataFrame(columns = columns)
        for i, option in enumerate(best_options):
            temp = pd.DataFrame(
                [[c[0]]+ [f' option {i+1}']+list(option.shape) + [option.weight, option.size_tier, option.storage_fees['combined'], option.fulfillment_fees['combined'],option.total_fee]],
                columns = columns)
            temp['savings,$'] = temp['total fee'] - item.total_fee
            temp_option = pd.concat([temp_option, temp])
        df = pd.concat([df, temp_product, temp_option])
        
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine = 'xlsxwriter') as writer:
        df.to_excel(writer, index = False)
    return buf
    