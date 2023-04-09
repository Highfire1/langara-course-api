#SingleInstance Force


; Designed to be run at 1920x1080 on firefox, at 90%, with bookmarks hidden
; Pull requests welcome

^i:: {	
	; enter data generated by TransferParser.py
	input := InputBox("Enter courses:")


	for subject in StrSplit(input.value, ",") {

		items := StrSplit(subject, ":") 
		
		Send '^{t}'
		Send 'https://www.bctransferguide.ca/transfer-options/search-courses/?fromTo=from'
		Send "{Enter}"

		Sleep 5000

		Send "{Tab 20}"
		Sleep 2000

		Click "1000, 125"
		Send "Lang{Enter}"
		Sleep 2000	

		Click "1000, 250"
		Send items[1] . "{Enter}"
		Sleep 1000

		for code in StrSplit(items[2], " ") {
			Click "1000, 375"
			Send "^a" . "{BackSpace}"
			Send code
			Click "1000, 575"
			Sleep 100
		}

		Sleep 500
		Send "{Tab 2}" ; scroll down
		Sleep 500

		Click "600, 1050" ; press search
		Sleep 1000
	}
}

; ABST - Aboriginal Studies,1100 1102,AHIS - Art History,1110 1111,



^j:: {
	input := InputBox()

	blocks := 200

	Sleep blocks*10

	MouseMove 0, -220, 0, "R"
	Sleep 100

	for val in StrSplit(input.value, A_Space) {

		if not IsInteger(val)	{
					
			MouseMove 0, -140, 0, "R"

			Click
			Send val . " - "
			Send "{enter}"
			Sleep blocks*2
			MouseMove 0, 140, 0, "R"

			Sleep blocks*2
			
		} else {
			Click
			Send "{BackSpace}{BackSpace}{BackSpace}{BackSpace}" . val
			MouseMove 0, 220, 0, "R"
			Click
			MouseMove 0, -220, 0, "R"

			Sleep blocks*0.5

		}
	}
}




^k:: {
	Reload
}



