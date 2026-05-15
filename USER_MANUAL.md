# Chilli Care — User Manual

**Version 1.0 | AI-Powered Chilli Disease Detection System**

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Getting Started — Accessing the System](#2-getting-started--accessing-the-system)
3. [Creating a New Account (Registration)](#3-creating-a-new-account-registration)
4. [Logging In](#4-logging-in)
5. [Detecting a Chilli Disease](#5-detecting-a-chilli-disease)
6. [Understanding Your Results](#6-understanding-your-results)
7. [Viewing Your Prediction History](#7-viewing-your-prediction-history)
8. [Browsing the Disease Reference Guide](#8-browsing-the-disease-reference-guide)
9. [Checking Analytics](#9-checking-analytics)
10. [Contacting Support](#10-contacting-support)
11. [Managing Your Account](#11-managing-your-account)
12. [Admin Dashboard Guide](#12-admin-dashboard-guide)
13. [Using the System on a Mobile Device](#13-using-the-system-on-a-mobile-device)
14. [Notifications](#14-notifications)
15. [Troubleshooting Common Problems](#15-troubleshooting-common-problems)

---

## 1. Introduction

Chilli Care is a web-based application that uses artificial intelligence to help farmers and agricultural professionals identify diseases in chilli plants. You simply take or upload a photo of a chilli leaf, and the system will analyse it and tell you what disease is present — along with recommended treatments.

**What the system can detect:**

| Disease | Type |
|---|---|
| Chilli Whitefly | Pest infestation |
| Chilli Yellowish | Nutrient deficiency / stress |
| Chilli Anthracnose | Fungal disease |
| Chilli Leaf Curl Virus | Viral disease |
| Healthy Plant | No disease detected |

The full disease reference guide inside the platform covers 31 conditions in total.

---

## 2. Getting Started — Accessing the System

**Step 1.** Open a web browser on your computer or mobile device (Chrome, Firefox, Safari, or Edge are all supported).

**Step 2.** Type the application address into the browser address bar and press **Enter**.

- On a local network: `http://<server-ip-address>:5000`
- On your own machine: `http://127.0.0.1:5000`

**Step 3.** The Chilli Care home page will load. From here you can register, log in, or use the detection tool as a guest.

> **Note:** A stable internet connection is required for AI-powered image validation and for loading the application on the first visit.

---

## 3. Creating a New Account (Registration)

You do not need an account to run a single detection, but creating one allows you to save and review your detection history.

**Step 1.** On the home page, click the **Sign Up** button in the top navigation bar.

**Step 2.** Fill in the registration form:
- **Full Name** — Your first and last name.
- **Email Address** — A valid email you have access to.
- **Password** — Choose a strong password (minimum 6 characters).
- **Confirm Password** — Re-enter your password exactly as typed above.

**Step 3.** Click the **Create Account** button.

**Step 4.** If all fields are correct, your account will be created and you will be logged in automatically.

> **Note:** Your password is securely stored using bcrypt encryption — it is never saved in plain text.

---

## 4. Logging In

**Step 1.** Click **Log In** in the top navigation bar.

**Step 2.** Enter your registered **email address** and **password**.

**Step 3.** Click the **Login** button.

**Step 4.** On success, you will be redirected to the home page with your account name displayed in the navigation bar.

> **Tip:** Your session stays active for 7 days. You will not need to log in again unless you manually log out or the session expires.

---

## 5. Detecting a Chilli Disease

This is the core feature of Chilli Care. Follow the steps below to get an AI diagnosis for your chilli plant.

### Option A — Upload an Image from Your Device

**Step 1.** On the home page, locate the **Disease Detection** panel.

**Step 2.** Click the **Upload Image** area (or drag and drop an image file onto it).

**Step 3.** Select a photo from your device. Accepted formats are **JPG**, **JPEG**, and **PNG**.

**Step 4.** A preview of the selected image will appear on screen.

**Step 5.** Click the **Analyze Disease** button.

**Step 6.** Wait 2–5 seconds while the AI processes your image.

**Step 7.** Your results will appear below the image automatically.

---

### Option B — Capture a Photo Using Your Camera

**Step 1.** On the home page, click the **Camera** button inside the detection panel.

**Step 2.** Your browser will ask for permission to access your camera. Click **Allow**.

**Step 3.** A live camera preview will appear. If your device has a front and back camera, use the **Switch Camera** button to toggle between them.

**Step 4.** Position your chilli leaf clearly within the camera frame, then click **Capture**.

**Step 5.** A preview of the captured photo will appear.

**Step 6.** Click **Analyze Disease** to run the detection.

> **Important:** For the most accurate result, photograph the **leaf** of the plant in good lighting. Avoid blurry or dark images. The AI will reject images that do not appear to be chilli plant leaves.

---

## 6. Understanding Your Results

After analysis, the system displays a detailed results panel. Here is what each section means:

| Result Section | What It Tells You |
|---|---|
| **Disease Name** | The detected condition (e.g., "Chilli Leaf Curl Virus") |
| **Confidence Score** | How certain the AI is — shown as a percentage (e.g., 94.2%) |
| **Probability Chart** | A breakdown of likelihood scores across all 5 detectable classes |
| **Symptoms** | Key visual signs associated with the detected disease |
| **Cause** | The biological or environmental reason for the condition |
| **Treatment Recommendations** | Chemical or conventional treatment options |
| **Organic Solutions** | Natural and eco-friendly treatment alternatives |
| **Prevention Tips** | Steps to avoid the disease in future plantings |
| **Prognosis Card** | Estimated plant life expectancy, expected yield impact, and next likely disease risk |
| **Location** | Your automatically detected district (based on your IP address) |

> **Reminder:** Results are generated by an AI model and are intended as guidance. Always consult a qualified agricultural professional before applying treatments.

---

## 7. Viewing Your Prediction History

This feature is available to registered, logged-in users only.

**Step 1.** Log in to your account (see Section 4).

**Step 2.** Click your profile name or navigate to **History** in the navigation menu.

**Step 3.** Your past detections will be listed in order from newest to oldest.

**Step 4.** Each entry shows the date, the detected disease, the confidence score, and your location at the time of the scan.

**Step 5.** Click any entry to expand and view the full result details for that scan.

---

## 8. Browsing the Disease Reference Guide

The Disease Reference Guide provides detailed information on 31 chilli diseases and pests — beyond what the AI model detects.

**Step 1.** Click **Diseases** in the top navigation bar.

**Step 2.** A list of all diseases and pests is displayed, organised by category (Fungal, Bacterial, Viral, Pest, Nutritional).

**Step 3.** Click on any disease card to expand it and read:
- Description and overview
- Visual symptoms to look for
- Known causes and risk factors
- Prevention and management strategies

**Step 4.** Use the **Search** bar at the top of the page to quickly find a specific disease by name.

---

## 9. Checking Analytics

The Analytics page shows platform-wide statistics about detections made by all users.

**Step 1.** Click **Analytics** in the navigation bar.

**Step 2.** The dashboard displays:
- Total number of scans performed on the platform
- Most frequently detected diseases
- Detection trends over time (charts)
- Geographic distribution of detections by district

This page is publicly accessible — no login is required.

---

## 10. Contacting Support

**Step 1.** Click **Contact** in the navigation bar or footer.

**Step 2.** Fill in the contact form:
- **Your Name**
- **Email Address**
- **Subject** — A brief title for your query
- **Message** — Describe your issue or question in detail

**Step 3.** Click **Send Message**.

**Step 4.** A confirmation message will appear on screen, and the support team will receive an email notification.

---

## 11. Managing Your Account

### Logging Out

**Step 1.** Click your profile name or account menu in the navigation bar.

**Step 2.** Select **Log Out**.

**Step 3.** You will be signed out and redirected to the home page.

---

### Deleting Your Account

> **Warning:** This action is permanent. All your prediction history and account data will be deleted and cannot be recovered.

**Step 1.** Go to your account settings or profile page.

**Step 2.** Scroll to the **Delete Account** section.

**Step 3.** Click **Delete My Account** and confirm the action when prompted.

---

## 12. Admin Dashboard Guide

The admin dashboard is accessible only to system administrators.

### Accessing the Admin Panel

**Step 1.** Log in using your admin credentials.

**Step 2.** Navigate to `/admin/dashboard` or click the **Admin Panel** link that appears in the navigation bar for admin accounts.

---

### Admin Features — Step by Step

#### A. Viewing All Users

1. In the admin dashboard, click the **Users** tab.
2. A table lists all registered farmer accounts with their email, registration date, and number of scans.

#### B. Viewing All Predictions

1. Click the **Predictions** tab.
2. Browse all detections submitted across the platform, filterable by date, disease, and user.

#### C. Reading Contact Messages

1. Click the **Messages** tab.
2. All contact form submissions are listed here with the sender's name, email, subject, and message body.
3. Click **Reply** to open a pre-filled email to respond to the user.

#### D. Sending a Broadcast Notification

1. Click the **Notifications** tab.
2. Type a message in the broadcast field.
3. Click **Send to All Users**.
4. The notification will appear for all logged-in users the next time they visit the platform.

#### E. Editing Disease Information

1. Click the **Disease Database** tab.
2. Select a disease record to edit.
3. Update the fields (symptoms, treatment, prevention, etc.) as needed.
4. Click **Save Changes**.

---

## 13. Using the System on a Mobile Device

Chilli Care is fully optimised for smartphones and tablets.

**Step 1.** Open your mobile browser and navigate to the application address.

**Step 2.** The interface will automatically adjust to your screen size.

**Step 3.** Tap the **Camera** button to use your phone camera directly — no separate app is required.

**Step 4.** For the best experience on mobile, tap **Add to Home Screen** from your browser menu. This installs Chilli Care as a Progressive Web App (PWA), which:
- Loads faster on repeat visits
- Works partially offline using cached pages
- Behaves like a native app without requiring a download from an app store

---

## 14. Notifications

When logged in, you may receive in-app notifications for:
- System-wide announcements from administrators
- Disease alerts relevant to your region

**To view notifications:**

1. Look for the **bell icon** in the navigation bar.
2. Click it to open the notifications panel.
3. Unread notifications are highlighted.

---

## 15. Troubleshooting Common Problems

| Problem | Likely Cause | What to Do |
|---|---|---|
| "Invalid image" error after upload | The image does not appear to contain a chilli plant leaf | Retake the photo focusing on a clear leaf in good lighting |
| Detection result shows low confidence (below 50%) | The image is blurry, too dark, or the leaf is partially obscured | Capture a clearer, well-lit image and try again |
| Camera permission denied | Browser blocked camera access | Go to your browser settings, allow camera access for this site, then reload the page |
| Page not loading | No internet connection or server is offline | Check your connection; if the problem continues, try refreshing or contact support |
| Login fails with correct credentials | Session expired or account issue | Clear browser cookies, reload the page, and try again |
| History page shows no records | You are not logged in | Log in first, then revisit the History page |
| Contact form not sending | Email fields left blank or invalid email | Check all required fields are filled correctly and resubmit |

---

## Quick Reference — Navigation Summary

| Page | URL | Who Can Access |
|---|---|---|
| Home / Disease Detection | `/` | Everyone |
| Disease Reference Guide | `/diseases` | Everyone |
| Analytics Dashboard | `/analytics` | Everyone |
| Contact Form | `/contact` | Everyone |
| About Page | `/about` | Everyone |
| FAQs | `/faqs` | Everyone |
| Login | `/login` | Everyone |
| Sign Up | `/signup` | Everyone |
| Prediction History | `/history` | Logged-in users |
| Admin Dashboard | `/admin/dashboard` | Admins only |

---

*Chilli Care — Protecting Chilli Crops with AI Intelligence*
