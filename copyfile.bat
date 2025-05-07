@echo off
REM 设置命令提示符代码页为简体中文，以正确显示中文字符
chcp 936

setlocal enabledelayedexpansion

echo DEBUG: Script starting...

REM 设置源目录和目标目录变量
set "SOURCE_AIEducation=AIEducation"
set "SOURCE_AIEducationBackend=AIEducationBackend"
set "DEST_DIR=AIEducationAll"
set "EXCLUDE_AIEducation=node_modules"
set "EXCLUDE_AIEducationBackend=venv"

REM 设置目标子目录
set "DEST_FRONT=%DEST_DIR%\frontend"
set "DEST_BACKEND=%DEST_DIR%\backend"

echo DEBUG: Variables set.
echo DEBUG: SOURCE_AIEducation = %SOURCE_AIEducation%
echo DEBUG: SOURCE_AIEducationBackend = %SOURCE_AIEducationBackend%
echo DEBUG: DEST_DIR = %DEST_DIR%
echo DEBUG: EXCLUDE_AIEducation = %EXCLUDE_AIEducation%
echo DEBUG: EXCLUDE_AIEducationBackend = %EXCLUDE_AIEducationBackend%
echo DEBUG: DEST_FRONT = %DEST_FRONT%
echo DEBUG: DEST_BACKEND = %DEST_BACKEND%
echo.

echo ==================================================
echo 开始执行目录复制任务
echo ==================================================
echo.

REM --- 检查阶段 ---
echo DEBUG: Checking source directory 1: %SOURCE_AIEducation%
if not exist "%SOURCE_AIEducation%" (
    echo 错误: 源目录 "%SOURCE_AIEducation%" 不存在。
    goto EndScript
) else (
    echo DEBUG: Source directory 1 exists. Checking exclusion dir: %SOURCE_AIEducation%\%EXCLUDE_AIEducation%
    if exist "%SOURCE_AIEducation%\%EXCLUDE_AIEducation%" (
      echo DEBUG: Exclusion directory 1 exists.
    ) else (
      echo DEBUG: WARNING - Exclusion directory %SOURCE_AIEducation%\%EXCLUDE_AIEducation% NOT found! Exclusion might not work as expected.
    )
)

echo DEBUG: Checking source directory 2: %SOURCE_AIEducationBackend%
if not exist "%SOURCE_AIEducationBackend%" (
    echo 错误: 源目录 "%SOURCE_AIEducationBackend%" 不存在。
    goto EndScript
) else (
    echo DEBUG: Source directory 2 exists. Checking exclusion dir: %SOURCE_AIEducationBackend%\%EXCLUDE_AIEducationBackend%
    if exist "%SOURCE_AIEducationBackend%\%EXCLUDE_AIEducationBackend%" (
      echo DEBUG: Exclusion directory 2 exists.
    ) else (
      echo DEBUG: WARNING - Exclusion directory %SOURCE_AIEducationBackend%\%EXCLUDE_AIEducationBackend% NOT found! Exclusion might not work as expected.
    )
)

echo DEBUG: Checking destination base directory: %DEST_DIR%
REM 如果目标基础目录不存在，则创建它
if not exist "%DEST_DIR%" (
    echo 目标目录 "%DEST_DIR%" 不存在，正在创建...
    mkdir "%DEST_DIR%"
    if errorlevel 1 (
        echo 错误: 无法创建目标目录 "%DEST_DIR%"。请检查权限。
        goto EndScript
    ) else (
        echo 目标目录 "%DEST_DIR%" 创建成功。
    )
) else (
    echo DEBUG: Destination base directory exists.
)
echo.

REM ************************************************
REM *** 修改：清理旧的目标子目录内容 (使用更稳健的检查方式) ***
REM ************************************************
echo DEBUG: Starting cleanup of destination subdirectories...

echo DEBUG: Checking if destination subdirectory %DEST_FRONT% exists for cleanup...
if exist "%DEST_FRONT%" (
    echo 正在清理目标子目录: "%DEST_FRONT%" ...
    RMDIR /S /Q "%DEST_FRONT%"
    REM 修改：执行 RMDIR 后，再次检查目录是否存在来判断是否成功
    if exist "%DEST_FRONT%" (
        echo 警告: 清理 "%DEST_FRONT%" 后目录仍然存在。可能是权限或文件锁定问题。
        REM 根据需要，可以在这里添加错误处理，比如 goto EndScript
    ) else (
        echo 目录 "%DEST_FRONT%" 已成功删除。 Robocopy 将重新创建它。
    )
) else (
    echo DEBUG: Destination subdirectory %DEST_FRONT% does not exist, no cleanup needed.
)

echo DEBUG: Checking if destination subdirectory %DEST_BACKEND% exists for cleanup...
if exist "%DEST_BACKEND%" (
    echo 正在清理目标子目录: "%DEST_BACKEND%" ...
    RMDIR /S /Q "%DEST_BACKEND%"
    REM 修改：执行 RMDIR 后，再次检查目录是否存在来判断是否成功
    if exist "%DEST_BACKEND%" (
        echo 警告: 清理 "%DEST_BACKEND%" 后目录仍然存在。可能是权限或文件锁定问题。
        REM 根据需要，可以在这里添加错误处理，比如 goto EndScript
    ) else (
        echo 目录 "%DEST_BACKEND%" 已成功删除。 Robocopy 将重新创建它。
    )
) else (
    echo DEBUG: Destination subdirectory %DEST_BACKEND% does not exist, no cleanup needed.
)
echo.
REM ************************************************
REM *** 清理完成 ***
REM ************************************************


REM --- 任务 1 ---
echo DEBUG: Starting Task 1: Robocopy %SOURCE_AIEducation% to %DEST_FRONT% excluding %EXCLUDE_AIEducation%
echo 正在复制 "%SOURCE_AIEducation%" (排除 "%EXCLUDE_AIEducation%") 到 "%DEST_FRONT%" ...

REM 使用 ROBOCOPY 命令进行复制 (可以根据需要恢复 /NFL /NDL /NJH /NJS 参数以简化输出)
robocopy "%SOURCE_AIEducation%" "%DEST_FRONT%" /E /XD "%EXCLUDE_AIEducation%" /LOG+:robocopy_log.txt

echo DEBUG: Robocopy Task 1 finished with errorlevel: !errorlevel!

REM --- 任务 2 ---
echo DEBUG: Starting Task 2: Robocopy %SOURCE_AIEducationBackend% to %DEST_BACKEND% excluding %EXCLUDE_AIEducationBackend%
echo 正在复制 "%SOURCE_AIEducationBackend%" (排除 "%EXCLUDE_AIEducationBackend%") 到 "%DEST_BACKEND%" ...

REM 使用 ROBOCOPY 命令进行复制 (可以根据需要恢复 /NFL /NDL /NJH /NJS 参数以简化输出)
robocopy "%SOURCE_AIEducationBackend%" "%DEST_BACKEND%" /E /XD "%EXCLUDE_AIEducationBackend%" /LOG+:robocopy_log.txt

echo DEBUG: Robocopy Task 2 finished with errorlevel: !errorlevel!

echo ==================================================
echo 复制任务全部完成
echo ==================================================
echo.

:EndScript
echo DEBUG: Reached EndScript label.
REM 添加 pause 以便在手动运行时查看输出，如果不需要可以删除下一行
pause
endlocal
exit /b 0