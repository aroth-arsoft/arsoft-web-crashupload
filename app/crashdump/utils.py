#!/usr/bin/python
# -*- coding: utf-8 -*-
# kate: space-indent on; indent-width 4; mixedindent off; indent-mode python;

crashdump_use_jinja2 = False

def _(msg):
    return msg

def tag_a(name, title=None, href=None, alt=None):
    from xml.etree.ElementTree import Element, tostring
    a = Element('a')
    a.text = name
    if href:
        a.set('href', href)
    if title:
        a.set('title', title)
    if alt:
        a.set('alt', alt)
    return tostring(a, encoding="utf8", method='html').decode()

def _hex_format(number, prefix='0x', width=None, bits=None):
    if isinstance(number, str):
        try:
            number = int(number)
        except ValueError:
            number = None
    if number is None:
        return '(none)'
    if bits is not None:
        if bits == 32:
            number = number & 0xffffffff
            if width is None:
                width = 8
        elif bits == 64:
            number = number & 0xffffffffffffffff
            if width is None:
                width = 16

    if width is None:
        if number > 2**48:
            width = 16
        elif number > 2**40:
            width = 12
        elif number > 2**32:
            width = 10
        elif number > 2**24:
            width = 8
        elif number > 2**16:
            width = 6
        elif number > 2**8:
            width = 4
        else:
            width = 2
    fmt = '%%0%ix' % width
    return prefix + fmt % number

def hex_format(number, prefix='0x', width=None, bits=None):
    if isinstance(number, list):
        nums = []
        for n in number:
            nums.append(_hex_format(n, prefix, width, bits))
        return ','.join(nums)
    else:
        return _hex_format(number, prefix, width, bits)

def hex_format_bits(number, bits):
    return hex_format(number, bits=bits)

def addr_format(number, prefix='0x', bits=64):
    if number == 0:
        return 'NULL'
    elif number < 256:
        return hex_format(number, 'NULL+' + prefix, bits=bits)
    else:
        return hex_format(number, prefix, bits=bits)

def addr_format_64(number, prefix='0x'):
    if number == 0:
        return 'NULL'
    elif number < 256:
        return hex_format(number, 'NULL+' + prefix, bits=64)
    else:
        return hex_format(number, prefix, bits=64)

def addr_format_32(number, prefix='0x'):
    if number == 0:
        return 'NULL'
    elif number < 256:
        return hex_format(number, 'NULL+' + prefix, bits=32)
    else:
        return hex_format(number, prefix, bits=32)

def addr_format_bits(number, bits=64):
    return addr_format(number, bits=bits)

def exception_code(platform_type, code, name):
    if platform_type is None:
        return 'Platform unknown'
    elif platform_type == 'Linux':
        return tag_a(str(name) + '(' + hex_format(code) + ')', href='https://en.wikipedia.org/wiki/Unix_signal')
    elif platform_type == 'Windows NT':
        return tag_a(str(name) + '(' + hex_format(code) + ')', href='https://en.wikipedia.org/wiki/Windows_NT')
    elif platform_type == 'Windows':
        return tag_a(str(name) + '(' + hex_format(code) + ')', href='https://en.wikipedia.org/wiki/Microsoft_Windows')
    else:
        return tag_a(str(name) + '(' + hex_format(code) + ')', href='https://en.wikipedia.org/wiki/Special:Search/' + str(platform_type))

def format_bool_yesno(val):
    if isinstance(val, str) or isinstance(val, unicode):
        try:
            val = bool(val)
        except ValueError:
            val = None
    if val is None:
        return '(none)'
    elif val == True:
        return _('yes')
    elif val == False:
        return _('no')
    else:
        return _('neither')

def format_source_line(source, line, line_offset=None, source_url=None):
    if source is None:
        return _('unknown')
    else:
        title = str(source) + ':' + str(line)
        if line_offset is not None:
            title += '+' + hex_format(line_offset)
        if source_url is not None:
            href = source_url
        else:
            href='file:///' + str(source)
        return tag_a(title, href=href)

def format_function_plus_offset(function, funcoff=None):
    if function is None:
        return _('unknown')
    else:
        if funcoff:
            return str(function) + '+' + hex_format(funcoff)
        else:
            return str(function)

def str_or_unknown(str):
    if str is None:
        return _('unknown')
    else:
        return str

