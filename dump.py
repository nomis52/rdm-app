#!/usr/bin/python
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Library General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# ola_rdm_get.py
# Copyright (C) 2010 Simon Newton

'''Get a PID from a UID.'''

__author__ = 'nomis52@gmail.com (Simon Newton)'

import getopt
import os.path
import sys
import textwrap
import pprint
from ola import PidStore



VALIDATOR_TO_VALUE = {
    PidStore.RootDeviceValidator: 0,
    PidStore.SubDeviceValidator: 1,
    PidStore.NonBroadcastSubDeviceValiator: 2,
    PidStore.SpecificSubDeviceValidator: 3
}

TYPE_TO_STRING = {
  PidStore.Bool: 'bool',
  PidStore.UInt8: 'uint8',
  PidStore.UInt16: 'uint16',
  PidStore.UInt32: 'uint32',
  PidStore.String: 'string',
}

def BuildMessage(request):
  output = {
    'is_repeated': False,
    'items': [],
  }
  if isinstance(request, PidStore.RepeatedGroup):
    output['is_repeated'] = True
    if request.max:
      output['max_repeats'] = request.max

  for item in request:
    type = None

    data = {
        'name': item.name,
        'type': TYPE_TO_STRING[item.__class__],
    }
    if item.size and item.size != 1:
      data['size'] = item.size
    output['items'].append(data)
  return output


def BuildPid(pid):
  pid_dict = {
    'name': pid.name,
    'value': pid.value,
  }

  if pid._get_validators:
    pid_dict['get_sub_device_range'] = VALIDATOR_TO_VALUE[pid._get_validators[0]]
  if pid._set_validators:
    pid_dict['set_sub_device_range'] = VALIDATOR_TO_VALUE[pid._set_validators[0]]

  if pid._get_request is not None:
    output = BuildMessage(pid._get_request)
    pid_dict['get_request'] = output

  if pid._get_response is not None:
    output = BuildMessage(pid._get_response)
    pid_dict['get_response'] = output

  if pid._set_request is not None:
    output = BuildMessage(pid._set_request)
    pid_dict['set_request'] = output

  if pid._set_response is not None:
    output = BuildMessage(pid._set_response)
    pid_dict['set_response'] = output
  return pid_dict


def main():

  pid_store = PidStore.GetStore()

  pids = []
  manufacturers = []

  for pid in pid_store.Pids():
    pid_dict = BuildPid(pid)
    pids.append(pid_dict)

  for id, name in pid_store._manufacturer_id_to_name.iteritems():
    manufacturer = {
      'id': id,
      'name': name,
      'pids': []
    }
    for pid in pid_store._manufacturer_pids[id].values():
      pid_dict = BuildPid(pid)
      manufacturer['pids'].append(pid_dict)
    manufacturers.append(manufacturer)

  #pprint.pprint(manufacturers)

  pprint.pprint(pids)

if __name__ == '__main__':
  main()
