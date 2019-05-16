
import sys

from iris.coords import DimCoord, AuxCoord

from iris import coord_systems
import numpy as np


def main():
    in_file = sys.argv[1]
    out_file = sys.argv[2]



    import iris
    from iris_grib import _grib_cf_map
    import iris_grib

    print(iris_grib.__version__)
    print(iris.__version__)

    cf = _grib_cf_map.CFName(None, 'storm_surge', 'm')
    g2param = _grib_cf_map.G2Param(2, 10, 3, 193)
    _grib_cf_map.CF_TO_GRIB2[cf] = g2param

    cubes = iris.load(in_file)       # each variable in the netcdf file is a cube

    data = cubes[0]

    lon_coord = data.coords("longitude")[0]
    lat_coord = data.coords("latitude")[0]

    print(lon_coord.points[0, 0:10], lat_coord.points[0:10, 0])

    lons_new = np.linspace(lon_coord.points[0, 0], lon_coord.points[0, -1], lon_coord.shape[-1])
    lats_new = np.linspace(lat_coord.points[0, 0], lat_coord.points[-1, 0], lat_coord.shape[-1])
    print(lons_new[0], lons_new[-1], (lons_new[-1] - lons_new[0]) / (lons_new.shape[0] - 1))
    print(lats_new[0], lats_new[-1], (lons_new[-1] - lons_new[0]) / (lons_new.shape[0] - 1))





    data.remove_coord("longitude")
    data.remove_coord("latitude")

    print(lon_coord.attributes)
    cs = coord_systems.GeogCS(654321)





    assert isinstance(lon_coord, AuxCoord)
    lon_coord = DimCoord(np.linspace(lon_coord.points[0, 0], lon_coord.points[0, -1], lon_coord.shape[-1]),
                         attributes=lon_coord.attributes,
                         standard_name=lon_coord.standard_name,
                         long_name=lon_coord.long_name, var_name=lon_coord.var_name,
                         coord_system=cs, units="degrees"
                         )

    lat_coord = DimCoord(np.linspace(lat_coord.points[0, 0], lat_coord.points[-1, 0], lat_coord.shape[0]),
                         attributes=lat_coord.attributes,
                         standard_name=lat_coord.standard_name,
                         long_name=lat_coord.long_name, var_name=lat_coord.var_name,
                         coord_system=cs, units="degrees"
                         )

    import matplotlib.pyplot as plt
    plt.plot(np.diff(lat_coord.points[:]))
    plt.show()

    data.add_dim_coord(lon_coord, 2)
    data.add_dim_coord(lat_coord, 1)
    data.add_aux_coord(iris.coords.DimCoord(0, standard_name='forecast_period', units='hours'))
    data.add_aux_coord(iris.coords.DimCoord(0, "height", units="m"))

    assert isinstance(data, iris.cube.Cube)

    data.var_name = "ETSRG"
    # data.standard_name = "ETSRG"
    data.long_name = "storm_surge"

    print(data)
    print(data.shape)

    iris.save(data, out_file)    # save a specific variable to grib


if __name__ == '__main__':
    main()
