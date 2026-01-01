# GA4 Quick Start Guide

**Measurement ID:** `G-E4CZCZ0HG5`

## Status: ✅ ACTIVE

Google Analytics 4 is now tracking your Hair Purchase Site.

## Quick Links

- [GA4 Dashboard](https://analytics.google.com/analytics/web/)
- [Full Setup Documentation](./GA4_SETUP.md)
- [Google Analytics Help](https://support.google.com/analytics)

## What's Installed

✅ **GA4 Tracking Code** - Added to `templates/index.html`  
✅ **Automatic Data Collection** - Page views, sessions, user engagement  
✅ **Real-time Reporting** - Monitor activity as it happens  

## Verify It's Working (2-minute check)

1. **Open your website** in a browser
2. **Go to Analytics Dashboard:** https://analytics.google.com/
3. **Navigate to:** Reports → Real-time → Overview
4. **You should see:** Active users and page views

## Check in Browser

Open browser DevTools (F12) and run:

```javascript
console.log(gtag)  // Should show the gtag function is loaded
```

Or trigger a test event:

```javascript
gtag('event', 'test_event', {
  'test_parameter': 'test_value'
});
```

## Common Tasks

### Track a Button Click

```html
<button onclick="gtag('event', 'button_click', {'button_name': 'my_button'})">Click Me</button>
```

### Track a Page View (auto-tracked, but can be manual)

```javascript
gtag('config', 'G-E4CZCZ0HG5', {
  'page_title': 'Product Page',
  'page_location': window.location.href
});
```

### Track a Form Submission

```html
<form onsubmit="gtag('event', 'form_submit', {'form_name': 'contact_form'})">
  <!-- form fields -->
</form>
```

### Track a Purchase

```javascript
gtag('event', 'purchase', {
  'transaction_id': '12345',
  'value': 99.99,
  'currency': 'USD',
  'items': [{
    'item_id': 'product_123',
    'item_name': 'Hair Product',
    'quantity': 1,
    'price': 99.99
  }]
});
```

## Data Collection Settings

### What's Being Tracked ✅
- User interactions
- Page performance
- Device information
- Geographic location
- Traffic source

### What's NOT Being Tracked ❌
- Email addresses (unless explicitly sent)
- Password or credit card data
- Personally identifiable information (PII) - unless explicitly configured

## Important Reminders

⚠️ **Privacy Compliance**
- Update privacy policy to mention GA4
- Implement cookie consent if needed
- Respect user privacy settings

⚠️ **Data Accuracy**
- Avoid tracking sensitive information
- Use consistent event naming
- Document custom events for team

⚠️ **Performance**
- GA4 code is loaded asynchronously (doesn't block page load)
- Minimal performance impact
- No additional server resources needed

## Reporting Timeline

- **Real-time Reports:** 0-2 minutes delay
- **Overview Reports:** Up to 24-48 hours delay
- **Detailed Reports:** Up to 3 days delay

## Troubleshooting

### No data showing?

1. Wait 24 hours (first time takes longer)
2. Check that GA4 code is in page source (Ctrl+U)
3. Disable ad blockers on test visit
4. Verify Measurement ID: `G-E4CZCZ0HG5`

### Events not firing?

1. Check browser console (F12) for errors
2. Verify event names are correct
3. Ensure gtag function is called after page load
4. Check Network tab for requests to googletagmanager.com

## Useful Reports to Check

📊 **Overview**
- Users
- Sessions
- Bounce rate
- Session duration

📊 **User Engagement**
- Page views
- Events per user
- Conversion rate

📊 **Acquisition**
- Traffic sources
- New vs returning users
- Conversion funnel

## Resources for Your Team

📖 **Documentation**
- [GA4 Implementation Guide](https://support.google.com/analytics/answer/10109185)
- [GA4 Event Reference](https://support.google.com/analytics/answer/9267744)

📖 **Tools**
- [Google Tag Assistant](https://support.google.com/tagassistant/)
- [Google Analytics Debugger](https://chrome.google.com/webstore/detail/google-analytics-debugger/)

📖 **Learning**
- [Analytics Academy](https://analytics.google.com/analytics/academy/)
- [GA4 Community](https://www.en.advertisercommunity.com/)

## Need Help?

1. **Setup Questions?** → See [GA4_SETUP.md](./GA4_SETUP.md)
2. **Implementation Issues?** → Check Google Analytics Help
3. **Event Tracking?** → Review GA4 Event Reference guide

---

**Status:** Active ✅  
**Last Updated:** January 1, 2026  
**Measurement ID:** G-E4CZCZ0HG5
