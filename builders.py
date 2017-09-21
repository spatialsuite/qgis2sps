
# -*- coding: utf-8 -*-
import os.path
from qgis.core import QgsMessageLog
import xmltodict
import time
import math
import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import codecs
path_to_yattag = str(os.path.realpath(__file__)[:-12] + 'yattag')
sys.path.append(os.path.realpath(__file__)[:-12] + 'yattag')
from yattag import Doc
from yattag import indent

def epds(input):
    modulename = input[0]
    module_path = input[1]
    qgis_input = input[6]
    endpoints = []
    doc, tag, text, line = Doc().ttl()
    doc.asis('<?xml version="1.0" encoding="UTF-8"?>')
    with tag('datasources'):
        for i in range (0,len(qgis_input)):
            connection = qgis_input[i]['host'] + ':'+ qgis_input[i]['port'] + '/'+ qgis_input[i]['dbname']
            if connection not in endpoints:
                with tag('endpoint', endpointtype='postgis', name='ep_' + modulename + '_'+ qgis_input[i]['dbname']):
                    with tag('connect'):
                        text(connection)
                    with tag('user'):
                        text(qgis_input[i]['user'])
                    with tag('pwd'):
                        text(qgis_input[i]['password'])
            endpoints.append(connection)
        for b in range (0,len(qgis_input)):
            with tag('datasource', endpoint = 'ep_' + modulename + '_'+ qgis_input[b]['dbname'], name= 'ds_'  + modulename + '_' + qgis_input[b]['layername']):
                with tag('table', geometrycolumn=qgis_input[b]['geom'], name=qgis_input[b]['table'], pkcolumn= qgis_input[b]['key']):
                    ''
    result = indent(doc.getvalue())
    f = open(module_path + '/datasources/datasources.xml', 'w')
    f.write(result)
    f.close()
    
def pres(input):
    name = input[0]
    path = input[1]
    layers = input[2]
    qmls = input[3]
    for y in range(0,len(qmls)):
        fields = []
        with open(qmls[y]) as f:
            d = xmltodict.parse(f)
            a = dict(d['qgis']['edittypes'])
            b = a['edittype']
            for i in range(0,len(b)):
                fields.append(b[i]['@name'])
        doc, tag, text, line = Doc().ttl()
        doc.asis('<?xml version="1.0" encoding="UTF-8"?>')
        with tag('presentation'):
            doc.asis('<text name="'+layers[y]+'" plural="'+layers[y]+'" value="'+layers[y]+'"/>')
            with tag('columns'):
                with tag('column', format='heading'):
                    doc.asis("<label>'"+layers[y]+"'</label>")
                    doc.asis("<value>'"+layers[y]+"'</value>")
                for i in range(0, len(fields)):
                    with tag('column'):
                        doc.asis("<label>'"+fields[i]+"'</label>")
                        doc.asis("<value>"+fields[i]+"</value>")
        result = indent(doc.getvalue())
        f = open(path + '/presentations/pres-'+name+'_'+layers[y]+'.xml', 'w')
        f.write(result)
        f.close()
        
def target(input):
    name = input[0]
    path = input[1]
    layers = input[2]
    doc, tag, text, line = Doc().ttl()
    doc.asis('<?xml version="1.0" encoding="UTF-8"?>')
    with tag('targetset', name=name):
        for i in range(0, len(layers)):
            with tag('target', displayname= layers[i], presentation='[module:'+name+'.dir]/presentations/pres-'+name+'_'+layers[i], themecondition='theme-'+name+'_'+layers[i]):
                doc.asis('<datasource name="ds_'+name+'_'+layers[i] +'"/>')
    result = indent(doc.getvalue())
    f = open(path + '/queries/targetset-'+name+'.xml', 'w')
    f.write(result)
    f.close()
    
def themegroups(input):
    name = input[0]
    doc, tag, text, line = Doc().ttl()
    doc.asis('<?xml version="1.0" encoding="UTF-8"?>')
    with tag('themegroups'):
        doc.stag('themegroup',displayname = name, expanded='false', name = name, type = 'checkbutton')
    result = indent(doc.getvalue())
    f = open(input[1] + '/profiles/includes/themegroups.xml', 'w')
    f.write(result)
    f.close()

