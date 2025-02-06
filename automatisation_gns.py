# -*- coding: utf-8 -*-
"""automatisation_gns.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1pAcB4yAjf9f9aQyevm6XWvSgI7phzTR4
"""

# -*- coding: utf-8 -*-

import os
import json
from datetime import datetime

# Dictionnaire des fichiers existants à remplacer
existing_files = {
    "R11": "/home/cytech/GNS3/projects/projetV1/project-files/dynamips/60fabd85-12e6-49c3-9f68-d061de5e3a17/configs/i3_startup-config.cfg",
    "R12": "/home/cytech/GNS3/projects/projetV1/project-files/dynamips/b6791346-fa11-453e-8ec8-dd09cc7214f6/configs/i2_startup-config.cfg",
    "R13": "/home/cytech/GNS3/projects/projetV1/project-files/dynamips/0bff2c07-79d9-4313-8188-a396ba8a62fc/configs/i1_startup-config.cfg",
    "R14": "/home/cytech/GNS3/projects/projetV1/project-files/dynamips/00a8eafc-0899-4047-8503-af2599244f4b/configs/i15_startup-config.cfg",
    "R15": "/home/cytech/GNS3/projects/projetV1/project-files/dynamips/c03efee3-e4e9-419c-b090-c5c4a457f9c6/configs/i6_startup-config.cfg",
    "R16": "/home/cytech/GNS3/projects/projetV1/project-files/dynamips/f75c6c19-6ccd-45ab-b1e0-c9598317625e/configs/i5_startup-config.cfg",
    "R17": "/home/cytech/GNS3/projects/projetV1/project-files/dynamips/83f99861-8637-4af7-bec9-625e4fbfab0b/configs/i4_startup-config.cfg",
    "R21": "/home/cytech/GNS3/projects/projetV1/project-files/dynamips/335fd4d8-0172-43d1-a6c0-ed65bf167c87/configs/i7_startup-config.cfg",
    "R22": "/home/cytech/GNS3/projects/projetV1/project-files/dynamips/1c6f0bcc-06ab-4816-8331-6a929a1b2b92/configs/i12_startup-config.cfg",
    "R23": "/home/cytech/GNS3/projects/projetV1/project-files/dynamips/c76fc161-1702-4a59-abfd-5f15f8310bfd/configs/i9_startup-config.cfg",
    "R24": "/home/cytech/GNS3/projects/projetV1/project-files/dynamips/09efb542-94fe-41a8-8e44-28be342ef9ba/configs/i8_startup-config.cfg",
    "R25": "/home/cytech/GNS3/projects/projetV1/project-files/dynamips/3eb24aa3-52ac-4b0d-953e-3ab603d5e048/configs/i10_startup-config.cfg",
    "R26": "/home/cytech/GNS3/projects/projetV1/project-files/dynamips/d925147d-732f-4d3b-965e-6f756e89de5a/configs/i11_startup-config.cfg",
    "R27": "/home/cytech/GNS3/projects/projetV1/project-files/dynamips/d99d4e53-9e5f-45e5-9578-f0129e6894db/configs/i13_startup-config.cfg",
}

