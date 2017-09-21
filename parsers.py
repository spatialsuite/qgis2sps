# -*- coding: utf-8 -*-
import xmltodict


def singlesymbol(self, qml):
    with open(qml) as f:
        styler = []
        style = {}
        parsed = xmltodict.parse(f)
        renderer = dict(parsed['qgis']['renderer-v2']['symbols']['symbol'])
        style['alpha'] = renderer['@alpha']
        layer = dict(parsed['qgis']['renderer-v2']['symbols']['symbol']['layer'])

        for i in range(0, len(layer['prop'])):
            style[str(layer['prop'][i]['@k'])] = str(layer['prop'][i]['@v'])

        styler.append(style)

    return styler