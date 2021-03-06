#!/usr/bin/python
# -*- coding: utf-8; -*-
#
# (c) 2012 Mandriva, http://www.mandriva.com/
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
# along with Pulse 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

"""
Anticipated executing of scheduled tasks on scheduler.
"""
import logging 
from time import sleep

from pulse2.inventoryserver.utils import InventoryUtils, MMCProxy


class AttemptToScheduler :
    """
    Trigger to early executions of scheduled attempts.

    This engine is called when an inventory is received.
    """

    # First delay after the inventory reception
    # TODO - move the delays in a .ini file ?
    FIRST_DELAY = 60 
    BETWEEN_TASKS_DELAY = 1

    def __init__(self, from_ip, uuid):
        """
        @param from_ip: IP address of inventory source 
        @type from_ip: string

        @param uuid: Host UUID
        @type uuid: string

        """
        # Test to resolve the inventory source
  
        if not InventoryUtils.is_comming_from_pxe(from_ip) :

            logging.getLogger().info("<scheduler> : Start")
            self.uuid = uuid
            mmc = MMCProxy()
            if not mmc.failure :
                self.proxy = mmc.proxy
                self.dispatch_msc()
            else :
                logging.getLogger().warn("<scheduler> : Building the mmc proxy failed")
                logging.getLogger().warn("<scheduler> : Exit the scheduler trigger")
            logging.getLogger().info("<scheduler> : Return to inventory")

        else :

            logging.getLogger().info("<scheduler> : Incoming from PXE : ignore")


    def dispatch_msc (self):
        """ 
        Get a filtered list of scheduled tasks and executing each of them.
        """

        params = {"uuid" : self.uuid}
        try :
            result = self.proxy.msc.displayLogs(params)
        except Exception, err :

            logging.getLogger().error("<scheduler> : Error while executing 'msc.displayLogs'")
            logging.getLogger().error("<scheduler> : %s" % err)                        
            return False

        _size, _tasks = result

        unauthorised_states = ['failed',
                               'done',
                               'upload_in_progress',
                               'execution_in_progress',
                               'delete_in_progress',
                               'inventory_in_progress',
                               'reboot_in_progress',
                               'wol_in_progress',
                               'halt_in_progress',
                               ]
 
        # task queryset structure (single line):
        # commands__columns, id, current_state, command_on_host__columns

        # we need only ids (cohs) excluding unauthorised states
        tasks = [a[1] for a in _tasks if a[2] not in unauthorised_states]

        if len(tasks) == 0 :
            logging.getLogger().debug("<scheduler> : Nothing to execute :")
            logging.getLogger().debug("<scheduler> : Exit")
            return
        else :
            # execute all commands on host :
            total = len(tasks)
            logging.getLogger().info("<scheduler> : Total tasks to execute: %s" % str(total))

            success = self.start_all_tasks_on_host(tasks)

            if not success :
                return False
            
    def start_all_tasks_on_host(self, tasks):
        """
        Listing of all the commands to execute, including the delays 
        before and between the executions.

        @param tasks: list of ids (coh) command_on_host.id
        @type tasks: list

        @return: bool
        
        """
        logging.getLogger().info("<scheduler> : All tasks will be executed at %s seconds" % str(self.FIRST_DELAY))

        sleep(self.FIRST_DELAY)

        for id in tasks :

            try :
                self.proxy.msc.start_command_on_host(id)

            except Exception, err :

                logging.getLogger().error("<scheduler> : Error while executing 'msc.start_command_on_host'")
                logging.getLogger().error("<scheduler> : %s" % err)                        
                return False

            logging.getLogger().info("<scheduler> : Task id (coH): %s executed on host(uuid=%s)" % (str(id), self.uuid))
            sleep(self.BETWEEN_TASKS_DELAY)

        return True

