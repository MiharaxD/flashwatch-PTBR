"""Build a per-user Windows MSI around the verified, unchanged application.

Requires Windows and Python 3.11 (stdlib msilib) on the BUILD machine only.
No application launch, downloaded compiler, or dependency installation.
"""
from __future__ import annotations

import argparse
import ctypes
import gc
import hashlib
import json
from pathlib import Path
import re
import uuid
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning, module=".*")
import msilib
from msilib import schema, sequence

ROOT = Path(__file__).resolve().parent
APP_SHA256 = "2a68302e15d94143d3127e98dad18d8e34916e0364146bbdb7b8079ad1cb7d4a"
UPGRADE_CODE = "{42E9D8B6-729D-4D25-8CD8-47326AD6D016}"
REG_KEY = r"Software\FlashWatchPTBR\Installer"


def guid(name: str) -> str:
    return "{" + str(uuid.uuid5(uuid.UUID(UPGRADE_CODE.strip("{}")), name)).upper() + "}"


def import_codepage(database: Path, folder: Path) -> None:
    """The low-level stdlib MSI wrapper omits MsiDatabaseImportW."""
    native = ctypes.WinDLL("msi")
    native.MsiOpenDatabaseW.argtypes = [ctypes.c_wchar_p, ctypes.c_void_p,
                                       ctypes.POINTER(ctypes.c_uint)]
    native.MsiDatabaseImportW.argtypes = [ctypes.c_uint, ctypes.c_wchar_p, ctypes.c_wchar_p]
    native.MsiDatabaseCommit.argtypes = [ctypes.c_uint]
    native.MsiCloseHandle.argtypes = [ctypes.c_uint]
    handle = ctypes.c_uint()
    result = native.MsiOpenDatabaseW(str(database), 1, ctypes.byref(handle))
    if result:
        raise OSError(result, "MsiOpenDatabaseW")
    try:
        result = native.MsiDatabaseImportW(handle.value, str(folder), "codepage.idt")
        if result:
            raise OSError(result, "MsiDatabaseImportW")
        result = native.MsiDatabaseCommit(handle.value)
        if result:
            raise OSError(result, "MsiDatabaseCommit")
    finally:
        native.MsiCloseHandle(handle.value)


def add_ui(db):
    add = lambda table, rows: msilib.add_data(db, table, rows)
    add("TextStyle", [("Normal", "Segoe UI", 9, 0, 0), ("Title", "Segoe UI", 16, 0, 1)])
    add("CheckBox", [("DESKTOP_SHORTCUT", "1")])

    def dialog(name, first, default, cancel, title="FlashWatch PT-BR", modal=True):
        d = msilib.Dialog(db, name, 50, 50, 380, 290, 3 if modal else 1,
                          title, first, default, cancel)
        d.text("Title", 20, 18, 340, 30, 3, r"{\Title}FlashWatch PT-BR")
        d.line("Line", 20, 248, 340, 1)
        return d

    welcome = dialog("Welcome", "Desktop", "Install", "Cancel")
    welcome.text("Intro", 20, 57, 340, 25, 3, "Instalar a versão com cartões persistentes.")
    welcome.text("Path", 20, 86, 340, 38, 3, "Pasta de instalação:\n[INSTALLDIR]")
    welcome.checkbox("Desktop", 20, 128, 340, 18, 3, "DESKTOP_SHORTCUT",
                     "Criar atalho na área de trabalho", "Install")
    welcome.text("Info", 20, 157, 340, 40, 3,
                 "O menu Iniciar terá um atalho. Não precisa instalar Python.\nO aplicativo não será aberto ao concluir.")
    welcome.text("License", 20, 207, 340, 32, 3,
                 "Distribuído sob licença MIT. A licença integral e os avisos acompanham o programa.")
    welcome.pushbutton("Install", 195, 260, 80, 19, 3, "Instalar", "Cancel").event("EndDialog", "Return")
    welcome.pushbutton("Cancel", 282, 260, 78, 19, 3, "Cancelar", "Desktop").event("EndDialog", "Exit")

    maintenance = dialog("Maintenance", "Repair", "Repair", "Cancel")
    maintenance.text("Text", 20, 80, 340, 70, 3,
                     "O FlashWatch PT-BR já está instalado.\n\nVocê pode reparar os arquivos ou desinstalar. Suas configurações e o cache serão preservados.")
    repair = maintenance.pushbutton("Repair", 100, 260, 80, 19, 3, "Reparar", "Remove")
    repair.event("[REINSTALL]", "ALL", ordering=1)
    repair.event("[REINSTALLMODE]", "vomus", ordering=2)
    repair.event("EndDialog", "Return", ordering=3)
    remove = maintenance.pushbutton("Remove", 187, 260, 86, 19, 3, "Desinstalar", "Cancel")
    remove.event("[REMOVE]", "ALL", ordering=1)
    remove.event("EndDialog", "Return", ordering=2)
    maintenance.pushbutton("Cancel", 282, 260, 78, 19, 3, "Cancelar", "Repair").event("EndDialog", "Exit")

    progress = dialog("ProgressDlg", "Cancel", "Cancel", "Cancel", modal=False)
    progress.text("Text", 20, 75, 340, 30, 3, "Aguarde enquanto os arquivos são processados.")
    action = progress.text("Action", 20, 115, 340, 40, 3, "Preparando...")
    action.mapping("ActionText", "Text")
    bar = progress.control("Progress", "ProgressBar", 20, 170, 340, 14, 1, None, None, None, None)
    bar.mapping("SetProgress", "Progress")
    progress.pushbutton("Cancel", 282, 260, 78, 19, 3, "Cancelar", None).event("EndDialog", "Exit")

    for name, text in (
            ("ExitDialog", "Operação concluída.\n\nSe você instalou o programa, abra FlashWatch PT-BR pelo menu Iniciar."),
            ("FatalError", "Não foi possível concluir. Os arquivos existentes foram preservados quando possível.\n\nFeche o FlashWatch pela bandeja antes de tentar novamente."),
            ("UserExit", "Operação cancelada.")):
        d = dialog(name, "Finish", "Finish", "Finish")
        d.text("Text", 20, 80, 340, 110, 3, text)
        d.pushbutton("Finish", 282, 260, 78, 19, 3, "Fechar", None).event("EndDialog", "Return")

    add("InstallUISequence", [("Welcome", "NOT Installed", 1230),
                              ("Maintenance", 'Installed AND NOT REMOVE', 1231),
                              ("ProgressDlg", None, 1280)])


