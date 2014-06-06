@ECHO OFF
del /AH /S *.o *.obj *.manifest *.ilk *.suo *.ncb *.pyc *.dblite BuildLog.htm *.user *.dll  *.lib *.exe *.exp
del /A-H /S *.o *.obj *.manifest *.ilk *.suo *.ncb *.pyc *.dblite BuildLog.htm *.user *.dll  *.lib *.exe *.passed *.exp *.a
PAUSE