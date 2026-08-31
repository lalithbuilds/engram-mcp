Output assets/demo.gif
Set FontSize 15
Set Width 900
Set Height 450
Set Padding 40
Set WindowBar Colorful
Set Margin 20
Set MarginFill "#282a36" 
Set BorderRadius 12
Set FontFamily "Fira Code"
Set Theme "Dracula"
Set TypingSpeed 40ms

Hide
Type "alias engram='python3 engram.py'" Enter
Type "rm -f memory.db*" Enter
Type "clear" Enter
Show

Sleep 500ms
Type "engram save 'Deployed the new caching layer using Redis' -c devops"
Sleep 200ms
Enter
Sleep 1s

Type "engram save 'Redis connection string is in AWS Secrets Manager'"
Sleep 200ms
Enter
Sleep 1s

Type "engram search 'Redis'"
Sleep 200ms
Enter
Sleep 2s

Type "engram stats"
Sleep 200ms
Enter
Sleep 3s
