# required for display purpose only , comment when not using 
#%matplotlib nbagg

# lib required for functioning.
import numpy as np
from scipy.interpolate import splprep, splev
from shapely.geometry import Polygon, Point
import pandas as pd


#lib required for visualization only
import matplotlib.pyplot as plt

class gloabl_path_coverage:
    
    def __init__(self,fileName,lgt_upper_lim,lat_upper_lim,inter,data_sep=" "):
        self.gps_file_name = fileName
        self.longitude_upper_limit = lgt_upper_lim
        self.latitude_upper_limit = lat_upper_lim
        self.data_separator = data_sep
        self.list_boundaries = []
        self.list_polygons= []
        self.moves=[[0,-inter],[-inter,0],[0,inter],[inter,0]]
        

    def load_data(self):
        try:
            
            #read data from file with format  "Latitude Longitude"
            dataframe = pd.read_csv(self.gps_file_name, sep=self.data_separator, header=None)
            
            #numpy array of shape nx2 of all points present in file
            array_points  = dataframe.apply(pd.to_numeric, args=('coerce',)).values
            
        except Exception as ex:
            print ("gloabl_path_coverage.load_data: Exception while reading data from file and converting to numpy array : " + str(ex))
            return False
            
        # in case file read with no errors proceed further.
        # code to separate different boundaries (Lawn parameter and Obstacle parameter) from file 
        # and store in list format with initial element as "Lawn parameter list"
        try:
            
            tempBoundary = []
            for point in array_points:
                
                # if value recieved in NAN then add in final list of boundaries
                # else keep on cumulating the points in tempBoundary
                
                if np.isnan(point).any():
                    self.list_boundaries.append(tempBoundary)
                    tempBoundary = []
                    continue
    
                tempBoundary.append(point)
            
        except Exception as ex:
            print ("gloabl_path_coverage.load_data: Exception while separting various different boundaries and stoaring in a List.  : " + str(ex)) 
            return False
        
        # in case no issues return true stating success
        return True
      
    def prepare_polygon(self):
        try:
            for boundary in self.list_boundaries:
                points = np.array(boundary)
                self.list_polygons.append(Polygon(points))
                
        except Exception as ex:
            print ("gloabl_path_coverage.prepare_polygon---: Exception while preparing polygon list from boundary lists  : " + str(ex)) 
            return False
        
        # in case no issues return true stating success
        return True 
      
    def display_parameter(self):
        try:
            for boundary in self.list_boundaries:
                for points in boundary:
                    plt.plot(points[0],points[1],'o')
            plt.show()   
        except Exception as ex:
            print ("gloabl_path_coverage.display_parameter: Exception while displaying parameters : " + str(ex)) 
            
    #called by internal function , need not be called explicitly
    def prepare_edges(self):
        try:
            min_x,min_y,max_x,max_y=self.list_polygons[0].bounds
            longitude = np.arange(min_x,max_x + self.longitude_upper_limit )
            latitude = np.arange(min_y,max_y + self.latitude_upper_limit )
            edges =[]
            for x in range(0,len(longitude)):
                for y in range(0,len(latitude)):
                    point = Point([longitude[x],latitude[y]])
                    
                    # to check if point found is inside the parameter or on the lawn boundary 
                    # in that case check if it's not inside any of obstacle value
                    if self.list_polygons[0].contains(point) or np.any(np.equal([longitude[x],latitude[y]] , self.list_boundaries[0]).all(axis=1)):
                        for obstacle_poly in self.list_polygons[1:]:
                            if not obstacle_poly.contains(point):
                                edges.append([longitude[x],latitude[y]])
            
        except Exception as ex:
            print ("gloabl_path_coverage.prepare_edges : Can't process edges: " + str(ex))
            return []
        return edges
    
    #called by internal function , need not be called explicitly
    def move_next(self,curr_pos,traversed_list):
        try:
            for move in self.moves:
                next_x = curr_pos[0] + move[0]
                next_y = curr_pos[1] + move[1]
                point = Point(next_x , next_y)
                if [next_x , next_y] not in traversed_list:
                    ### check this logic
                    if self.list_polygons[0].contains(point) or np.any(np.equal([next_x , next_y] , self.list_boundaries[0]).all(axis=1)):
                        if( len(self.list_polygons) > 1):
                            for obstacle_poly in self.list_polygons[1:]:
                                if not obstacle_poly.contains(point):
                                    return [next_x,next_y]
                        else:
                            return [next_x,next_y]
            return None
        except Exception as ex:
            print ("gloabl_path_coverage.move_next : Exception in calculating next move : " + str(ex))
    
    #function
    #Returns : list of points to be traversed
    def gen_traversedList(self):
        
        try:
            edges = self.prepare_edges()
            current_pos = edges[0]
            traversed_list = []

            while len(edges)!=0 :

                if current_pos == None:
                    current_pos = edges[0]
                edges.remove(current_pos)
                traversed_list.append(current_pos)
                current_pos = self.move_next(current_pos,traversed_list)

            return traversed_list
        except Exception as ex :
            print ("gloabl_path_coverage.gen_traversedList : Exception in generating traversed list : " + str(ex))
            return []
        
        