def format_cpu_type(cputype):
    cputype = cputype.lower()
    if cputype == 'amd64':
        href='http://en.wikipedia.org/wiki/X86-64'
        title = 'x86-64 (also known as x64, x86_64 and AMD64)'
    elif cputype == 'x86':
        href='http://en.wikipedia.org/wiki/X86'
        title = 'x86 (also known as i386)'
    elif cputype == 'mips':
        href='http://en.wikipedia.org/wiki/MIPS_instruction_set'
        title = 'MIPS  instruction set'
    elif cputype == 'alpha':
        href='http://en.wikipedia.org/wiki/DEC_Alpha'
        title = 'Alpha, originally known as Alpha AXP'
    elif cputype == 'alpha64':
        href='http://en.wikipedia.org/wiki/DEC_Alpha'
        title = 'Alpha64, originally known as Alpha AXP'
    elif cputype == 'powerpc':
        href='http://en.wikipedia.org/wiki/PowerPC'
        title = 'PowerPC'
    elif cputype == 'powerpc64':
        href='http://en.wikipedia.org/wiki/Ppc64'
        title = 'PowerPC64 or ppc64'
    elif cputype == 'arm':
        href='http://en.wikipedia.org/wiki/ARM_architecture'
        title = 'ARM'
    elif cputype == 'arm64':
        href='http://en.wikipedia.org/wiki/ARM_architecture#64-bit'
        title = 'ARM 64-bit'
    elif cputype == 'sparc':
        href='http://en.wikipedia.org/wiki/SPARC'
        title = 'SPARC ("scalable processor architecture")'
    elif cputype == 'ia64':
        href='http://en.wikipedia.org/wiki/Itanium'
        title = 'Intel Itanium architecture (IA-64)'
    elif cputype == 'msil':
        href='http://en.wikipedia.org/wiki/Common_Intermediate_Language'
        title = 'Microsoft Intermediate Language (MSIL)'
    elif cputype == 'x64 wow':
        href='http://en.wikipedia.org/wiki/WoW64'
        title = 'Microsoft WoW64'
    else:
        href = 'http://en.wikipedia.org/wiki/Central_processing_unit'
        title = 'Unknown:%s' % cputype
    return tag_a(title, title=cputype, href=href)

def format_cpu_vendor(vendor):
    if vendor == 'AuthenticAMD':
        title = 'AMD'
        href = 'http://en.wikipedia.org/wiki/Advanced_Micro_Devices'
    elif vendor == 'GenuineIntel':
        title = 'Intel'
        href = 'http://en.wikipedia.org/wiki/Intel'
    elif vendor == 'Microsoft Hv':
        title = 'Microsoft Hyper-V'
        href = 'http://en.wikipedia.org/wiki/Hyper-V'
    elif vendor == 'VMwareVMware':
        title = 'VMware'
        href = 'http://en.wikipedia.org/wiki/VMware'
    elif vendor == 'KVMKVMKVMKVM':
        title = 'KVM'
        href = 'http://en.wikipedia.org/wiki/Kernel-based_Virtual_Machine'
    elif vendor == 'XenVMMXenVMM':
        title = 'Xen'
        href = 'http://en.wikipedia.org/wiki/Xen'
    else:
        title = vendor
        href = 'http://en.wikipedia.org/wiki/List_of_x86_manufacturers'
    return tag_a(title, title=vendor, href=href)

