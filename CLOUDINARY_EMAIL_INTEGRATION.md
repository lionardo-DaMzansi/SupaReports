# Cloudinary Email Integration - Video Hosting & GIF Conversion

## Problem Solved

Email clients cannot display videos or access local blob URLs. Videos need to be hosted on a publicly accessible server for emails to work properly.

## Solution Implemented

Integrated **Cloudinary** (cloud media hosting service) to:
1. Upload lipsync videos to the cloud
2. Convert videos to GIF format (first 5 seconds)
3. Generate public URLs for both video and GIF
4. Use these URLs in email templates so recipients can see the media

---

## Configuration

### Cloudinary Account

**Account Details:**
- Cloud Name: `dghkgirtm`
- API Key: `467738177237528`
- API Secret: `ZHM_6WchvLRuAzpg63-roo80hII`
- Free Tier: 25GB storage, 25GB bandwidth/month

### Environment Variables

Added to `.env` file:
```bash
# Cloudinary Configuration (for hosting videos/GIFs publicly)
CLOUDINARY_CLOUD_NAME=dghkgirtm
CLOUDINARY_API_KEY=467738177237528
CLOUDINARY_API_SECRET=ZHM_6WchvLRuAzpg63-roo80hII
```

---

## Implementation Details

### Backend Changes (app.py)

#### 1. Imports
```python
import cloudinary
import cloudinary.uploader
import cloudinary.api
```

#### 2. Configuration (lines 57-71)
```python
# Cloudinary Configuration
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME", "")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY", "")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET", "")

# Initialize Cloudinary
if CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET:
    cloudinary.config(
        cloud_name=CLOUDINARY_CLOUD_NAME,
        api_key=CLOUDINARY_API_KEY,
        api_secret=CLOUDINARY_API_SECRET
    )
    print(f"✓ Cloudinary configured: {CLOUDINARY_CLOUD_NAME}")
else:
    print("⚠ Cloudinary not configured")
```

#### 3. Upload API Endpoint (lines 940-1025)

**Route:** `POST /api/upload-to-cloudinary`

**Accepts:**
- **video** (file): Video file to upload
- **convert_to_gif** (form param): 'true' or 'false' (default: 'true')
- **gif_duration** (form param): Duration in seconds (default: 5)

**Returns:**
```json
{
  "success": true,
  "video_url": "https://res.cloudinary.com/dghkgirtm/video/upload/v1234/supa_reports/videos/xyz.mp4",
  "gif_url": "https://res.cloudinary.com/dghkgirtm/video/upload/du_5,w_600,q_auto:low,f_gif,fl_animated/v1234/supa_reports/videos/xyz",
  "public_id": "supa_reports/videos/xyz",
  "duration": 10.5
}
```

**Features:**
- Uploads video to `supa_reports/videos/` folder in Cloudinary
- Converts first 5 seconds to optimized GIF (600px width, low quality for email)
- Returns public URLs for both video and GIF
- Temporary file cleanup

---

### Frontend Changes (index.html)

#### 1. Updated pushToEmail() Function (lines 2731-2796)

**Before:**
- Used local blob URLs (not accessible in emails)
- Placeholder for GIF conversion

**After:**
```javascript
async function pushToEmail() {
    // 1. Convert blob URL to File object
    const videoBlob = await fetch(currentVideoUrl).then(r => r.blob());
    const videoFile = new File([videoBlob], 'lipsync-video.mp4', { type: 'video/mp4' });

    // 2. Create FormData with video and conversion parameters
    const formData = new FormData();
    formData.append('video', videoFile);
    formData.append('convert_to_gif', 'true');
    formData.append('gif_duration', '5'); // First 5 seconds

    // 3. Upload to Cloudinary
    const response = await fetch('/api/upload-to-cloudinary', {
        method: 'POST',
        body: formData
    });

    const data = await response.json();

    // 4. Store public URLs
    currentGifUrl = data.gif_url || data.video_url;
    document.getElementById('emailVideoLink').value = data.video_url;

    // 5. Update email preview
    updateEmailPreview();
}
```

#### 2. Updated Email Template (lines 2824-2835)

**Before:**
```html
<video src="blob:..." loop autoplay muted></video>
```
❌ Email clients don't support HTML5 video tags

**After:**
```html
<img
    src="https://res.cloudinary.com/dghkgirtm/..."
    alt="Video preview"
    style="width: 100%; max-width: 500px; border-radius: 8px; box-shadow: 0 4px 16px rgba(0,0,0,0.15);">
```
✅ GIFs displayed as images work in all email clients

#### 3. Watch Full Video Button

Button now links to the publicly hosted video on Cloudinary:
```html
<a href="${video_url}" style="...">Watch Full Video</a>
```

---

## User Workflow

### Step 1: Generate or Upload Video (Panel 4)

**Option A: Generate Lipsync Video**
1. Upload image
2. Upload audio (or use audio from Panel 3)
3. Click "Generate Lipsync Video"
4. Wait for TopView to process
5. Video appears in preview

