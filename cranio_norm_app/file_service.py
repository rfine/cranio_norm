import numpy as np 
from plyfile import PlyData

class FileService:

    def __init__(self, file):
        self.file = file


    def convertFile(self):
        plydata = PlyData.read(self.file)
        point_cloud_array = np.array([[x, y, z] for x, y, z in plydata["vertex"].data])
        point_cloud_list = point_cloud_array.tolist()
        return (point_cloud_array, point_cloud_list)
