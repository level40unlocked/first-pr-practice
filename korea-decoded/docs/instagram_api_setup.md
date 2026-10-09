# Instagram API setup (Reels publishing)

Goal: Claude publishes Reels from `korea_decoded/instagram.py`. Done once, on a PC browser (not the phone app).

## Operator steps
1. Instagram app: Settings → Account type → switch to **Professional (Creator or Business)**.
2. developers.facebook.com → My Apps → Create App → type **Business** → add product **Instagram** → "API setup with Instagram login".
3. Add the Instagram account under *Instagram Accounts / Roles → Instagram testers*, then accept the invite in the Instagram app (Settings → Apps and websites → Tester invites). While the app stays in development mode, only your own account can be used, which is all we need (no app review).
4. In that API-setup page choose the permissions `instagram_business_basic` and `instagram_business_content_publish`, then press **Generate token** for the account. This is a long-lived token (60 days).
5. Add two environment variables in the Claude cloud environment (Edit environment): `INSTAGRAM_ACCESS_TOKEN` and `INSTAGRAM_USER_ID`. Never paste the token into the chat. A new session picks them up.

## Limits to know
- API publishing is publish-now only; no scheduled posts, so timing means Claude runs at that time (or you use Meta Business Suite scheduling by hand).
- About 100 API-published posts per 24 h; Reels max 15 min (shorts here are ~1 min), 9:16, MP4.
- The token expires after 60 days; `InstagramPublisher.refresh_token()` renews it (then update the environment variable).
- Uploads and publishing happen only after the operator's explicit approval.
