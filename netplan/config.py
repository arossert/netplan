# Copyright (c) 2018  StorPool.
# All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Convenience classes for the fully-parsed netplan configuration.
"""

from . import interface as npiface


class NetPlan(object):
    """
    A full netplan configuration; the "data" member is a dictionary of
    interface names to netplan.interface.* classes.
    """
    VERSION = '0.2.1.dev1'

    def __init__(self, data):
        self.data = data

    def __str__(self):
        """
        Provide a human-readable list of the interfaces grouped by section.
        """
        # Group the interfaces by section
        by_section = {}
        for iface, cfg in self.data.items():
            if cfg.section not in by_section:
                by_section[cfg.section] = []
            by_section[cfg.section].append(iface)

        # Sort the interface names within each section
        collected = [
            '{sect}: {ifaces}'.format(
                sect=section,
                ifaces=', '.join(sorted(data)))
            for (section, data) in by_section.items()
        ]

        # Return a list sorted by section name
        return '; '.join(sorted(collected))

    def __repr__(self):
        """
        Provide a Python-style representation.
        """
        return 'NetPlan({d})'.format(d=repr(self.data))

    def get_all_interfaces(self, ifaces):
        """
        Get the configuration of the interfaces with the specified names and
        all their parents recursively.
        """
        cur = set()
        new = set(ifaces)
        while new:
            cur = cur.union(new)
            newnew = set()
            for iface in new:
                newnew = newnew.union(
                    set(self.data[iface].get_parent_names()) - cur)
            new = newnew
        return NetPlan({iface: self.data[iface] for iface in cur})

    def get_physical_interfaces(self, ifaces):
        """
        Similar to get_all_interfaces(), but only return physical interfaces.
        For instance, for a VLAN interface over a bridge over two VLANs
        over Ethernet interfaces this function would only return
        the definitions for the Ethernet interfaces.  For an Ethernet or
        wireless interface this function would return its own configuration.
        """
        related = self.get_all_interfaces(ifaces)
        phys = [d for d in related.data.values()
                if isinstance(d, npiface.PhysicalInterface)]
        return NetPlan({d.name: d for d in phys})
