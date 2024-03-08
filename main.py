from impacket.dcerpc.v5 import transport
import argparse
from service_actions import create_service, delete_service, start_service_whandle, start_service
from file_actions import upload_file

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
parser.add_argument("--upload_binary", type=str, help="Path to binary to upload")
parser.add_argument("--upload_location", type=str, help="Path to upload the binary to")

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
upload_binary = args.upload_binary
upload_location = args.upload_location

def create_conn(host, username, password, domain=None, lm_hash=None, nt_hash=None, aes_key=None):
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

    dce_rpc = rpc_transport.get_dce_rpc()
    dce_rpc.connect()
    smb_conn = rpc_transport.get_smb_connection()
    return dce_rpc, smb_conn

dce_rpc, smb_conn = create_conn(host, username, password, domain, lm_hash, nt_hash, aes_key)
if upload_file(smb_conn, upload_binary, upload_location):
    print(f"Check file location: {upload_location}")
service_handle = create_service(dce_rpc, service_name, service_display_name, r"C:\Windows\Temp\test.exe")
start_handle = start_service_whandle(dce_rpc, service_handle)
#print(start_handle)
delete_service(dce_rpc, service_handle)
smb_conn.deleteFile("C$", upload_location)