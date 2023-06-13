import os
import pytesseract
from gtts import gTTS
from moviepy.editor import TextClip, concatenate_videoclips, AudioFileClip, ImageClip, CompositeVideoClip

# Set the path to the Tesseract OCR executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

video_width = 1080
video_height = 720
output_file = "ocr_result.txt"

def ocr_directory(directory):
    concatenated_text = ''
    for filename in os.listdir(directory):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            image_path = os.path.join(directory, filename)
            text = pytesseract.image_to_string(image_path)
            concatenated_text += text + '\n'
    return concatenated_text

# Prompt the user to enter the image directory
image_directory = input("Enter the location of the directory: ")
if image_directory == "":
    image_directory = "./images"

# Perform OCR on the images in the directory
result = ocr_directory(image_directory)

# Save the concatenated text to a file
with open(output_file, 'w') as file:
    file.write(f"Please fix and summarize this in about 500 words or more possible: \n{result}")

print("OCR completed. Result saved in", output_file)
print("Paste the response that you get after pasting the response into ChatGPT in the ocr_result.txt file")
_ = input("Please press Enter when done: ")
with open(file=output_file, mode="r") as file:
    result = file.read()

print("Creating...")

# Split the concatenated text into chunks of 500 words
words_per_slide = 100
words = result.split()
chunks = [' '.join(words[i:i + words_per_slide]) for i in range(0, len(words), words_per_slide)]

# Create video clips with the non-empty text chunks
clips = []
audio_start_time = 0  # Start time of the audio for each slide
temp_audio_files = []

for i, chunk in enumerate(chunks):
    if chunk.strip():
        # Generate audio from the text chunk
        audio_file = f"temp_audio_{i}.mp3"
        tts = gTTS(chunk, lang='en')
        tts.save(audio_file)

        # Load the audio file as an AudioFileClip
        audio = AudioFileClip(audio_file)

        temp_audio_files.append(audio_file)

        # Create the video clip with the text chunk
        text_clip = TextClip(chunk, fontsize=30, font="Georgia", color='black', bg_color='transparent', size=(video_height, None), method='caption', align='center')
        text_clip = text_clip.set_duration(audio.duration)

        # Set the audio for the video clip
        video_clip = CompositeVideoClip([text_clip.set_position('center')], size=(video_width, video_height)).set_audio(audio)

        clips.append(video_clip.set_start(audio_start_time))

        # Update the start time for the next slide
        audio_start_time += audio.duration

# Concatenate the video clips
final_video = concatenate_videoclips(clips, method="compose")

# Load the background image
bg_image = ImageClip("./background.jpg", duration=final_video.duration).resize(height=video_height, width=video_width)

# Set the background image
final_video = CompositeVideoClip([bg_image, final_video])

# Set the output video file name
output_video_file = "output_video.mp4"

# Export the final video
final_video.write_videofile(output_video_file, codec='libx264', fps=1)

for audio_file in temp_audio_files:
    os.remove(audio_file)

print("Video creation completed. Result saved in", output_video_file)
