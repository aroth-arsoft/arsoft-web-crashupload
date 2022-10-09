#!/usr/bin/python
# -*- coding: utf-8 -*-
# kate: space-indent on; indent-width 4; mixedindent off; indent-mode python;

from django import template
from django.urls import get_script_prefix
from django.conf import settings
from django.utils.html import escape
from django.urls.resolvers import *

register = template.Library()

class URLListNode(template.Node):
    def __init__(self, urllist):
        self._urllist = template.Variable(urllist)

    def render_url_list(self, urllist, context, depth=0):
        ret = ''
        try:
            it = iter(urllist)
        except Exception:
            it = None
        if it:
            #ret += '<ul>depth=%i&nbsp;' % depth
            ret += '<ul>'
            for entry in it:
                if entry is None:
                    continue
                ret += '<li>'

                name = None
                props = {}
                
                if isinstance(entry, str):
                    name = str(entry)
                elif isinstance(entry, URLResolver):
                    #name = 'URLResolver(%s)' % entry.urlconf_name
                    name = 'URLResolver'
                    props['pattern'] = entry.pattern
                    props['namespace'] = entry.namespace
                    props['app_name'] = entry.app_name
                    props['default_kwargs'] = entry.default_kwargs
                    props['namespace_dict'] = entry.namespace_dict

                    
                elif isinstance(entry, URLPattern):
                    name = 'URLPattern(%s)' % entry.name
                    props['pattern'] = entry.pattern
                elif isinstance(entry, list):
                    name = 'list(%i): ' % len(list)
                elif isinstance(entry,CheckURLMixin):
                    name = 'CheckURLMixin(%s): ' % entry.describe()
                else:
                    if hasattr(entry, 'regex'):
                        props['regex'] = str(entry.regex)
                    if hasattr(entry, 'urlconf_name'):
                        name = entry.urlconf_name
                if name:
                    ret += escape(name) + ':'
                
                for k,v in props.items():
                    ret += '%s=%s, ' % (k, escape(v))

                if hasattr(entry, 'url_patterns'):
                    ret += self.render_url_list(entry.url_patterns, context, depth=depth + 1)        
                elif isinstance(entry, list):
                    ret += self.render_url_list(entry, context, depth=depth + 1)        
    
                ret += '</li>'
            ret += '</ul>'
        elif isinstance(urllist, URLResolver):
            ret += self.render_url_list([urllist], context, depth=depth + 1)        
        else:
            ret += 'No-It: %s' % escape(urllist)
        return ret

    def render(self, context):
        try:
            urllist = self._urllist.resolve(context)
            return self.render_url_list(urllist, context)
        except template.VariableDoesNotExist:
            return 'Variable %s does not exist' % self._urllist

def do_show_url_list(parser, token):
    url = None
    # split_contents() knows not to split quoted strings.
    e = token.split_contents()
    if len(e) >= 2:
        url = e[1]
    return URLListNode(url)

register.tag('show_url_list', do_show_url_list)
