import json
import argparse

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("api_json", default="sdk/public/steam/steam_api.json", nargs="?")
    ap.add_argument("class_name", default="SteamWrapper", nargs="?")
    args = ap.parse_args()

    with open(args.api_json) as f:
        api = json.load(f)


    methods = []
    for interface in api["interfaces"]:
        for method in interface["methods"]:
            for existing_method in methods:
                if method["methodname_flat"] == existing_method["methodname_flat"]:
                    break
            else:
                method["namespace"] = interface["classname"]
                method["interface"] = True
                method["simplename"] = method["methodname_flat"].removeprefix("SteamAPI_")
                methods.append(method)

    for struct in api["structs"]:
        for method in interface["methods"]:
            for existing_method in methods:
                if method["methodname_flat"] == existing_method["methodname_flat"]:
                    break
            else:
                method["namespace"] = struct["struct"]
                methods.append(method)

    function_pointer_declarations = ''
    function_pointer_assignments = ''
    thunks = ''
    thunk_declarations = ''
    for method in methods:
        function_pointer_declarations += f'\n    static decltype({method['methodname_flat']})* {method['simplename']};'
        function_pointer_assignments += f'\n        {method['simplename']} = reinterpret_cast<decltype({method['methodname_flat']})*>(GetProcAddress(steamApi, "{method['methodname_flat']}"));'
        
        params = ''
        paramnames = ''
        if method["interface"]:
            params += f'{method["namespace"]}* self, '
            paramnames += 'self, '
        for param in method['params']:
            if 'paramtype_flat' in param:
                params += f'{param['paramtype_flat']} {param['paramname']}, '
            else:
                params += f'{param['paramtype']} {param['paramname']}, '
            paramnames += f'{param['paramname']}, '
        params = params.removesuffix(', ')
        paramnames = paramnames.removesuffix(', ')
        
        if 'returntype_flat' in method:
            thunks += f'\n{method['returntype_flat']} S_CALLTYPE {method['methodname_flat']}({params}) {{return {args.class_name}::{method['simplename']}({paramnames}); }}'
        else:
            thunks += f'\n{method['returntype']} S_CALLTYPE {method['methodname_flat']}({params}) {{return {args.class_name}::{method['simplename']}({paramnames}); }}'

    with open(args.class_name + ".cpp", 'w') as cpp:
        cpp.write(f"""#define STEAM_API_NODLL
#include <steam_api_flat.h>

namespace {args.class_name}
{{
    static decltype(SteamInternal_SteamAPI_Init)* Init;
    static decltype(SteamAPI_InitFlat)* InitFlat;
    static decltype(SteamAPI_Shutdown)* Shutdown;
    static decltype(SteamAPI_RestartAppIfNecessary)* RestartAppIfNecessary;
    static decltype(SteamAPI_ReleaseCurrentThreadMemory)* ReleaseCurrentThreadMemory;
    static decltype(SteamAPI_WriteMiniDump)* WriteMiniDump;
    static decltype(SteamAPI_SetMiniDumpComment)* SetMiniDumpComment;
    static decltype(SteamAPI_IsSteamRunning)* IsSteamRunning;
    static decltype(SteamAPI_SetTryCatchCallbacks)* SetTryCatchCallbacks;
    static decltype(SteamAPI_ManualDispatch_Init)* ManualDispatch_Init;
    static decltype(SteamAPI_ManualDispatch_RunFrame)* ManualDispatch_RunFrame;
    static decltype(SteamAPI_ManualDispatch_GetNextCallback)* ManualDispatch_GetNextCallback;
    static decltype(SteamAPI_ManualDispatch_FreeLastCallback)* ManualDispatch_FreeLastCallback;
    static decltype(SteamAPI_ManualDispatch_GetAPICallResult)* ManualDispatch_GetAPICallResult;
#if defined( VERSION_SAFE_STEAM_API_INTERFACES )
    static decltype(SteamAPI_InitSafe)* InitSafe;
#endif
#if defined(USE_BREAKPAD_HANDLER) || defined(STEAM_API_EXPORTS)
    static decltype(SteamAPI_UseBreakpadCrashHandler)* UseBreakpadCrashHandler;
    static decltype(SteamAPI_SetBreakpadAppID)* SetBreakpadAppId;
#endif
{function_pointer_declarations}
    bool InitWrapper()
    {{
        HMODULE steamApi = LoadLibrary("steam_api.dll");
        if (steamApi == nullptr) return false;

        Init = reinterpret_cast<decltype(SteamInternal_SteamAPI_Init)*>(GetProcAddress(steamApi, "SteamInternal_SteamAPI_Init"));
        InitFlat = reinterpret_cast<decltype(SteamAPI_InitFlat)*>(GetProcAddress(steamApi, "SteamAPI_InitFlat"));
        Shutdown = reinterpret_cast<decltype(SteamAPI_Shutdown)*>(GetProcAddress(steamApi, "SteamAPI_Shutdown"));
        RestartAppIfNecessary = reinterpret_cast<decltype(SteamAPI_RestartAppIfNecessary)*>(GetProcAddress(steamApi, "SteamAPI_RestartAppIfNecessary"));
        ReleaseCurrentThreadMemory = reinterpret_cast<decltype(SteamAPI_ReleaseCurrentThreadMemory)*>(GetProcAddress(steamApi, "SteamAPI_ReleaseCurrentThreadMemory"));
        WriteMiniDump = reinterpret_cast<decltype(SteamAPI_WriteMiniDump)*>(GetProcAddress(steamApi, "SteamAPI_WriteMiniDump"));
        SetMiniDumpComment = reinterpret_cast<decltype(SteamAPI_SetMiniDumpComment)*>(GetProcAddress(steamApi, "SteamAPI_SetMiniDumpComment"));
        IsSteamRunning = reinterpret_cast<decltype(SteamAPI_IsSteamRunning)*>(GetProcAddress(steamApi, "SteamAPI_IsSteamRunning"));
        SetTryCatchCallbacks = reinterpret_cast<decltype(SteamAPI_SetTryCatchCallbacks)*>(GetProcAddress(steamApi, "SteamAPI_SetTryCatchCallbacks"));
        ManualDispatch_Init = reinterpret_cast<decltype(SteamAPI_ManualDispatch_Init)*>(GetProcAddress(steamApi, "SteamAPI_ManualDispatch_Init"));
        ManualDispatch_RunFrame = reinterpret_cast<decltype(SteamAPI_ManualDispatch_RunFrame)*>(GetProcAddress(steamApi, "SteamAPI_ManualDispatch_RunFrame"));
        ManualDispatch_GetNextCallback = reinterpret_cast<decltype(SteamAPI_ManualDispatch_GetNextCallback)*>(GetProcAddress(steamApi, "SteamAPI_ManualDispatch_GetNextCallback"));
        ManualDispatch_FreeLastCallback = reinterpret_cast<decltype(SteamAPI_ManualDispatch_FreeLastCallback)*>(GetProcAddress(steamApi, "SteamAPI_ManualDispatch_FreeLastCallback"));
        ManualDispatch_GetAPICallResult = reinterpret_cast<decltype(SteamAPI_ManualDispatch_GetAPICallResult)*>(GetProcAddress(steamApi, "SteamAPI_ManualDispatch_GetAPICallResult"));
#if defined( VERSION_SAFE_STEAM_API_INTERFACES )
        InitSafe = reinterpret_cast<decltype(SteamAPI_InitSafe)*>(GetProcAddress(steamApi, "SteamAPI_InitSafe"));
#endif
#if defined(USE_BREAKPAD_HANDLER) || defined(STEAM_API_EXPORTS)
        UseBreakpadCrashHandler = reinterpret_cast<decltype(SteamAPI_UseBreakpadCrashHandler)*>(GetProcAddress(steamApi, "SteamAPI_UseBreakpadCrashHandler"));
        SetBreakpadAppId = reinterpret_cast<decltype(SteamAPI_SetBreakpadAppID)*>(GetProcAddress(steamApi, "SteamAPI_SetBreakpadAppID"));
#endif
        {function_pointer_assignments}

        return true;
    }}
}};

ESteamAPIInitResult S_CALLTYPE SteamInternal_SteamAPI_Init( const char *pszInternalCheckInterfaceVersions, SteamErrMsg *pOutErrMsg ) {{ return SteamWrapper::Init(pszInternalCheckInterfaceVersions, pOutErrMsg); }}
ESteamAPIInitResult S_CALLTYPE SteamAPI_InitFlat( SteamErrMsg *pOutErrMsg ) {{ return SteamWrapper::InitFlat(pOutErrMsg); }}
void S_CALLTYPE SteamAPI_Shutdown() {{ return SteamWrapper::Shutdown(); }}
bool S_CALLTYPE SteamAPI_RestartAppIfNecessary( uint32 unOwnAppID ) {{ return SteamWrapper::RestartAppIfNecessary(unOwnAppID); }}
void S_CALLTYPE SteamAPI_ReleaseCurrentThreadMemory() {{ return SteamWrapper::ReleaseCurrentThreadMemory(); }}
void S_CALLTYPE SteamAPI_WriteMiniDump( uint32 uStructuredExceptionCode, void* pvExceptionInfo, uint32 uBuildID ) {{ return SteamWrapper::WriteMiniDump(uStructuredExceptionCode, pvExceptionInfo, uBuildID); }}
void S_CALLTYPE SteamAPI_SetMiniDumpComment( const char *pchMsg ) {{ return SteamWrapper::SetMiniDumpComment(pchMsg); }}
bool S_CALLTYPE SteamAPI_IsSteamRunning() {{ return SteamWrapper::IsSteamRunning(); }}
void SteamAPI_SetTryCatchCallbacks( bool bTryCatchCallbacks ) {{ return SteamWrapper::SetTryCatchCallbacks(bTryCatchCallbacks); }}
void S_CALLTYPE SteamAPI_ManualDispatch_Init() {{ return SteamWrapper::ManualDispatch_Init(); }}
void S_CALLTYPE SteamAPI_ManualDispatch_RunFrame( HSteamPipe hSteamPipe ) {{ return SteamWrapper::ManualDispatch_RunFrame(hSteamPipe); }}
bool S_CALLTYPE SteamAPI_ManualDispatch_GetNextCallback( HSteamPipe hSteamPipe, CallbackMsg_t *pCallbackMsg ) {{ return SteamWrapper::ManualDispatch_GetNextCallback(hSteamPipe, pCallbackMsg); }}
void S_CALLTYPE SteamAPI_ManualDispatch_FreeLastCallback( HSteamPipe hSteamPipe ) {{ return SteamWrapper::ManualDispatch_FreeLastCallback(hSteamPipe); }}
bool S_CALLTYPE SteamAPI_ManualDispatch_GetAPICallResult( HSteamPipe hSteamPipe, SteamAPICall_t hSteamAPICall, void *pCallback, int cubCallback, int iCallbackExpected, bool *pbFailed ) {{ return SteamWrapper::ManualDispatch_GetAPICallResult(hSteamPipe, hSteamAPICall, pCallback, cubCallback, iCallbackExpected, pbFailed); }}
#if defined( VERSION_SAFE_STEAM_API_INTERFACES )
bool S_CALLTYPE SteamAPI_InitSafe() {{ return SteamWrapper::InitSafe(); }}
#endif
#if defined(USE_BREAKPAD_HANDLER) || defined(STEAM_API_EXPORTS)
void S_CALLTYPE SteamAPI_UseBreakpadCrashHandler( char const *pchVersion, char const *pchDate, char const *pchTime, bool bFullMemoryDumps, void *pvContext, PFNPreMinidumpCallback m_pfnPreMinidumpCallback ) {{ return SteamWrapper::UseBreakpadCrashHandler(pchVersion, pchDate, pchTime, bFullMemoryDumps, pvContext, m_pfnPreMinidumpCallback); }}
void S_CALLTYPE SteamAPI_SetBreakpadAppID( uint32 unAppID ) {{ return SteamWrapper::SetBreakpadAppID(unAppID); }}
#endif
{thunks}
""")

    with open(args.class_name + ".h", 'w') as h:
        h.write(f"""#pragma once
namespace SteamWrapper
{{
    bool InitWrapper();
}}
""")

if __name__ == '__main__':
    main()
