#!/usr/bin/python
# -*- coding: utf-8 -*-
# kate: space-indent on; indent-width 4; mixedindent off; indent-mode python;

import sys
from datetime import datetime
from uuid import UUID
from lxml import etree

class XMLReport(object):
    _crash_dump_fields = ['uuid', 'crash_timestamp', 'report_time', 'report_fqdn',
                          'report_username', 'application', 'command_line',
                          'symbol_directories', 'image_directories', 'environment']


    _system_info_fields = ['platform_type', 'cpu_type', 'cpu_name', 'cpu_level', 'cpu_revision', 'cpu_vendor',
                            'number_of_cpus', 'os_version', 'os_version_info',
                            'distribution_id', 'distribution_release', 'distribution_codename', 'distribution_description' ]
    _file_info_fields = ['log']
    _exception_fields = ['thread', 'code', 'name', 'info', 'address', 'flags']

    def __init__(self, filename=None):
        self._filename = filename
        self._xml = etree.parse(filename)

    def _crash_dump(self):
        if r:
            return r[0]
        else:
            return None

    @staticmethod
    def _value_convert(value_str, data_type):
        if data_type == 'uuid':
            return UUID(value_str)
        elif data_type == 'QString':
            return value_str
        elif data_type == 'QDateTime':
            return datetime.strptime(value_str, '%Y-%m-%d %H:%M:%S')
        elif data_type == 'int':
            return int(value_str, 10)
        elif data_type == 'uint':
            return int(value_str, 16)
        else:
            return value_str

    @staticmethod
    def _get_node_value(node, child, default_value=None):
        r = node.xpath(child + '/@type')
        data_type = r[0] if r else None

        if data_type == 'QStringList':
            all_subitems = node.xpath(child + '/item/text()')
            ret = []
            for c in all_subitems:
                ret.append(c)
        elif data_type == 'QVariantMap':
            all_subitems = node.xpath(child + '/item')
            ret = {}
            for item in all_subitems:
                r = item.xpath('@key')
                item_key = r[0] if r else None

                r = item.xpath('@type')
                item_data_type = r[0] if r else None

                r = item.xpath('text()')
                item_value = r[0] if r else None

                ret[item_key] = XMLReport._value_convert(item_value, item_data_type)
        else:
            r = node.xpath(child + '/text()')
            if r:
                ret = XMLReport._value_convert(r[0], data_type)
            else:
                ret = default_value
        return ret

    @staticmethod
    def _get_first_node(node, child):
        r = node.xpath('/' + str(child))
        return r[0] if r else None

    @property
    def crash_info(self):
        i = XMLReport._get_first_node(self._xml, 'crash_dump')
        ret = { }
        for f in XMLReport._crash_dump_fields:
            ret[f] = XMLReport._get_node_value(i, f)
        return ret

    @property
    def system_info(self):
        i = XMLReport._get_first_node(self._xml, 'crash_dump/system_info')
        ret = { }
        for f in XMLReport._system_info_fields:
            ret[f] = XMLReport._get_node_value(i, f)
        return ret

    @property
    def file_info(self):
        i = XMLReport._get_first_node(self._xml, 'crash_dump/file_info')
        ret = { }
        for f in XMLReport._file_info_fields:
            ret[f] = XMLReport._get_node_value(i, f)
        return ret

    @property
    def exception(self):
        i = XMLReport._get_first_node(self._xml, 'crash_dump/exception')
        ret = { }
        for f in XMLReport._exception_fields:
            ret[f] = XMLReport._get_node_value(i, f)
        return ret

    def to_html(self):
        return str(self.crash_info)


if __name__ == '__main__':
    xmlreport = XMLReport(sys.argv[1])
    print(xmlreport.crash_info)
    print(xmlreport.system_info)
    print(xmlreport.file_info)

