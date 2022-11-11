# Based on https://pastebin.com/jMA2GqbS

import configparser
import subprocess
import os
import logging
import sys

from DownloaderLib import create_folder, get_ffmpeg_merge_command, get_overlay_command, parse_twitch_vod

# file deepcode ignore CommandInjection
config = configparser.ConfigParser()
config.read('config.ini')

# Initialize logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S',
    handlers=[logging.FileHandler('Downloader.log'),
              logging.StreamHandler()])

logger = logging.getLogger("Downloader")


def main():
    args = sys.argv[1:]
    # Read arguments
    if len(args) == 2 and args[0] == "-v":
        vod_id = args[1]
    else:
        twitch_vod = input("Enter Twitch VOD URL or ID: ")
        # Parse twitch vod url or id
        vod_id = parse_twitch_vod(twitch_vod)

    logger.info("Downloading VOD: " + vod_id)

    # Create VOD folder if it doesn't exist
    vod_folder = config['Application']['DownloadFolder']
    vod_folder_absolute = os.path.join(os.getcwd(), vod_folder, vod_id)
    create_folder(vod_folder_absolute)

    # Paths
    vod_download_path = os.path.join(vod_folder_absolute, vod_id + ".mp4")
    chat_download_path = os.path.join(vod_folder_absolute,
                                      vod_id + "_chat.json")
    chat_video_path = os.path.join(vod_folder_absolute, vod_id + "_chat.mp4")
    mask_video_path = os.path.join(vod_folder_absolute,
                                   vod_id + "_chat_mask.mp4")
    merged_video_path = os.path.join(vod_folder_absolute,
                                     vod_id + "_merged.mp4")
    ffmpeg_path = os.path.join(os.getcwd(),
                               config['Application']['FFmpegPath'])
    temp_path = os.path.join(os.getcwd(), "temp")
    create_folder(temp_path)

    # Get twitch downloader root folder
    twitch_downloader_root = os.path.join(
        os.getcwd(), os.path.normpath(config['TwitchDownloader']['Path']))
    twitch_downloader_exec = os.path.join(twitch_downloader_root,
                                          "TwitchDownloaderCLI.exe")

    # Base config

    render_chat_as_overlay = config['Application'].getboolean(
        'RenderChatAsOverlay')
    if render_chat_as_overlay:
        logger.info("Rendering chat as overlay")
    else:
        logger.info("Rendering chat as video side by side")

    # TwitchDownloaderCLI config
    embed_emotes = "--embed-emotes" if config['TwitchDownloader'].getboolean(
        'EmbedEmotes') else ""
    bttv_emotes = config['TwitchDownloader'].getboolean('BTTVEmotes')
    ffz_emotes = config['TwitchDownloader'].getboolean('FFZEmotes')
    stv_emotes = config['TwitchDownloader'].getboolean('7TVEmotes')
    chat_output_args = "--output-args=\"" + config['TwitchDownloader'][
        'OutputArgs'] + "\""
    background_color = "--background-color \"#" + config['TwitchDownloader'][
        'BackgroundColor'] + "\""
    message_color = "--message-color \"#" + config['TwitchDownloader'][
        'MessageColor'] + "\""
    chat_width = "--chat-width " + config['TwitchDownloader']['ChatWidth']
    chat_height = "--chat-height " + config['TwitchDownloader']['ChatHeight']
    font = "--font \"" + config['TwitchDownloader']['Font'] + "\""
    font_size = "--font-size " + config['TwitchDownloader']['FontSize']
    ignore_users = "--ignore-users \"" + config['TwitchDownloader'][
        'IgnoreUsers'] + "\""

    # Commands
    twitch_chat_download_cmd = f"{twitch_downloader_exec} -m ChatDownload --id {vod_id} {embed_emotes} --bttv={bttv_emotes} --ffz={ffz_emotes} --stv={stv_emotes} -o \"{chat_download_path}\""
    twitch_chat_render_cmd = f"{twitch_downloader_exec} -m ChatRender --temp-path \"{temp_path}\" -i \"{chat_download_path}\" -o \"{chat_video_path}\" --generate-mask={render_chat_as_overlay} {background_color} {message_color} {chat_width} {chat_height} {font} {font_size} {ignore_users} {chat_output_args}"
    twitch_video_download_cmd = f"{twitch_downloader_exec} --ffmpeg-path \"{ffmpeg_path}\" --temp-path \"{temp_path}\" -m VideoDownload --id {vod_id} -o \"{vod_download_path}\""
    ffmpeg_merge_cmd = get_ffmpeg_merge_command(vod_download_path,
                                                chat_video_path,
                                                mask_video_path,
                                                merged_video_path)

    # Run TwitchDownloaderCLI
    if os.path.exists(chat_download_path):
        logger.info("Chat file already exists, skipping download")
    else:
        logger.info("Downloading chat...")
        chat_downloader_result = subprocess.run(twitch_chat_download_cmd,
                                                cwd=twitch_downloader_root,
                                                shell=True)
        if chat_downloader_result.returncode == 0:
            print()
            logger.info("Chat downloaded")
        else:
            logger.error("Chat download failed")
            sys.exit(-1)

    # Check if chat video already exists, and rerender if needed
    render_chat = (render_chat_as_overlay and
                   (not os.path.exists(mask_video_path)
                    or not os.path.exists(chat_video_path))) or (
                        not render_chat_as_overlay
                        and not os.path.exists(chat_video_path))
    if render_chat:
        logger.info("Rendering chat...")
        chat_render_result = subprocess.run(twitch_chat_render_cmd,
                                            cwd=twitch_downloader_root,
                                            shell=True)
        if chat_render_result.returncode == 0:
            logger.info("Chat rendered")
        else:
            logger.error("Chat render failed")
            sys.exit(-1)
    else:
        logger.info("Chat video already exists, skipping render")

    if os.path.exists(vod_download_path):
        logger.info("VOD already exists, skipping download")
    else:
        logger.info("Downloading VOD...")
        video_download_result = subprocess.run(twitch_video_download_cmd,
                                               shell=True,
                                               cwd=twitch_downloader_root)
        if video_download_result.returncode == 0:
            logger.info("VOD downloaded")
        else:
            logger.error("VOD download failed")
            sys.exit(-1)

    if os.path.exists(merged_video_path):
        logger.info(
            "Merged video already exists, are you sure you want to continue? This will overwrite the existing file."
        )
        confirm = input("Continue? (y/n): ")
        if confirm != "y":
            sys.exit(0)

    logger.info("Merging VOD and chat...")
    ffmpeg_merge_result = subprocess.run(ffmpeg_merge_cmd, shell=True)
    if ffmpeg_merge_result.returncode == 0:
        logger.info("VOD and chat merged")
    else:
        logger.error("VOD and chat merge failed")
        sys.exit(-1)

    logger.info("Done!")


if __name__ == "__main__":
    main()