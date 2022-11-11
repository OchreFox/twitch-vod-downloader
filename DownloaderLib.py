import configparser
import os
import sys
import logging
from typing import Union
from urllib.parse import urlparse

logger = logging.getLogger("Downloader")
config = configparser.ConfigParser()
config.read('config.ini')


def create_folder(folder_path):
    if not os.path.exists(folder_path):
        logger.info("Creating folder: " + folder_path)
        os.makedirs(folder_path)


def parse_twitch_vod(twitch_vod):
    if twitch_vod.startswith("https://www.twitch.tv/videos/"):
        # Remove query string from url
        twitch_vod = urlparse(twitch_vod).path
        twitch_vod = twitch_vod.replace("/videos/", "")
        print("VOD ID: " + twitch_vod)
        # twitch_vod = twitch_vod.replace("https://www.twitch.tv/videos/", "")
        # twitch_vod = twitch_vod.split("?")[0]
        return twitch_vod
    else:
        logger.error("Invalid Twitch VOD URL")
        sys.exit(-1)


def get_overlay_command(overlay_position: int) -> Union[str, None]:
    # 0 = Top Left
    # 1 = Top Right
    # 2 = Bottom Left
    # 3 = Bottom Right
    # 4 = Left
    # 5 = Right
    if overlay_position == 0:
        ffmpeg_overlay = "overlay=0:0"
    elif overlay_position == 1:
        ffmpeg_overlay = "overlay=x=main_w-overlay_w:y=0"
    elif overlay_position == 2:
        ffmpeg_overlay = "overlay=0:main_h-overlay_h"
    elif overlay_position == 3:
        ffmpeg_overlay = "overlay=main_w-overlay_w:main_h-overlay_h"
    elif overlay_position == 4:
        ffmpeg_overlay = "overlay=x=(main_w-overlay_w)/2:y=0"
    elif overlay_position == 5:
        ffmpeg_overlay = "overlay=x=(main_w-overlay_w)/2:y=main_h-overlay_h"
    else:
        logger.error("Invalid overlay position")
        sys.exit(-1)
    return ffmpeg_overlay


def get_ffmpeg_merge_command(vod_download_path: str, chat_video_path: str,
                             mask_video_path: str,
                             merged_video_path: str) -> str:
    render_chat_as_overlay = config['Application'].getboolean(
        'RenderChatAsOverlay')
    output_width = config['Application']['OutputWidth']
    output_height = config['Application']['OutputHeight']
    chat_width = "--chat-width " + config['TwitchDownloader']['ChatWidth']
    quality_preset = config['Application']['QualityPreset']
    # FFmpeg config
    input_params_1 = config['FFmpeg']['InputParams1']
    input_params_2 = config['FFmpeg']['InputParams2']
    overlay_position = config['Application'].getint('OverlayPosition')

    ffmpeg_path = os.path.join(os.getcwd(),
                               config['Application']['FFmpegPath'])

    ffmpeg_overlay = get_overlay_command(overlay_position)

    if render_chat_as_overlay:
        if quality_preset == "Fast":
            output_params = config['FFmpeg']['OutputParamsOverlay']
        elif quality_preset == "Best":
            output_params = config['FFmpeg']['OutputParamsOverlayYUV']
        else:
            logger.error("Invalid quality preset")
            sys.exit(-1)
        output_params = output_params.replace(
            "&output_height", output_height).replace(
                "&background_alpha",
                str(config['TwitchDownloader'].getfloat(
                    'BackgroundOpacity'))).replace("&overlay", ffmpeg_overlay)

        ffmpeg_merge_cmd = f"{ffmpeg_path} {input_params_1} -i {vod_download_path} {input_params_2} -i {chat_video_path} -i {mask_video_path} {output_params} {merged_video_path}"
    else:
        adjusted_output_width = int(output_width) - int(chat_width)
        output_params = config['FFmpeg']['OutputParams'].replace(
            "&output_height",
            output_height).replace("&output_width", output_width).replace(
                "&adjusted_output_width", adjusted_output_width)
        ffmpeg_merge_cmd = f"{ffmpeg_path} {input_params_1} -i {vod_download_path} {input_params_2} -i {chat_video_path} {output_params} {merged_video_path}"
    return ffmpeg_merge_cmd