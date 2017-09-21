# -*- coding: utf-8 -*-
"""
/***************************************************************************
 qgis2sps
                                 A QGIS plugin
 Export qgis project to sps module
                              -------------------
        begin                : 2017-02-13
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Sweco
        email                : mortenwinther.fuglsang@sweco.dk
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import os.path
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QUrl
from PyQt4.QtGui import QAction, QIcon, QFileDialog
from PyQt4.QtWebKit import QWebView
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from qgis2sps_dialog import qgis2spsDialog

from qgis.core import QgsMessageLog
from qgis.utils import *
import functions
from yattag import Doc
from yattag import indent
import xmltodict
import time
import parsers
import builders




class qgis2sps:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
		# Save reference to the QGIS interface
        self.iface = iface
		# initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
		# initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
			self.plugin_dir,
			'i18n',
			'qgis2sps_{}.qm'.format(locale))

        if os.path.exists(locale_path):
			self.translator = QTranslator()
			self.translator.load(locale_path)

			if qVersion() > '4.3.3':
				QCoreApplication.installTranslator(self.translator)
        self.dlg = qgis2spsDialog()

		# Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Spatial Suite')
		# TODO: We are going to let the user set this up in a future iteration
        #self.toolbar = self.iface.addToolBar(u'qgis2sps')
        #self.toolbar.setObjectName(u'qgis2sps')




    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('qgis2sps', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=False,
        status_tip=None,
        whats_this=None,
        parent=None):

        # Create the dialog (after translation) and keep reference
        self.dlg = qgis2spsDialog()
        self.dlg.lineEdit.clear()
        self.dlg.pushButton.clicked.connect(self.select_output_file)
        self.dlg.pushButton_2.clicked.connect(self.build_module)
        self.dlg.pushButton_3.clicked.connect(self.close_clean)
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)
        if status_tip is not None:
            action.setStatusTip(status_tip)
        if whats_this is not None:
            action.setWhatsThis(whats_this)
        if add_to_toolbar:
            self.toolbar.addAction(action)
        if add_to_menu:
            self.iface.addPluginToWebMenu(
                self.menu,
                action)
        self.actions.append(action)
        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/qgis2sps/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Qgis2sps'),
            callback=self.run,
            parent=self.iface.mainWindow())

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginWebMenu(
                self.tr(u'&Spatial Suite'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        #del self.toolbar


    def qgisPrepareData(self, connections, layers):
        outputs = []
        path = self.dlg.lineEdit.text()
        module_name = self.dlg.lineEdit_2.text()

        try:
            os.mkdir(path + '/' + module_name)
        except:
            pass
        try:
            os.mkdir(path + '/' + module_name + '/datasources')
        except:
            pass
        try:
            os.mkdir(path + '/' + module_name + '/themes')
        except:
            pass
        try:
            os.mkdir(path + '/' + module_name + '/presentations')
        except:
            pass
        try:
            os.mkdir(path + '/' + module_name + '/profiles')
        except:
            pass
        try:
            os.mkdir(path + '/' + module_name + '/profiles/includes')
        except:
            pass
        try:
            os.mkdir(path + '/' + module_name + '/queries')
        except:
            pass
        try:
            os.mkdir(path + '/' + module_name + '/qml')
        except:
            pass
        try:
            os.mkdir(path + '/' + module_name + '/temp')
        except:
            pass

        #Options
        options = {}
        if self.dlg.includes.isChecked():
            options['include'] = 'true'
        else:
            options['include'] = 'false'
        if self.dlg.presentations.isChecked():
            options['presentations'] = 'true'
        else:
            options['presentations'] = 'false'
        if self.dlg.targets.isChecked():
            options['targets'] = 'true'
        else:
            options['targets'] = 'false'

        #Selected layers
        items = self.dlg.listWidget.selectedItems()
        x = []
        for i in list(items):
            x.append(str(i.text()))
        names = []
        qmlfiles = []
        for i in range (0,len(x)):
            name = x[i].split(' - ')[0]
            names.append(name)
            for layer in layers:
                layername = self.encode_and_transform_names(layer.name())
                if layername == name:
                    pathtoqml = path.replace('\\', '/') + '/' + module_name + '/qml/' + self.encode_and_transform_names(layer.name()) + '.qml'
                    layer.saveNamedStyle(pathtoqml)
                    qmlfiles.append(pathtoqml)
        outputs.append(module_name)
        outputs.append(path.replace('\\', '/') + '/' + module_name)
        outputs.append(names)
        outputs.append(qmlfiles)
        outputs.append(options)
        outputs.append(x)
        outputs.append(connections)
        return outputs
        
##################################################
## MAIN BUILDER BLOCK                           ##
##################################################
        
    def build_module(self):
        items = self.dlg.listWidget.selectedItems()
        path = self.dlg.lineEdit.text()
        module_name = self.dlg.lineEdit_2.text()
        if len(items) == 0:
            self.writeerror('Udpeg lag')
        else:
            if len(path) == 0:
                self.writeerror('Angiv folder')
            else:
                if len(module_name) == 0:
                    self.writeerror('Angiv modulnavn')

                else:
                    if os.path.isdir(path + '/' + module_name):
                        self.writeerror('Mappen findes allerede')
                    else:
                        inputs = self.qgisPrepareData(connections, layers)

        builders.epds(inputs)
        global errors
        errors = 0
        # Themes
        for i in range(0, len(inputs[5])):
            layertype = inputs[5][i].split(' - ')[2]
            render = inputs[5][i].split(' - ')[1]
            qml_file = inputs[3][i]
            if layertype in ('MultiPolygonZ', 'MultiPolygon', 'Polygon', 'PolygonZ'):
                if render == 'Singlesymbol':
                    try:
                        styled = self.singlesymbol(qml_file)
                        builders.singlesymbol(styled, inputs[0], inputs[1] , inputs[2][i], 'POLYGON')
                        self.theme_done(str(inputs[2][i]))

                    except:
                        self.theme_error(str(inputs[2][i]))
                if render == 'Graduatedsymbol':
                    try:
                        styled = self.graduated(qml_file)
                        builders.graduated(styled, inputs[0], inputs[1] , inputs[2][i], 'POLYGON')
                        self.theme_done(str(inputs[2][i]))
                    except:
                        self.theme_error(str(inputs[2][i]))
                if render == 'Categorizedsymbol':
                    try:
                        styled = self.categorized(qml_file)
                        builders.categorized(styled, inputs[0], inputs[1] , inputs[2][i], 'POLYGON')
                        self.theme_done(str(inputs[2][i]))
                    except:
                        self.theme_error(str(inputs[2][i]))
            if layertype in ('MultiLineStringZ', 'MultiLineString', 'LineString', 'LineStringZ'):
                if render == 'Singlesymbol':
                    try:
                        styled = self.singlesymbol(qml_file)
                        builders.singlesymbol(styled, inputs[0], inputs[1] , inputs[2][i], 'LINE')
                        self.theme_done(str(inputs[2][i]))
                    except:
                        self.theme_error(str(inputs[2][i]))
                if render == 'Graduatedsymbol':
                    try:
                        styled = self.graduated(qml_file)
                        builders.graduated(styled, inputs[0], inputs[1] , inputs[2][i], 'LINE')
                        self.theme_done(str(inputs[2][i]))
                    except:
                        self.theme_error(str(inputs[2][i]))
                if render == 'Categorizedsymbol':
                    try:
                        styled = self.categorized(qml_file)
                        builders.categorized(styled, inputs[0], inputs[1] , inputs[2][i], 'LINE')
                        self.theme_done(str(inputs[2][i]))
                    except:
                        self.theme_error(str(inputs[2][i]))
            if layertype in  ('MultiPointZ', 'MultiPoint', 'Point', 'PointZ'):
                if render == 'Singlesymbol':
                    try:
                        styled = self.singlesymbol(qml_file)
                        builders.singlesymbol(styled, inputs[0], inputs[1] , inputs[2][i], 'POINT')
                        self.theme_done(str(inputs[2][i]))
                    except:
                        self.theme_error(str(inputs[2][i]))
                if render == 'Graduatedsymbol':
                    try:
                        styled = self.graduated(qml_file)
                        builders.graduated(styled, inputs[0], inputs[1] , inputs[2][i], 'POINT')
                        self.theme_done(str(inputs[2][i]))
                    except:
                        self.theme_error(str(inputs[2][i]))
                if render == 'Categorizedsymbol':
                    try:
                        styled = self.categorized(qml_file)
                        builders.categorized(styled, inputs[0], inputs[1] , inputs[2][i], 'POINT')
                        sself.theme_done(str(inputs[2][i]))
                    except:
                        self.theme_error(str(inputs[2][i]))
        if self.dlg.presentations.isChecked():
            builders.pres(inputs)
        if self.dlg.targets.isChecked():
            builders.target(inputs)
        if self.dlg.includes.isChecked():
            builders.themegroups(inputs)
            builders.themes(inputs)
        builders.readme(inputs)
        self.dlg.textEdit.append('Modul afsluttet!')
        if errors == 0:
            self.writesuccess('Modul afsluttet uden fejl')
        else:
            self.writeerror('Modul afsluttet med fejl')

##################################################
## PARSERS                                      ##
##################################################
           
## Catogorized style parser
    def categorized(self, qml):
        with open(qml) as f:
            styler = [] 
            parsed = xmltodict.parse(f)
            categories = parsed['qgis']['renderer-v2']['categories']  
            renderer = parsed['qgis']['renderer-v2']
            symbols = parsed['qgis']['renderer-v2']['symbols'] 
            category = categories['category']
            for i in range(0, len(category)):
                symbol = symbols['symbol']
                for b in range (0, len(symbol)):
                    if str(symbol[b]['@name']) ==  str(category[i]['@symbol']):
                        style = {}
                        style['pair'] = str(symbol[b]['@name'])+','+ str(category[i]['@symbol'])
                        style['value'] = str(category[i]['@value'])
                        style['label'] = str(category[i]['@label'])
                        style['symbol'] = str(category[i]['@symbol'])
                        style['render'] = str(category[i]['@render'])
                        style['attribute'] = str(renderer['@attr'])
                        style['alpha'] =  str(symbol[b]['@alpha'])
                        props = symbol[b]['layer']['prop']
                        for t in range (0, len(props)):
                            style[str(props[t]['@k'])] = str(props[t]['@v'])
                        styler.append(style)
        return styler
        
## Graduated style parser
    def graduated(self, qml):
        with open(qml) as f:
            styler = [] 
            parsed = xmltodict.parse(f)
            ranges = parsed['qgis']['renderer-v2']['ranges']
            renderer = parsed['qgis']['renderer-v2']
            symbols = parsed['qgis']['renderer-v2']['symbols'] 
            datarange = ranges['range']
            for i in datarange:
                symbol = symbols['symbol']
                for b in symbol:
                    if str(b['@name']) ==  str(i['@symbol']):
                        style = {}
                        style['pair'] = str(b['@name'])+','+ str(i['@symbol'])
                        style['upper'] = str(i['@upper'])
                        style['lower'] = str(i['@lower'])
                        style['label'] = str(i['@label'])
                        style['render'] = str(i['@render'])
                        style['attribute'] = str(renderer['@attr'])
                        style['alpha'] =  str(b['@alpha'])             
                        props = b['layer']['prop']
                        for t in props:
                            style[str(t['@k'])] = str(t['@v'])
                        styler.append(style)
        return styler
        
## Single symbol parser
    def singlesymbol(self, qml):
        with open(qml) as f:
            styler = []
            style = {}
            parsed = xmltodict.parse(f)
            renderer = dict(parsed['qgis']['renderer-v2']['symbols']['symbol'])
            style['alpha'] =  renderer['@alpha']
            layer = dict(parsed['qgis']['renderer-v2']['symbols']['symbol']['layer'])
            for i in range(0, len(layer['prop'])):
               style[str(layer['prop'][i]['@k'])] =  str(layer['prop'][i]['@v'])
            styler.append(style)
        return styler

##################################################
## Prepare the GUI                              ##
##################################################

    def init_gui(self):
        global layers
        layers = self.iface.legendInterface().layers()
        global connections
        connections = []
        self.close_clean()
        self.dlg.listWidget.clear()
        self.dlg.lineEdit_2.setText('')
        self.dlg.lineEdit.setText('')
        self.write_to_status('Plugin initialiseret!')
        compatible_types = ['Singlesymbol', 'singleSymbol', 'Categorizedsymbol', 'categorizedSymbol', 'Graduatedsymbol',
                            'graduatedSymbol']
        compatibleLayers = 0
        incompatibleLayers = 0
        for layer in layers:
            connection = layer.source()
            conn = {}
            elements = connection.replace("'", "").replace('"', '').split(' ')

            elm_dict = {}

            for i in range(len(elements)):
                try:
                    elm = elements[i].split('=')
                    obj = elm[0]
                    value = elm[1]
                    elm_dict[obj] = value
                except:
                    elm = elements[i].replace('(', '').replace(')', '')

                    elm_dict['geom'] = elm

            try:
                conn['displayname'] = layer.name()
                conn['layername'] = self.encode_and_transform_names(layer.name())
                conn['dbname'] = elm_dict['dbname']
                conn['host'] = elm_dict['host']
                conn['port'] = elm_dict['port']
                conn['user'] = elm_dict['user']
                conn['password'] = elm_dict['password']
                conn['key'] = elm_dict['key']
                conn['srid'] = elm_dict['srid']
                conn['type'] = elm_dict['type']
                conn['table'] = elm_dict['table']
                conn['geom'] = elm_dict['geom']
                renderer = layer.rendererV2().type()
                if renderer.capitalize() in compatible_types:
                    name = self.encode_and_transform_names(layer.name())
                    self.dlg.listWidget.addItem(name + ' - ' + renderer.capitalize() + ' - ' + conn['type'])
                    connections.append(conn)
                    compatibleLayers += 1
                else:
                    y = 0
            except:
                incompatibleLayers += 1
        self.write_to_status('Kompatible lag : ' + str(compatibleLayers))
        self.write_to_status('Inkompatible lag : ' + str(incompatibleLayers))

        file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "docs.html"))
        local_url = QUrl.fromLocalFile(file_path)
        self.dlg.webView.load(local_url)


##################################################
## Communication                                ##
##################################################

    def writeerror(self, text):
        iface.messageBar().pushMessage("Error", text, level=QgsMessageBar.CRITICAL, duration=5)

    def writesuccess(self, text):
        iface.messageBar().pushMessage("Info", text, level=QgsMessageBar.INFO, duration=3)

    def write_to_status(self, text):
        self.dlg.textEdit.append(text)

    def theme_error(self, themename):
        self.dlg.textEdit.append('Fejl i tema ' + str(themename))
        self.writeerror('Fejl i tema ' + str(themename))
        errors += 1

    def theme_done(self, themename):
        self.dlg.textEdit.append('Tema ' + str(themename) + ' dannet')

##################################################
## Misc                                         ##
##################################################

    def encode_and_transform_names(self, name):
        formatted_name = name.encode('utf8').lower().replace(' ', '_').replace('å', 'aa').replace('ø', 'oe').replace('æ', 'ae')
        return formatted_name

    def select_output_file(self):
        #filename = QFileDialog.getSaveFileName(self.dlg, "Select output file ","", '*.txt')
        folder = QFileDialog.getExistingDirectory(self.dlg, "Select Directory")
        self.dlg.lineEdit.setText(folder)

    def close_clean(self):
        self.dlg.accept()
        self.clean()

    def clean(self):
        self.dlg.textEdit.clear()

##################################################
## INIT METHODS                                 ##
##################################################

    def run(self):
        """Run method that performs all the real work"""
        self.init_gui()
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            pass

