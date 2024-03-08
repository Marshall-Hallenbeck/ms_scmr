from impacket.dcerpc.v5 import scmr

def create_service(dce_rpc, service_name=None, service_display_name=None, binary_path=None):  # noqa: E501
    dce_rpc.bind(scmr.MSRPC_UUID_SCMR)
    open_mgr_resp = scmr.hROpenSCManagerW(dce_rpc)
    open_mgr_handle = open_mgr_resp['lpScHandle']

    create_svc_resp = scmr.hRCreateServiceW(
        dce_rpc,
        open_mgr_handle,
        service_name,
        service_display_name,
        lpBinaryPathName=binary_path,
        dwStartType=scmr.SERVICE_DEMAND_START,
    )
    svc_handle = create_svc_resp['lpServiceHandle']

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
    change_service_config['hService'] = svc_handle
    change_service_config['Info'] = config_info
    dce_rpc.request(change_service_config)
    return svc_handle

def start_service(dce_rpc, service_name):
    dce_rpc.bind(scmr.MSRPC_UUID_SCMR)
    open_mgr_resp = scmr.hROpenSCManagerW(dce_rpc)
    mgr_handle = open_mgr_resp['lpScHandle']
    open_svc_handle = scmr.hROpenServiceW(
        dce_rpc,
        mgr_handle,
        scmr.checkNullString(service_name)
    )
    start_svc_handle = scmr.hRStartServiceW(dce_rpc, open_svc_handle)
    return start_svc_handle

def start_service_whandle(dce_rpc, service_handle):
    start_svc_handle = scmr.hRStartServiceW(dce_rpc, service_handle)
    return start_svc_handle

def delete_service(dce_rpc, service_handle):
    scmr.hRDeleteService(dce_rpc, service_handle)
    scmr.hRCloseServiceHandle(dce_rpc, service_handle)