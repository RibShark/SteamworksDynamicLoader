# Steamworks Dynamic Loader
Steamworks Dynamic Loader is a C++ code generator written in Python that makes loading the Steamworks API at runtime as simple as calling a single function. Currently works only on Windows but should be easily tweakable to work cross-platform.

## Why?
If the Steamworks API is linked normally into a game's executable through standard dynamic linking, that executable is then tied to Steam; it cannot be run without Steam loaded and logged in.
Instead, we can generate a CPP file (based on the `steam_api.json` API metadata bundled with the Steamworks API) that will instead load the library at runtime and import the functions, allowing runtime checks of whether `steam_api.dll` is available so the code can take an alternate path when running without Steam.

## Usage
````
usage: generate_dynamic_wrapper.py [-h] [api_json] [filename]

positional arguments:
  api_json    The location of the Steamworks api.json file.
  filename    The filename of the CPP/H to output (minus extension).
````

Once generated:
````
#include <steam_api.h>
#include "SteamWrapper.h"

int main() {
    // ...
    if (SteamWrapper::InitWrapper())
    {
        SteamAPI_RestartAppIfNecessary(appid);
        SteamAPI_Init();
        // etc
    }
    else // non-Steam codepath
}
````
