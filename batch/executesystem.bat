@echo off

SET sdkpath=%xilinxpath%\SDK\2015.4\bin

SET cfile=%~1
SET jsonfilepath=%~2
SET projectname=%~3

SET toolchainpath=%~dp0

if not {%~1} == {} if not {%~2} == {} if not {%~3} == {} (
    
  python %toolchainpath%\python\generateexecutesdktcl.py %cfile% %jsonfile% %projectname%
  %sdkpath%\xsdk.bat -batch -source %projectname%_config_sdk.tcl
  %sdkpath%\xsdk.bat -batch -source %projectname%_execute_sdk.tcl

) else (
  echo "few arguments!"
)