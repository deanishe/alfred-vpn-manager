#!/usr/bin/osascript

-- Return true if VPN is active
on vpn_is_active(vpn_name)
	tell application "Viscosity"
		repeat with the_connection in connections
			if (name of the_connection) is equal to vpn_name then
				if (state of the_connection) is equal to "Connected" then
					return true
				else
					return false
				end if
			end if
		end repeat
	end tell
	return false
end vpn_is_active

-- Connect to specified VPN
on connect_vpn(vpn_name)
	tell application "Viscosity"
		connect vpn_name
	end tell
end connect_vpn


on run argv
	set vpn_name to item 1 of argv
	if my vpn_is_active(vpn_name) then
		log "VPN " & quote & vpn_name & quote & " is already active."
		return
	end if
	connect_vpn(vpn_name)
end run