def format_cpu_name(vendor, name):
    # http://en.wikipedia.org/wiki/CPUID
    # http://www.sandpile.org/x86/cpuid.htm
    if vendor == 'AuthenticAMD':
        if name is None:
            title = 'Unknown AMD CPU'
            href = 'http://en.wikipedia.org/wiki/Advanced_Micro_Devices'
        elif name.startswith('AMD Ryzen'):
            href = 'https://en.wikipedia.org/wiki/Ryzen'
            title = 'AMD Ryzen'
        elif name.startswith('AMD FX'):
            href = 'http://en.wikipedia.org/wiki/List_of_AMD_FX_microprocessors'
            title = 'AMD FX-series'
        elif name.startswith('AMD Phenom'):
            href = 'https://en.wikipedia.org/wiki/List_of_AMD_Phenom_microprocessors'
            title = 'AMD Phenom family'
        elif name.startswith('AMD Opteron'):
            href = 'https://en.wikipedia.org/wiki/List_of_AMD_Opteron_microprocessors'
            title = 'AMD Opteron family'
        elif name.startswith('AMD Sempron'):
            href = 'https://en.wikipedia.org/wiki/List_of_AMD_Sempron_microprocessors'
            title = 'AMD Sempron family'
        elif name.startswith('AMD Turion'):
            href = 'https://en.wikipedia.org/wiki/List_of_AMD_Turion_microprocessors'
            title = 'AMD Turion family'
        elif name.startswith('AMD A'):
            href = 'https://en.wikipedia.org/wiki/List_of_AMD_accelerated_processing_unit_microprocessors'
            title = 'AMD APU series'
        else:
            title = 'Unknown AMD CPU'
            href = 'http://en.wikipedia.org/wiki/Advanced_Micro_Devices'
        title = title + ' (%s)' % name
    elif vendor == 'GenuineIntel':
        if name is None:
            title = 'Unknown Intel CPU'
            href = 'https://en.wikipedia.org/wiki/List_of_Intel_microprocessors'
        elif name.startswith('Intel(R) Core(TM) i3'):
            title = 'Intel Core i3 series'
            href = 'http://en.wikipedia.org/wiki/Intel_Core'
        elif name.startswith('Intel(R) Core(TM) i5'):
            title = 'Intel Core i5 series'
            href = 'http://en.wikipedia.org/wiki/Intel_Core'
        elif name.startswith('Intel(R) Core(TM) i7'):
            title = 'Intel Core i7 series'
            href = 'http://en.wikipedia.org/wiki/Intel_Core'
        elif name.startswith('Intel(R) Core(TM) i9'):
            title = 'Intel Core i9 series'
            href = 'http://en.wikipedia.org/wiki/Intel_Core'
        elif name.startswith('Intel(R) Core(TM)'):
            title = 'Unknown Intel Core series'
            href = 'http://en.wikipedia.org/wiki/Intel_Core'
        elif name.startswith('Intel(R) Xeon(R)') or name.startswith('Intel(R) Xeon(TM)'):
            title = 'Intel Xeon series'
            href = 'http://en.wikipedia.org/wiki/Xeon'
        else:
            title = 'Unknown Intel CPU'
            href = 'https://en.wikipedia.org/wiki/List_of_Intel_microprocessors'
        title = title + ' (%s)' % name
    else:
        title = name
        href = 'http://en.wikipedia.org/wiki/List_of_x86_manufacturers'
    return tag_a(name, title=title, href=href)

def format_distribution_id(distro_id):
    if distro_id == 'Debian':
        name = 'Debian'
        href = 'http://www.debian.org'
    elif distro_id == 'Ubuntu':
        name = 'Ubuntu'
        href = 'http://www.ubuntu.com'
    else:
        name = distro_id
        href = 'http://distrowatch.com/' + distro_id
    return tag_a(name, title=distro_id, href=href)

def format_distribution_codename(distro_id, distro_codename):
    if distro_id == 'Debian':
        name = '%s %s' % (distro_id.capitalize(), distro_codename.capitalize())
        href = 'http://www.debian.org/%s%s' % (distro_id.capitalize(), distro_codename.capitalize())
    elif distro_id == 'Ubuntu':
        name = '%s %s' % (distro_id.capitalize(), distro_codename.capitalize())
        href = 'http://ubuntuguide.org/wiki/%s_%s' % (distro_id.capitalize(), distro_codename.capitalize())
    else:
        name = distro_id
        href = 'http://distrowatch.com/' + distro_id
    return tag_a(name, title=distro_id, href=href)

def format_seconds(s):
    if s is None:
        return 'None'
    elif s >= 3600:
        hr = int(float(s) / 3600.0)
        from math import fmod
        m = fmod(float(s), 3600.0) / 60.0
        return '%ihr %0.1fmin' % (hr, m)
    elif s >= 60:
        m = float(s) / 60.0
        return '%0.1fmin' % m
    elif s >= 1:
        return  '%0.1fs' % s
    else:
        return  '%0.1fms' % ( s * 1000.0 )

def format_milliseconds(ms):
    if ms is None:
        return 'None'
    elif ms > 1000:
        s = float(ms) / 1000.0
        return format_seconds(s)
    else:
        return  '%ims' % ms

def format_trust_level(tl):
    if tl == 0 or tl is None:
        return 'Unknown'
    elif tl == 1:
        return 'Stack scan'
    elif tl == 2:
        return 'CFI scan'
    elif tl == 3:
        return 'FP'
    elif tl == 4:
        return 'CFI'
    elif tl == 5:
        return 'External'
    elif tl == 6:
        return 'IP'
    else:
        return 'unknown(%i)' % tl

_suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
def format_size(nbytes):
    if isinstance(nbytes, str):
        try:
            nbytes = int(nbytes)
        except ValueError:
            nbytes = None
    if nbytes == 0: return '0 B'
    elif nbytes is None: return 'None'
    i = 0
    while nbytes >= 1024 and i < len(_suffixes)-1:
        nbytes /= 1024.
        i += 1
    f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
    return '%s&nbsp;%s' % (f, _suffixes[i])

def format_memory_usagetype(usage):
    if usage == 0 or usage is None:
        return 'Unknown'
    elif usage == 1:
        return 'Stack'
    elif usage == 2:
        return 'TEB'
    elif usage == 3:
        return 'PEB'
    elif usage == 4:
        return 'Process Parameters'
    elif usage == 5:
        return 'Environment'
    elif usage == 6:
        return 'IP'
    elif usage == 7:
        return 'Process Heap Handles'
    elif usage == 8:
        return 'Process Heap'
    elif usage == 9:
        return 'TLS'
    elif usage == 10:
        return 'Thread info block'
    else:
        return 'unknown(%i)' % usage

def format_gl_extension_name(ext):
    khronos_extension_base_url = 'https://www.khronos.org/registry/OpenGL/extensions'
    unknown_extension_url = 'https://www.khronos.org/opengl/wiki/OpenGL_Extension'
    title = ext
    name = ext
    href = unknown_extension_url
    vendor = None
    ext_name = None
    if ext.startswith('GL_'):
        vendor_end = ext.index('_', 3)
        if vendor_end > 0:
            vendor = ext[3:vendor_end]
            ext_name = ext[3:]
    elif ext.startswith('GLX_') or ext.startswith('WGL_'):
        vendor_end = ext.index('_', 4)
        if vendor_end > 0:
            vendor = ext[4:vendor_end]
            ext_name = ext
    if vendor and ext_name:
        href = khronos_extension_base_url + '/%s/%s.txt' % (vendor, ext_name)
    return tag_a(name, title=title, href=href)

def format_version_number(num):
    if isinstance(num, str) or isinstance(num, unicode):
        try:
            num = int(num)
        except ValueError:
            num = None
    if num is None: return 'None'
    m, n, o, p = (num >> 48) & 0xffff, (num >> 32) & 0xffff, (num >> 16) & 0xffff, (num >> 0) & 0xffff
    return '%i.%i.%i.%i' % (m, n, o, p)

def format_platform_type(platform_type):
    if platform_type is None:
        return _('Platform unknown')
    elif platform_type == 'Linux':
        return tag_a('Linux', href='https://en.wikipedia.org/wiki/Linux')
    elif platform_type == 'Windows NT':
        return tag_a('Windows NT',href='https://en.wikipedia.org/wiki/Windows_NT')
    elif platform_type == 'Windows':
        return tag_a('Windows', href='https://en.wikipedia.org/wiki/Microsoft_Windows')
    else:
        return tag_a(platform_type, href='https://en.wikipedia.org/wiki/Special:Search/' + str(platform_type))

def _get_version_digit(s):
    i = -1
    for j, c in enumerate(s):
        if not str.isnumeric(c):
            i = j
            break
    if i > 0:
        s = s[0:i]
    ret = None
    try:
        ret = int(s)
    except ValueError:
        pass
    return ret

def _get_version_from_string(number_str):
    elems = number_str.split('.')
    major = 0
    minor = 0
    patch = 0
    build = 0
    if len(elems) >= 1:
        major = _get_version_digit(elems[0])
    if len(elems) >= 2:
        minor = _get_version_digit(elems[1])
    if len(elems) >= 3:
        patch = _get_version_digit(elems[2])
    if len(elems) >= 4:
        build = _get_version_digit(elems[3])
    return major, minor, patch, build

def _get_version_from_numbers(os_version_number, os_build_number):
    #print('_get_version_from_numbers %s, %s' % (os_version_number, os_build_number))
    if isinstance(os_version_number, int):
        major = os_version_number >> 48 & 0xffff
        minor = os_version_number >> 32 & 0xffff
        patch = os_version_number >> 16 & 0xffff
        build = os_version_number & 0xffff
        if build == 0 and os_build_number:
            build = int(os_build_number) if os_build_number is not None else 0
    else:
        major, minor, patch, build = _get_version_from_string(os_version_number)
    #print('%x, %s -> %i.%i.%i.%i' % (os_version_number, os_build_number, major, minor, patch, build))
    return major, minor, patch, build

