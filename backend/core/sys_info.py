import shutil

def detect_toolchains() -> str:
    """Probes host OS for available native build tools."""
    tools = {
        "g++": shutil.which("g++"),
        "gcc": shutil.which("gcc"),
        "clang++": shutil.which("clang++"),
        "nvcc (CUDA)": shutil.which("nvcc"),
        "emcc (Emscripten)": shutil.which("emcc"),
        "python": shutil.which("python") or shutil.which("python3"),
        "cmake": shutil.which("cmake")
    }
    
    available = [name for name, path in tools.items() if path is not None]
    return ", ".join(available) if available else "Standard Shell Tools Only"
