# Copyright (C) 2009 The Android Open Source Project
# Copyright (c) 2011, The Linux Foundation. All rights reserved.
# Copyright (C) 2019 The LineageOS Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import hashlib
import common
import re

def FullOTA_InstallBegin(info):
  info.script.AppendExtra('assert(getprop("ro.boot.super_partition") == "system" || abort("ERROR: This recovery does not support retrofit dynamic partitions."););')
  input_zip = info.input_zip
  info.script.AppendExtra('ifelse(is_mounted("/system_root"),unmount("/system_root"));')
  info.script.AppendExtra('ifelse(is_mounted("/vendor"),unmount("/vendor"));')
  info.script.AppendExtra('run_program("/system/bin/toybox", "blkdiscard", "/dev/block/bootdevice/by-name/system"); || abort("ERROR: Failed to discard data on system partition.");')
  info.script.AppendExtra('run_program("/system/bin/toybox", "blkdiscard", "/dev/block/bootdevice/by-name/vendor"); || abort("ERROR: Failed to discard data on vendor partition.");')
  info.script.AppendExtra('ui_print("- Flashing super_empty onto system partition...");')
  AddImage(info, "RADIO", "super_dummy.img", "/dev/block/bootdevice/by-name/system");
  return

def FullOTA_InstallEnd(info):
  input_zip = info.input_zip
  OTA_InstallEnd(info, input_zip)
  return

def IncrementalOTA_InstallEnd(info):
  input_zip = info.target_zip
  OTA_InstallEnd(info, input_zip)
  return

def AddImage(info, dir, basename, dest):
  input_zip = info.input_zip
  path = dir + "/" + basename
  if path not in input_zip.namelist():
    return

  data = input_zip.read(path)
  common.ZipWriteStr(info.output_zip, basename, data)
  info.script.Print("Patching {} image unconditionally...".format(dest.split('/')[-1]))
  info.script.AppendExtra('package_extract_file("%s", "%s");' % (basename, dest))

def OTA_InstallEnd(info, input_zip):
  info.script.Print("Patching device-tree and verity images...")
  AddImage(info, "IMAGES", "dtbo.img", "/dev/block/bootdevice/by-name/dtbo")
  AddImage(info, "IMAGES", "vbmeta.img", "/dev/block/bootdevice/by-name/vbmeta")
  return