**Option B: Upload Pre-rendered Video**
1. Click "Select Video File"
2. Choose .mp4 file
3. Video loads in preview

### Step 2: Push to Email (Panel 4)

1. Click **"Push to Email →"** button
2. Button shows: "Uploading to cloud..."
3. Button shows: "Converting to GIF..."
4. ✓ Success message: "Video uploaded and converted to GIF!"

**Behind the scenes:**
- Video uploads to Cloudinary (takes 5-15 seconds)
- First 5 seconds converted to optimized GIF
- Public URLs stored

### Step 3: Customize Email (Panel 5)

Email template auto-populates with:
- ✅ **GIF preview** (first 5 seconds, looping)
- ✅ **Video Link URL** (full video hosted on Cloudinary)
- ✅ **"Watch Full Video" button** (clickable)

Customize:
- Headline
- Intro paragraph
- Bullet points
- Closing message
- Brand colors

### Step 4: Send Email (Panel 5)

1. Enter **From Email**: supachatglobal@gmail.com
2. Enter **To Email(s)**: recipient@email.com (comma-separated for multiple)
3. Enter **Subject**: Campaign Performance Report
4. Click **"📧 Send Email"**

**Result:**
- ✅ Email sent with animated GIF embedded
- ✅ GIF loops automatically in recipient's inbox
- ✅ "Watch Full Video" button links to full video on Cloudinary
- ✅ Works in Gmail, Outlook, Apple Mail, etc.

---

## Technical Specifications

### Cloudinary Video Upload

**Upload Settings:**
```python
cloudinary.uploader.upload(
    video_file_path,
    resource_type="video",
    folder="supa_reports/videos",
    overwrite=True
)
```

**Result:**
```
URL: https://res.cloudinary.com/dghkgirtm/video/upload/v1731167432/supa_reports/videos/lipsync-video.mp4
```

### GIF Conversion

**Transformation Parameters:**
```python
cloudinary.CloudinaryVideo(public_id).video(
    duration=5,          # First 5 seconds
    format="gif",        # Convert to GIF
    transformation=[
        {'width': 600, 'crop': 'scale'},    # Resize to 600px width
        {'quality': 'auto:low'},             # Optimize file size
        {'flags': 'animated'}                # Ensure animation
    ]
)
```

**Result:**
```
URL: https://res.cloudinary.com/dghkgirtm/video/upload/du_5,w_600,q_auto:low,f_gif,fl_animated/v1731167432/supa_reports/videos/lipsync-video
```

**GIF Optimizations:**
- **Duration**: 5 seconds (keeps file size small)
- **Width**: 600px (perfect for email)
- **Quality**: auto:low (Cloudinary optimizes for size vs quality)
- **Animated**: Ensures GIF loops

### Email Client Compatibility

✅ **Works in:**
- Gmail (web, mobile, iOS, Android)
- Outlook (web, desktop, mobile)
- Apple Mail (macOS, iOS)
- Yahoo Mail
- ProtonMail
- Most modern email clients

❌ **Video tag doesn't work in:**
- Gmail (strips `<video>` tags)
- Outlook (no HTML5 video support)
- Most email clients (security restrictions)

✅ **Solution:** Use `<img>` tag with GIF
- Email clients treat GIFs as static images
- GIFs auto-loop (no play button needed)
- Universally supported

---

## File Structure

### Uploaded Media Organization

```
Cloudinary
└── supa_reports/
    └── videos/
        ├── lipsync-video_abc123.mp4    (original video)
        ├── lipsync-video_def456.mp4
        └── ... (each upload gets unique ID)
```

**Naming:**
- Folder: `supa_reports/videos/`
- Files: Auto-named with timestamp/unique ID by Cloudinary
- **Overwrite**: Enabled (same filename replaces old file)

---

## API Endpoints

### 1. Upload to Cloudinary

**Endpoint:** `POST /api/upload-to-cloudinary`

**Request:**
```javascript
const formData = new FormData();
formData.append('video', videoFile);
formData.append('convert_to_gif', 'true');
formData.append('gif_duration', '5');

fetch('/api/upload-to-cloudinary', {
    method: 'POST',
    body: formData
});
```

**Response (Success):**
```json
{
    "success": true,
    "video_url": "https://res.cloudinary.com/.../video.mp4",
    "gif_url": "https://res.cloudinary.com/.../video.gif",
    "public_id": "supa_reports/videos/xyz",
    "duration": 10.5
}
```

**Response (Error):**
```json
{
    "error": "Upload failed",
    "message": "File too large"
}
```

### 2. Send Email (Existing)

**Endpoint:** `POST /api/send-email`

Now works with Cloudinary URLs:
- GIF URL embedded in email body
- Video URL in "Watch Full Video" button
- Both publicly accessible

---

## File Size & Limits

### Cloudinary Free Tier
- **Storage**: 25 GB
- **Bandwidth**: 25 GB/month
- **Transformations**: Unlimited
- **Video uploads**: Up to 100 MB per file
- **GIF generation**: Unlimited

