# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007 Mandriva, http://www.mandriva.com/
#
# $Id$
#
# This file is part of Mandriva Management Console (MMC).
#
# MMC is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# MMC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MMC; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import logging
import os

import mmc.plugins.imaging.images
import mmc.plugins.imaging.iso
from mmc.plugins.imaging.config import ImagingConfig
from mmc.support.mmctools import *
from pulse2.database.imaging import ImagingDatabase

VERSION = "0.1"
APIVERSION = "0:0:0"
REVISION = int("$Rev$".split(':')[1].strip(' $'))

def getVersion(): return VERSION
def getApiVersion(): return APIVERSION
def getRevision(): return REVISION

def activate():
    """
    Run some tests to ensure the module is ready to operate.
    """
    logger = logging.getLogger()
    config = ImagingConfig()
    config.init("imaging")

    if config.disable:
        logger.warning("Plugin imaging: disabled by configuration.")
        return False
    # TODO: check images directories exists    
    return True    

class ContextMaker(ContextMakerI):
    def getContext(self):
        s = SecurityContext()
        s.userid = self.userid
        return s

class RpcProxy(RpcProxyI):
    """ XML/RPC Bindings """

    """ DEPRECATED """
    def getPublicImagesList():
        """
        Return a list of public images

        Only images names are returned
        """
        mylist = []
        for image in mmc.plugins.imaging.images.getPublicImages().values():
            mylist.append(image.name)
        return mylist

    def getPublicImageInfos(name):
        """
        Return some informations about an Image

        """
        return xmlrpcCleanup(mmc.plugins.imaging.images.Image(name).getRawInfo())

    def deletePublicImage(name):
        """
        delete an Image

        """
        mmc.plugins.imaging.images.Image(name).delete()

    def isAnImage(name):
        """
        Check if pub image is a real image

        """
        config = mmc.plugins.imaging.ImagingConfig("imaging")
        return mmc.plugins.imaging.images.hasImagingData(os.path.join(config.publicpath, name))

    def duplicatePublicImage(name, newname):
        """
        duplicate an Image

        """
        config = mmc.plugins.imaging.ImagingConfig("imaging")
        newpath = os.path.join(config.publicpath, newname)
        if os.path.exists(newpath): # target already exists
            return 1
        if os.path.islink(newpath): # target already exists
            return 1
        try:
            mmc.plugins.imaging.images.Image(name).copy(newname)
        except: # something weird append
            shutil.rmtree(newpath)
            return 255
        else:   # copy succedeed
            return 0

    def setPublicImageData(name, newname, title, desc):
        """
        duplicate an Image

        """
        config = mmc.plugins.imaging.ImagingConfig("imaging")
        newpath = os.path.join(config.publicpath, newname)
        if name != newname:
            if os.path.exists(newpath): # target already exists
                return 1
            if os.path.islink(newpath): # target already exists
                return 1
            try:
                mmc.plugins.imaging.images.Image(name).move(newname)
            except: # something weird append
                return 255
        mmc.plugins.imaging.images.Image(newname).setTitle(title)
        mmc.plugins.imaging.images.Image(newname).setDesc(desc)
        return 0

    def createIsoFromImage(name, filename, size):
        """
        create an iso from an image

        """
        config = mmc.plugins.imaging.ImagingConfig("imaging")
        image = mmc.plugins.imaging.iso.Iso(name, filename, size)
        image.prepareImage()
        image.createImage()
        return 0

    """ END DEPRECATED """

    def getMachineBootMenu(self, id):
        return [
            ['Start computer', 'Boot on system hard drive', True, True, True, True],
            ['Create rescue image', 'Backup system hard drive', "", True, "", True],
            ['Create master', 'Backup system hard drive as a master', "", True, "", True]
        ]

    def getProfileBootMenu(self, id):
        return [
            ['Start computer', 'Boot on system hard drive', True, True, True, True],
            ['Create rescue image', 'Backup system hard drive', "", True, "", True],
            ['Create master', 'Backup system hard drive as a master', "", True, "", True]
        ]

    def getMachineImages(self, id):
        return {
            'images': [
                ['MDV 2008.0', 'Mandriva 2008 Backup', '2009-02-25 17:38', '1GB', True]
            ],
            'masters': [
                ['MDV 2008.0', 'Mandriva 2008 Master', '2009-02-25 17:38', '1GB', False]
            ]
        }

    def getProfileImages(self, id):
        return {
            'images': [
                ['MDV 2008.0', 'Mandriva 2008 Backup', '2009-02-25 17:38', '1GB', True]
            ],
            'masters': [
                ['MDV 2008.0', 'Mandriva 2008 Master', '2009-02-25 17:38', '1GB', False]
            ]
        }

    def getMachineBootServices(self, id):
        return [
            ['Local hard disk', True],
            ['Create image', True],
            ['Create master', True],
            ['Memtest', False],
            ['MBR Fix', False]
        ]

    def getProfileBootServices(self, id):
        return [
            ['Local hard disk', True],
            ['Create image', True],
            ['Create master', True],
            ['Memtest', False],
            ['MBR Fix', False]
        ]

    def getMachineLogs(self, id, start, end):
        ret = [
            ['23/10/2009 18:00 - Backup image', '75', 'backup_in_progress'],
            ['20/10/2009 16:44 - Restore of image MDV 2008', '100', 'restore_done'],
            ['18/10/2009 12:00 - Restore of image MDV 2008', '22', 'restore_fail'],
            ['16/10/2009 12:00 - Restore of image MDV 2008', '45', 'plop'],
            ['23/10/2009 18:00 - Backup image', '75', 'backup_in_progress'],
            ['20/10/2009 16:44 - Restore of image MDV 2008', '100', 'restore_done'],
            ['18/10/2009 12:00 - Restore of image MDV 2008', '22', 'restore_fail'],
            ['16/10/2009 12:00 - Restore of image MDV 2008', '45', 'plop'],
            ['23/10/2009 18:00 - Backup image', '75', 'backup_in_progress'],
            ['20/10/2009 16:44 - Restore of image MDV 2008', '100', 'restore_done'],
            ['18/10/2009 12:00 - Restore of image MDV 2008', '22', 'restore_fail'],
            ['16/10/2009 12:00 - Restore of image MDV 2008', '45', 'plop'],
            ['23/10/2009 18:00 - Backup image', '75', 'backup_in_progress'],
            ['20/10/2009 16:44 - Restore of image MDV 2008', '100', 'restore_done'],
            ['18/10/2009 12:00 - Restore of image MDV 2008', '22', 'restore_fail'],
            ['16/10/2009 12:00 - Restore of image MDV 2008', '45', 'plop'],
        ]

        return [len(ret), ret[int(start):int(end)+1]]

    def getProfileLogs(self, id, start, end):
        return [ 4, [
            ['23/10/2009 18:00 - Backup image', '75', 'backup_in_progress'],
            ['20/10/2009 16:44 - Restore of image MDV 2008', '100', 'restore_done'],
            ['18/10/2009 12:00 - Restore of image MDV 2008', '22', 'restore_fail'],
            ['16/10/2009 12:00 - Restore of image MDV 2008', '45', 'plop'],
        ]]
