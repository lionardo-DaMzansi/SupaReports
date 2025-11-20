# Manual Video Upload Feature

## Overview
Added the ability to manually upload pre-rendered videos to Panel 4 (Bring To Life), enabling users to work around timeout issues when TopView takes longer than expected to generate videos.

## Problem Solved

When video generation times out on the backend (e.g., for long scripts that take 60+ minutes to render), TopView may still be processing the video in the background. Users can now:

1. Download the completed video from TopView separately
2. Upload it manually to Supa Reports
3. Push it to the email template in Panel 5

## Implementation

### UI Addition (Panel 4 - Left Column)

Added new upload section after image upload:

```html
<!-- Manual Video Upload (for timeout cases) -->
<div class="form-section" style="margin-top: 2rem;">
    <div class="form-section-title">Or Upload Finished Video</div>
    <div class="form-group">
        <label>Select Video File</label>
        <input type="file" id="manualVideoUpload" class="compact-input" accept="video/*">
        <div class="help-text">Upload a pre-rendered video (if generation timed out)</div>
    </div>
</div>
```

### JavaScript Handler

```javascript
// Manual video upload handler
const manualVideoInput = document.getElementById('manualVideoUpload');
if (manualVideoInput) {
    manualVideoInput.addEventListener('change', async function(event) {
        const file = event.target.files[0];
        if (file) {
            // Create blob URL from uploaded file
            const videoBlob = new Blob([await file.arrayBuffer()], { type: file.type });
            const videoBlobUrl = URL.createObjectURL(videoBlob);

            // Store video URL for download and push to email
            currentVideoUrl = videoBlobUrl;

            // Update video source and show player
            videoSource.src = videoBlobUrl;
            videoPlayer.load();
            videoPlayer.style.display = 'block';
            videoPlaceholder.style.display = 'none';

            // Show action buttons (Expand, Download, Push to Email)
            expandBtn.style.display = 'block';
            downloadBtn.style.display = 'block';
            pushBtn.style.display = 'block';
        }
    });
}
```

## Expanded Video Modal - Close Functionality

The modal already has three ways to close:

### 1. X Button (Top Right)
```html
<span class="video-modal-close" onclick="closeVideoModal()">&times;</span>
```

Visual appearance:
- Large × symbol in top right corner
- White color, turns gold on hover
- Font size: 3rem (48px)
- Position: Absolute, top-right of modal

### 2. Click Outside Video
```javascript
document.getElementById('videoModal').addEventListener('click', function(e) {
    if (e.target === this) {
        closeVideoModal();
    }
});
```

### 3. ESC Key
```javascript
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeVideoModal();
    }
});
```

## User Workflow

### Scenario: Video Generation Times Out

**Step 1: Generation Timeout**
```
User clicks "Bring To Life" → Backend processes for estimated time → Timeout occurs
Message: "Your video is busy processing, please go make yourself a coffee..."
After timeout: "Video generation timed out. TopView may still be processing - check back later."
```

**Step 2: Retrieve Video from TopView**
- User logs into TopView dashboard separately
- Downloads the completed video file

**Step 3: Upload to Supa Reports**
1. Navigate back to Panel 4 in Supa Reports
2. Click "Select Video File" in "Or Upload Finished Video" section
3. Choose the downloaded .mp4 file
4. Video automatically loads in preview

**Step 4: Push to Email**
1. Click "Push to Email →" button
2. Video converts to GIF (first 5 seconds)
3. GIF appears in Panel 5 email template
4. Customize email and send

## Features

