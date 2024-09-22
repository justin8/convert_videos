import subprocess


def check_hardware_acceleration_support():
    support = {"intel_quicksync": False, "nvidia_nvenc": False}

    lsmod_output = subprocess.run(["lsmod"], capture_output=True, text=True)

    if "i915" in lsmod_output.stdout:
        support["intel_quicksync"] = True
    if "nvidia" in lsmod_output.stdout:
        support["nvidia_nvenc"] = True

    return support
