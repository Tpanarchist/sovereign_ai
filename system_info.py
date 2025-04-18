import platform
import socket
import os
import psutil
import datetime
import json

def get_system_info():
    """Collect comprehensive system information"""
    
    # Basic system info
    system_info = {
        "system": platform.system(),
        "node": platform.node(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "architecture": platform.architecture(),
        "python_version": platform.python_version(),
        "hostname": socket.gethostname(),
        "ip_address": socket.gethostbyname(socket.gethostname())
    }
    
    # CPU information
    cpu_info = {
        "physical_cores": psutil.cpu_count(logical=False),
        "total_cores": psutil.cpu_count(logical=True),
        "cpu_freq_max": psutil.cpu_freq().max if hasattr(psutil.cpu_freq(), 'max') else None,
        "cpu_freq_current": psutil.cpu_freq().current if hasattr(psutil.cpu_freq(), 'current') else None,
        "cpu_percent": psutil.cpu_percent(interval=1)
    }
    
    # Memory information
    memory = psutil.virtual_memory()
    memory_info = {
        "total": memory.total,
        "available": memory.available,
        "used": memory.used,
        "percent": memory.percent
    }
    
    # Disk information
    disk_info = {}
    for partition in psutil.disk_partitions():
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
            disk_info[partition.device] = {
                "mountpoint": partition.mountpoint,
                "fstype": partition.fstype,
                "total_size": partition_usage.total,
                "used": partition_usage.used,
                "free": partition_usage.free,
                "percent": partition_usage.percent
            }
        except PermissionError:
            # Some disk partitions may not be accessible
            continue
            
    # Network information
    network_info = {}
    for interface_name, interface_addresses in psutil.net_if_addrs().items():
        addresses = []
        for address in interface_addresses:
            addresses.append({
                "family": str(address.family),
                "address": address.address,
                "netmask": address.netmask,
                "broadcast": address.broadcast
            })
        network_info[interface_name] = addresses
    
    # Process information (top 5 by memory usage)
    process_info = []
    for proc in sorted(psutil.process_iter(['pid', 'name', 'username', 'memory_percent']), 
                      key=lambda x: x.info['memory_percent'] or 0, 
                      reverse=True)[:5]:
        try:
            process_info.append({
                "pid": proc.info['pid'],
                "name": proc.info['name'],
                "username": proc.info['username'],
                "memory_percent": proc.info['memory_percent']
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    # Current time
    current_time = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "timezone": datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo.tzname(None)
    }
    
    # Combine all information
    complete_info = {
        "system_info": system_info,
        "cpu_info": cpu_info,
        "memory_info": memory_info,
        "disk_info": disk_info,
        "network_info": network_info,
        "top_processes": process_info,
        "current_time": current_time
    }
    
    return complete_info

# Output formatted JSON
if __name__ == "__main__":
    system_data = get_system_info()
    print(json.dumps(system_data, indent=4))