def build(version: str, output: Path) -> Path:
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("Use uma versão do instalador como 1.0.0")
    major, minor, patch = map(int, version.split("."))
    if major > 255 or minor > 255 or patch > 65535:
        raise ValueError("Versão fora dos limites do Windows Installer")
    executable = ROOT / "dist/cartoes-persistentes/FlashWatch-PTBR.exe"
    if hashlib.sha256(executable.read_bytes()).hexdigest() != APP_SHA256:
        raise ValueError("O executável não corresponde à última build validada")
    output.mkdir(parents=True, exist_ok=True)
    target = output / "FlashWatch-PTBR-Setup.msi"
    product_code = guid("product:" + version)
    db = msilib.init_database(str(target), schema, "FlashWatch PT-BR", product_code,
                             version, "FlashWatch PT-BR")
    work = ROOT / "build/installer"
    work.mkdir(parents=True, exist_ok=True)
    (work / "codepage.idt").write_bytes(b"\r\n\r\n1252\t_ForceCodepage\r\n")
    db.Commit()
    del db
    import_codepage(target, work)
    db = msilib.OpenDatabase(str(target), msilib.MSIDBOPEN_TRANSACT)
    si = db.GetSummaryInformation(20)
    si.SetProperty(msilib.PID_TEMPLATE, "x64;1046")
    si.SetProperty(msilib.PID_CODEPAGE, 1252)
    si.SetProperty(msilib.PID_WORDCOUNT, 10)  # compressed + no elevated privileges
    si.SetProperty(msilib.PID_PAGECOUNT, 400)
    si.SetProperty(msilib.PID_APPNAME, "FlashWatch PT-BR MSI builder")
    si.Persist()
    del si
    view = db.OpenView("UPDATE `Property` SET `Value`='1046' WHERE `Property`='ProductLanguage'")
    view.Execute(None)
    view.Close()
    add = lambda table, rows: msilib.add_data(db, table, rows)
    add("Property", [("UpgradeCode", UPGRADE_CODE), ("DefaultUIFont", "Normal"),
                     ("ARPNOMODIFY", "1"), ("ARPPRODUCTICON", "AppIcon"),
                     ("REBOOT", "ReallySuppress"), ("MSIRESTARTMANAGERCONTROL", "Disable"),
                     ("SecureCustomProperties", "OLDPRODUCTS;NEWERPRODUCTS;DESKTOP_SHORTCUT"),
                     ("ARPHELPLINK", "https://github.com/abenfraj/flashwatch")])
    msilib.add_tables(db, sequence)
    for table in ("InstallUISequence", "InstallExecuteSequence"):
        view = db.OpenView(f"UPDATE `{table}` SET `Sequence`=25 WHERE `Action`='FindRelatedProducts'")
        view.Execute(None)
        view.Close()
    add("LaunchCondition", [("VersionNT64", "Este instalador requer Windows de 64 bits."),
                             ("Installed OR NOT NEWERPRODUCTS", "Já existe um instalador mais recente desta edição instalado.")])
    add("Upgrade", [(UPGRADE_CODE, None, version, None, 1, None, "OLDPRODUCTS"),
                     (UPGRADE_CODE, version, None, None, 258, None, "NEWERPRODUCTS")])
    add("Directory", [("TARGETDIR", None, "SourceDir"),
                       ("LocalAppDataFolder", "TARGETDIR", "."),
                       ("LocalPrograms", "LocalAppDataFolder", "Programs"),
                       ("INSTALLDIR", "LocalPrograms", "FWPTBR|FlashWatch PT-BR"),
                       ("DOCSDIR", "INSTALLDIR", "docs"),
                       ("ProgramMenuFolder", "TARGETDIR", "."),
                       ("MenuFolder", "ProgramMenuFolder", "FWPTBR|FlashWatch PT-BR"),
                       ("DesktopFolder", "TARGETDIR", ".")])
    add("Feature", [("Application", None, "FlashWatch PT-BR", "Programa e documentação", 1, 1, "INSTALLDIR", 0)])
    for component, directory, condition in (("ApplicationFiles", "INSTALLDIR", None),
                                             ("Documentation", "DOCSDIR", None),
                                             ("DesktopShortcut", "INSTALLDIR", 'DESKTOP_SHORTCUT="1"')):
        add("Component", [(component, guid("component:" + component), directory, 260, condition, component + "Reg")])
        add("FeatureComponents", [("Application", component)])
        add("Registry", [(component + "Reg", 1, REG_KEY, component, "[INSTALLDIR]", component)])
    add("Icon", [("AppIcon", msilib.Binary(str(ROOT / "resources/brand/flashwatch.ico")))])
    add("Shortcut", [("StartMenu", "MenuFolder", "FLASHW~1|FlashWatch PT-BR", "ApplicationFiles",
                      "[INSTALLDIR]FlashWatch-PTBR.exe", None, "FlashWatch em Português Brasileiro", None, "AppIcon", 0, 1, "INSTALLDIR"),
                     ("Uninstall", "MenuFolder", "DESINS~1|Desinstalar FlashWatch PT-BR", "ApplicationFiles",
                      "[SystemFolder]msiexec.exe", "/x [ProductCode]", "Remover o programa", None, None, None, 1, None),
                     ("Desktop", "DesktopFolder", "FLASHW~1|FlashWatch PT-BR", "DesktopShortcut",
                      "[INSTALLDIR]FlashWatch-PTBR.exe", None, None, None, "AppIcon", 0, 1, "INSTALLDIR")])
    add("RemoveFile", [("RemoveMenuFolder", "ApplicationFiles", None, "MenuFolder", 2),
                        ("RemoveDocsFolder", "Documentation", None, "DOCSDIR", 2),
                        ("RemoveEmptyAppFolder", "ApplicationFiles", None, "INSTALLDIR", 2)])
    add_ui(db)
    cab = msilib.CAB("application.cab")
    payload = [(executable, "ApplicationFiles", executable.name),
               (ROOT / "LICENSE", "ApplicationFiles", "LICENSE"),
               (ROOT / "NOTICE-PTBR.md", "ApplicationFiles", "NOTICE-PTBR.md"),
               (ROOT / "resources/fonts/Mulish-OFL.txt", "ApplicationFiles", "Mulish-OFL.txt"),
               (ROOT / "docs/INSTALADOR.md", "ApplicationFiles", "LEIA-ME.md")]
    payload += [(p, "Documentation", p.name) for p in sorted((ROOT / "docs").glob("*.md"))]
    manifest = []
    for index, (source, component, filename) in enumerate(payload, 1):
        file_id = f"File{index:03}"
        number, logical = cab.append(str(source), filename, file_id)
        short = f"FILE{index:03}.DAT"
        add("File", [(logical, component, short + "|" + filename, source.stat().st_size,
                      None, None, 512, number)])
        manifest.append(dict(id=file_id, component=component, name=filename,
                             bytes=source.stat().st_size, sha256=hashlib.sha256(source.read_bytes()).hexdigest()))
    print("Compactando o executável validado e a documentação...", flush=True)
    cab.commit(db)
    db.Commit()
    del view
    del db
    gc.collect()  # release MSI handles before hashing; close compacts the file
    report = dict(installer=str(target), product_code=product_code, upgrade_code=UPGRADE_CODE,
                  installer_version=version, application_sha256=APP_SHA256,
                  files=manifest, bytes=target.stat().st_size,
                  sha256=hashlib.sha256(target.read_bytes()).hexdigest())
    (work / "manifest.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), "utf-8")
    (output / (target.name + ".sha256")).write_text(report["sha256"] + "  " + target.name + "\n", "ascii")
    print(f"Criado: {target} ({target.stat().st_size:,} bytes)")
    return target


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--version", default="1.0.0", help="Versão do pacote MSI; não altera o aplicativo")
    cli.add_argument("--out", type=Path, default=ROOT / "dist/instalador")
    args = cli.parse_args()
    build(args.version, args.out.resolve())
