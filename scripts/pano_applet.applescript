on open theFiles
	repeat with f in theFiles
		set p to POSIX path of f
		try
			do shell script "/bin/zsh '/Users/xiaohuiliang/Library/Application Support/PanoViewer/pano.sh' " & quoted form of p
			exit repeat
		end try
	end repeat
end open

on run
	set theFile to choose file with prompt "选择 360° 全景照片" of type {"public.image"}
	set p to POSIX path of theFile
	do shell script "/bin/zsh '/Users/xiaohuiliang/Library/Application Support/PanoViewer/pano.sh' " & quoted form of p
end run
