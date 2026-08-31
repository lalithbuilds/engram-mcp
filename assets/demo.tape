Output assets/demo.gif
Set FontSize 16
Set Width 1000
Set Height 450
Set Padding 40
Set WindowBar Colorful
Set Margin 20
Set MarginFill "#6B50FF"
Set BorderRadius 10
Set FontFamily "JetBrains Mono"
Set Theme "Catppuccin Mocha"

Hide
Type "alias engram='python3 engram.py'" Enter
Type "rm -f memory.db*" Enter
Type "engram save 'Initial boot'" Enter
Type "clear" Enter
Show

Type "engram save 'Deployed the new caching layer using Redis' -c devops" Enter
Sleep 1s
Type "engram save 'Redis connection string is in AWS Secrets Manager'" Enter
Sleep 2s
Type "engram search 'Redis'" Enter
Sleep 4s
Type "engram stats" Enter
Sleep 5s