def themes(input):
    layers = input[2]
    doc, tag, text, line = Doc().ttl()
    doc.asis('<?xml version="1.0" encoding="UTF-8"?>')
    with tag('themes'):
        for i in range(0, len(layers)):
            with tag('theme', module= input[0], name = 'theme-'+input[0]+'_' + layers[i]):
                with tag('themeselector'):
                    with tag('initialstate'):
                        text('available')
                    with tag('group'):
                        text(input[0])
                    with tag('displayname'):
                        text(layers[i])
                    with tag('selectable'):
                        text('true')
                with tag('downloadable'):
                    text('false')
    result = indent(doc.getvalue())
    f = open(input[1] + '/profiles/includes/themes.xml', 'w')
    f.write(result)
    f.close()
    
def readme(input):
    file= input[1]+"/read.me"
    with open(file, "w+") as myfile:
        myfile.write("===============================================================\n")
        myfile.write("QGIS2SPS\n")    
        myfile.write("===============================================================\n")
        myfile.write('$Date:'+ time.strftime("%d/%m/%Y")+' $\n')
        myfile.write('$Revision: 1 $\n') 
        myfile.write('$Author: qgis2sps $\n') 
        myfile.write("===============================================================\n")
        myfile.write('\n')
        myfile.write('--------------------\n') 
        myfile.write(input[0] +'\n') 
        myfile.write('--------------------\n') 
        myfile.write('\n')
        myfile.write('**Type description here**\n')
        myfile.write('\n')
        myfile.write('--------------------\n') 
        myfile.write('Installation\n') 
        myfile.write('--------------------\n') 
        myfile.write('\n')
        myfile.write('1: Installation\n')
        myfile.write('\n')
        myfile.write('1.a:  Copy the module to modules/custom\n')
        myfile.write('\n')
        myfile.write('1.b:  Add the following line to the modules file:\n')
        myfile.write('\n')
        myfile.write('        <module name="'+input[0]+'" dir="custom/'+input[0]+'" permissionlevel="public" />\n')
        myfile.write('\n')
        myfile.write('2:    Include the following resources in your profile:\n')
        myfile.write('\n')
        myfile.write('        <include onlychildnodes="true" src="[module:'+input[0]+'.dir]/profiles/includes/themegroups.xml" />\n')
        myfile.write('        <include onlychildnodes="true" src="[module:'+input[0]+'.dir]/profiles/includes/themes.xml" />\n')
        myfile.write('\n')
        myfile.write('3:    Include the following target in relevant targetset files:\n')
        myfile.write('\n')
        myfile.write('        <include onlychildnodes="true" src="[module:'+input[0]+'.dir]/queries/targetset-'+input[0]+'.xml" />\n')
        myfile.write('\n')
        myfile.write('4:    Modify your themes and presentations where needed - not all QGIS configuration can be translated to Mapserver...')
        myfile.close()

def calculatetransparency(colorstring, alpha):
    color_input = str(colorstring)
    opacity = float(alpha)
    color_alpha = float((color_input.split(",")[3]))/255
    return int((color_alpha * opacity)*100)
        
