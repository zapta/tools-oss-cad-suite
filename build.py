"""A Python script to build the oss-cad-suite package for a given platform"""

# This script is called from the github build workflow.
#
# To install 7z on mac:
#   brew install p7zip

import os
import subprocess
from dataclasses import dataclass
from typing import List, Callable
import argparse
import shutil
from pathlib import Path

# -- Command line options.
parser = argparse.ArgumentParser()


# The platform id. E.g. "darwin-arm64"
parser.add_argument("--platform_id", required=True, type=str, help="Platform to build")

# The the package file tag. E.g "20250608".
parser.add_argument(
    "--package-tag", required=True, type=str, help="Package file name tag"
)

# Path to the properties file with the build info.
parser.add_argument(
    "--build-info-file", required=True, type=str, help="Text file with build properties"
)

args = parser.parse_args()

# -- This is the version of Yosys we pick.
YOSYS_TAG = "2025-06-08"


def run(cmd_args: List[str]) -> None:
    """Run a command and check that it succeeded."""
    print(f"\nRun: {cmd_args}")
    subprocess.run(cmd_args, check=True)
    print("Run done\n")


def rsync_yosys_package(yosys_dir: Path, package_dir: Path) -> None:
    """Copy yosys package files to the destination package."""

    # -- Check that yosys dir is not empty and package dir is.
    assert any(yosys_dir.iterdir())
    assert not any(package_dir.iterdir())

    # -- Copy the package directory tree. We avoid 'cp' because it copies 
    # -- symlinks as files and inflates the package.
    # -- The flag 'q' is for 'quiet'.
    run(["rsync", "-aq", f"{yosys_dir}/", f"{package_dir}/"])

    # -- Rename VERSION to YOSYS-VERSION
    # if (package_dir / "VERSION").exists():
    (package_dir / "VERSION").rename(package_dir / "YOSYS-VERSION")


def check_package_executables(package_dir: Path, executables: List[str]) -> None:
    """Check that a few binaries exists and are executable."""
    for bin_file in executables:
        file_path = package_dir / bin_file
        print(f"Checking executable: {file_path}")
        assert file_path.is_file(), file_path
        assert os.access(file_path, os.X_OK), file_path


def darwin_arm64_packager(yosys_dir: Path, package_dir: Path) -> None:
    """Copy the files from yosys dir to our package dir."""

    # -- Copy files.
    rsync_yosys_package(yosys_dir, package_dir)

    # -- Check that a few binaries exists and are executable..
    check_package_executables(
        package_dir,
        [
            "bin/yosys",
            "bin/nextpnr-ice40",
            "bin/nextpnr-ecp5",
            "bin/nextpnr-himbaechel",
            "bin/dot",
            "bin/gtkwave",
        ],
    )

    # Check that the libusb backend exists. We use it to list USB devices.
    assert (package_dir / "lib/libusb-1.0.0.dylib").is_file()


def darwin_x86_64_packger(yosys_dir: Path, package_dir: Path) -> None:
    """Copy the files from yosys dir to our package dir."""

    # -- Copy files.
    rsync_yosys_package(yosys_dir, package_dir)

    # -- Check that a few binaries exists and are executable..
    check_package_executables(
        package_dir,
        [
            "bin/yosys",
            "bin/nextpnr-ice40",
            "bin/nextpnr-ecp5",
            "bin/nextpnr-himbaechel",
            "bin/dot",
            "bin/gtkwave",
        ],
    )

    # Check that the libusb backend exists. We use it to list USB devices.
    assert (package_dir / "lib/libusb-1.0.0.dylib").is_file()


def linux_x86_64_packager(yosys_dir: Path, package_dir: Path) -> None:
    """Copy the files from yosys dir to our package dir."""

    # -- Copy files.
    rsync_yosys_package(yosys_dir, package_dir)

    # -- Check that a few binaries exists and are executable..
    check_package_executables(
        package_dir,
        [
            "bin/yosys",
            "bin/nextpnr-ice40",
            "bin/nextpnr-ecp5",
            "bin/nextpnr-himbaechel",
            "bin/dot",
            "bin/gtkwave",
        ],
    )


def linux_aarch64_packager(yosys_dir: Path, package_dir: Path) -> None:
    """Copy the files from yosys dir to our package dir."""

    # -- Copy files.
    rsync_yosys_package(yosys_dir, package_dir)

    # -- Check that a few binaries exists and are executable..
    check_package_executables(
        package_dir,
        [
            "bin/yosys",
            "bin/nextpnr-ice40",
            "bin/nextpnr-ecp5",
            "bin/nextpnr-himbaechel",
            "bin/dot",
            "bin/gtkwave",
        ],
    )


def windows_amd64_packager(yosys_dir: Path, package_dir: Path) -> None:
    """Copy the files from yosys dir to our package dir."""

    # -- Copy files.
    rsync_yosys_package(yosys_dir, package_dir)

    # -- Check that a few binaries exists and are executable..
    check_package_executables(
        package_dir,
        [
            "bin/yosys.exe",
            "bin/nextpnr-ice40.exe",
            "bin/nextpnr-ecp5.exe",
            "bin/nextpnr-himbaechel.exe",
            "bin/gtkwave.exe",
        ],
    )


@dataclass(frozen=True)
class PlatformInfo:
    """Represents the properties of a platform."""

    yosys_platform_id: str
    yosys_file_ext: str
    unarchive_cmd: List[str]
    packager_function: Callable[[Path, Path], None]


