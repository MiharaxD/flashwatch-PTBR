"""Verify the MSI and extract its payload; never install or launch FlashWatch."""
from __future__ import annotations
import ctypes
import hashlib
import json
from pathlib import Path
import subprocess
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import msilib

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "build/installer"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def native_plan(installer):
    """Costing and launch conditions only: never execute INSTALL actions."""
    api = ctypes.WinDLL("msi")
    api.MsiSetInternalUI.argtypes = [ctypes.c_uint, ctypes.c_void_p]
    api.MsiSetInternalUI(2, None)
    api.MsiOpenPackageExW.argtypes = [ctypes.c_wchar_p, ctypes.c_uint, ctypes.POINTER(ctypes.c_uint)]
    api.MsiDoActionW.argtypes = [ctypes.c_uint, ctypes.c_wchar_p]
    api.MsiSetPropertyW.argtypes = [ctypes.c_uint, ctypes.c_wchar_p, ctypes.c_wchar_p]
    api.MsiCloseHandle.argtypes = [ctypes.c_uint]
    handle = ctypes.c_uint()
    results = {"OpenPackage": api.MsiOpenPackageExW(str(installer), 1, ctypes.byref(handle))}
    if results["OpenPackage"] == 0:
        try:
            api.MsiSetPropertyW(handle.value, "ACTION", "INSTALL")
            api.MsiSetPropertyW(handle.value, "INSTALLDIR", str(WORK / "cost-only"))
            for action in ("CostInitialize", "FileCost", "CostFinalize", "LaunchConditions"):
                results[action] = api.MsiDoActionW(handle.value, action)
        finally:
            api.MsiCloseHandle(handle.value)
    return results


def main():
    manifest = json.loads((WORK / "manifest.json").read_text("utf-8"))
    MSI = Path(manifest["installer"])
    checks = {"installer_hash": digest(MSI) == manifest["sha256"]}
    api = ctypes.WinDLL("msi")
    api.MsiVerifyPackageW.argtypes = [ctypes.c_wchar_p]
    checks["windows_recognizes_msi"] = api.MsiVerifyPackageW(str(MSI)) == 0
    destination = WORK / ("payload-" + manifest["sha256"][:12])
    destination.mkdir(exist_ok=True)
    archive_tool = Path(r"C:\Program Files\7-Zip\7z.exe")
    with (WORK / "archive-check.log").open("w", encoding="utf-8") as log:
        subprocess.run([str(archive_tool), "t", str(MSI)], check=True, stdout=log, stderr=subprocess.STDOUT)
        subprocess.run([str(archive_tool), "x", str(MSI), "-o" + str(destination), "-y"],
                       check=True, stdout=log, stderr=subprocess.STDOUT)
    for item in manifest["files"]:
        checks["payload:" + item["name"]] = digest(destination / item["id"]) == item["sha256"]
    checks["exact_file_inventory"] = {p.name for p in destination.iterdir()} == {f["id"] for f in manifest["files"]}
    checks["latest_application_unchanged"] = digest(destination / "File001") == manifest["application_sha256"]
    checks["no_user_assets_or_capture"] = not any(
        "assets" in f["name"].lower() or "settings.json" in f["name"].lower()
        or "clipboard" in f["name"].lower() or f["name"].lower().endswith((".png", ".log"))
        for f in manifest["files"])
    db = msilib.OpenDatabase(str(MSI), msilib.MSIDBOPEN_READONLY)

    def rows(table, columns):
        query = "SELECT " + ",".join("`" + c + "`" for c in columns) + " FROM `" + table + "`"
        view = db.OpenView(query)
        view.Execute(None)
        result = []
        while (record := view.Fetch()) is not None:
            result.append(tuple(record.GetString(i + 1) for i in range(len(columns))))
        view.Close()
        return result

    props = dict(rows("Property", ["Property", "Value"]))
    checks["per_user_default"] = not props.get("ALLUSERS")
    checks["portuguese"] = props["ProductLanguage"] == "1046"
    summary = db.GetSummaryInformation(0)
    checks["x64_package"] = summary.GetProperty(msilib.PID_TEMPLATE) == b"x64;1046"
    checks["no_elevation_required"] = bool(summary.GetProperty(msilib.PID_WORDCOUNT) & 8)
    checks["no_custom_program_launch"] = rows("CustomAction", ["Action"]) == []
    checks["no_process_auto_close"] = props["MSIRESTARTMANAGERCONTROL"] == "Disable"
    registry = rows("Registry", ["Root", "Key"])
    checks["registry_current_user_only"] = all(root == "1" for root, _ in registry)
    checks["no_autostart_modification"] = all("currentversion\\run" not in key.lower() for _, key in registry)
    removals = rows("RemoveFile", ["FileName", "InstallMode"])
    checks["only_empty_folders_removed"] = all(not name and mode == "2" for name, mode in removals)
    shortcuts = dict((name, target) for name, target in rows("Shortcut", ["Shortcut", "Target"]))
    checks["start_menu_shortcut"] = shortcuts["StartMenu"] == "[INSTALLDIR]FlashWatch-PTBR.exe"
    checks["uninstall_shortcut"] = shortcuts["Uninstall"] == "[SystemFolder]msiexec.exe"
    checks["desktop_shortcut"] = shortcuts["Desktop"] == "[INSTALLDIR]FlashWatch-PTBR.exe"
    icons = dict((name, icon) for name, icon in rows("Shortcut", ["Shortcut", "Icon_"]))
    checks["shortcuts_follow_exe_icon"] = not icons["StartMenu"] and not icons["Desktop"]
    components = dict(rows("Component", ["Component", "Condition"]))
    checks["desktop_is_optional"] = components["DesktopShortcut"] == 'DESKTOP_SHORTCUT="1"'
    directories = dict(rows("Directory", ["Directory", "Directory_Parent"]))
    checks["install_under_localappdata"] = directories["INSTALLDIR"] == "LocalPrograms" and directories["LocalPrograms"] == "LocalAppDataFolder"
    controls = set(rows("Control", ["Dialog_", "Control"]))
    for name, first, default, cancel in rows("Dialog", ["Dialog", "Control_First", "Control_Default", "Control_Cancel"]):
        checks["dialog_controls:" + name] = all(not c or (name, c) in controls for c in (first, default, cancel))
    for table in ("InstallUISequence", "InstallExecuteSequence"):
        actions = dict((a, int(n)) for a, n in rows(table, ["Action", "Sequence"]))
        checks["upgrade_detection_order:" + table] = actions["FindRelatedProducts"] < actions["LaunchConditions"]
    planning = native_plan(MSI)
    (WORK / "native-costing.json").write_text(json.dumps(planning, indent=2), "utf-8")
    checks["native_installation_planning"] = len(planning) == 5 and all(code == 0 for code in planning.values())
    checks["hash_still_stable"] = digest(MSI) == manifest["sha256"]
    report = dict(installer=str(MSI), sha256=manifest["sha256"], bytes=MSI.stat().st_size,
                  application_sha256=manifest["application_sha256"], checks=checks,
                  passed=all(checks.values()), full_installation_tested=False,
                  limitation="No full installation/uninstallation test. Archive extraction and native planning only; no FlashWatch or LoL execution.")
    (WORK / "verification.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), "utf-8")
    print(f"{sum(checks.values())}/{len(checks)} verificações aprovadas")
    for name, ok in checks.items():
        if not ok:
            print("FAIL", name)
    raise SystemExit(not report["passed"])


if __name__ == "__main__":
    main()
