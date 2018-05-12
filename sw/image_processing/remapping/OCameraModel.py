# TODO: comment and reformat code

import numpy as np


class OCameraModel():
    def __init__(self):

        self._pol = []
        self._length_pol = int(0),
        self._invpol = None,
        self._xc = None
        self._yc = None
        self._c = None
        self._d = None
        self._e = None
        self._width = None
        self._height = None

        self._filename = None

        self._model_loaded = False

    def get_ocam_model(self, filename):
        self._filename = filename

        with open(self._filename, 'r') as f:
            data = f.readlines()

        # Read polynominal coefficients
        current_line = data[2]
        self._length_pol, self._pol = self._read_poly_line(current_line)

        # Read inverse polynominal coefficients
        current_line = data[6]
        self._length_invpol, self._invpol = self._read_poly_line(current_line)

        # Read center coordinates
        current_line = data[10].split()
        self._xc = float(current_line[0])
        self._yc = float(current_line[1])

        # Read affine coefficients
        current_line = data[14].split()
        self._c = float(current_line[0])
        self._d = float(current_line[1])
        self._e = float(current_line[2])

        # Read image size
        current_line = data[18].split()
        self._height = float(current_line[0])
        self._width = float(current_line[1])

        self._model_loaded = True

    def cam2world(self, point2d):

        if not self._model_loaded:
            print "No OCam model loaded. Load a model first using 'get_ocam_model'-method!"
        else:
            invdet = 1.0 / (self._c - self._d * self._e)
            xp = invdet * ((point2d[0] - self._xc) - self._d * (point2d[1] - self._yc))
            yp = invdet * (-self._e * (point2d[0] - self._xc) + self._c * (point2d[1] - self._yc))

            r = np.sqrt(xp * xp + yp * yp)
            zp = self._pol[0]
            r_i = 1

            for i in xrange(1, self._length_pol):
                r_i *= r
                zp += r_i * self._pol[i]

            invnorm = 1 / np.sqrt(xp * xp + yp * yp + zp * zp)

            point3d = np.zeros(3, np.float)
            point3d[0] = invnorm * xp
            point3d[1] = invnorm * yp
            point3d[2] = invnorm * zp

            return point3d

    def world2cam(self, point3d):
        if not self._model_loaded:
            print "No OCam model loaded. Load a model first using 'get_ocam_model'-method!"
        else:
            norm = np.sqrt(point3d[0] * point3d[0] + point3d[1] * point3d[1])
            theta = np.arctan(point3d[2] / norm)

            point2d = np.zeros(2, np.float)

            if norm != 0:
                invnorm = 1 / norm
                t = theta
                rho = self._invpol[0]
                t_i = 1

                for i in xrange(1, self._length_invpol):
                    t_i *= t
                    rho += t_i * self._invpol[i]

                x = point3d[0] * invnorm * rho
                y = point3d[1] * invnorm * rho

                point2d[0] = x * self._c + y * self._d + self._xc
                point2d[1] = x * self._e + y + self._yc

            else:
                point2d[0] = self._xc
                point2d[1] = self._yc

            return point2d

    def create_perspective_undistortion_lut(self, height, width, sf):
        height = int(height)
        width = int(width)

        nxc = height / 2.0
        nyc = width / 2.0
        nz = -width / sf

        mapx = np.zeros([height, width], np.float32)
        mapy = np.zeros([height, width], np.float32)

        m = np.zeros(3, np.float)

        for i in xrange(height):
            for j in xrange(width):
                m[0] = i - nxc
                m[1] = j - nyc
                m[2] = nz

                remapped_m = self.world2cam(m)

                mapx[i, j] = remapped_m[1]
                mapy[i, j] = remapped_m[0]

        return mapx, mapy

    def create_panoramic_undistortion_lut(self, height, width, rmax=470, rmin=20):
        height = int(height)
        width = int(width)

        mapx = np.zeros([height, width], np.float32)
        mapy = np.zeros([height, width], np.float32)

        for i in xrange(height):
            for j in xrange(width):
                theta = -(float(j)) / width * 2 * np.pi
                rho = rmax - (rmax - rmin) / height * i

                mapx[i, j] = self._yc + rho * np.sin(theta)
                mapy[i, j] = self._xc + rho * np.cos(theta)

        return mapx, mapy

    @staticmethod
    def _read_poly_line(line):
        poly_data = line.split()
        n = int(poly_data[0])

        polys = []
        for i in xrange(1, n + 1):
            polys.append(float(poly_data[i]))

        return n, polys


if __name__ == '__main__':
    app = OCameraModel()
    app.get_ocam_model('calib_results.txt')
    vec = [2, 2]
    print app.cam2world(vec)
    print app.world2cam(app.cam2world(vec))
    print app.create_perspective_undistortion_lut(10, 10, 6)