def get_os_version_number(platform_type, os_version_number, os_build_number):
    if platform_type is None or os_version_number is None:
        return 0
    if platform_type == 'Linux':
        major, minor, patch, build = _get_version_from_string(os_version_number)
    elif platform_type == 'Windows NT':
        major, minor, patch, build = _get_version_from_string(os_version_number)
        if major >= 10:
            build = patch
            patch = 0
    else:
        major = 0
        minor = 0
        patch = 0
        build = 0
    ret = (major << 48) | (minor << 32) | (patch << 16) | build
    #print('ver in %s -> %x' % (os_version_number, ret))
    return ret

def get_os_build_number(platform_type, os_version_number, os_build_number):
    if platform_type is None or os_version_number is None:
        return 0
    if platform_type == 'Linux':
        build = 0
    elif platform_type == 'Windows NT':
        major, minor, patch, build = _get_version_from_string(os_version_number)
        if major >= 10:
            build = patch
    else:
        build = 0
    #print('build in %s -> %x' % (os_version_number, build))
    return build

def os_version_info(platform_type, os_version_number, os_build_number):
    ret = {'text': 'unknown' }
    if platform_type is None or os_version_number is None:
        return ret
    major, minor, patch, build = _get_version_from_numbers(os_version_number, os_build_number)
    if platform_type == 'Linux':
        ret['text'] = 'Linux %i.%i.%i.%i' % (major, minor, patch, build)
        ret['href'] = 'https://en.wikipedia.org/wiki/Linux'
    elif platform_type == 'Windows NT':
        productName = 'Windows %i.%i' % (major, minor)
        marketingName = None
        if (major < 6):
            productName = "Windows XP"
            ret['short'] = 'WinXP'
            ret['href'] = 'https://en.wikipedia.org/wiki/Windows_XP'
        elif (major == 6 and minor == 0):
            productName = "Windows Vista"
            ret['short'] = 'WinVista'
            ret['href'] = 'https://en.wikipedia.org/wiki/Windows_Vista'
        elif (major == 6 and minor == 1):
            productName = "Windows 7"
            ret['short'] = 'Win7'
            ret['href'] = 'https://en.wikipedia.org/wiki/Windows_7'
        elif (major == 6 and minor == 2):
            productName = "Windows 8"
            ret['short'] = 'Win8'
            ret['href'] = 'https://en.wikipedia.org/wiki/Windows_8'
        elif (major == 6 and minor == 3):
            productName = "Windows 8.1"
            ret['short'] = 'Win8.1'
            ret['href'] = 'https://en.wikipedia.org/wiki/Windows_8'
        elif (major == 10):
            ret['href'] = 'https://en.wikipedia.org/wiki/Windows_10'
            # See https://en.wikipedia.org/wiki/Windows_10_version_history
            if build <= 10240:
                ret['short'] = 'Win10'
                productName = "Windows 10"
                marketingName = ''
            elif(build <= 10586):
                ret['short'] = 'Win10/1511'
                productName = "Windows 10 Version 1511"
                marketingName = "November Update"
            elif (build <= 14393):
                ret['short'] = 'Win10/1607'
                productName = "Windows 10 Version 1607"
                marketingName = "Anniversary Update"
            elif (build <= 15063):
                ret['short'] = 'Win10/1703'
                productName = "Windows 10 Version 1703"
                marketingName = "Creators Update"
            elif (build <= 16299):
                ret['short'] = 'Win10/1709'
                productName = "Windows 10 Version 1709"
                marketingName = "Fall Creators Update"
            elif (build <= 17134):
                ret['short'] = 'Win10/1803'
                productName = "Windows 10 Version 1803"
                marketingName = "April 2018 Update"
            elif (build <= 18204):
                ret['short'] = 'Win10/1809'
                productName = "Windows 10 Version 1809"
                marketingName = "October 2018 Update"
            elif (build <= 18362):
                ret['short'] = 'Win10/1903'
                productName = "Windows 10 Version 1903"
                marketingName = "May 2019 Update"
            elif (build <= 18363):
                ret['short'] = 'Win10/1909'
                productName = "Windows 10 Version 1909"
                marketingName = "November 2019 Update"
            elif (build <= 19041):
                ret['short'] = 'Win10/2004'
                productName = "Windows 10 Version 2004"
                marketingName = "May 2020 Update"
            elif (build <= 19042):
                ret['short'] = 'Win10/20H2'
                productName = "Windows 10 Version 20H2"
                marketingName = '20H2'
            elif (build <= 19043):
                ret['short'] = 'Win10/21H1'
                productName = "Windows 10 Version 21H1"
                marketingName = '21H1'
            elif (build <= 19044):
                ret['short'] = 'Win10/21H2'
                productName = "Windows 10 Version 21H2"
                marketingName = '21H2'
            elif (build <= 19045):
                ret['short'] = 'Win10/22H2'
                productName = "Windows 10 Version 22H2"
                marketingName = '22H2'
            else:
                ret['short'] = 'Win10/TBA'
                productName = 'Windows 10 Build %i' % build
        elif (major == 11):
            ret['href'] = 'https://en.wikipedia.org/wiki/Windows_11'
            # See https://en.wikipedia.org/wiki/Windows_11_version_history
            if (build <= 22000):
                ret['short'] = 'Win11/21H2'
                productName = "Windows 11 Version 21H2"
                marketingName = '21H2'
            elif (build <= 22621):
                ret['short'] = 'Win11/22H2'
                productName = "Windows 11 Version 22H2"
                marketingName = '21H2'
            else:
                ret['short'] = 'Win11/TBA'
                productName = 'Windows 11 Build %i' % build
        if marketingName:
            ret['text'] = '%s (%s)' % (productName, marketingName)
        else:
            ret['text'] = productName
        ret['full'] = ret['text'] + ' %i.%i.%i.%i' % (major, minor, patch, build)

    elif platform_type == 'Windows':
        ret['text'] = 'Windows %i.%i' % (major, minor)
        ret['href'] = 'https://en.wikipedia.org/wiki/Microsoft_Windows'
    return ret