def generate_router_config(router, as_data, network_data, is_ebgp):
    config = []
    config.append("!\n!\n!\n!")
    config.append("!")
    config.append("version 15.2")
    config.append("service timestamps debug datetime msec")
    config.append("service timestamps log datetime msec")
    config.append("!")
    config.append(f"hostname {router['hostname']}")
    config.append("!")
    config.append("boot-start-marker")
    config.append("boot-end-marker")
    config.append("!")
    config.append("no aaa new-model")
    config.append("no ip icmp rate-limit unreachable")
    config.append("ip cef")
    config.append("!")
    config.append("ipv6 unicast-routing")
    config.append("ipv6 cef")
    config.append("!")
    config.append("interface Loopback1")
    config.append(" no ip address")
    config.append(f" ipv6 address {as_data['prefix_loopback_ip']}::{router['hostname'][-2:]}/128")
    config.append(" ipv6 enable")
    if as_data["protocol"] == "OSPF":
        config.append(f" ipv6 ospf {as_data['ospf_process_id']} area {router['area']}")
    config.append("!")

    # Identifier les interfaces eBGP
    ebgp_interfaces = []
    for neighbor in as_data["bgp"].get("ebgp_neighbors", []):
        if neighbor["connected_router"] == router["hostname"]:
            ebgp_interfaces.append(neighbor["gigabitEthernet"])
            config.append(f" neighbor {neighbor['to_router_ip']} remote-as {neighbor['to_as']}")
            # Pour une session eBGP, utiliser Loopback1 en source et autoriser le multihop
            if as_data["bgp"]["local_as"] != neighbor["to_as"]:
                config.append(f" neighbor {neighbor['to_router_ip']} update-source Loopback1")
                config.append(f" neighbor {neighbor['to_router_ip']} ebgp-multihop 2")

    for interface in router["interfaces"]:
        int_name = f"GigabitEthernet{interface['gigabitEthernet']}/0"
        gig = interface['gigabitEthernet']

        # Déterminer si l'interface est eBGP
        is_ebgp_interface = gig in ebgp_interfaces
        if "ipv6" in interface:
            interface_ip = f"2025:100:1:37::{router['hostname'][-2:]}/64"
        else:
        # Choisir le préfixe approprié
            if is_ebgp_interface:
                # Trouver l'AS voisin et extraire le préfixe
                to_as = None
                for neighbor in as_data["bgp"]["ebgp_neighbors"]:
                    if neighbor["connected_router"] == router['hostname'] and neighbor["gigabitEthernet"] == gig:
                        to_as = neighbor["to_as"]
                        break
                # Trouver les données de l'AS voisin
                neighbor_as = next((a for a in network_data["AS"] if a["id"] == to_as), None)
                if neighbor_as:
                    prefix_ip = "2025:100:1:37::"


            else:
                prefix_ip = as_data["prefix_interface_ip"]

                interface_ip = f"{as_data['prefix_interface_ip']}{gig}::{router['hostname'][-2:]}/64"


        config.append(f"interface {int_name}")
        config.append(" no ip address")
        config.append(" negotiation auto")
        config.append(f" ipv6 address {interface_ip}")
        config.append(" ipv6 enable")
        config.append(" no shutdown")

        rip_process_name = f"RIP_{as_data['id']}"

        if as_data["protocol"] == "OSPF" and interface.get("connected_to"):
                config.append(f" ipv6 ospf {as_data['ospf_process_id']} area {router['area']}")

        elif as_data["protocol"] == "RIP" and interface.get("connected_to"):
            config.append(f" ipv6 rip {rip_process_name} enable")
        config.append("!")

    config.append("!")

     # Configuration BGP de base
    config.append(f"router bgp {as_data['bgp']['local_as']}")
    config.append(f" bgp router-id {router['id']}")
    config.append(" bgp log-neighbor-changes")
    config.append(" no bgp default ipv4-unicast")

    # Ajouter les voisins eBGP
    for neighbor in as_data["bgp"].get("ebgp_neighbors", []):
        if neighbor["connected_router"] == router["hostname"]:
            config.append(f" neighbor {neighbor['to_router_ip']} remote-as {neighbor['to_as']}")
            config.append(f" neighbor {neighbor['to_router_ip']} activate")

    # Ajouter les voisins iBGP (même pour les routeurs eBGP)
    for peer in as_data["bgp"]["ibgp"][0]["peers"]:
        if peer != router["hostname"]:
            peer_loopback = f"{as_data['prefix_loopback_ip']}::{peer[-2:]}"
            config.append(f" neighbor {peer_loopback} remote-as {as_data['bgp']['local_as']}")
            config.append(f" neighbor {peer_loopback} update-source Loopback1")

    config.append(" !")
    config.append(" address-family ipv4")
    config.append(" exit-address-family")
    config.append(" !")
    config.append(" address-family ipv6")
    config.append("  redistribute connected")
    if as_data["protocol"] == "RIP":
        config.append("  redistribute rip RIP_AS" + as_data["id"])
    elif as_data["protocol"] == "OSPF":
        config.append("  redistribute ospf " + as_data["ospf_process_id"])

    for interface in router["interfaces"]:
        if interface.get("connected_to"):
            gig = interface["gigabitEthernet"]
            network_prefix = f"{as_data['prefix_interface_ip']}{gig}::/64"
            config.append(f"  network {network_prefix}")
    for neighbor in as_data["bgp"].get("ebgp_neighbors", []):
        if neighbor["connected_router"] == router['hostname']:
            config.append(f"  neighbor {neighbor['to_router_ip']} activate")
    for peer in as_data["bgp"]["ibgp"][0]["peers"]:
        if peer != router['hostname']:
            peer_loopback = f"{as_data['prefix_loopback_ip']}::{peer[-2:]}"
            config.append(f"  neighbor {peer_loopback} activate")
    config.append(" exit-address-family")
    config.append("!")

    if as_data["protocol"] == "RIP":
        config.append(f"ipv6 router rip {rip_process_name}")
        config.append(" redistribute connected")
    elif as_data["protocol"] == "OSPF":
        config.append(f"ipv6 router ospf {as_data['ospf_process_id']}")
        config.append(f" router-id {router['id']}")

    config.append("!")
    config.append("end")

    return "\n".join(config)