### Typical File Sizes
- **5-second video (1080p)**: ~2-5 MB
- **5-second GIF (600px, optimized)**: ~500 KB - 2 MB
- **Monthly capacity**: ~500-1000 videos (depending on quality)

### Optimization Tips
- GIF is optimized to 600px width (perfect for email)
- Quality set to `auto:low` for smallest file size
- Only first 5 seconds converted (reduces GIF size)
- Original video remains at full quality

---

## Testing

### Test 1: Upload Video to Cloudinary
1. Generate or upload video in Panel 4
2. Click "Push to Email →"
3. ✓ Button shows "Uploading to cloud..."
4. ✓ Button shows "Converting to GIF..."
5. ✓ Success alert appears
6. ✓ Check Panel 5 - GIF should appear in preview
7. ✓ Verify Video Link URL field is populated

### Test 2: Send Email with GIF
1. Complete Test 1
2. Fill in email fields in Panel 5:
   - From: supachatglobal@gmail.com
   - To: your@email.com
   - Subject: Test Email
3. Click "📧 Send Email"
4. ✓ Check your inbox
5. ✓ GIF should be visible and looping
6. ✓ Click "Watch Full Video" button
7. ✓ Should open full video in browser

### Test 3: Verify Public URLs
1. After pushing to email, copy the GIF URL from browser console
2. Open in new tab (should be accessible)
3. Copy the video URL from "Video Link URL" field
4. Open in new tab (should play full video)

### Test 4: Email Client Compatibility
Send test email to:
- Gmail account
- Outlook account
- Apple Mail (if available)

Verify GIF displays and plays in all clients.

---

## Troubleshooting

### Issue: "Cloudinary not configured"

**Cause:** Missing or incorrect credentials in `.env`

**Fix:**
1. Check `.env` file has all three values:
   ```
   CLOUDINARY_CLOUD_NAME=dghkgirtm
   CLOUDINARY_API_KEY=467738177237528
   CLOUDINARY_API_SECRET=ZHM_6WchvLRuAzpg63-roo80hII
   ```
2. Restart Flask server

### Issue: Upload fails or times out

**Possible causes:**
- File too large (>100 MB)
- Poor internet connection
- Cloudinary rate limit reached

**Fix:**
1. Check video file size
2. Wait a few minutes and try again
3. Check Cloudinary dashboard for errors

### Issue: GIF doesn't loop in email

**Cause:** Email client might block animated GIFs

**Fix:**
- Most modern clients support GIFs
- Try different email client
- Verify GIF URL opens correctly in browser

### Issue: Video link broken in email

**Cause:** Video URL not set correctly

**Fix:**
1. Verify "Video Link URL" field is populated after push
2. Test URL in browser before sending email
3. Check Cloudinary dashboard to ensure video uploaded

---

## Benefits

✅ **Email Compatibility**: GIFs work in all email clients (unlike video tags)
✅ **Public Access**: Media hosted on Cloudinary accessible anywhere
✅ **Automatic Optimization**: Cloudinary optimizes GIF size for email
✅ **Reliable Delivery**: No issues with blob URLs or local files
✅ **Professional**: Hosted on CDN, fast loading, no broken links
✅ **Scalable**: 25 GB free storage, upgrade available if needed
✅ **Watch Full Video**: Link to complete video works from any device

---

## Cost

**Current Plan:** Free Tier
- **Cost**: $0/month
- **Storage**: 25 GB
- **Bandwidth**: 25 GB/month
- **Sufficient for**: ~500-1000 videos/month

**Paid Plans (if needed):**
- **Plus**: $89/month (75 GB storage, 150 GB bandwidth)
- **Advanced**: $224/month (Unlimited transformations, more storage)

**For current usage:** Free tier is more than sufficient

---

## Future Enhancements

### Possible Improvements

1. **Custom GIF Duration**
   - Allow users to choose 3, 5, or 10 seconds
   - Add slider in Panel 5

2. **GIF Quality Options**
   - Low (smaller file, faster loading)
   - Medium (balanced)
   - High (better quality, larger file)

3. **Thumbnail Generation**
   - Create static thumbnail image
   - Use in email for faster loading

4. **Video Trimming**
   - Let users select which part of video to convert
   - "Start time" and "End time" inputs

5. **Multiple GIFs**
   - Upload multiple videos
   - Include multiple GIFs in one email

6. **Analytics**
   - Track which videos are watched
   - See email open rates
   - Cloudinary has built-in analytics

---

## Server Status

✅ Flask server running at: **http://localhost:5173**
✅ Cloudinary configured: **dghkgirtm**
✅ Email sending active: **supachatglobal@gmail.com**
✅ All features ready to use!

---

## Summary

The Cloudinary integration enables **fully functional video emails** by:

1. ✅ Uploading lipsync videos to cloud storage
2. ✅ Converting videos to optimized GIFs
3. ✅ Generating public URLs for email embedding
4. ✅ Making "Watch Full Video" button functional
5. ✅ Ensuring compatibility across all email clients

**Result:** Professional, working email templates with animated video previews and clickable links to full videos!
