# -*- coding: utf-8 -*-
"""
/***************************************************************************
 qgis2sps
                                 A QGIS plugin
 Export qgis project to sps module
                             -------------------
        begin                : 2017-02-13
        copyright            : (C) 2017 by Sweco
        email                : mortenwinther.fuglsang@sweco.dk
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load qgis2sps class from file qgis2sps.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .qgis2sps import qgis2sps
    return qgis2sps(iface)
