#!/usr/bin/python
# -*- coding: utf-8 -*-
# kate: space-indent on; indent-width 4; mixedindent off; indent-mode python;

from django import template
from functools import partial
from crashdump.utils import *

register = template.Library()


def do_tag_function_wrapper(func, parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, number = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag takes one argument" % token.contents.split()[0])
    class Node(template.Node):
        def __init__(self, func, number):
            self._func = func
            self.number = template.Variable(number)
        def render(self, context):
            return self._func(self.number.resolve(context))
    return Node(func, number)

def do_tag_function_wrapper2(func, parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, number, number2 = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag takes two arguments" % token.contents.split()[0])
    class Node(template.Node):
        def __init__(self, func, number, number2):
            self._func = func
            self.number = template.Variable(number)
            self.number2 = template.Variable(number2)
        def render(self, context):
            return self._func(self.number.resolve(context), self.number2.resolve(context))
    return Node(func, number, number2)

def do_tag_function_wrapper3(func, parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, number, number2, number3 = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag takes three arguments" % token.contents.split()[0])
    class Node(template.Node):
        def __init__(self, func, number, number2, number3):
            self._func = func
            self.number = template.Variable(number)
            self.number2 = template.Variable(number2)
            self.number3 = template.Variable(number3)
        def render(self, context):
            return self._func(self.number.resolve(context), self.number2.resolve(context), self.number3.resolve(context))
    return Node(func, number, number2, number3)

register.tag('format_size', partial(do_tag_function_wrapper, format_size))
register.tag('format_seconds', partial(do_tag_function_wrapper, format_seconds))
register.tag('format_milliseconds', partial(do_tag_function_wrapper, format_milliseconds))
register.tag('hex_format', partial(do_tag_function_wrapper, hex_format))
register.tag('hex_format_bits', partial(do_tag_function_wrapper2, hex_format_bits))
register.tag('addr_format', partial(do_tag_function_wrapper, addr_format))
register.tag('addr_format_bits', partial(do_tag_function_wrapper2, addr_format_bits))
register.tag('format_trust_level', partial(do_tag_function_wrapper, format_trust_level))

register.tag('format_source_line', partial(do_tag_function_wrapper2, format_source_line))
register.tag('exception_code', partial(do_tag_function_wrapper3, exception_code))
register.tag('format_bool_yesno', partial(do_tag_function_wrapper, format_bool_yesno))
register.tag('format_function_plus_offset', partial(do_tag_function_wrapper2, format_function_plus_offset))
register.tag('str_or_unknown', partial(do_tag_function_wrapper, str_or_unknown))

register.tag('format_cpu_type', partial(do_tag_function_wrapper, format_cpu_type))
register.tag('format_cpu_vendor', partial(do_tag_function_wrapper, format_cpu_vendor))
register.tag('format_cpu_name', partial(do_tag_function_wrapper2, format_cpu_name))

register.tag('format_distribution_id', partial(do_tag_function_wrapper, format_distribution_id))
register.tag('format_distribution_codename', partial(do_tag_function_wrapper2, format_distribution_codename))

register.tag('format_memory_usagetype', partial(do_tag_function_wrapper, format_memory_usagetype))
register.tag('format_gl_extension_name', partial(do_tag_function_wrapper, format_gl_extension_name))
register.tag('format_version_number', partial(do_tag_function_wrapper, format_version_number))
register.tag('format_platform_type', partial(do_tag_function_wrapper, format_platform_type))
register.tag('format_os_version', partial(do_tag_function_wrapper3, format_os_version))
register.tag('language_from_qlocale_language_enum', partial(do_tag_function_wrapper, language_from_qlocale_language_enum))
register.tag('country_from_qlocale_country_enum', partial(do_tag_function_wrapper, country_from_qlocale_country_enum))
register.tag('script_from_qlocale_script_enum', partial(do_tag_function_wrapper, script_from_qlocale_script_enum))
register.tag('thread_extra_info', partial(do_tag_function_wrapper, thread_extra_info))
register.tag('format_thread', partial(do_tag_function_wrapper, format_thread))
register.tag('format_stack_frame', partial(do_tag_function_wrapper, format_stack_frame))
