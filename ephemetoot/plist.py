default_file = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>ephemetoot.scheduler</string>
  <key>WorkingDirectory</key>
  <string>/FILEPATH/ephemetoot</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/local/bin/ephemetoot</string>
    <string>--config</string>
    <string>config.yaml</string>
  </array>
  <key>StandardOutPath</key>
  <string>ephemetoot.log</string>
  <key>StandardErrorPath</key>
  <string>ephemetoot.error.log</string>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key>
    <integer>9</integer>
    <key>Minute</key>
    <integer>00</integer>
  </dict>
</dict>
</plist>"""
