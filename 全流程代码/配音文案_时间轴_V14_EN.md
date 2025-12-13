# Sobel V14 Script - Timeline Version (English)

## Time Calculation Notes

- **slow_wait(time)**: Actual wait time = time × 2.0
- **slow_play(animation, base_run_time)**: Actual animation duration = base_run_time × 2.0
- **hud.show(text, wait_after)**: wait_after is direct wait time (not doubled)
- **ask_question()**: Uses slow_wait internally, wait time is doubled

**Time Format**: `[Scene Start Time] Cumulative Time | Script Content`

---

## Scene 0: Intuition and Chaos

**Scene Start Time**: 0:00

| Time | Cumulative | Script Content | Notes |
|------|-----------|----------------|-------|
| 0:00 | 0:00 | If you were to draw the outline of this image, how would you do it? | Question (ask_question, wait 4s) |
| 0:04 | 0:04 | Your eyes can automatically ignore these noise points and see the underlying lines. | Human vision capability (wait 1s) |
| 0:05 | 0:05 | But for a computer, every noise point is a dramatic numerical jump. | Computer's challenge (wait 1s) |
| 0:06 | 0:06 | Noise obscures the structure of the image. | Noise impact (wait 1.2s) |
| 0:07 | 0:07 | How can a machine distinguish between 'real edges' and 'random noise'? | Core question (wait 1.5s) |
| 0:09 | 0:09 | This is the power of edge detection. | Solution (wait 1s) |

**Scene End Time**: ~0:10

---

## Scene 1: Losing the Limit

**Scene Start Time**: 0:10

| Time | Cumulative | Script Content | Notes |
|------|-----------|----------------|-------|
| 0:10 | 0:10 | In the mathematical ideal, the derivative is the slope of the tangent line. | Mathematical ideal (wait 1s) |
| 0:11 | 0:11 | Calculus tells us that the derivative is the slope. But in the pixel world, we hit a physical barrier: pixels are discrete. | Pixel world challenge (wait 1.5s) |
| 0:13 | 0:13 | We can't approach infinity—the smallest step size is 1. | Step size limitation (wait 1s) |
| 0:14 | 0:14 | Each pixel is a bucket, and the function gets quantized into piecewise approximations. | Pixel quantization (wait 0.8s) |
| 0:15 | 0:15 | The minimum step size is constrained; Δx can't get any smaller. | Step size constraint (wait 0.8s) |
| 0:16 | 0:16 | The minimum step size is 1 pixel—we've lost the limit. | Losing the limit (wait 1.2s) |
| 0:17 | 0:17 | We can only make secant estimates; we can't approach the true tangent. | Secant estimation (wait 1s) |

**Scene End Time**: ~0:18

---

## Scene 1.5: The Limit's Dilemma

**Scene Start Time**: 0:18

| Time | Cumulative | Script Content | Notes |
|------|-----------|----------------|-------|
| 0:18 | 0:18 | When calculus' 'infinite subdivision' collides with pixels' 'graininess', does the derivative still exist? | Question (wait 3s) |
| 0:21 | 0:21 | The slope is converging, but the pixel world has hard constraints. | Convergence and constraint (wait 3s) |
| 0:24 | 0:24 | In digital images, Δx is at minimum 1 pixel. | Minimum unit (wait 3s) |
| 0:27 | 0:27 | Conclusion: we need a new approach to reconstruct the derivative in pixels. | Conclusion (wait 3s) |

**Scene End Time**: ~0:30

---

## Scene 2: Taylor Cancellation → Central Difference

**Scene Start Time**: 0:30

| Time | Cumulative | Script Content | Notes |
|------|-----------|----------------|-------|
| 0:30 | 0:30 | Since we can't approach infinity, we settle for the next best thing: estimate using neighboring points. This is called 'finite differences'. | Difference introduction (wait 1.5s) |
| 0:32 | 0:32 | But directly subtracting introduces error. | Error problem (wait 1s) |
| 0:33 | 0:33 | Forward and backward differences each have systematic errors: odd and even order terms get mixed together. | Systematic error (wait 1.5s) |
| 0:35 | 0:35 | Here's a mathematical coincidence: if we look at both the point to the left and the point to the right (using Taylor expansion)... | Mathematical coincidence (wait 1.5s) |
| 0:37 | 0:37 | You'll find that their errors point in opposite directions. | Error direction (wait 1.5s) |
| 0:39 | 0:39 | If we add them together... something magical happens: the errors cancel each other out. | Error cancellation (wait 1.5s) |
| 0:41 | 0:41 | This is the central difference method, and it's half the soul of Sobel. | Central difference (wait 1.5s) |

