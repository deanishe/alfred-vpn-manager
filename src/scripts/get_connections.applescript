#!/usr/bin/osascript

-- Return a string of the_list joined with delimiter
on join_list(the_list, delimiter)
	set the_string to ""
	set old_delims to AppleScript's text item delimiters
	repeat with the_item in the_list
		if the_string is equal to "" then
			set the_string to the_item
		else
			set the_string to the_string & delimiter & the_item
		end if
	end repeat
	set AppleScript's text item delimiters to old_delims
	return the_string
end join_list


tell application "Viscosity"
	set vpn_connections to {}
	repeat with the_connection in connections
		set the end of vpn_connections to (name of the_connection) & tab & (state of the_connection)
	end repeat
	return my join_list(vpn_connections, linefeed)
end tell