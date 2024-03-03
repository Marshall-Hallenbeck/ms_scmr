from impacket.dcerpc.v5 import transport, scmr
import argparse

parser = argparse.ArgumentParser(description="Create Windows service")
parser.add_argument("--host", type=str, help="Target host IP address")
parser.add_argument("--username", type=str, help="Username")
parser.add_argument("--password", type=str, help="Password")
parser.add_argument("--domain", type=str, help="Domain")
parser.add_argument("--lm_hash", type=str, default="", help="LM hash")
parser.add_argument("--nt_hash", type=str, default="", help="NT hash")
parser.add_argument("--aes_key", type=str, default="", help="AES key")
parser.add_argument("--service_name", type=str, default="MyService", help="Service name")
parser.add_argument("--display_name", type=str, default="My Service", help="Service display name")
parser.add_argument("--description", type=str, default="This is my service", help="Service description")
parser.add_argument("--binary_path", type=str, default="C:\\Windows\\System32\\cmd.exe", help="Binary path")

args = parser.parse_args()

host = args.host
username = args.username
password = args.password
domain = args.domain
lm_hash = args.lm_hash
nt_hash = args.nt_hash
aes_key = args.aes_key
service_name = args.service_name
service_display_name = args.display_name
service_description = args.description
binary_path = args.binary_path

string_binding = f"ncacn_np:{host}[\\pipe\\svcctl]"
rpc_transport = transport.DCERPCTransportFactory(string_binding)
rpc_transport.set_dport("445")

rpc_transport.set_credentials(
    username,
    password,
    domain,
    lm_hash,
    nt_hash,
    aes_key,
)

ms_scmr = rpc_transport.get_dce_rpc()
ms_scmr.connect()
smb_conn = rpc_transport.get_smb_connection()
ms_scmr.bind(scmr.MSRPC_UUID_SCMR)
open_mgr_resp = scmr.hROpenSCManagerW(ms_scmr)
sc_handle = open_mgr_resp['lpScHandle']

create_service_resp = scmr.hRCreateServiceW(
    ms_scmr,
    sc_handle,
    service_name,
    service_display_name,
    lpBinaryPathName=binary_path,
    dwStartType=scmr.SERVICE_DEMAND_START,
)
service_handle = create_service_resp['lpServiceHandle']

description = scmr.SERVICE_DESCRIPTIONW()
description['lpDescription'] = scmr.checkNullString("Service Description")

pointer = scmr.LPSERVICE_DESCRIPTIONW()
pointer['Data'] = description

union_instance = scmr.SC_RPC_CONFIG_INFOW_UNION()
union_instance['tag'] = 1
union_instance['psd'] = pointer

config_info = scmr.SC_RPC_CONFIG_INFOW()
config_info['dwInfoLevel'] = 1
config_info['Union'] = union_instance

change_service_config = scmr.RChangeServiceConfig2W()
change_service_config['hService'] = service_handle
change_service_config['Info'] = config_info
ms_scmr.request(change_service_config)

scmr.hRDeleteService(ms_scmr, service_handle)
scmr.hRCloseServiceHandle(ms_scmr, service_handle)