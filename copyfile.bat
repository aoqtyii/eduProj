@echo off
REM ����������ʾ������ҳΪ�������ģ�����ȷ��ʾ�����ַ�
chcp 936

setlocal enabledelayedexpansion

echo DEBUG: Script starting...

REM ����ԴĿ¼��Ŀ��Ŀ¼����
set "SOURCE_AIEducation=AIEducation"
set "SOURCE_AIEducationBackend=AIEducationBackend"
set "DEST_DIR=AIEducationAll"
set "EXCLUDE_AIEducation=node_modules"
set "EXCLUDE_AIEducationBackend=venv"

REM ����Ŀ����Ŀ¼
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
echo ��ʼִ��Ŀ¼��������
echo ==================================================
echo.

REM --- ���׶� ---
echo DEBUG: Checking source directory 1: %SOURCE_AIEducation%
if not exist "%SOURCE_AIEducation%" (
    echo ����: ԴĿ¼ "%SOURCE_AIEducation%" �����ڡ�
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
    echo ����: ԴĿ¼ "%SOURCE_AIEducationBackend%" �����ڡ�
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
REM ���Ŀ�����Ŀ¼�����ڣ��򴴽���
if not exist "%DEST_DIR%" (
    echo Ŀ��Ŀ¼ "%DEST_DIR%" �����ڣ����ڴ���...
    mkdir "%DEST_DIR%"
    if errorlevel 1 (
        echo ����: �޷�����Ŀ��Ŀ¼ "%DEST_DIR%"������Ȩ�ޡ�
        goto EndScript
    ) else (
        echo Ŀ��Ŀ¼ "%DEST_DIR%" �����ɹ���
    )
) else (
    echo DEBUG: Destination base directory exists.
)
echo.

REM ************************************************
REM *** �޸ģ�����ɵ�Ŀ����Ŀ¼���� (ʹ�ø��Ƚ��ļ�鷽ʽ) ***
REM ************************************************
echo DEBUG: Starting cleanup of destination subdirectories...

echo DEBUG: Checking if destination subdirectory %DEST_FRONT% exists for cleanup...
if exist "%DEST_FRONT%" (
    echo ��������Ŀ����Ŀ¼: "%DEST_FRONT%" ...
    RMDIR /S /Q "%DEST_FRONT%"
    REM �޸ģ�ִ�� RMDIR ���ٴμ��Ŀ¼�Ƿ�������ж��Ƿ�ɹ�
    if exist "%DEST_FRONT%" (
        echo ����: ���� "%DEST_FRONT%" ��Ŀ¼��Ȼ���ڡ�������Ȩ�޻��ļ��������⡣
        REM ������Ҫ��������������Ӵ��������� goto EndScript
    ) else (
        echo Ŀ¼ "%DEST_FRONT%" �ѳɹ�ɾ���� Robocopy �����´�������
    )
) else (
    echo DEBUG: Destination subdirectory %DEST_FRONT% does not exist, no cleanup needed.
)

echo DEBUG: Checking if destination subdirectory %DEST_BACKEND% exists for cleanup...
if exist "%DEST_BACKEND%" (
    echo ��������Ŀ����Ŀ¼: "%DEST_BACKEND%" ...
    RMDIR /S /Q "%DEST_BACKEND%"
    REM �޸ģ�ִ�� RMDIR ���ٴμ��Ŀ¼�Ƿ�������ж��Ƿ�ɹ�
    if exist "%DEST_BACKEND%" (
        echo ����: ���� "%DEST_BACKEND%" ��Ŀ¼��Ȼ���ڡ�������Ȩ�޻��ļ��������⡣
        REM ������Ҫ��������������Ӵ��������� goto EndScript
    ) else (
        echo Ŀ¼ "%DEST_BACKEND%" �ѳɹ�ɾ���� Robocopy �����´�������
    )
) else (
    echo DEBUG: Destination subdirectory %DEST_BACKEND% does not exist, no cleanup needed.
)
echo.
REM ************************************************
REM *** ������� ***
REM ************************************************


REM --- ���� 1 ---
echo DEBUG: Starting Task 1: Robocopy %SOURCE_AIEducation% to %DEST_FRONT% excluding %EXCLUDE_AIEducation%
echo ���ڸ��� "%SOURCE_AIEducation%" (�ų� "%EXCLUDE_AIEducation%") �� "%DEST_FRONT%" ...

REM ʹ�� ROBOCOPY ������и��� (���Ը�����Ҫ�ָ� /NFL /NDL /NJH /NJS �����Լ����)
robocopy "%SOURCE_AIEducation%" "%DEST_FRONT%" /E /XD "%EXCLUDE_AIEducation%" /LOG+:robocopy_log.txt

echo DEBUG: Robocopy Task 1 finished with errorlevel: !errorlevel!

REM --- ���� 2 ---
echo DEBUG: Starting Task 2: Robocopy %SOURCE_AIEducationBackend% to %DEST_BACKEND% excluding %EXCLUDE_AIEducationBackend%
echo ���ڸ��� "%SOURCE_AIEducationBackend%" (�ų� "%EXCLUDE_AIEducationBackend%") �� "%DEST_BACKEND%" ...

REM ʹ�� ROBOCOPY ������и��� (���Ը�����Ҫ�ָ� /NFL /NDL /NJH /NJS �����Լ����)
robocopy "%SOURCE_AIEducationBackend%" "%DEST_BACKEND%" /E /XD "%EXCLUDE_AIEducationBackend%" /LOG+:robocopy_log.txt

echo DEBUG: Robocopy Task 2 finished with errorlevel: !errorlevel!

echo ==================================================
echo ��������ȫ�����
echo ==================================================
echo.

:EndScript
echo DEBUG: Reached EndScript label.
REM ��� pause �Ա����ֶ�����ʱ�鿴������������Ҫ����ɾ����һ��
pause
endlocal
exit /b 0