import maya.cmds

for obj in cmds.ls(sl=1):
    cmds.setAttr(f'{obj}.String_On_Off', edit=True, keyable=True)