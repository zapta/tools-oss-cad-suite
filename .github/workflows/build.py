"""A Python script to build the oss-cad-suite package for a given platform"""

# This script is called from the github build workflow and and runs
# in the top dir of this repo. it uses ./_upstream and ./_packages
# directories for input and output files respectively.
#
# To install 7z on mac:
#   brew install p7zip

import os
import json
import subprocess
from dataclasses import dataclass
from typing import List, Callable, Union
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
    "--build-info-json", required=True, type=str, help="JSON with build properties"
)

args = parser.parse_args()

# -- This is the version of Yosys we pick.
YOSYS_RELEASE_TAG = "2025-06-08"

# -- The tag as placed in the file name.
YOSYS_FILE_TAG = YOSYS_RELEASE_TAG.replace("-", "")


def run(cmd_args: Union[List[str], str], shell: bool = False) -> None:
    """Run a command and check that it succeeded. Select shell=true to enable
    shell features such as '*' glob."""
    print(f"\nRun: {cmd_args}")
    print(f"{shell=}")
    subprocess.run(cmd_args, check=True, shell=shell)
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


def darwin_x86_64_packager(yosys_dir: Path, package_dir: Path) -> None:
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

    # Check that the libusb backend exists. We use it to list USB devices.
    assert (package_dir / "lib/libusb-1.0.so.0").is_file()


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

    # Check that the libusb backend exists. We use it to list USB devices.
    assert (package_dir / "lib/libusb-1.0.so.0").is_file()


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

    # Check that the libusb backend exists. We use it to list USB devices.
    assert (package_dir / "lib/libusb-1.0.dll").is_file()


@dataclass(frozen=True)
class PlatformInfo:
    """Represents the properties of a platform."""

    yosys_fname: str
    unarchive_cmd: List[str]
    packager_function: Callable[[Path, Path], None]


# -- Maps apio platform codes to their attributes.
PLATFORMS = {
    "darwin-arm64": PlatformInfo(
        f"oss-cad-suite-darwin-arm64-{YOSYS_FILE_TAG}.tgz",
        ["tar", "zxf"],
        darwin_arm64_packager,
    ),
    "darwin-x86-64": PlatformInfo(
        f"oss-cad-suite-darwin-x64-{YOSYS_FILE_TAG}.tgz",
        ["tar", "zxf"],
        darwin_x86_64_packager,
    ),
    "linux-x86-64": PlatformInfo(
        f"oss-cad-suite-linux-x64-{YOSYS_FILE_TAG}.tgz",
        ["tar", "zxf"],
        linux_x86_64_packager,
    ),
    "linux-aarch64": PlatformInfo(
        f"oss-cad-suite-linux-arm64-{YOSYS_FILE_TAG}.tgz",
        ["tar", "zxf"],
        linux_aarch64_packager,
    ),
    "windows-amd64": PlatformInfo(
        f"oss-cad-suite-windows-x64-{YOSYS_FILE_TAG}.exe",
        ["7z", "x"],
        windows_amd64_packager,
    ),
}


def main():
    """Builds the Apio oss-cad-suite package for one platform."""

    # pylint: disable=too-many-statements

    # -- Print build parameters
    print("Apio oss-cad-suite builder")

    print("\nPARAMS:")
    print(f"  Platform ID:         {args.platform_id}")
    print(f"  Yosys release tag:   {YOSYS_RELEASE_TAG}")
    print(f"  Yosys file tag:      {YOSYS_FILE_TAG}")
    print(f"  Package tag:         {args.package_tag}")
    print(f"  Build info file:     {args.build_info_json}")

    # -- Save the start dir. It is assume to be at top of this repo.
    work_dir: Path = Path.cwd()
    print(f"\n{work_dir=}")

    # -- Map to Yosys's platform info
    platform_info = PLATFORMS[args.platform_id]
    print(f"\n{platform_info=}")

    # -- Save absolute input build-info.json file path
    input_json_file = Path(args.build_info_json).absolute()
    print(f"{input_json_file=}")
    assert input_json_file.exists()
    assert input_json_file.is_file()

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
        ".tar.gz",
    ]
    package_filename = "".join(parts)
    print(f"\n{package_filename=}")

    # -- Construct Yosys URL
    parts = [
        "https://github.com/YosysHQ/oss-cad-suite-build/releases/download",
        "/",
        YOSYS_RELEASE_TAG,
        "/",
        platform_info.yosys_fname,
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
    run(platform_info.unarchive_cmd + [platform_info.yosys_fname])
    run(["ls", "-al"])

    # -- Delete the Yosys archive (large).
    print("Deleting the Yosys archive file")
    Path(platform_info.yosys_fname).unlink()
    run(["ls", "-al"])

    # -- Call the packager function to copy files from the yosys
    # -- dir to the output package dir.
    print(f"\nCalling packager function {platform_info.packager_function}")
    print(f"  Source dir: {upstream_dir / 'oss-cad-suite'}")
    print(f"  Dest dir:   {package_dir}")
    platform_info.packager_function(upstream_dir / "oss-cad-suite", package_dir)

    # -- Read the build info json
    with input_json_file.open("r", encoding="utf-8") as f:
        json_data = json.load(f)

    # Add platform specific fields.
    json_data["target-platform"] = args.platform_id
    json_data["yosys-tag"] = YOSYS_RELEASE_TAG
    json_data["file-name"] = package_filename

    # Write updated data to a new file
    output_json_file = package_dir / "build-info.json"
    with output_json_file.open("w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2)
        f.write("\n")  # Ensure the file ends with a newline
    run(["ls", "-al", package_dir])
    run(["cat", "-n", output_json_file])

    # Format the json file
    run(["json-align", "--in-place", "--spaces", "2", output_json_file])
    run(["ls", "-al", package_dir])
    run(["cat", "-n", output_json_file])

    # -- Compress the package. We run it in the shell for '*" to expand.
    print("Compressing the  package.")
    os.chdir(package_dir)
    run(f"tar zcf ../{package_filename} ./*", shell=True)

    # -- Delete the package dir (large)
    print(f"\nDeleting package dir {package_dir}")
    shutil.rmtree(package_dir)

    # -- Final check
    os.chdir(work_dir)
    print(f"\n{Path.cwd()=}")
    run(["ls", "-al"])
    run(["ls", "-al", "_packages"])
    assert (Path("_packages") / package_filename).is_file()

    # -- All done


if __name__ == "__main__":
    main()
