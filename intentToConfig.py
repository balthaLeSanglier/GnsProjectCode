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
            interface_ip = interface["ipv6"]
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
        
                interface_ip = f"{prefix_ip}{gig}::{router['hostname'][-2:]}/64"
        
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
            config.append(f"  neighbor {neighbor['to_router_ip']} activate")
    
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