def categorized(styles, module_name, module_path, layer_name, render_type):
    doc, tag, text, line = Doc().ttl()
    doc.asis('<?xml version="1.0" encoding="utf-8"?>')
    with tag('theme'):
        with tag('cbinfo-metadata'):
            doc.asis('<param name="copyright-text"></param>')
        with tag('clientlayers'):
            with tag('clientlayer'):
                doc.asis('<singletile>true</singletile>')
        with tag('layer', datasource= 'ds_'+ module_name + '_'+ layer_name, name= module_name + '_'+ layer_name, type=render_type):
            for c in range(len(styles)):
                with tag('class'):
                    with tag('name'):
                        encoded_name = styles[c]['value'].encode('utf8').replace('æ', '*ae*').replace('ø', '*oe*').replace('å', '*aa*')
                        text(encoded_name)
                    with tag('expression'):
                        text('(\'['+str(styles[c]['attribute'])+']\' eq \''+str(encoded_name.decode('utf8'))+'\')')
                    if render_type == 'POLYGON':
                        with tag('style'):
                            value = calculatetransparency(styles[c]['color'], styles[c]['alpha'])
                            with tag('opacity'):
                                text(str(value))
                            with tag('color'):
                                text(' '.join(styles[c]['color'].split(",")[:3]))
                            if styles[c]['outline_color'].split(",")[3] == '0':
                                line_opacity = 100
                            else:
                                with tag('outlinecolor'):
                                    encoded_value = ' '.join(styles[c]['outline_color'].split(",")[:3])
                                    text(encoded_value)
                                with tag('outlinewidth'):
                                    width_type = styles[c]['outline_width_unit']
                                    if width_type == 'MM':
                                        encoded_value = math.floor(float(styles[c]['outline_width']) * 10)
                                    else:
                                        encoded_value = float(styles[c]['outline_width'])
                                    text(encoded_value)

                    if render_type == 'LINE':
                        with tag('style'):
                            value = calculatetransparency(styles[c]['line_color'],styles[c]['alpha'] )
                            with tag('opacity'):
                                text(str(value))
                            with tag('color'):
                                text(' '.join(styles[c]['line_color'].split(",")[:3]))
                            with tag('width'):
                                width_type = styles[c]['line_width_unit']
                                if width_type == 'MM':
                                    encoded_value = math.floor(float(styles[c]['line_width']) * 10)
                                else:
                                    encoded_value = float(styles[c]['line_width'])
                                text(encoded_value)
                            dashing = styles[c]['line_style']
                            if dashing != 'solid':
                                with tag('pattern'):
                                    if dashing == 'dash':
                                        text('10 4')
                                    elif dashing == 'dot':
                                        text('4 4')
                                    elif dashing == 'dash dot':
                                        text('10 4 4 4')
                                    elif dashing == 'dash dot dot':
                                        text('10 4 4 4 4 2')
                                    else:
                                        text('10 4')

                    if render_type == 'POINT':
                        with tag('style'):
                            value = calculatetransparency(styles[c]['color'], styles[c]['alpha'])
                            with tag('opacity'):
                                text(str(value))
                            with tag('color'):
                                text(' '.join(styles[c]['color'].split(",")[:3]))
                            with tag('size'):
                                width_type = styles[c]['size_unit']
                                if width_type == 'MM':
                                    encoded_value = math.floor(float(styles[c]['size']) * 4)
                                else:
                                    encoded_value = float(styles[c]['size'])
                                text(encoded_value)
                            if styles[c]['outline_color'].split(",")[3] == '0':
                                line_opacity = 100
                            else:
                                with tag('outlinecolor'):
                                    encoded_value = ' '.join(styles[c]['outline_color'].split(",")[:3])
                                    text(encoded_value)
                                with tag('outlinewidth'):
                                    width_type = styles[c]['outline_width_unit']
                                    if width_type == 'MM':
                                        encoded_value = math.floor(float(styles[c]['outline_width']) * 10)
                                    else:
                                        encoded_value = float(styles[c]['outline_width'])
                                    text(encoded_value)
                            with tag('symbol'):
                                symbol = styles[c]['name']
                                if symbol == 'square':
                                    text('square')
                                elif symbol == 'star':
                                    text('star')
                                elif symbol == 'cross2':
                                    text('cross')
                                else:
                                    text('circle')
    result = indent(doc.getvalue())
    f = open(module_path +'/temp/theme-temp.xml', 'w')
    f.write(result)
    f.close()
    a = codecs.open(module_path +'/themes/theme-'+ module_name + '_'+ layer_name +'.xml', 'a', 'utf-8')
    f = open(module_path +'/temp/theme-temp.xml', 'r')
    for line in iter(f):
        format_line = line.replace('*oe*', 'ø').replace('*ae*', 'æ').replace('*aa*', 'å')
        if 'layer type=' in line:
            a.write(format_line.decode('utf8').encode('utf8'))
            a.write('[datasource:ds_'+module_name + '_'+ layer_name+'.mapfile-datasource]\n')
        else:
            a.write(format_line.decode('utf8').encode('utf8'))
    a.close()
    f.close()
    os.remove(module_path +'/temp/theme-temp.xml')

