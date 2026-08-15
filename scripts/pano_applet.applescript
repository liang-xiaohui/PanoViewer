on open theFiles
	set launcher to POSIX path of (path to resource "pano.sh")
	repeat with f in theFiles
		set p to POSIX path of f
		try
			do shell script "/bin/zsh " & quoted form of launcher & " " & quoted form of p
			exit repeat
		end try
	end repeat
end open

on run
	set theFile to choose file with prompt "选择 360° 全景照片" of type {"public.image"}
	set p to POSIX path of theFile
	set launcher to POSIX path of (path to resource "pano.sh")
	do shell script "/bin/zsh " & quoted form of launcher & " " & quoted form of p
end run
