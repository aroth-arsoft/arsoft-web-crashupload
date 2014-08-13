#!/usr/bin/python
# -*- coding: utf-8 -*-
# kate: space-indent on; indent-width 4; mixedindent off; indent-mode python;

import sys
import base64
from datetime import datetime
from uuid import UUID
from lxml import etree

class XMLReport(object):
    _crash_dump_fields = ['uuid', 'crash_timestamp', 'report_time', 'report_fqdn',
                          'report_username', 'application', 'command_line',
                          'symbol_directories', 'image_directories', 'environment']


    _system_info_fields = ['platform_type', 'cpu_type', 'cpu_64_bit', 'cpu_name', 'cpu_level', 'cpu_revision', 'cpu_vendor',
                            'number_of_cpus', 'os_version', 'os_version_info',
                            'distribution_id', 'distribution_release', 'distribution_codename', 'distribution_description' ]
    _file_info_fields = ['log']
    _exception_fields = ['thread', 'code', 'name', 'info', 'address', 'flags']
    _assertion_fields = ['expression', 'function', 'source', 'line']

    _module_fields = ['base', 'size', 'timestamp', 'product_version', 'file_version', 'name', 'symbol_file', 'flags' ]
    _thread_fields = ['id', 'exception', 'name', 'memory', 'start_addr', 'create_time', 'exit_time', 'kernel_time', 'user_time' ]
    _memory_region_fields = ['base_addr', 'size', 'alloc_base', 'alloc_prot', 'type', 'protect', 'state' ]
    _memory_block_fields = ['num', 'base', 'size', 'memory']
    _handle_fields = ['handle', 'type', 'name', 'count', 'pointers' ]

    _stackdump_fields = ['threadid', 'exception']
    _stack_frame_fields = ['num', 'addr', 'retaddr', 'param0', 'param1', 'param2', 'param3', 'module', 'function', 'source' ]

    def __init__(self, filename=None):
        self._filename = filename
        self._xml = etree.parse(filename)

    class XMLReportEntity(object):
        def __init__(self, owner):
            self._owner = owner

        def __str__(self):
            ret = ''
            for (k,v) in self.__dict__.items():
                if k[0] != '_':
                    if ret:
                        ret += ', '
                    ret = ret + '%s=%s' % (k,v)
            return ret

    class CrashInfo(XMLReportEntity):
        def __init__(self, owner):
            super(XMLReport.CrashInfo, self).__init__(owner)

    class SystemInfo(XMLReportEntity):
        def __init__(self, owner):
            super(XMLReport.SystemInfo, self).__init__(owner)

    class FileInfo(XMLReportEntity):
        def __init__(self, owner):
            super(XMLReport.FileInfo, self).__init__(owner)

    class Exception(XMLReportEntity):
        def __init__(self, owner):
            super(XMLReport.Exception, self).__init__(owner)

    class Assertion(XMLReportEntity):
        def __init__(self, owner):
            super(XMLReport.Assertion, self).__init__(owner)

    class Module(XMLReportEntity):
        def __init__(self, owner):
            super(XMLReport.Module, self).__init__(owner)

    class Thread(XMLReportEntity):
        def __init__(self, owner):
            super(XMLReport.Thread, self).__init__(owner)

    class MemoryRegion(XMLReportEntity):
        def __init__(self, owner):
            super(XMLReport.MemoryRegion, self).__init__(owner)

    class MemoryBlock(XMLReportEntity):
        def __init__(self, owner):
            super(XMLReport.MemoryRegion, self).__init__(owner)

    class Handle(XMLReportEntity):
        def __init__(self, owner):
            super(XMLReport.Handle, self).__init__(owner)

    class StackDump(XMLReportEntity):
        def __init__(self, owner):
            super(XMLReport.StackDump, self).__init__(owner)

    class StackFrame(XMLReportEntity):
        def __init__(self, owner):
            super(XMLReport.StackFrame, self).__init__(owner)

    @staticmethod
    def _value_convert(value_str, data_type):
        if data_type == 'uuid':
            return UUID(value_str)
        elif data_type == 'QString':
            return value_str
        elif data_type == 'QDateTime':
            return datetime.strptime(value_str, '%Y-%m-%d %H:%M:%S')
        elif data_type == 'bool':
            if value_str == 'true':
                return True
            elif value_str == 'false':
                return False
            else:
                return None
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
        elif data_type == 'QByteArray':
            r = node.xpath(child + '/@encoding-type')
            encoding_type = r[0] if r else None

            r = node.xpath(child + '/text()')
            value = r[0] if r else None
            if r:
                if encoding_type == 'base64':
                    ret = base64.b64decode(r[0])
                else:
                    ret = r[0]
            else:
                ret = default_value
        else:
            r = node.xpath(child + '/text()')
            if r:
                ret = XMLReport._value_convert(r[0], data_type)
            else:
                ret = default_value
        return ret

    @staticmethod
    def _get_attribute(node, attr_name, default_value=None):
        r = node.xpath('@' + attr_name)
        attr_value = r[0] if r else None

        ret = None
        if attr_value:
            try:
                ret = int(attr_value)
            except ValueError:
                try:
                    ret = bool(attr_value)
                except ValueError:
                    pass
            if ret is None:
                ret = attr_value
        return ret

    @staticmethod
    def _get_first_node(node, child):
        r = node.xpath('/' + str(child))
        return r[0] if r else None

    @property
    def crash_info(self):
        i = XMLReport._get_first_node(self._xml, 'crash_dump')
        ret = XMLReport.CrashInfo(self) if i is not None else None
        if i is not None:
            for f in XMLReport._crash_dump_fields:
                setattr(ret, f, XMLReport._get_node_value(i, f))
        return ret

    @property
    def system_info(self):
        i = XMLReport._get_first_node(self._xml, 'crash_dump/system_info')
        ret = XMLReport.SystemInfo(self) if i is not None else None
        if i is not None:
            for f in XMLReport._system_info_fields:
                setattr(ret, f, XMLReport._get_node_value(i, f))
        return ret

    @property
    def file_info(self):
        i = XMLReport._get_first_node(self._xml, 'crash_dump/file_info')
        ret = XMLReport.FileInfo(self) if i is not None else None
        if i is not None:
            for f in XMLReport._file_info_fields:
                setattr(ret, f, XMLReport._get_node_value(i, f))
        return ret

    @property
    def exception(self):
        i = XMLReport._get_first_node(self._xml, 'crash_dump/exception')
        ret = XMLReport.Exception(self) if i is not None else None
        if i is not None:
            for f in XMLReport._exception_fields:
                setattr(ret, f, XMLReport._get_node_value(i, f))
        return ret

    @property
    def assertion(self):
        i = XMLReport._get_first_node(self._xml, 'crash_dump/assertion')
        ret = XMLReport.Assertion(self) if i is not None else None
        if i is not None:
            for f in XMLReport._assertion_fields:
                setattr(ret, f, XMLReport._get_node_value(i, f))
        return ret

    @property
    def modules(self):
        i = XMLReport._get_first_node(self._xml, 'crash_dump/modules')
        ret = []
        all_subitems = i.xpath('module') if i is not None else None
        if all_subitems is not None:
            for item in all_subitems:
                m = XMLReport.Module(self)
                for f in XMLReport._module_fields:
                    setattr(m, f, XMLReport._get_node_value(item, f))
                ret.append(m)
        return ret

    @property
    def threads(self):
        i = XMLReport._get_first_node(self._xml, 'crash_dump/threads')
        ret = []
        all_subitems = i.xpath('thread') if i is not None else None
        if all_subitems is not None:
            for item in all_subitems:
                m = XMLReport.Thread(self)
                for f in XMLReport._thread_fields:
                    setattr(m, f, XMLReport._get_node_value(item, f))
                ret.append(m)
        return ret

    @property
    def memory_regions(self):
        i = XMLReport._get_first_node(self._xml, 'crash_dump/memory')
        ret = []
        all_subitems = i.xpath('memory') if i is not None else None
        if all_subitems is not None:
            for item in all_subitems:
                m = XMLReport.MemoryRegion(self)
                for f in XMLReport._memory_region_fields:
                    setattr(m, f, XMLReport._get_node_value(item, f))
                ret.append(m)
        return ret

    @property
    def memory_blocks(self):
        i = XMLReport._get_first_node(self._xml, 'crash_dump/memory_blocks')
        ret = []
        all_subitems = i.xpath('memory_block') if i is not None else None
        if all_subitems is not None:
            for item in all_subitems:
                m = XMLReport.MemoryRegion(self)
                for f in XMLReport._memory_block_fields:
                    setattr(m, f, XMLReport._get_node_value(item, f))
                ret.append(m)
        return ret

    @property
    def handles(self):
        i = XMLReport._get_first_node(self._xml, 'crash_dump/handle')
        ret = []
        all_subitems = i.xpath('handle') if i is not None else None
        if all_subitems is not None:
            for item in all_subitems:
                m = XMLReport.Handle(self)
                for f in XMLReport._handle_fields:
                    setattr(m, f, XMLReport._get_node_value(item, f))
                ret.append(m)
        return ret

    @property
    def stackdumps(self):
        i = XMLReport._get_first_node(self._xml, 'crash_dump/stackdumps')
        ret = []
        all_subitems = i.xpath('stackdump') if i is not None else None
        if all_subitems is not None:
            for item in all_subitems:
                m = XMLReport.StackDump(self)
                for f in XMLReport._stackdump_fields:
                    setattr(m, f, XMLReport._get_attribute(item, f))

                m.callstack = []
                all_subitems = item.xpath('frame')
                if all_subitems is not None:
                    for item in all_subitems:
                        frame = XMLReport.StackFrame(self)
                        for f in XMLReport._stack_frame_fields:
                            setattr(frame, f, XMLReport._get_node_value(item, f))
                        m.callstack.append(frame)

                ret.append(m)
        return ret

    @property
    def fields(self):
        return ['crash_info', 'system_info', 'file_info', 'exception',
                'assertion', 'modules', 'threads', 'memory_regions',
                'memory_blocks', 'handles', 'stackdumps' ]

    def to_html(self):
        return str(self.crash_info)


if __name__ == '__main__':
    xmlreport = XMLReport(sys.argv[1])
    print(xmlreport.crash_info)
    print(xmlreport.system_info)
    print(xmlreport.file_info)
    for m in xmlreport.modules:
        print(m)
    for m in xmlreport.threads:
        print(m)
    for m in xmlreport.handles:
        print(m)
    for m in xmlreport.memory_regions:
        print(m)
    for m in xmlreport.stackdumps:
        print(m.threadid)
        for f in m.callstack:
            print(f)
    for m in xmlreport.memory_blocks:
        print(m)


