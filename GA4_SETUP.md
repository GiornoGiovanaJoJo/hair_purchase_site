# Google Analytics 4 (GA4) Setup Documentation

**Measurement ID:** `G-E4CZCZ0HG5`

## Overview

Google Analytics 4 has been successfully integrated into your Hair Purchase Site. GA4 provides comprehensive tracking of user interactions, conversions, and site performance metrics.

## Implementation Details

### Code Location

The GA4 tracking code has been added to:
- **File:** `templates/index.html`
- **Location:** Inside the `<head>` tag (immediately after `<meta>` tags)

### Tracking Code

```html
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-E4CZCZ0HG5"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-E4CZCZ0HG5');
</script>
```

## What Gets Tracked Automatically

With this configuration, GA4 automatically collects:

✅ **Page Views** - Every page loaded on the site
✅ **Sessions** - User session information and duration
✅ **User Engagement** - Time on page, scrolling, clicks
✅ **Device Information** - Browser, OS, device type, screen resolution
✅ **Geographic Data** - Country, region, city
✅ **Traffic Source** - How users arrived (organic, direct, referral, etc.)
✅ **User ID** - Unique visitor identification

## Event Tracking

### Default Events Captured
- `page_view` - Page loads
- `session_start` - New session begins
- `user_engagement` - User interactions
- `first_visit` - First time visitor

### Recommended Custom Events to Track

Consider adding tracking for these business-critical events:

**1. Product Views**
```javascript
gtag('event', 'view_item', {
  'items': [{
    'item_id': 'product_id',
    'item_name': 'product_name',
    'price': 'price'
  }]
});
```

**2. Add to Cart**
```javascript
gtag('event', 'add_to_cart', {
  'value': price,
  'currency': 'USD',
  'items': [{
    'item_id': 'product_id',
    'item_name': 'product_name',
    'quantity': quantity
  }]
});
```

**3. Purchase**
```javascript
gtag('event', 'purchase', {
  'transaction_id': 'order_id',
  'value': total_value,
  'currency': 'USD',
  'items': [purchase_items]
});
```

**4. Conversion Events**
```javascript
gtag('event', 'conversion', {
  'conversion_type': 'lead',
  'conversion_value': 'value'
});
```

## Verification

### How to Verify Implementation

1. **Check Real-Time Reporting:**
   - Go to Google Analytics dashboard
   - Navigate to **Reports → Real-time → Overview**
   - Load your website in a browser
   - You should see active users and page views within seconds

2. **Use Google Tag Assistant:**
   - Install [Tag Assistant](https://chrome.google.com/webstore/detail/tag-assistant-companion/daejbmnodkfeoecnkccnjlgnbigblema) Chrome extension
   - Open your site and enable the extension
   - Look for the GA4 tag with ID `G-E4CZCZ0HG5`

3. **Check Browser Console:**
   ```javascript
   // In browser console (F12 → Console tab)
   console.log(gtag)  // Should show the gtag function
   gtag('event', 'test_event')  // Test sending an event
   ```

## Django Template Integration

Since this is a Django project, ensure:

1. **Template Inheritance** - If using a base template, add the GA4 code once to the base template
2. **Static Files** - No Django static files are needed for GA4 code (it's external)
3. **Production Domain** - Update the canonical URL after deployment to your production domain

## Configuration for Different Environments

### Development
```html
<!-- Use same tracking code for development to test events -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-E4CZCZ0HG5"></script>
```

### Production
```html
<!-- Ensure your site is on production domain before enabling GA4 -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-E4CZCZ0HG5"></script>
```

## Privacy and Data Collection

⚠️ **Important Compliance Notes:**

1. **GDPR Compliance** - If serving EU users, implement cookie consent
2. **Privacy Policy** - Update your privacy policy to mention GA4 tracking
3. **User Data** - Review what personal data is being collected
4. **Data Retention** - Default is 14 months (can be adjusted in GA4 settings)

### Cookie Consent Example

If using a cookie banner:

```javascript
// Only enable GA4 if user consents
if (userHasConsentedToAnalytics) {
  gtag('consent', 'default', {
    'analytics_storage': 'granted',
    'ad_storage': 'granted'
  });
} else {
  gtag('consent', 'default', {
    'analytics_storage': 'denied',
    'ad_storage': 'denied'
  });
}
```

## Key Reports to Monitor

### Essential Metrics

1. **Overview Dashboard**
   - Users
   - Sessions
   - Bounce rate
   - Session duration
   - Conversion rate

2. **User Engagement**
   - Pages per session
   - Average session duration
   - Events per user
   - Engaged sessions

3. **Acquisition**
   - Traffic sources
   - User acquisition cost (if applicable)
   - Conversion funnel

4. **Retention**
   - New vs returning users
   - User retention cohorts
   - Repeat purchase rate

## Troubleshooting

### GA4 Not Collecting Data

**Issue:** No data appears in GA4 after 24 hours

**Solutions:**
1. Verify tracking code is present in page source (view page source in browser)
2. Check that Measurement ID is correct: `G-E4CZCZ0HG5`
3. Ensure no ad blockers are preventing Google Analytics script
4. Check Network tab in browser DevTools for successful requests to `googletagmanager.com`
5. Verify data stream is active in GA4 settings

### Events Not Firing

**Issue:** Custom events not appearing in GA4

**Solutions:**
1. Ensure gtag is loaded before triggering events
2. Check event name spelling (case-sensitive)
3. Verify required parameters are included
4. Check browser console for JavaScript errors
5. Wait up to 24 hours for events to appear in reports

## Next Steps

1. ✅ **Monitor Real-time Data** - Watch the first 24 hours of data collection
2. ✅ **Verify Events** - Confirm all important events are being tracked
3. ✅ **Set Up Conversions** - Define conversion goals in GA4
4. ✅ **Create Audiences** - Build segments for remarketing
5. ✅ **Configure Alerts** - Set up notifications for anomalies

## Resources

- [Google Analytics 4 Documentation](https://support.google.com/analytics/answer/10089681)
- [GA4 Event Reference](https://support.google.com/analytics/answer/9267744)
- [GA4 Implementation Guide](https://support.google.com/analytics/answer/10109185)
- [Google Tag Assistant](https://support.google.com/tagassistant/answer/6102821)

## Support

For issues or questions about GA4 implementation:
- Visit [Google Analytics Help Center](https://support.google.com/analytics)
- Check [GA4 Community](https://www.en.advertisercommunity.com/)
- Review [Analytics Academy](https://analytics.google.com/analytics/academy/)

---

**Last Updated:** January 1, 2026  
**Status:** ✅ Active and monitoring
