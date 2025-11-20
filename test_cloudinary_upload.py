#!/usr/bin/env python3
"""Test Cloudinary upload endpoint"""
import requests
import os
import tempfile
import subprocess

print("=" * 60)
print("Testing Cloudinary Upload Endpoint")
print("=" * 60)
print()

# Create a simple test video using FFmpeg (if available)
print("Step 1: Creating test video file...")
try:
    # Create a 2-second test video (black screen)
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video:
        video_path = temp_video.name

    # Use ffmpeg to create a simple 2-second black video
    result = subprocess.run([
        'ffmpeg', '-f', 'lavfi', '-i', 'color=c=black:s=640x480:d=2',
        '-c:v', 'libx264', '-t', '2', '-pix_fmt', 'yuv420p',
        video_path, '-y'
    ], capture_output=True, text=True, timeout=10)

    if result.returncode != 0:
        print(f"❌ Failed to create video: {result.stderr}")
        exit(1)

    file_size = os.path.getsize(video_path)
    print(f"✓ Test video created: {video_path}")
    print(f"  Size: {file_size / 1024:.2f} KB")
    print()

    # Test upload to Cloudinary
    print("Step 2: Uploading to Cloudinary...")
    with open(video_path, 'rb') as f:
        files = {'video': ('test-video.mp4', f, 'video/mp4')}
        data = {
            'convert_to_gif': 'true',
            'gif_duration': '2'  # Use full 2 seconds
        }

        response = requests.post(
            'http://localhost:5173/api/upload-to-cloudinary',
            files=files,
            data=data,
            timeout=60
        )

    print(f"Response Status: {response.status_code}")
    print()

    if response.status_code == 200:
        data = response.json()
        print("✅ SUCCESS! Upload completed:")
        print(f"  Video URL: {data.get('video_url', 'N/A')}")
        print(f"  GIF URL: {data.get('gif_url', 'N/A')}")
        print(f"  Public ID: {data.get('public_id', 'N/A')}")
        print(f"  Duration: {data.get('duration', 'N/A')} seconds")
        print()
        print("=" * 60)
        print("✓ Cloudinary integration is working correctly!")
        print("=" * 60)
    else:
        error_data = response.json()
        print(f"❌ ERROR: {error_data.get('error', 'Unknown error')}")
        print(f"  Message: {error_data.get('message', 'No message')}")
        print()
        print("Check server logs for more details.")

    # Clean up
    os.unlink(video_path)

except subprocess.TimeoutExpired:
    print("❌ FFmpeg command timed out")
except FileNotFoundError:
    print("❌ FFmpeg not found. Please install FFmpeg to run this test.")
    print("   Install: brew install ffmpeg (on macOS)")
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