**Scene End Time**: ~0:43

---

## Scene 2.5: Difference Comparison

**Scene Start Time**: 0:43

| Time | Cumulative | Script Content | Notes |
|------|-----------|----------------|-------|
| 0:43 | 0:43 | Three types of differences: forward, backward, and central—which has the smallest error? | Question (wait 1.5s) |
| 0:45 | 0:45 | Central difference uses information from both sides, giving it a higher order of accuracy. | Central difference advantage (wait 1.5s) |
| 0:47 | 0:47 | Central difference is the 'coolest'—it has the lowest error. | Lowest error (wait 1.2s) |
| 0:48 | 0:48 | Conclusion: central difference = low error, symmetric sampling. | Conclusion (wait 1.4s) |

**Scene End Time**: ~0:50

---

## Scene 3: The Birth of Sobel

**Scene Start Time**: 0:50

| Time | Cumulative | Script Content | Notes |
|------|-----------|----------------|-------|
| 0:50 | 0:50 | Now we have two tools: smoothing (to deal with noise) and central difference (to calculate slope). | Two tools (wait 1.5s) |
| 0:52 | 0:52 | Direct differentiation amplifies noise. | Direct differentiation problem (wait 1s) |
| 0:53 | 0:53 | Smooth first, then differentiate: use [1,2,1]^T for low-pass filtering, then [-1,0,1] for high-pass. | Solution (wait 1.5s) |
| 0:55 | 0:55 | The smoothing kernel slides over the signal: points within the window get weighted and averaged, flattening out. | Smoothing process (wait 1.2s) |
| 0:56 | 0:56 | After smoothing, noise is suppressed, and the signal structure becomes clearer. | Smoothing effect (wait 1.5s) |
| 0:58 | 0:58 | The Sobel operator isn't really a new invention—it just cleverly packages these two actions into a single 3×3 box. | Sobel essence (wait 1.5s) |
| 1:00 | 1:00 | One hand suppresses noise, the other extracts edges. | Sobel function (wait 2s) |

**Scene End Time**: ~1:02

---

## Scene 3.5: Convolution Visualization

**Scene Start Time**: 1:02

| Time | Cumulative | Script Content | Notes |
|------|-----------|----------------|-------|
| 1:02 | 1:02 | Convolution equals a sliding window's weighted sum. Let's see how Sobel works. | Convolution definition (wait 1.5s) |
| 1:04 | 1:04 | The window scans row by row, computing G = kernel · local patch at each step. | Scanning process (wait 1s) |
| 1:05 | 1:05 | The convolution result fills in gradually: red = strong edges, blue-green = weak. | Result filling (wait 1.2s) |

**Scene End Time**: ~1:06

---

## Scene 4.2: Multi-Scale Edges

**Scene Start Time**: 1:06

| Time | Cumulative | Script Content | Notes |
|------|-----------|----------------|-------|
| 1:06 | 1:06 | Scale determines detail: small kernels catch fine lines, large kernels catch coarse outlines. | Scale determines detail (wait 1.5s) |
| 1:08 | 1:08 | 3×3 catches details, 7×7 is smoother with thicker edges. | Different scale effects (wait 1.4s) |
| 1:09 | 1:09 | Fusing multiple scales: we preserve both detail and outline. | Multi-scale fusion (wait 1.2s) |

**Scene End Time**: ~1:10

---

## Scene 4: 3D Scanning

**Scene Start Time**: 1:10

| Time | Cumulative | Script Content | Notes |
|------|-----------|----------------|-------|
| 1:10 | 1:10 | Map brightness to height, and the image becomes a 3D terrain. | 3D mapping (wait 1.8s) |
| 1:12 | 1:12 | Scan with a sliding window: the window's color changes with gradient magnitude. | Scanning process (wait 1.8s) |

