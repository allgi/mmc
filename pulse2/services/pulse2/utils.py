# -*- coding: utf-8; -*-
#
# (c) 2007-2010 Mandriva, http://www.mandriva.com/
#
# $Id$
#
# This file is part of Pulse 2, http://pulse2.mandriva.org
#
# Pulse 2 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2.  If not, see <http://www.gnu.org/licenses/>.

"""
Some common utility methods used by Pulse 2 components
"""

# to build Pulse2ConfigParser on top of ConfigParser()
from ConfigParser import ConfigParser

# some imports to convert stuff in xmlrpcCleanup()
import datetime
import re
import os
from time import struct_time
import inspect

# python 2.3 fallback for set() in xmlrpcleanup
try:
    set
except NameError:
    from sets import Set as set

try:
    import mx.DateTime as mxDateTime
except ImportError:
    mxDateTime = None

class Singleton(object):
    """
        Duplicate from the Singleton() class from the MMC Project,
        to remove unwanted dependancies
    """
    def __new__(type):
        if not '_the_instance' in type.__dict__:
            type._the_instance = object.__new__(type)
        return type._the_instance

class Pulse2ConfigParser(ConfigParser):
    """
        Duplicate from the MMCConfigParser() class from the MMC Project,
        to remove unwanted dependancies
    """
    def __init__(self):
        ConfigParser.__init__(self)

    def getpassword(self, section, option):
        """
        Like get, but interpret the value as a obfuscated password if a
        password scheme is specified.

        For example: passwd = {base64}bWFuL2RyaXZhMjAwOA==
        """
        value = self.get(section, option)
        m = re.search('^{(\w+)}(.+)$', value)
        if m:
            scheme = m.group(1)
            obfuscated = m.group(2)
            ret = obfuscated.decode(scheme)
        else:
            ret = value
        return ret


def xmlrpcCleanup(data):
    """
        Duplicate from mmc.support.mmctools.xmlrpcCleanup()
        to remove unwanted dependancies
    """
    if type(data) == dict:
        ret = {}
        for key in data.keys():
            # array keys must be string
            ret[str(key)] = xmlrpcCleanup(data[key])
    elif type(data) == list:
        ret = []
        for item in data:
            ret.append(xmlrpcCleanup(item))
    elif type(data) == set:
        ret = []
        for item in data:
            ret.append(xmlrpcCleanup(item))
    elif type(data) == datetime.date:
        ret = tuple(data.timetuple())
    elif type(data) == datetime.datetime:
        ret = tuple(data.timetuple())
    elif mxDateTime and type(data) == mxDateTime.DateTimeType:
        ret = data.tuple()
    elif type(data) == struct_time:
        ret = tuple(data)
    elif data == None:
        ret = False
    elif type(data) == tuple:
        ret = map(lambda x: xmlrpcCleanup(x), data)
    elif type(data) == long:
        ret = str(data)
    else:
        ret = data
    return ret



def unique(s):
    """
    Return a list of the elements in s, but without duplicates.

    For example, unique([1,2,3,1,2,3]) is some permutation of [1,2,3],
    unique("abcabc") some permutation of ["a", "b", "c"], and
    unique(([1, 2], [2, 3], [1, 2])) some permutation of
    [[2, 3], [1, 2]].

    For best speed, all sequence elements should be hashable.  Then
    unique() will usually work in linear time.

    If not possible, the sequence elements should enjoy a total
    ordering, and if list(s).sort() doesn't raise TypeError it's
    assumed that they do enjoy a total ordering.  Then unique() will
    usually work in O(N*log2(N)) time.

    If that's not possible either, the sequence elements must support
    equality-testing.  Then unique() will usually work in quadratic
    time.
    """

    n = len(s)
    if n == 0:
        return []

    # Try using a dict first, as that's the fastest and will usually
    # work.  If it doesn't work, it will usually fail quickly, so it
    # usually doesn't cost much to *try* it.  It requires that all the
    # sequence elements be hashable, and support equality comparison.
    u = {}
    try:
        for x in s:
            u[x] = 1
    except TypeError:
        u = None # move on to the next method

    if u != None:
        return u.keys()
    del u

    # We can't hash all the elements.  Second fastest is to sort,
    # which brings the equal elements together; then duplicates are
    # easy to weed out in a single pass.
    # NOTE:  Python's list.sort() was designed to be efficient in the
    # presence of many duplicate elements.  This isn't true of all
    # sort functions in all languages or libraries, so this approach
    # is more effective in Python than it may be elsewhere.
    try:
        t = list(s)
        t.sort()
    except TypeError:
        t = None # move on to the next method

    if t != None:
        assert n > 0
        last = t[0]
        lasti = i = 1
        while i < n:
            if t[i] != last:
                t[lasti] = last = t[i]
                lasti += 1
            i += 1
        return t[:lasti]
    else:
        del t

    # Brute force is all that's left.
    u = []
    for x in s:
        if x not in u:
            u.append(x)
    return u

