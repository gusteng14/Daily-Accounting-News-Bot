# Daily Accounting News Bot (Philippines)

A Python bot that curates daily accounting, tax, and business news from Philippine government agencies (BIR, SEC, PRC), professional organizations (PICPA), and major news outlets (via Google News RSS). It automatically publishes a daily roundup to a Facebook Page.

## Requirements

- Python 3.8+
- A Facebook Page (where you have admin access)
- A Facebook Developer Account and App

## 1. Facebook App Setup & Access Token

To post automatically, you need a long-lived Page Access Token. Do not share this token publicly.

1. Go to [Facebook Developers](https://developers.facebook.com/) and click **Create App**. 
   - When asked what you want your app to do, you MUST select **"Other"**.
   - Then select **"Business"** as the app type.
2. In your new App Dashboard, look at the **Left-Hand Menu Sidebar**.
   - **If you see "Use cases":** Click it, then click the blue **"Add Use Case"** button on the right. Add **"Customize what appears on your Page"** (or Business / Pages API).
   - **If you DO NOT see "Use cases" (and instead see "Products", "App Review", etc.):** Great! Your app already has the right underlying structure for a Business App. You can **skip this step**.
3. Now go to **Graph API Explorer** (Tools > Graph API Explorer).
4. Under "Facebook App", select your new App. 
5. **Workaround for Facebook API Bug ("Invalid Scopes"):** 
   - DO NOT select "Get Page Access Token" yet.
   - Instead, under the "User or Page" dropdown, select **"Get User Access Token"**.
6. Under **"Add a Permission"**, manually search for and select:
   - `pages_manage_posts`
   - `pages_read_engagement`
   - `pages_show_list` (If this causes the error again, remove it and proceed with just the first two).
7. Click **"Generate Access Token"** and go through the Facebook login popup to authorize it.
8. Once authorized, click the **"User or Page" dropdown again**. Your Facebook Page should now appear in the list underneath "User Token". **Select your Page**.
9. The Token in the box will instantly swap to a **Page Access Token**.
10. To make it long-lived (valid for 60 days or permanent):
   - Go to the **Access Token Info** tool (the 'i' icon next to the token in Explorer) and click **"Open in Access Token Tool"**.
   - Click **"Extend Access Token"**.
11. Copy the Page ID and the extended Access Token.

## 2. Project Setup

1. Rename `.env.example` to `.env`.
2. Open `.env` and fill in your details:
   ```
   FB_PAGE_ID=your_page_id_here
   FB_PAGE_ACCESS_TOKEN=your_extended_token_here
   ```
3. Install dependencies (if not already done via the virtual environment):
   ```cmd
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

## 3. Testing the Bot

Run the main script to see what news it fetches and to test the post. 

```cmd
.\venv\Scripts\python main.py
```

*Note: It will fetch the news, print a draft of the Facebook post, and then attempt to post it. Ensure your `.env` is configured properly.*

## 4. Scheduling the Bot (Windows Task Scheduler)

To make it run daily without your intervention:

1. Open **Task Scheduler** in Windows.
2. Click **Create Basic Task...** on the right panel.
3. Name it "Daily Accounting News Bot" and click Next.
4. Set Trigger to **Daily** and choose a time (e.g., 8:00 AM). Click Next.
5. Set Action to **Start a program**. Click Next.
6. In **Program/script**, browse and select the python executable inside your virtual environment: `C:\Users\apoll\OneDrive\Desktop\Codes\Daily Accounting News Bot\venv\Scripts\python.exe`
7. In **Add arguments (optional)**, type: `main.py`
8. In **Start in (optional)**, paste the absolute path to your folder: `C:\Users\apoll\OneDrive\Desktop\Codes\Daily Accounting News Bot\`
9. Click Next, then Finish.

Your bot is now scheduled to run every day!