**Scene End Time**: ~1:14 (Note: 3D scanning animation is longer, ~12 seconds)

---

## Scene 4.6: Real Image Processing

**Scene Start Time**: ~1:26 (after 3D scanning ends)

| Time | Cumulative | Script Content | Notes |
|------|-----------|----------------|-------|
| 1:26 | 1:26 | Real pipeline: original image → grayscale → Sobel X/Y → gradient magnitude → threshold. | Processing pipeline (wait 1.2s) |
| 1:27 | 1:27 | Adjust the threshold: too low = noise, too high = broken edges. | Threshold adjustment (wait 1.2s) |

**Scene End Time**: ~1:29

---

## Scene 4.5: Application Comparison

**Scene Start Time**: 1:29

| Time | Cumulative | Script Content | Notes |
|------|-----------|----------------|-------|
| 1:29 | 1:29 | Look at real-world images: original on the left, edge extraction on the right. | Real-world images (wait 1.6s) |
| 1:31 | 1:31 | Sobel highlights structure: road boundaries, strokes, facial contours, building windows. | Structure highlighting (wait 2s) |

**Scene End Time**: ~1:33

---

## Scene 5: Summary and Outro

**Scene Start Time**: 1:33

| Time | Cumulative | Script Content | Notes |
|------|-----------|----------------|-------|
| 1:33 | 1:33 | From continuous derivatives to discrete differences, from noise to contours—what have we seen? | Review (wait 2s) |
| 1:35 | 1:35 | Theory meets practice: mathematical ideal Δx→0, engineering reality pixel=1. | Theory and practice (wait 2s) |

**Scene End Time**: ~1:37

---

## Total Duration Statistics

- **Scene 0**: ~10 seconds
- **Scene 1**: ~8 seconds
- **Scene 1.5**: ~12 seconds
- **Scene 2**: ~13 seconds
- **Scene 2.5**: ~7 seconds
- **Scene 3**: ~12 seconds
- **Scene 3.5**: ~4 seconds
- **Scene 4.2**: ~4 seconds
- **Scene 4**: ~16 seconds (includes 12s 3D scanning animation)
- **Scene 4.6**: ~3 seconds
- **Scene 4.5**: ~4 seconds
- **Scene 5**: ~4 seconds

**Total Duration**: ~**97 seconds** (1 minute 37 seconds)

---

## Voice-Over Notes

1. **Pacing Control**:
   - Normal pace: ~150-180 words per minute
   - Important concepts can be slightly slower
   - Questions should have a thoughtful feel

2. **Emotional Expression**:
   - **Question parts** (0:00, 0:18, 0:43): thoughtful, exploratory tone
   - **Challenge parts** (0:11, 0:32, 0:52): puzzled, challenging tone
   - **Solution parts** (0:35, 0:53, 0:58): discovery, surprise tone
   - **Conclusion parts** (0:27, 0:48, 1:33): summary, elevated tone

3. **Pause Suggestions**:
   - Comma: brief pause (0.3-0.5s)
   - Period: normal pause (0.5-1s)
   - Question mark: longer pause (1-1.5s)
   - Ellipsis: thoughtful pause (1-2s)

4. **Key Terms to Emphasize**:
   - "central difference", "Sobel", "edge detection"
   - "error cancellation", "smoothing", "convolution"
   - "pixel", "discrete", "derivative"

5. **Time Tolerance**:
   - Actual voice-over time may vary ±2-3 seconds from timeline
   - Recommend marking key time points for post-production alignment

---

## Quick Reference Table (Chronological Order)

