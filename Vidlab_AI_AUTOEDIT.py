import os
import cv2
import moviepy.editor as mpe
import numpy as np
from moviepy.video.fx.all import resize
from PySceneDetect import VideoManager, SceneManager
from PySceneDetect.detectors import ContentDetector
from whisper import load_model
import mediapipe as mp


class AutoEdit:
    def __init__(self, logo_path: str):
        self.logo_path = logo_path
        self.logo_img = cv2.imread(logo_path, cv2.IMREAD_UNCHANGED)
        if self.logo_img is None:
            raise FileNotFoundError(f"Logo file not found: {logo_path}")
        self.mp_selfie_segmentation = mp.solutions.selfie_segmentation.SelfieSegmentation(model_selection=1)

    def detect_scenes(self, video_path: str):
        video_manager = VideoManager([video_path])
        scene_manager = SceneManager()
        scene_manager.add_detector(ContentDetector())

        video_manager.start()
        scene_manager.detect_scenes(frame_source=video_manager)
        scene_list = scene_manager.get_scene_list()
        video_manager.release()

        return scene_list

    def transcribe_audio(self, video_path: str):
        model = load_model("base")  # 使用Whisper base模型
        result = model.transcribe(video_path)
        return result['text']

    def apply_logo(self, clip: mpe.VideoFileClip):
        logo_clip = mpe.ImageClip(self.logo_path).set_duration(clip.duration)

        # 计算logo放置位置：top middle
        video_w, video_h = clip.size
        logo_w, logo_h = logo_clip.size

        pos_x = (video_w - logo_w) / 2
        pos_y = 10  # 距离顶部10px

        return mpe.CompositeVideoClip([clip, logo_clip.set_pos((pos_x, pos_y))])

    def segment_human(self, frame: np.ndarray):
        # 使用MediaPipe人像分割
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.mp_selfie_segmentation.process(img_rgb)
        mask = results.segmentation_mask
        if mask is None:
            return frame
        condition = mask > 0.1
        bg_img = np.zeros(frame.shape, dtype=np.uint8)
        output_img = np.where(condition[..., None], frame, bg_img)
        return output_img

    def autoedit_footage(self, input_video_path: str, output_path: str):
        # 1. 镜头切割
        scenes = self.detect_scenes(input_video_path)

        clips = []
        video = mpe.VideoFileClip(input_video_path)

        for start, end in scenes:
            clip = video.subclip(start.get_seconds(), end.get_seconds())

            # 2. 这里可以调用segment_human对每帧做人像分割（如果需要）
            # 但这里为了示范只简单添加Logo

            # 3. 添加Logo
            clip = self.apply_logo(clip)

            clips.append(clip)

        # 拼接所有剪辑片段
        final_clip = mpe.concatenate_videoclips(clips)

        # 输出视频
        final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')

        # 4. 音频转录
        transcript = self.transcribe_audio(input_video_path)

        return transcript, output_path


# 作为独立函数调用示范

def autoedit_footage(input_video_path: str, m_code: str):
    logo_path = '/Users/gggcapital/Desktop/VIDLAB PROJECT/final_data/script/ASSETS/COMPANY LOGO/GGG2.png'  # 你实际logo路径
    output_path = f'./Final Video (V CODE)/{m_code}_VCODE_output.mp4'

    editor = AutoEdit(logo_path)
    transcript, out_file = editor.autoedit_footage(input_video_path, output_path)

    print(f'自动剪辑完成，输出文件: {out_file}')
    print(f'转录内容: {transcript[:100]}...')

    # 返回V_CODE和输出文件路径
    v_code = f'{m_code}_VCODE'
    return v_code, out_file


# 简单测试示范
if __name__ == '__main__':
    test_video_path = './Footage (M CODE)/test_footage.mp4'
    v_code, out_path = autoedit_footage(test_video_path, 'TEST_M0001')
    print(f'Test output: V_CODE={v_code}, path={out_path}')
