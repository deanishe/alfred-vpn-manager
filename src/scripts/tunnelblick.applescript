#!/usr/bin/osascript

-- Return a string of the_list joined with delimiter
on join_list(the_list, delimiter)
	set the_string to ""
	set old_delims to AppleScript's text item delimiters
	repeat with the_item in the_list
		if the_string is equal to "" then
			set the_string to the_string & the_item
		else
			set the_string to the_string & delimiter & the_item
		end if
	end repeat
	set AppleScript's text item delimiters to old_delims
	return the_string
end join_list

-- Return all connections
on list_connections()
	set connections to {}
	tell application "Tunnelblick"
		--repeat with the_conf in (get configurations)
		set i to 1
		repeat (count of (get configurations)) times
			set the_name to (get name of configuration i)
			set the_state to (get state of configuration i)

			if the_state = "CONNECTED" then
				set the_string to "1 "
			else
				set the_string to "0 "
			end if
			set the_string to the_string & the_name
			set the end of connections to the_string
			set i to i + 1
		end repeat
	end tell
	return join_list(connections, linefeed)
end list_connections

on run (argv)
	if (count of argv) is 0 then
		log "Usage: tunnelblick <command> [<name>]"
		return
	end if

	set the_command to first item of argv

	if the_command = "list" then
		return my list_connections()
	end if

	if the_command = "disconnect-all" then
		tell application "Tunnelblick" to disconnect all
		return
	end if

	-- Other commands also require a name
	if (count of argv) is not 2 then
		log "Usage: tunnelblick <command> [<name>]"
		return
	end if

	set the_name to second item of argv

	if the_command = "connect" then
		tell application "Tunnelblick" to connect the_name
		return
	end if

	if the_command = "disconnect" then
		tell application "Tunnelblick" to disconnect the_name
		return
	end if
end run