import base64
import hmac
import hashlib
import time
import requests
from urllib.parse import quote
import sys
from time import sleep
from azure.iot.hub import IoTHubRegistryManager
from azure.iot.hub.models import Device, Module, Twin, TwinProperties, QuerySpecification, QueryResult, CloudToDeviceMethod

def registry_mgr(hub_own_str):
    ihub_reg_mgr = IoTHubRegistryManager(hub_own_str)
    return ihub_reg_mgr

def get_edge_devices(hub_own_str):
    try:
        reg_mgr = registry_mgr(hub_own_str)
        device_query = QuerySpecification(query="SELECT * FROM devices WHERE capabilities.iotEdge = true")
        device_result = reg_mgr.query_iot_hub(device_query, None, 100)
        device_list = [twin.device_id for twin in device_result.items]
        return device_list

    except Exception as ex:
        print("Unexpected error {0}".format(ex))
        return

def get_edge_modules(hub_own_str):
    try:
        reg_mgr = registry_mgr(hub_own_str)
        device_list = get_edge_devices(hub_own_str)
        # print(device_list)
        # print(f"Device list: {devices}")
        # devices = f"{devices}"
        module_list = []
        substring = "CIS"
        device_len = len(device_list)
        # print(f"Length: {length}")
        for i in range(device_len):
            # print(devices[i])
            device_modules = reg_mgr.get_modules(device_list[i])
            # print(f"Device: \n {devices[i]}\n Modules: \n{device_modules}")
            for module in device_modules:
                if substring in f"{module}":
                    deviceId = module.device_id
                    moduleId = module.module_id
                    print(f"Device:  {deviceId}")
                    print(f"Module:  {moduleId}\n")
                    module_dict = {
                        "deviceId": deviceId,
                        "moduleId": moduleId
                    }
                    module_list.append(module_dict)
        # return (device_list, module_list)
        return (module_list)

    except Exception as ex:
        print("Unexpected error {0}".format(ex))
        return

def get_module_twins(hub_own_str, device, module):
    
    reg_mgr = registry_mgr(hub_own_str)
    module_twin = reg_mgr.get_module_twin(device, module)
    module_twin_data = module_twin.properties.desired
    module_twin_data["id"]=f"{device}-{module}"
    module_twin_data["deviceId"]= device
    module_twin_data["moduleId"]= module

    return module_twin_data

def patch_module_twins(hub_own_str, deviceId, moduleId, twin_update):
    try:
        reg_mgr = registry_mgr(hub_own_str)
        print(f"Twin patch payload: {twin_update}")
        module_twin = reg_mgr.get_module_twin(deviceId, moduleId)
        twin_patch = Twin()
        twin_patch.properties = TwinProperties(desired=twin_update)
        updated_module_twin = reg_mgr.update_module_twin(
            deviceId, moduleId, twin_patch, module_twin.etag
        )
        return True
    except:
        return False

def restart_module(hub_own_str, deviceId, moduleId):
    reg_mgr = registry_mgr(hub_own_str)
    restart_dict = {
        "schemaVersion": "1.0",
        "id": moduleId
    }
    target_module = "$edgeAgent"
    restart_module_method = CloudToDeviceMethod(method_name='RestartModule', payload=restart_dict)
    reg_mgr.invoke_device_module_method(deviceId, target_module, restart_module_method)
    
    return True