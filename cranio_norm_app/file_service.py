import numpy as np
from plyfile import PlyData
import aspose.threed as a3d
import os
import os.path
import time


class FileService:

    def __init__(self, file):
        self.file = file
        start_time = time.time()
        self.uploadFile()
        print("--- %s seconds uploadSTLToPLY ---" % (time.time() - start_time))

    # def convertFile(self):
    #     start_time = time.time()
    #     plydata = PlyData.read("./files/ply/test.ply")
    #     point_cloud_array = np.array([[x, y, z]
    #                                   for x, y, z, nx, ny, nz in plydata["vertex"].data])
    #     point_cloud_list = point_cloud_array.tolist()
    #     print("--- %s seconds convertFile() ---" % (time.time() - start_time))
    #     return (point_cloud_array, point_cloud_list)

    # want to upload the file with the temp filename
    #  TODO come back to remove the hardcoding path
    def uploadFile(self):
        if not os.path.exists('./cranio_norm_app/static/ply/'):
            os.mkdir('./cranio_norm_app/static/ply/')
        with open('./cranio_norm_app/static/ply/'+self.file.name, 'w+') as destination:
            for chunk in self.file.chunks():
                destination.write(chunk.decode('utf-8'))

    # want to then convert the STL file to PLY
    # TODO return the file name, let the original file name be used to name the new PLY
    def convertSTLToPLY(self):
        scene = a3d.Scene.from_file(
            "./cranio_norm_app/static/ply/"+self.file.name)
        original_file_name = self.file.name.replace(".stl", '')
        n_ply_file_name = original_file_name+'.ply'
        scene.save("./cranio_norm_app/static/ply/"+n_ply_file_name)
        return n_ply_file_name