def format_os_version(platform_type, os_version_number, os_build_number):
    info = os_version_info(platform_type, os_version_number, os_build_number)
    if 'href' in info:
        return tag_a(info.get('text'), href=info.get('href'))
    else:
        return info.get('text')

def format_os_version_short(platform_type, os_version_number, os_build_number):
    info = os_version_info(platform_type, os_version_number, os_build_number)
    if 'short' in info:
        return info.get('short')
    else:
        return info.get('text')

def language_from_qlocale_language_enum(num):
    _codes = {
        0: 'Any language',
        31: 'English',
        42: 'German',
    }
    if num in _codes:
        return _codes[num]
    else:
        return str(num)

# See https://doc.qt.io/qt-5/qlocale.html#Country-enum
def country_from_qlocale_country_enum(num):
    _codes = {
        0: 'Any country',
        82: 'Germany',
        224: 'United Kingdom',
        225: 'United States',
    }
    if num in _codes:
        return _codes[num]
    else:
        return str(num)

# https://doc.qt.io/qt-5/qlocale.html#Script-enum
def script_from_qlocale_script_enum(num):
    _codes = {
        0: 'Any script',
        1: 'Arabic',
        2: 'Cyrillic',
        16: 'Greek',
        7: 'Latin',
    }
    if num in _codes:
        return _codes[num]
    else:
        return str(num)

def thread_extra_info(thread):
    if thread is None:
        return _('N/A')
    elif thread.main_thread:
        return '*@' if thread.exception else '@'
    elif thread.rpc_thread:
        return '*[RPC]' if thread.exception else '[RPC]'
    elif thread.exception:
        return '*'
    else:
        return ''

def format_thread(thread):
    if thread is None:
        return _('N/A')
    else:
        if thread.main_thread:
            ret = _('Main thread')
        elif thread.rpc_thread:
            ret = _('RPC thread')
        else:
            ret = _('Thread')
        ret = ret + ' ' + hex_format(thread.id)
        if thread.name:
            ret = ret + ' ' + thread.name
        if thread.exception:
            ret = ret + ' ' + _('with exception')
        return ret

def format_stack_frame(frame):
    if frame is None:
        return _('N/A')
    else:
        if frame.function is None:
            offset = frame.addr - frame.module_base
            if frame.module:
                return frame.module + '+' + hex_format(offset)
            else:
                return frame.addr
        else:
            return format_function_plus_offset(frame.function, frame.funcoff)

if __name__ == '__main__':
    x = _get_version_from_string("6.1 Service Pack 1")
    print(x)