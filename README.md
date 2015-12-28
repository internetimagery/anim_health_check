# Animation Health Check

A set of modules that run together to check over your animation for technical issues. Not perfect, but can be a time saver if used well.

# Installation:

Simply copy the folder into your scripts directory in Maya. The folder should be named "animsanity".

# Usage

Within Maya, create a shelf icon with the following PYTHON code:

	import anim_health_check
	anim_health_check.Main()

* Select your object / control to check the animations.

* Click "Check Animation" to run checks.

* For any failed checks. Click "Show" to provide more information on the affected keys / area. You may need the graph editor open to display keys.

* Click the "?" to learn more about what the check does.

* If you are happy with what it found, you can get stuck in and fix the issue. This is typically the preferred method, as we can't always trust a computer to get it right. ;) Having said that, the tool DOES offer a auto-fix option to fix the problem for you. Press "Fix it!" to let the tool attempt to fix it for you.

* Click "Reset" to reset the checks and start again if need be.
