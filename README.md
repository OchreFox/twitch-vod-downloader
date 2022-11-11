# Twitch VOD Downloader with Chat

This is a simple script to download a Twitch VOD with the chat overlayed on top.

## Requirements

- [FFmpeg](https://ffmpeg.org/)
  - Note: This project uses a custom-built FFmpeg with proprietary modules.
  - You can get the pre-built binaries [here](https://pastebin.com/jMA2GqbS), or you can also check the documentation for [building FFmpeg](https://github.com/m-ab-s/media-autobuild_suite) yourself.
- [Python 3](https://www.python.org/) (Optional if you want to use the script)
- [Twitch Downloader CLI](https://github.com/lay295/TwitchDownloader)

## Usage

1. Clone this repository or download the executable.
2. Set the `FFmpegPath` variable in `config.ini` to the path of your FFmpeg executable.
3. Set the Twitch Downloader CLI `Path` variable in `config.ini` to the path of your Twitch Downloader CLI executable.
4. Set the `RenderChatAsOverlay` variable in `config.ini` to `true` if you want the chat to be rendered as an overlay, or `false` if you want the chat to be rendered to the side of the VOD.
5. Run the script with `python main.py`, or the executable in a terminal with `TwitchVODDownloader.exe`.
   1. You can pass the `-v` flag to the script to set the VOD ID.
   2. Or you can just run the script and enter the VOD ID or URL when prompted.
6. The script will download the VOD and chat, and then render the chat to the VOD.
   1. If you set `RenderChatAsOverlay` to `true`, the chat will be rendered as an overlay.
   2. You can set the `BackgroundOpacity` variable in `config.ini` to change the background opacity of the chat.
   3. You can customize the chat overlay position by setting the `OverlayPosition` variable in `config.ini`.
      - 0 = Top Left
      - 1 = Top Right
      - 2 = Bottom Left
      - 3 = Bottom Right
      - 4 = Left Center
      - 5 = Right Center
7. The script will then merge the VOD and chat into a single video file, and save it to the `DownloadFolder` path.

## Recommended Settings

The recommended directory structure for this script is as follows:

```text
twitch-vod-downloader/
├─ ffmpeg-custom/
│  ├─ (...)
│  ├─ ffmpeg.exe
├─ TwitchDownloader/
│  ├─ TwitchDownloader.cli
├─ VODs/
├─ main.py
├─ DownloaderLib.py
```

Other settings hints can be found in the `config.ini`.

## Known Issues

- Rendering the chat without overlay is not fully tested.

## Credits

- [lay295](https://github.com/lay295) for [Twitch Downloader CLI](https://github.com/lay295/TwitchDownloader)
- [m-ab-s](https://github.com/m-ab-s/media-autobuild_suite) for the custom FFmpeg build with CUDA.
- [Mugnum](https://twitter.com/syrtsevser) for creating the original [script](https://pastebin.com/jMA2GqbS).
