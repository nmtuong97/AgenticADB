import subprocess
from typing import Optional, Tuple

from agentic_adb.exceptions import DeviceNotFoundError


def _get_android_devices() -> list[str]:
    """Lấy danh sách các Android device ID từ `adb devices`."""
    try:
        result = subprocess.run(
            ["adb", "devices"], capture_output=True, text=True, check=True
        )
        lines = result.stdout.strip().split("\n")[1:]  # Bỏ qua dòng header
        devices = []
        for line in lines:
            if line.strip():
                parts = line.split()
                # Chấp nhận 'device' và có thể 'emulator' (đôi khi offline cũng bỏ qua, ở đây chỉ lấy 'device')
                if len(parts) >= 2 and parts[1] == "device":
                    devices.append(parts[0])
        return devices
    except (subprocess.SubprocessError, FileNotFoundError):
        return []


def _get_ios_devices() -> list[str]:
    """Lấy danh sách các iOS device ID từ `idb list-targets`."""
    try:
        result = subprocess.run(
            ["idb", "list-targets"], capture_output=True, text=True, check=True
        )
        lines = result.stdout.strip().split("\n")
        devices = []
        for line in lines:
            if line.strip():
                # Format idb thường là: iPhone 14 Pro | 1111-2222 | Booted | simulator | iOS 16.4
                # Ta lấy phần tử có format của UUID/UDID (phần tử thứ 2 nếu split by '|')
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 2:
                    devices.append(parts[1])
        return devices
    except (subprocess.SubprocessError, FileNotFoundError):
        return []


def get_connected_devices() -> Tuple[list[str], list[str]]:
    """Trả về tuple chứa (android_devices, ios_devices)."""
    return _get_android_devices(), _get_ios_devices()


def resolve_device(device_id: Optional[str] = None, os_override: Optional[str] = None) -> Tuple[Optional[str], str]:
    """
    Xác định thiết bị và OS tương ứng.

    Args:
        device_id: ID thiết bị do người dùng cung cấp (nếu có).
        os_override: Bỏ qua auto-detect và sử dụng hệ điều hành này.

    Returns:
        Tuple (device_id, os_type) nơi os_type là "android" hoặc "ios".

    Raises:
        DeviceNotFoundError: Khi không tìm thấy hoặc có sự không rõ ràng (nhiều hơn 1 thiết bị mà không chỉ định).
    """
    android_devices, ios_devices = get_connected_devices()

    if device_id:
        if os_override:
            return device_id, os_override

        # Tìm trong danh sách
        if device_id in android_devices:
            return device_id, "android"
        if device_id in ios_devices:
            return device_id, "ios"

        # Nếu không tìm thấy trong danh sách đang connect, ta vẫn phải đưa ra 1 lựa chọn hoặc báo lỗi
        # Nhưng idb / adb có thể kết nối mà lệnh trên chưa update kịp, hoặc mock có vấn đề.
        # Ở đây ta yêu cầu strict routing, nhưng nếu ko có auto detect được thì dùng os_override,
        # nếu ko có override luôn, ta ném ngoại lệ vì không biết route vào client nào.
        raise DeviceNotFoundError(f"Device '{device_id}' not found in connected Android or iOS devices. Please specify --os.")

    else:
        # Không cung cấp device_id
        total_devices = len(android_devices) + len(ios_devices)
        if total_devices == 0:
            raise DeviceNotFoundError("No devices connected. Please connect a device or specify --device and --os.")

        if total_devices == 1:
            if android_devices:
                return android_devices[0], "android"
            else:
                return ios_devices[0], "ios"

        # Lớn hơn 1 thiết bị
        if os_override:
            # Nếu truyền --os nhưng không truyền --device, và trong OS đó chỉ có 1 thiết bị thì lấy nó
            if os_override == "android" and len(android_devices) == 1:
                return android_devices[0], "android"
            elif os_override == "ios" and len(ios_devices) == 1:
                return ios_devices[0], "ios"

        raise DeviceNotFoundError("Multiple devices connected. Please specify exactly which device to use with --device <id>.")
