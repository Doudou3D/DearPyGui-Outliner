@echo off
setlocal enableDelayedExpansion

:: Define the command that will be run to obtain the list of files to process
set listCmd=dir /b /a-d "%~dp0*.svg"
set size=64

:: Define the command to run for each file, where "%%F" is an iterated file name from the list
::   something like YOUR_COMMAND -in "%%F" -out "%%~nF.ext"
set runCmd=""C:\Program Files\Inkscape\bin\inkscape.exe" "%%F" --export-width="%size%" --export-height="%size%" --export-filename="%%F_%size%.png""

:: Define the maximum number of parallel processes to run.
set "maxProc=%NUMBER_OF_PROCESSORS%"

::---------------------------------------------------------------------------------
:: The remainder of the code should remain constant
::

:: Get a unique base lock name for this particular instantiation.
:: Incorporate a timestamp from WMIC if possible, but does not fail if
:: WMIC not available. Also incorporate a random number.
  set "lock="
  for /f "skip=1 delims=-+ " %%T in ('2^>nul wmic os get localdatetime') do (
    set "lock=%%T"
    goto :break
  )
  :break
  set "lock=%temp%\lock%lock%_%random%_"

:: Initialize the counters
  set /a "startCount=0, endCount=0"

:: Clear any existing end flags
  for /l %%N in (1 1 %maxProc%) do set "endProc%%N="

:: Launch the commands in a loop
  set launch=1
  for /f "tokens=* delims=:" %%F in ('%listCmd%') do (
    if !startCount! lss %maxProc% (
      set /a "startCount+=1, nextProc=startCount"
    ) else (
      call :wait
    )
    set cmd!nextProc!=%runCmd%
    echo -------------------------------------------------------------------------------
    echo !time! - proc!nextProc!: starting %runCmd%
    2>nul del %lock%!nextProc!
    %= Redirect the lock handle to the lock file. The CMD process will     =%
    %= maintain an exclusive lock on the lock file until the process ends. =%
    start /b "" cmd /c >"%lock%!nextProc!" 2^>^&1 %runCmd%
  )
  set "launch="

:wait
:: Wait for procs to finish in a loop
:: If still launching then return as soon as a proc ends
:: else wait for all procs to finish
  :: redirect stderr to null to suppress any error message if redirection
  :: within the loop fails.
  for /l %%N in (1 1 %startCount%) do 2>nul (
    %= Redirect an unused file handle to the lock file. If the process is    =%
    %= still running then redirection will fail and the IF body will not run =%
    if not defined endProc%%N if exist "%lock%%%N" 9>>"%lock%%%N" (
      %= Made it inside the IF body so the process must have finished =%
      echo ===============================================================================
      echo !time! - proc%%N: finished !cmd%%N!
      type "%lock%%%N"
      if defined launch (
        set nextProc=%%N
        exit /b
      )
      set /a "endCount+=1, endProc%%N=1"
    )
  )
  if %endCount% lss %startCount% (
    timeout /t 1 /nobreak >nul
    goto :wait
  )

2>nul del %lock%*
echo ===============================================================================