def graduated(styles, module_name, module_path, layer_name, render_type):
    doc, tag, text, line = Doc().ttl()
    doc.asis('<?xml version="1.0" encoding="ISO-8859-1"?>')
    with tag('theme'):
        with tag('cbinfo-metadata'):
            doc.asis('<param name="copyright-text"></param>')
        with tag('clientlayers'):
            with tag('clientlayer'):
                doc.asis('<singletile>true</singletile>')
        with tag('layer', datasource= 'ds_'+ module_name + '_'+ layer_name, name= module_name + '_'+ layer_name, type=render_type):
            for c in range (0,len(styles)):
                with tag('class'):
                    with tag('name'):
                        text(str(styles[c]['label']))
                    with tag('expression'):
                        text('(['+str(styles[c]['attribute'])+'] ge '+str(styles[c]['lower'])+' and ['+str(styles[c]['attribute'])+'] lt '+str(styles[c]['upper'])+')')
                    if render_type == 'POLYGON':
                        with tag('style'):
                            value = calculatetransparency(styles[c]['color'], styles[c]['alpha'])
                            with tag('opacity'):
                                text(str(value))
                            with tag('color'):
                                text(' '.join(styles[c]['color'].split(",")[:3]))
                            if styles[c]['outline_color'].split(",")[3] == '0':
                                line_opacity = 100
                            else:
                                with tag('outlinecolor'):
                                    encoded_value = ' '.join(styles[c]['outline_color'].split(",")[:3])                     
                                    text(encoded_value)
                                with tag('outlinewidth'):
                                    width_type = styles[c]['outline_width_unit']              
                                    if width_type == 'MM':
                                        encoded_value = math.floor(float(styles[c]['outline_width']) * 10)
                                    else:
                                        encoded_value = float(styles[c]['outline_width'])
                                    text(encoded_value)
                    if render_type == 'LINE':
                        with tag('style'):
                            value = calculatetransparency(styles[c]['line_color'],styles[c]['alpha'])
                            with tag('opacity'):
                                text(str(value))
                            with tag('color'):                     
                                text(' '.join(styles[c]['line_color'].split(",")[:3]))
                            with tag('width'):
                                width_type = styles[c]['line_width_unit']              
                                if width_type == 'MM':
                                    encoded_value = math.floor(float(styles[c]['line_width']) * 10)
                                else:
                                    encoded_value = float(styles[c]['line_width'])
                                text(encoded_value)
                            dashing = styles[c]['line_style']
                            if dashing != 'solid':
                                with tag('pattern'):
                                    if dashing == 'dash':
                                        text('10 4')
                                    if dashing == 'dot':
                                        text('4 4')
                                    if dashing == 'dash dot':
                                        text('10 4 4 4')
                                    if dashing == 'dash dot dot':
                                        text('10 4 4 4 4 2')
                    if render_type == 'POINT':
                        with tag('style'):
                            value = calculatetransparency(styles[c]['color'], styles[c]['alpha'])
                            with tag('opacity'):
                                text(str(value))
                            with tag('color'):                     
                                text(' '.join(styles[c]['color'].split(",")[:3]))
                            with tag('size'):
                                width_type = styles[c]['size_unit']              
                                if width_type == 'MM':
                                    encoded_value = math.floor(float(styles[c]['size']) * 4)
                                else:
                                    encoded_value = float(styles[c]['size'])
                                text(encoded_value)
                            if styles[c]['outline_color'].split(",")[3] == '0':
                                line_opacity = 100
                            else:
                                with tag('outlinecolor'):
                                    encoded_value = ' '.join(styles[c]['outline_color'].split(",")[:3])                     
                                    text(encoded_value)
                                with tag('outlinewidth'):
                                    width_type = styles[c]['outline_width_unit']              
                                    if width_type == 'MM':
                                        encoded_value = math.floor(float(styles[c]['outline_width']) * 10)
                                    else:
                                        encoded_value = float(styles[c]['outline_width'])
                                    text(encoded_value)
                            with tag('symbol'):
                                symbol = styles[c]['name']
                                if symbol == 'square':
                                    text('square')
                                elif symbol == 'star':
                                    text('star')
                                elif symbol == 'cross2':
                                    text('cross')
                                else:
                                    text('circle')
    result = indent(doc.getvalue())
    f = open(module_path +'/temp/theme-temp.xml', 'w')
    f.write(result)
    f.close()
    a = open(module_path +'/themes/theme-'+ module_name + '_'+ layer_name +'.xml', 'a')
    f = open(module_path +'/temp/theme-temp.xml', 'r')
    for line in iter(f):
        if 'layer type=' in line:
            a.write(line)
            a.write('[datasource:ds_'+module_name + '_'+ layer_name+'.mapfile-datasource]\n')
        else:
            a.write(line)
    a.close()
    f.close()
    os.remove(module_path +'/temp/theme-temp.xml')