| Time | Script |
|------|--------|
| 0:00 | If you were to draw the outline of this image, how would you do it? |
| 0:04 | Your eyes can automatically ignore these noise points and see the underlying lines. |
| 0:05 | But for a computer, every noise point is a dramatic numerical jump. |
| 0:06 | Noise obscures the structure of the image. |
| 0:07 | How can a machine distinguish between 'real edges' and 'random noise'? |
| 0:09 | This is the power of edge detection. |
| 0:10 | In the mathematical ideal, the derivative is the slope of the tangent line. |
| 0:11 | Calculus tells us that the derivative is the slope. But in the pixel world, we hit a physical barrier: pixels are discrete. |
| 0:13 | We can't approach infinity—the smallest step size is 1. |
| 0:14 | Each pixel is a bucket, and the function gets quantized into piecewise approximations. |
| 0:15 | The minimum step size is constrained; Δx can't get any smaller. |
| 0:16 | The minimum step size is 1 pixel—we've lost the limit. |
| 0:17 | We can only make secant estimates; we can't approach the true tangent. |
| 0:18 | When calculus' 'infinite subdivision' collides with pixels' 'graininess', does the derivative still exist? |
| 0:21 | The slope is converging, but the pixel world has hard constraints. |
| 0:24 | In digital images, Δx is at minimum 1 pixel. |
| 0:27 | Conclusion: we need a new approach to reconstruct the derivative in pixels. |
| 0:30 | Since we can't approach infinity, we settle for the next best thing: estimate using neighboring points. This is called 'finite differences'. |
| 0:32 | But directly subtracting introduces error. |
| 0:33 | Forward and backward differences each have systematic errors: odd and even order terms get mixed together. |
| 0:35 | Here's a mathematical coincidence: if we look at both the point to the left and the point to the right (using Taylor expansion)... |
| 0:37 | You'll find that their errors point in opposite directions. |
| 0:39 | If we add them together... something magical happens: the errors cancel each other out. |
| 0:41 | This is the central difference method, and it's half the soul of Sobel. |
| 0:43 | Three types of differences: forward, backward, and central—which has the smallest error? |
| 0:45 | Central difference uses information from both sides, giving it a higher order of accuracy. |
| 0:47 | Central difference is the 'coolest'—it has the lowest error. |
| 0:48 | Conclusion: central difference = low error, symmetric sampling. |
| 0:50 | Now we have two tools: smoothing (to deal with noise) and central difference (to calculate slope). |
| 0:52 | Direct differentiation amplifies noise. |
| 0:53 | Smooth first, then differentiate: use [1,2,1]^T for low-pass filtering, then [-1,0,1] for high-pass. |
| 0:55 | The smoothing kernel slides over the signal: points within the window get weighted and averaged, flattening out. |
| 0:56 | After smoothing, noise is suppressed, and the signal structure becomes clearer. |
| 0:58 | The Sobel operator isn't really a new invention—it just cleverly packages these two actions into a single 3×3 box. |
| 1:00 | One hand suppresses noise, the other extracts edges. |
| 1:02 | Convolution equals a sliding window's weighted sum. Let's see how Sobel works. |
| 1:04 | The window scans row by row, computing G = kernel · local patch at each step. |
| 1:05 | The convolution result fills in gradually: red = strong edges, blue-green = weak. |
| 1:06 | Scale determines detail: small kernels catch fine lines, large kernels catch coarse outlines. |
| 1:08 | 3×3 catches details, 7×7 is smoother with thicker edges. |
| 1:09 | Fusing multiple scales: we preserve both detail and outline. |
| 1:10 | Map brightness to height, and the image becomes a 3D terrain. |
| 1:12 | Scan with a sliding window: the window's color changes with gradient magnitude. |
| 1:26 | Real pipeline: original image → grayscale → Sobel X/Y → gradient magnitude → threshold. |
| 1:27 | Adjust the threshold: too low = noise, too high = broken edges. |
| 1:29 | Look at real-world images: original on the left, edge extraction on the right. |
| 1:31 | Sobel highlights structure: road boundaries, strokes, facial contours, building windows. |
| 1:33 | From continuous derivatives to discrete differences, from noise to contours—what have we seen? |
| 1:35 | Theory meets practice: mathematical ideal Δx→0, engineering reality pixel=1. |

**Total: 49 scripts, total duration ~1 minute 37 seconds**

---

## Translation Notes

1. **Style**: Maintained 3Blue1Brown's conversational, accessible tone
2. **Technical Terms**: Used standard English terminology (e.g., "finite differences" instead of literal translation)
3. **Natural Flow**: Prioritized natural English expression over literal translation
4. **Emotional Tone**: Preserved the original emotional nuances (curiosity, challenge, discovery, conclusion)
5. **Mathematical Notation**: Kept mathematical symbols (Δx, 3×3, etc.) as they appear in the original

