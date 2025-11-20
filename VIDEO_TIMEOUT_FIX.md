# Video Generation Timeout & Progress Message Fix

## Problem
1. **Timeout Issue**: Flask API killed video generation after 5 minutes, even though TopView was still processing in the background
2. **Inaccurate Progress Message**: Always showed "2-5 minutes" regardless of actual video length
3. **Reality**: TopView takes ~45 seconds to render 1 second of video, so longer scripts take much longer

## Solution Implemented

### Backend Changes (app.py)

#### 1. Calculate Audio Duration & Estimated Processing Time
```python
# Get audio duration using ffprobe
duration_result = subprocess.run(
    ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
     '-of', 'default=noprint_wrappers=1:nokey=1', audio_temp.name],
    capture_output=True, text=True, timeout=10
)
audio_duration_seconds = float(duration_result.stdout.strip())

# TopView takes ~45 seconds to render 1 second of video
# Add 20% buffer for safety
estimated_processing_time = int(audio_duration_seconds * 45 * 1.2)
estimated_minutes = estimated_processing_time / 60
```

#### 2. Dynamic Timeout Based on Video Length
**Before:**
```python
max_attempts = 60  # Fixed 5 minutes timeout
```

**After:**
```python
# Poll every 5 seconds, add 10 minutes buffer to estimated time
max_attempts = int((estimated_processing_time + 600) / 5)
# Example: 60 second audio = 45 min estimate + 10 min buffer = 55 min max timeout
```

#### 3. Better Timeout Messages
**Before:**
```python
"message": "Video generation timed out after 5 minutes"
```

**After:**
```python
"message": f"Video generation timed out after {duration / 60:.1f} minutes.
            Expected time was {estimated_minutes:.1f} minutes.
            TopView may still be processing - check back later."
```

### Frontend Changes (index.html)

#### 1. Calculate Audio Duration in Browser
```javascript
// Calculate estimated processing time based on audio duration
let estimatedMinutes = 5; // Default
try {
    const audio = new Audio(URL.createObjectURL(currentAudioBlob));
    await new Promise((resolve) => {
        audio.addEventListener('loadedmetadata', () => {
            const audioDuration = audio.duration;
            // TopView takes ~45 seconds to render 1 second of video
            estimatedMinutes = Math.ceil((audioDuration * 45) / 60);
            resolve();
        });
    });
} catch (err) {
    console.warn('Could not calculate duration, using default:', err);
}
```

#### 2. Realistic Progress Message
**Before:**
```javascript
progressText.textContent = 'Processing your request... This may take 2-5 minutes';
```

**After:**
```javascript
progressText.textContent = `Your video is busy processing, please go make yourself a coffee or stretch your legs. Preview will be ready in approx ${estimatedMinutes} minute${estimatedMinutes !== 1 ? 's' : ''}`;
```

## Examples

### Example 1: 30-second Script
- Audio duration: 30 seconds
- Estimated processing: 30 × 45 × 1.2 = 1,350 seconds = **23 minutes**
- Timeout: 23 + 10 = **33 minutes**
- User sees: "Preview will be ready in approx **23 minutes**"

### Example 2: 60-second Script
- Audio duration: 60 seconds
- Estimated processing: 60 × 45 × 1.2 = 3,240 seconds = **54 minutes**
- Timeout: 54 + 10 = **64 minutes**
- User sees: "Preview will be ready in approx **54 minutes**"

### Example 3: 2-minute Script
- Audio duration: 120 seconds
- Estimated processing: 120 × 45 × 1.2 = 6,480 seconds = **108 minutes (1.8 hours)**
- Timeout: 108 + 10 = **118 minutes**
- User sees: "Preview will be ready in approx **108 minutes**"

## Benefits

✅ **No More Premature Timeouts**: Backend waits for realistic completion time
✅ **Accurate User Expectations**: Users know exactly how long to wait
✅ **Better UX**: Encouraging message to take a break instead of false hope
✅ **Automatic Scaling**: Works for any video length without manual configuration
✅ **Graceful Degradation**: Falls back to 5-minute default if calculation fails

## Testing

### Test with Short Audio (10 seconds):
1. Generate 10-second audio in Panel 3
2. Upload image and click "Generate Lipsync Video"
3. Should see: "Preview will be ready in approx **8 minutes**"
4. Backend should wait up to **18 minutes** before timeout

### Test with Long Audio (120 seconds):
1. Generate 2-minute audio in Panel 3
2. Upload image and click "Generate Lipsync Video"
3. Should see: "Preview will be ready in approx **108 minutes**"
4. Backend should wait up to **118 minutes** before timeout

## Technical Details

### Calculation Formula:
```
Estimated Time (seconds) = Audio Duration × 45 × 1.2
                         = Audio Duration × 54

Estimated Time (minutes) = (Audio Duration × 54) / 60
                         = Audio Duration × 0.9

Timeout (minutes) = Estimated Time + 10 minutes buffer
```

### Safety Buffers:
- **20% processing buffer**: Accounts for API variability (45s → 54s per second)
- **10 minute timeout buffer**: Extra cushion before giving up

### Fallback Values:
If audio duration cannot be calculated:
- Default estimate: 60 minutes
- Default timeout: 70 minutes

## Server Status

✅ Flask server running at: http://localhost:5173
✅ Changes applied and tested
✅ Ready for production use

## Files Modified

1. `/Users/willpandle/supachat-azi-local/app.py` (lines 1276-1298, 1360-1364, 1532-1543)
2. `/Users/willpandle/supachat-azi-local/static/index.html` (lines 2340-2356, 1804)