def same_network(ip1, ip2, netmask):
    try:
        ip1 = map(lambda x:int(x), ip1.split('.'))
        ip2 = map(lambda x:int(x), ip2.split('.'))
        netmask = map(lambda x:int(x), netmask.split('.'))
        for i in [0,1,2,3]:
            if ip1[i].__and__(netmask[i]) != ip2[i].__and__(netmask[i]):
                return False
    except ValueError:
        return False
    return True

def onlyAddNew(obj, value):
    if type(value) == list:
        for i in value:
            try:
                obj.index(i)
            except:
                obj.append(i)
    else:
        try:
            obj.index(value)
        except:
            obj.append(value)
    return obj


def getConfigFile(module, path = "/etc/mmc/plugins/"):
    """Return the path of the default config file for a plugin"""
    return os.path.join(path, module) + ".ini"

def isdigit(i):
    if type(i) == int or type(i) == long:
        return True
    if (type(i) == str or type(i) == unicode) and re.search("^\d*$",i):
        return True
    return False

def grep(string,list):
    expr = re.compile(string)
    return filter(expr.search,list)

def grepv(string,list):
    expr = re.compile(string)
    return [item for item in list if not expr.search(item)]

def whoami():
    return inspect.stack()[1][3]

def whosdaddy():
    return inspect.stack()[2][3]

def isCiscoMacAddress(mac_addr):
    """
    Check that the given MAC adress is a cisco-formatted MAC Address.

    @type mac_addr: str
    @param mac_addr: the mac addr to check
    @returns: returns True if the given MAC address is valid
    @rtype: bool
    """
    if type(mac_addr) != str:
        return False
    regex = '^([0-9a-f]{4}\.[0-9a-f]{4}\.[0-9a-f]{4})$'
    return re.match(regex, mac_addr) != None

def isLinuxMacAddress(mac_addr):
    """
    Check that the given MAC adress is a linux-formatted MAC Address.

    @type mac_addr: str
    @param mac_addr: the mac addr to check
    @returns: returns True if the given MAC address is valid
    @rtype: bool
    """
    if type(mac_addr) != str:
        return False
    regex = '^([0-9a-fA-F][0-9a-fA-F]:){5}([0-9a-fA-F][0-9a-fA-F])$'
    return re.match(regex, mac_addr) != None

def isWinMacAddress(mac_addr):
    """
    Check that the given MAC adress is a windows-formatted MAC Address.

    @type mac_addr: str
    @param mac_addr: the mac addr to check
    @returns: returns True if the given MAC address is valid
    @rtype: bool
    """

    if type(mac_addr) != str:
        return False
    regex = '^([0-9a-fA-F][0-9a-fA-F]-){5}([0-9a-fA-F][0-9a-fA-F])$'
    return re.match(regex, mac_addr) != None

def isShortMacAddress(mac_addr):
    """
    Check that the given MAC adress is a short-formatted MAC Address.

    @type mac_addr: str
    @param mac_addr: the mac addr to check
    @returns: returns True if the given MAC address is valid
    @rtype: bool
    """

    if type(mac_addr) != str:
        return False
    regex = '^(([0-9a-fA-F]){12})$'
    return re.match(regex, mac_addr) != None

def isMACAddress(mac_addr):
    """
    Check that the given MAC adress seems to be a MAC Address.

    @type mac_addr: str
    @param mac_addr: the mac addr to check
    @returns: returns True if the given MAC address is valid
    @rtype: bool
    """
    if type(mac_addr) != str:
        return False
    return isCiscoMacAddress(mac_addr) or isLinuxMacAddress(mac_addr) or isWinMacAddress(mac_addr) or isShortMacAddress(mac_addr)

def splitComputerPath(path):
    """
    Split the computer path according to this scheme:
     profile:/entity1/entity2/computerName

    @raise TypeError: if the computer path is not valid
    @returns: returns a tuple with (profile, entities, hostname, domain)
    @rtype: tuple
    """
    # Get profile
    m = re.match("^([a-zA-Z0-9]*):(.*)$", path)
    if m:
        profile = m.group(1)
        tail = m.group(2)
    else:
        profile = ''
        tail = path

    # Split entity path and computer FQDN
    entities, fqdn = os.path.split(tail)

    if entities and entities != '/':
        if not entities.startswith('/'):
            raise TypeError
        # Check entities
        for entity in entities.split('/'):
            # FIXME: re to check entity name ?
            if entity and not re.match('^[a-zA-Z0-9]{3,64}$', entity):
                raise TypeError, 'Bad entity: %s' % entity
    else:
        entities = ''

    if '.' in fqdn:
        hostname, domain = fqdn.split('.', 1)
    else:
        hostname = fqdn
        domain = ''

    if domain and not re.match('^([a-z][a-z0-9-]*[a-z0-9]\.){0,10}[a-z][a-z0-9-]*[a-z0-9]$', domain):
        raise TypeError, 'Bad domain: %s' % domain

    if not re.match('^[a-z][a-z0-9-]*[a-z0-9]$', hostname):
        raise TypeError, 'Bad hostname: %s' % hostname

    return (profile, entities, hostname, domain)