def singlesymbol(styles, module_name, module_path, layer_name, render_type):
    doc, tag, text, line = Doc().ttl()
    doc.asis('<?xml version="1.0" encoding="ISO-8859-1"?>')
    style = styles[0]
    with tag('theme'):
        with tag('cbinfo-metadata'):
            doc.asis('<param name="copyright-text"></param>')
        with tag('clientlayers'):
            with tag('clientlayer'):
                doc.asis('<singletile>true</singletile>')
    
        with tag('layer', datasource= 'ds_' + module_name + '_'+ layer_name, name= module_name + '_'+ layer_name, type=render_type):
                    if render_type == 'POLYGON':
                        with tag('class'):
                            with tag('name'):
                                text(layer_name)   
                            with tag('style'):
                                value = calculatetransparency(style['color'], style['alpha'])
                                with tag('opacity'):
                                    text(str(value))
                                with tag('color'):                     
                                    text(' '.join(style['color'].split(",")[:3]))
                                if style['outline_color'].split(",")[3] == '0':
                                    line_opacity = 100
                                else:
                                    with tag('outlinecolor'):
                                        encoded_value = ' '.join(style['outline_color'].split(",")[:3])                     
                                        text(encoded_value)
                                    with tag('outlinewidth'):
                                        width_type = style['outline_width_unit']              
                                        if width_type == 'MM':
                                            encoded_value = math.floor(float(style['outline_width']) * 10)
                                        else:
                                            encoded_value = float(style['outline_width'])
                                        text(encoded_value)

                    if render_type == 'LINE':
                        with tag('class'):
                            with tag('name'):
                                text(layer_name)                   
                            with tag('style'):
                                value = calculatetransparency(style['line_color'],style['alpha'])
                                with tag('opacity'):
                                    text(str(value))
                                with tag('color'):                     
                                    text(' '.join(style['line_color'].split(",")[:3]))
                                with tag('width'):
                                    width_type = style['line_width_unit']              
                                    if width_type == 'MM':
                                        encoded_value = math.floor(float(style['line_width']) * 10)
                                    else:
                                        encoded_value = float(style['line_width'])
                                    text(encoded_value)
                                dashing = style['line_style']
                                if dashing != 'solid':
                                    with tag('pattern'):
                                        
                                        if dashing == 'dash':
                                            text('10 4')
                                        if dashing == 'dot':
                                            text('4 4')
                                        if dashing == 'dash dot':
                                            text('10 4 4 4')
                                        if dashing == 'dash dot dot':
                                            text('10 4 4 4 4 2')

                    if render_type == 'POINT':
                        with tag('class'):
                            with tag('style'):
                                value = calculatetransparency(style['color'], style['alpha'])
                                with tag('opacity'):
                                    text(str(value))
                                with tag('color'):                     
                                    text(' '.join(style['color'].split(",")[:3]))
                                with tag('size'):
                                    width_type = style['size_unit']              
                                    if width_type == 'MM':
                                        encoded_value = math.floor(float(style['size']) * 4)
                                    else:
                                        encoded_value = float(style['size'])
                                    text(encoded_value)
                                if style['outline_color'].split(",")[3] == '0':
                                    line_opacity = 100
                                else:
                                    with tag('outlinecolor'):
                                        encoded_value = ' '.join(style['outline_color'].split(",")[:3])                     
                                        text(encoded_value)
                                    with tag('outlinewidth'):
                                        width_type = style['outline_width_unit']              
                                        if width_type == 'MM':
                                            encoded_value = math.floor(float(style['outline_width']) * 10)
                                        else:
                                            encoded_value = float(style['outline_width'])
                                        text(encoded_value)
                                with tag('symbol'):
                                    symbol = style['name']
                                    if symbol == 'square':
                                        text('square')
                                    elif symbol == 'star':
                                        text('star')
                                    elif symbol == 'cross2':
                                        text('cross')
                                    else:
                                        text('circle')
    result = indent(doc.getvalue())
    f = open(module_path +'/temp/theme-temp.xml', 'w')
    f.write(result)
    f.close()
    a = open(module_path +'/themes/theme-'+ module_name + '_'+ layer_name +'.xml', 'a')
    f = open(module_path +'/temp/theme-temp.xml', 'r')
    
    for line in iter(f):
        if 'layer type=' in line:
            a.write(line)
            a.write('[datasource:ds_'+module_name + '_'+ layer_name+'.mapfile-datasource]\n')
        else :
            a.write(line)
    a.close()
    f.close()
    os.remove(module_path +'/temp/theme-temp.xml')