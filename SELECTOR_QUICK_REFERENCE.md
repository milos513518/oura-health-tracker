# Quick Reference: Finding CSS Selectors

## 🎯 Quick Steps

1. **Open HeartCloud** → https://heartcloud.com/login
2. **Right-click element** → "Inspect" or "Inspect Element"
3. **Look at highlighted HTML** in DevTools
4. **Copy the selector**

## 🔍 Common Selector Patterns

### By ID (most specific)
```html
<input id="email">
```
**Selector:** `#email`

### By Class
```html
<div class="session-item">
```
**Selector:** `.session-item`

### By Attribute
```html
<input type="email" name="userEmail">
```
**Selectors:** 
- `input[type='email']`
- `input[name='userEmail']`

### By Type
```html
<button type="submit">
```
**Selector:** `button[type='submit']`

### Multiple Classes
```html
<span class="score coherence-value">
```
**Selectors:**
- `.score`
- `.coherence-value`
- `.score.coherence-value` (both classes)

## 🛠️ Browser DevTools Shortcuts

| Action | Chrome/Edge | Firefox | Safari |
|--------|-------------|---------|---------|
| Open DevTools | F12 | F12 | Cmd+Option+I |
| Inspect Element | Ctrl+Shift+C | Ctrl+Shift+C | Cmd+Option+C |
| Copy Selector | Right-click element → Copy → Copy selector | Right-click → Copy → CSS Selector | Right-click → Copy → CSS Path |

## 📸 How to Get the Selector

### Method 1: Copy Selector (Easiest)
1. Inspect element
2. In DevTools, **right-click** the highlighted line
3. **Copy** → **Copy selector**
4. Paste into your script

### Method 2: Read from HTML
1. Inspect element
2. Look at the HTML:
   ```html
   <span class="coherence-score" id="score-123">5.8</span>
   ```
3. Determine best selector:
   - By ID: `#score-123` (if ID is consistent)
   - By class: `.coherence-score` (better if ID changes)

### Method 3: Test in Console
1. Open DevTools Console tab
2. Type: `document.querySelector('.coherence-score')`
3. Hit Enter
4. If it returns the element, the selector works!
5. For multiple elements: `document.querySelectorAll('.session-item')`

## 🎨 Visual Guide

```
┌─────────────────────────────────────────┐
│  HeartCloud Login Page                  │
├─────────────────────────────────────────┤
│                                         │
│  Email:    [________________]           │  ← Inspect this
│            ↑                             │
│            This is #email or             │
│            input[name='email']           │
│                                         │
│  Password: [________________]           │  ← And this
│                                         │
│  [      Login      ]                    │  ← And this button
│                                         │
└─────────────────────────────────────────┘

After Login:
┌─────────────────────────────────────────┐
│  My Sessions                            │
├─────────────────────────────────────────┤
│  ┌───────────────────────────────────┐  │
│  │ Dec 30  | Coherence: 5.8 | 15min │  │ ← Inspect this row
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │ Dec 29  | Coherence: 6.2 | 12min │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘

Inspect the "5.8" to find: .coherence-score
```

## ⚠️ Common Mistakes

### ❌ Wrong: Using index-based selectors
```python
"coherence_score": "div:nth-child(3) > span:nth-child(2)"
```
**Problem:** Breaks if page structure changes

### ✅ Right: Using semantic selectors
```python
"coherence_score": ".coherence-score"
```
**Better:** Works even if position changes

### ❌ Wrong: Too specific
```python
"login_button": "body > div > div > form > button.btn.btn-primary.login-submit"
```
**Problem:** Fragile, breaks easily

### ✅ Right: Just specific enough
```python
"login_button": "button[type='submit']"
```
**Better:** Simple and robust

## 🧪 Testing Your Selectors

### In Browser Console:
```javascript
// Test if selector finds element
document.querySelector('#email')  // Should return the element
document.querySelector('.session-item')  // Should return first session

// Test if multiple elements found
document.querySelectorAll('.session-item').length  // Should return count

// Get text content
document.querySelector('.coherence-score').textContent  // Should return "5.8"
```

### In Python Script:
```python
# Add this after login to test
try:
    element = driver.find_element(By.CSS_SELECTOR, '.coherence-score')
    print(f"Found element with text: {element.text}")
except:
    print("Selector not found - needs updating")
```

## 📝 Selector Priority

Try selectors in this order:

1. **ID** - `#email` (most specific, but might be dynamic)
2. **Class** - `.coherence-score` (usually best choice)
3. **Data attribute** - `[data-metric='coherence']` (if available)
4. **Type + attribute** - `button[type='submit']` (good for forms)
5. **Type + class** - `span.score` (fallback)

## 💡 Pro Tips

### Tip 1: Check if selector is unique
```javascript
// In browser console
document.querySelectorAll('.your-selector').length
// Should return 1 for unique elements
// Can return multiple for lists (like session rows)
```

### Tip 2: Use more specific selectors for common elements
```python
# Instead of just .score (might be ambiguous)
".session-item .coherence-score"  # Score within session item
```

### Tip 3: Save screenshots of the HTML structure
When you find the right elements, take screenshots of the DevTools showing:
- The element highlighted
- The HTML structure
- The selector you're using

This helps when updating the script later!

## 🆘 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Selector not found | Element loaded by JavaScript - add `time.sleep(2)` |
| Returns wrong element | Selector too general - be more specific |
| Works in console, not in script | Element not loaded yet - use `WebDriverWait` |
| Selector finds multiple elements | Use `.session-item` for first, or loop through all |

## 📞 Need More Help?

1. Save the HeartCloud page source: Right-click → "View Page Source"
2. Take screenshot of the elements you need
3. Share both with me and I can identify the selectors for you!

---

**Remember:** The key is finding selectors that are:
- ✅ **Specific enough** to target the right element
- ✅ **General enough** to not break when page updates
- ✅ **Stable** across page loads

Good luck! You've got this! 🎯