def generate_all_router(network_data, output_directory):
    for as_data in network_data["AS"]:
        local_ebgp_routers = [n["connected_router"] for n in as_data["bgp"].get("ebgp_neighbors", [])]
        for router in as_data["routers"]:
            is_ebgp = router["hostname"] in local_ebgp_routers
            config = generate_router_config(router, as_data, network_data, is_ebgp)
            file_path = os.path.join(output_directory, f"i{router['hostname'].lstrip('R')}_startup-config.cfg")
            with open(file_path, "w") as file:
                file.write(config)


def replace_existing_files(network_data):
    for as_data in network_data["AS"]:
        for router in as_data["routers"]:
            router_name = router["hostname"]

            if router_name in existing_files:
                config = generate_router_config(router, as_data, network_data, is_ebgp=False)
                file_path = existing_files[router_name]

                with open(file_path, "w") as file:
                    file.write(config)
                print(f"✅ Fichier remplacé : {file_path}")

def start_generation():
    with open("Intent.json", "r") as file:
        network_data = json.load(file)

    output_directory = "router_configs"
    os.makedirs(output_directory, exist_ok=True)
    generate_all_router(network_data, output_directory)
    print(f"Configurations générées dans le dossier '{output_directory}'")

    replace_existing_files(network_data)
    print("✅ Toutes les configurations ciblées ont été mises à jour.")

start_generation()

# -*- coding: utf-8 -*-

import os
import json
from datetime import datetime

