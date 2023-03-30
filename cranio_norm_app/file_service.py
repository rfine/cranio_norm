import numpy as np
from plyfile import PlyData
import aspose.threed as a3d
import os
import os.path


class FileService:

    def __init__(self, file):
        self.file = file
        self.uploadFile()
        self.convertSTLToPLY()

    def convertFile(self):
        plydata = PlyData.read("./files/ply/test.ply")
        point_cloud_array = np.array([[x, y, z]
                                      for x, y, z, nx, ny, nz in plydata["vertex"].data])
        point_cloud_list = point_cloud_array.tolist()
        return (point_cloud_array, point_cloud_list)

    # want to upload the file with the temp filename
    #  TODO come back to remove the hardcoding path
    def uploadFile(self):
        if not os.path.exists('./files'):
            os.mkdir('./files')
        with open('./files/'+self.file.name, 'w+') as destination:
            for chunk in self.file.chunks():
                destination.write(chunk.decode('utf-8'))

    # want to then convert the STL file to PLY
    def convertSTLToPLY(self):
        scene = a3d.Scene.from_file("./files/"+self.file.name)
        scene.save("./files/ply/test.ply")

        # TODO idea we upload and manage the files directly here we do not need to use plydata in this case.  We will have lib in js handle it in the frontend
        # should reduce the runtime
