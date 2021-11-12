on open location this_URL
        set home to POSIX path of (path to home folder)
        set dialer to home & ".messages-tel/dialer.py"
	set cmd to "\"" & dialer & "\" \"" & this_URL & "\" >/dev/null 2>&1 &"
	do shell script cmd
end open location