# -- Maps apio platform codes to their attributes.
PLATFORMS = {
    "darwin-arm64": PlatformInfo(
        "darwin-arm64",
        "tgz",
        ["tar", "zxf"],
        darwin_arm64_packager,
    ),
    "darwin-x86-64": PlatformInfo(
        "darwin-x64",
        "tgz",
        ["tar", "zxf"],
        darwin_x86_64_packger,
    ),
    "linux-x86-64": PlatformInfo(
        "linux-x64",
        "tgz",
        ["tar", "zxf"],
        linux_x86_64_packager,
    ),
    "linux-aarch64": PlatformInfo(
        "linux-arm64",
        "tgz",
        ["tar", "zxf"],
        linux_aarch64_packager,
    ),
    "windows-amd64": PlatformInfo(
        "windows-x64",
        "exe",
        ["7z", "x"],
        windows_amd64_packager,
    ),
}


def main():
    """Builds the Apio oss-cad-suite package for one platform."""

    # -- Print build parameters
    print("Apio oss-cad-suite builder")

    print("\nPARAMS:")
    print(f"  Platform ID:       {args.platform_id}")
    print(f"  Yosys tag:         {YOSYS_TAG}")
    print(f"  Package tag:       {args.package_tag}")
    print(f"  Build info file:   {args.build_info_file}")

    # -- Map to Yosys's platform info
    platform_info = PLATFORMS[args.platform_id]

    # -- Save the start dir. It is assume to be at top of this repo.
    work_dir: Path = Path.cwd()
    print(f"\n{work_dir=}")

    # -- Save absolute build info file path
    build_info_path = Path(args.build_info_file).absolute()
    print(f"{build_info_path=}")
    assert build_info_path.exists()
    assert build_info_path.is_file()

    # --  Folder for storing the upstream packages
    upstream_dir: Path = work_dir / "_upstream" / args.platform_id
    print(f"\n{upstream_dir=}")
    upstream_dir.mkdir(parents=True, exist_ok=True)

    # -- Folder for storing the generated package file.
    package_dir: Path = work_dir / "_packages" / args.platform_id
    print(f"\n{package_dir=}")
    package_dir.mkdir(parents=True, exist_ok=True)

    # -- Construct target package file name
    parts = [
        "apio-oss-cad-suite",
        "-",
        args.platform_id,
        "-",
        args.package_tag,
        ".zip",
    ]
    package_filename = "".join(parts)
    print(f"\n{package_filename=}")

    # -- Construct Yosys file name
    parts = [
        "oss-cad-suite",
        "-",
        platform_info.yosys_platform_id,
        "-",
        YOSYS_TAG.replace("-", ""),
        ".",
        platform_info.yosys_file_ext,
    ]
    yosys_fname = "".join(parts)
    print(f"\n{yosys_fname=}")

    # -- Construct Yosys URL
    parts = [
        "https://github.com/YosysHQ/oss-cad-suite-build/releases/download",
        "/",
        YOSYS_TAG,
        "/",
        yosys_fname,
    ]
    yosys_url = "".join(parts)
    print(f"\n{yosys_url=}")

    # -- Download the Yosys file.
    print(f"\nChanging to UPSTREAM_DIR: {str(upstream_dir)}")
    os.chdir(upstream_dir)
    print(f"\nDownloading {yosys_url}")
    run(["wget", "-nv", yosys_url])
    run(["ls", "-al"])

    # -- Uncompress the yosys archive
    print("Uncompressing the Yosys file")
    run(platform_info.unarchive_cmd + [yosys_fname])
    run(["ls", "-al"])

    # -- Delete the Yosys archive, we don't need it anymore
    print("Deleting the Yosys archive file")
    Path(yosys_fname).unlink()
    run(["ls", "-al"])

    # -- Call the packager function to copy files from the yosys
    # -- dir to the output package dir.
    print(f"\nCalling packager function {platform_info.packager_function}")
    print(f"  Source dir: {upstream_dir / 'oss-cad-suite'}")
    print(f"  Dest dir:   {package_dir}")
    platform_info.packager_function(upstream_dir / "oss-cad-suite", package_dir)

    # -- Add to the package an BUILD info file. Use the base info file
    # -- and append to it the platform id property.
    package_build_info = package_dir / "BUILD-INFO"
    run(["cp", build_info_path, package_build_info])
    with package_build_info.open("a") as f:
        f.write(f"platform-id = {args.platform_id}\n")
        f.write(f"yosys-tag = {YOSYS_TAG}\n")
    run(["ls", "-al", package_dir])
    run(["cat", "-n", package_build_info])

    # -- Zip the package. We run zip in a shell for the '*' glob to exapnd.
    print("Compressing the  package.")
    os.chdir(package_dir)
    print(f"{Path.cwd()=}")
    # -- The flag 'q' is for 'quiet'.
    zip_cmd = f"zip -qr ../{package_filename} *"
    subprocess.run(zip_cmd, shell=True, check=True)

    # -- Delete the package dir
    print(f"\nDeleting package dir {package_dir}")
    shutil.rmtree(package_dir)

    # -- Final check
    os.chdir(work_dir)
    print(f"{Path.cwd()=}")
    run(["ls", "-al"])
    run(["ls", "-al", "_packages"])
    assert (Path("_packages") / package_filename).is_file()

    # -- All done


if __name__ == "__main__":
    main()