### Upload Capabilities
- ✅ Accepts any video format (video/*)
- ✅ Automatically creates blob URL for local playback
- ✅ No file size limit (handled client-side)
- ✅ Instant preview in video player
- ✅ Enables all action buttons (Expand, Download, Push to Email)

### Integration with Existing Features
- ✅ **Expand**: Opens full-screen modal with video
- ✅ **Download**: Downloads the uploaded video
- ✅ **Push to Email**: Converts video to GIF and pushes to Panel 5
- ✅ Works identically to API-generated videos

### Modal Close Options
- ✅ **X Button**: Top-right close button
- ✅ **Click Outside**: Click dark background to close
- ✅ **ESC Key**: Press Escape to close

## Use Cases

### Use Case 1: Long Script (2+ minutes)
```
Audio: 120 seconds
Expected processing: 108 minutes (1.8 hours)
Timeout: 118 minutes

If timeout occurs:
1. Check TopView dashboard after 2 hours
2. Download completed video
3. Upload to Panel 4 using "Or Upload Finished Video"
4. Continue workflow normally
```

### Use Case 2: External Video Creation
```
User creates lipsync video using different tool (D-ID, Synthesia, etc.)
1. Download video from external tool
2. Upload to Panel 4 in Supa Reports
3. Push to email template
4. Use Supa Reports email workflow
```

### Use Case 3: Pre-rendered Video Library
```
User has library of pre-rendered brand spokesperson videos
1. Select appropriate video for campaign
2. Upload to Panel 4
3. Push to email template for campaign distribution
```

## Technical Details

### File Handling
```javascript
// Convert File to Blob with proper MIME type
const videoBlob = new Blob([await file.arrayBuffer()], { type: file.type });

// Create blob URL for local playback
const videoBlobUrl = URL.createObjectURL(videoBlob);

// Store globally for other functions
currentVideoUrl = videoBlobUrl;
```

### Video Player Update
```javascript
// Update video source
videoSource.src = videoBlobUrl;
videoPlayer.load();

// Show player, hide placeholder
videoPlayer.style.display = 'block';
videoPlaceholder.style.display = 'none';
```

### Button States
```javascript
// Enable all action buttons
expandBtn.style.display = 'block';      // ⛶ Expand
downloadBtn.style.display = 'block';    // Download Video
pushBtn.style.display = 'block';        // Push to Email →
```

## Location in Code

### HTML
- **File**: `/Users/willpandle/supachat-azi-local/static/index.html`
- **Lines**: 1498-1506

### JavaScript
- **File**: `/Users/willpandle/supachat-azi-local/static/index.html`
- **Lines**: 2311-2350

### Modal Close Functionality
- **X Button HTML**: Line 1655
- **Click Outside**: Lines 2615-2619
- **ESC Key**: Lines 2622-2626
- **Close Function**: Lines 2603-2612

## Testing

### Test 1: Upload Video
1. Navigate to Panel 4
2. Click "Select Video File" in "Or Upload Finished Video"
3. Select any .mp4 file
4. ✓ Video should appear in preview
5. ✓ Expand, Download, Push to Email buttons should appear

### Test 2: Expand Video
1. Upload a video (Test 1)
2. Click "⛶ Expand" button
3. ✓ Full-screen modal should open
4. ✓ Video should auto-play
5. ✓ X button visible in top-right

### Test 3: Close Expanded Video - X Button
1. Expand video (Test 2)
2. Click X button in top-right corner
3. ✓ Modal should close
4. ✓ Video should stop playing

### Test 4: Close Expanded Video - Click Outside
1. Expand video (Test 2)
2. Click dark background area (not on video)
3. ✓ Modal should close
4. ✓ Video should stop playing

### Test 5: Close Expanded Video - ESC Key
1. Expand video (Test 2)
2. Press ESC key on keyboard
3. ✓ Modal should close
4. ✓ Video should stop playing

### Test 6: Push to Email
1. Upload a video (Test 1)
2. Click "Push to Email →" button
3. ✓ Should show processing message
4. ✓ GIF should appear in Panel 5 email template
5. ✓ Email preview should update with GIF

## Benefits

✅ **Workaround for Timeouts**: Users can continue workflow even if API times out
✅ **External Video Support**: Accept videos from any source
✅ **Seamless Integration**: Works identically to API-generated videos
✅ **User-Friendly**: Simple file upload interface
✅ **Multiple Close Options**: X button, click outside, ESC key
✅ **No Server Changes**: Purely client-side implementation

## Server Status

✅ Flask server running at: http://localhost:5173
✅ Feature ready to test!

## Files Modified

1. `/Users/willpandle/supachat-azi-local/static/index.html`
   - Added video upload input (lines 1498-1506)
   - Added upload handler (lines 2311-2350)
   - Existing modal close functionality (lines 1655, 2615-2626)