def generate_router_config(router, as_data, network_data, is_ebgp):
    config = []
    config.append("!\n!\n!\n!")
    config.append("!")
    config.append("version 15.2")
    config.append("service timestamps debug datetime msec")
    config.append("service timestamps log datetime msec")
    config.append("!")
    config.append(f"hostname {router['hostname']}")
    config.append("!")
    config.append("boot-start-marker")
    config.append("boot-end-marker")
    config.append("!")
    config.append("no aaa new-model")
    config.append("no ip icmp rate-limit unreachable")
    config.append("ip cef")
    config.append("!")
    config.append("ipv6 unicast-routing")
    config.append("ipv6 cef")
    config.append("!")
    config.append("interface Loopback1")
    config.append(" no ip address")
    config.append(f" ipv6 address {as_data['prefix_loopback_ip']}::{router['hostname'][-2:]}/128")
    config.append(" ipv6 enable")
    if as_data["protocol"] == "OSPF":
        config.append(f" ipv6 ospf {as_data['ospf_process_id']} area {router['area']}")
    config.append("!")

    # Identifier les interfaces eBGP
    ebgp_interfaces = []
    for neighbor in as_data["bgp"].get("ebgp_neighbors", []):
        if neighbor["connected_router"] == router["hostname"]:
            ebgp_interfaces.append(neighbor["gigabitEthernet"])
            config.append(f" neighbor {neighbor['to_router_ip']} remote-as {neighbor['to_as']}")
            # Pour une session eBGP, utiliser Loopback1 en source et autoriser le multihop
            if as_data["bgp"]["local_as"] != neighbor["to_as"]:
                config.append(f" neighbor {neighbor['to_router_ip']} update-source Loopback1")
                config.append(f" neighbor {neighbor['to_router_ip']} ebgp-multihop 2")

    for interface in router["interfaces"]:
        int_name = f"GigabitEthernet{interface['gigabitEthernet']}/0"
        gig = interface['gigabitEthernet']

        # Déterminer si l'interface est eBGP
        is_ebgp_interface = gig in ebgp_interfaces
        if "ipv6" in interface:
            interface_ip = f"2025:100:1:37::{router['hostname'][-2:]}/64"
        else:
        # Choisir le préfixe approprié
            if is_ebgp_interface:
                # Trouver l'AS voisin et extraire le préfixe
                to_as = None
                for neighbor in as_data["bgp"]["ebgp_neighbors"]:
                    if neighbor["connected_router"] == router['hostname'] and neighbor["gigabitEthernet"] == gig:
                        to_as = neighbor["to_as"]
                        break
                # Trouver les données de l'AS voisin
                neighbor_as = next((a for a in network_data["AS"] if a["id"] == to_as), None)
                if neighbor_as:
                    prefix_ip = "2025:100:1:37::"


            else:
                prefix_ip = as_data["prefix_interface_ip"]

                interface_ip = f"{as_data['prefix_interface_ip']}{gig}::{router['hostname'][-2:]}/64"


        config.append(f"interface {int_name}")
        config.append(" no ip address")
        config.append(" negotiation auto")
        config.append(f" ipv6 address {interface_ip}")
        config.append(" ipv6 enable")
        config.append(" no shutdown")

        rip_process_name = f"RIP_{as_data['id']}"

        if as_data["protocol"] == "OSPF" and interface.get("connected_to"):
                config.append(f" ipv6 ospf {as_data['ospf_process_id']} area {router['area']}")

        elif as_data["protocol"] == "RIP" and interface.get("connected_to"):
            config.append(f" ipv6 rip {rip_process_name} enable")
        config.append("!")

    config.append("!")

     # Configuration BGP de base
    config.append(f"router bgp {as_data['bgp']['local_as']}")
    config.append(f" bgp router-id {router['id']}")
    config.append(" bgp log-neighbor-changes")
    config.append(" no bgp default ipv4-unicast")

    # Ajouter les voisins eBGP
    for neighbor in as_data["bgp"].get("ebgp_neighbors", []):
        if neighbor["connected_router"] == router["hostname"]:
            config.append(f" neighbor {neighbor['to_router_ip']} remote-as {neighbor['to_as']}")
            config.append(f" neighbor {neighbor['to_router_ip']} activate")

    # Ajouter les voisins iBGP (même pour les routeurs eBGP)
    for peer in as_data["bgp"]["ibgp"][0]["peers"]:
        if peer != router["hostname"]:
            peer_loopback = f"{as_data['prefix_loopback_ip']}::{peer[-2:]}"
            config.append(f" neighbor {peer_loopback} remote-as {as_data['bgp']['local_as']}")
            config.append(f" neighbor {peer_loopback} update-source Loopback1")

    config.append(" !")
    config.append(" address-family ipv4")
    config.append(" exit-address-family")
    config.append(" !")
    config.append(" address-family ipv6")
    config.append("  redistribute connected")
    if as_data["protocol"] == "RIP":
        config.append("  redistribute rip RIP_AS" + as_data["id"])
    elif as_data["protocol"] == "OSPF":
        config.append("  redistribute ospf " + as_data["ospf_process_id"])

    for interface in router["interfaces"]:
        if interface.get("connected_to"):
            gig = interface["gigabitEthernet"]
            network_prefix = f"{as_data['prefix_interface_ip']}{gig}::/64"
            config.append(f"  network {network_prefix}")
    for neighbor in as_data["bgp"].get("ebgp_neighbors", []):
        if neighbor["connected_router"] == router['hostname']:
            config.append(f"  neighbor {neighbor['to_router_ip']} activate")
    for peer in as_data["bgp"]["ibgp"][0]["peers"]:
        if peer != router['hostname']:
            peer_loopback = f"{as_data['prefix_loopback_ip']}::{peer[-2:]}"
            config.append(f"  neighbor {peer_loopback} activate")
    config.append(" exit-address-family")
    config.append("!")

    if as_data["protocol"] == "RIP":
        config.append(f"ipv6 router rip {rip_process_name}")
        config.append(" redistribute connected")
    elif as_data["protocol"] == "OSPF":
        config.append(f"ipv6 router ospf {as_data['ospf_process_id']}")
        config.append(f" router-id {router['id']}")

    config.append("!")
    config.append("end")

    return "\n".join(config)

def generate_all_router(network_data, output_directory):
    for as_data in network_data["AS"]:
        local_ebgp_routers = [n["connected_router"] for n in as_data["bgp"].get("ebgp_neighbors", [])]
        for router in as_data["routers"]:
            is_ebgp = router["hostname"] in local_ebgp_routers
            config = generate_router_config(router, as_data, network_data, is_ebgp)
            file_path = os.path.join(output_directory, f"i{router['hostname'].lstrip('R')}_startup-config.cfg")
            with open(file_path, "w") as file:
                file.write(config)

def start_generation():
    with open("Intent.json", "r") as file:
        network_data = json.load(file)
    output_directory = "router_configs"
    os.makedirs(output_directory, exist_ok=True)
    generate_all_router(network_data, output_directory)
    print(f"Configurations générées dans le dossier '{output_directory}'")

start_generation()

